"""Build a first-pass collaboration network from selected songs.

This script stays within the selected-song dataset and MusicBrainz recording
search only. It supports resuming from partial outputs by re-reading the lookup
CSV and rebuilding graph state before continuing.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import networkx as nx
import requests

try:
    from pyvis.network import Network
except ImportError as exc:  # pragma: no cover - surfaced at runtime
    print("PyVis is required for this script.")
    print("Please run: pip install pyvis")
    raise SystemExit(1) from exc


ROOT = Path(__file__).resolve().parents[2]
EXPANDED_USABLE_MATCHES_CSV = ROOT / "data" / "network" / "expanded_usable_artist_matches.csv"
USABLE_MATCHES_CSV = EXPANDED_USABLE_MATCHES_CSV if EXPANDED_USABLE_MATCHES_CSV.exists() else ROOT / "data" / "network" / "usable_artist_matches.csv"
SONG_SOURCE_CSV = ROOT / "data" / "lyrics_data" / "lyrics_with_sentiment_translated.csv"
LOOKUP_CSV = ROOT / "data" / "network" / "selected_song_recording_lookup.csv"
EDGES_CSV = ROOT / "data" / "network" / "selected_song_collaboration_edges.csv"
NODES_CSV = ROOT / "data" / "network" / "selected_song_collaboration_nodes.csv"
GRAPH_JSON = ROOT / "data" / "network" / "selected_song_artist_network.json"
SUMMARY_TXT = ROOT / "data" / "network" / "selected_song_network_summary.txt"
HTML_PATH = ROOT / "website" / "public" / "network" / "selected_song_artist_network.html"
CACHE_DIR = ROOT / "data" / "network" / "cache" / "recording_search"

BASE_URL = "https://musicbrainz.org/ws/2/"
USER_AGENT = "CSS-Project-A/1.0"
REQUEST_DELAY_SECONDS = 1
MAX_SONGS_PER_ARTIST = 15
SEARCH_LIMIT = 10
HTML_NODE_LIMIT = 200

LOOKUP_COLUMNS = [
    "input_artist_name",
    "input_song_title",
    "seed_artist_mbid",
    "recording_title",
    "recording_mbid",
    "first_date",
    "year",
    "credited_artist_names",
    "credited_artist_mbids",
    "musicbrainz_score",
    "lookup_strategy_used",
    "lookup_status",
    "country",
    "period",
]

EDGE_COLUMNS = [
    "artist_a_name",
    "artist_a_mbid",
    "artist_b_name",
    "artist_b_mbid",
    "weight",
    "recordings",
    "recording_mbids",
    "recording_titles",
    "recording_years",
    "source_artists",
    "source_countries",
    "source_periods",
]

NODE_COLUMNS = [
    "artist_name",
    "artist_mbid",
    "recording_count",
    "weighted_degree",
    "degree",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_str(row: Dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None:
        return ""
    return str(value).strip()


def safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return fallback


def normalize_name(value: str) -> str:
    text = (value or "").lower().strip()
    text = text.replace("’", "'").replace("`", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^\w\s]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text(value: str) -> str:
    text = (value or "").strip()
    text = text.replace("’", "'").replace("`", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\((feat\.|featuring|ft\.|with).*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[\u2010-\u2015\-_/|]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def query_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def cache_key_for_query(strategy: str, artist_name: str, song_title: str, query: str) -> str:
    digest = hashlib.sha1(f"{strategy}\n{artist_name}\n{song_title}\n{query}".encode("utf-8")).hexdigest()[:12]
    slug_artist = re.sub(r"[^a-z0-9]+", "_", normalize_name(artist_name))[:32] or "artist"
    slug_song = re.sub(r"[^a-z0-9]+", "_", normalize_name(song_title))[:32] or "song"
    return f"{slug_artist}__{slug_song}__{strategy}__{digest}.json"


def load_cached_response(strategy: str, artist_name: str, song_title: str, query: str) -> Optional[Dict[str, Any]]:
    cache_path = CACHE_DIR / cache_key_for_query(strategy, artist_name, song_title, query)
    if not cache_path.exists():
        return None
    with cache_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_cached_response(strategy: str, artist_name: str, song_title: str, query: str, payload: Dict[str, Any]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / cache_key_for_query(strategy, artist_name, song_title, query)
    with cache_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def search_musicbrainz_recordings(strategy: str, query: str, artist_name: str, song_title: str) -> Dict[str, Any]:
    cached = load_cached_response(strategy, artist_name, song_title, query)
    if cached is not None:
        return cached

    url = f"{BASE_URL}recording/"
    params = {"query": query, "fmt": "json", "limit": SEARCH_LIMIT}
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return {"error": f"connection_error: {exc}", "recordings": [], "query": query}

    time.sleep(REQUEST_DELAY_SECONDS)

    if response.status_code != 200:
        return {
            "error": f"bad_status_code: {response.status_code}",
            "status_code": response.status_code,
            "response_text": response.text[:1000],
            "recordings": [],
            "query": query,
        }

    try:
        payload = response.json()
    except ValueError:
        return {"error": "json_decode_error", "recordings": [], "query": query}

    payload["query"] = query
    save_cached_response(strategy, artist_name, song_title, query, payload)
    return payload


def split_delimited(value: str) -> List[str]:
    if not value:
        return []
    parts = [part.strip() for part in value.split("|")]
    return [part for part in parts if part]


def parse_recording_credit(recording: Dict[str, Any]) -> Tuple[List[str], List[str], str]:
    names: List[str] = []
    mbids: List[str] = []
    phrases: List[str] = []
    for credit in recording.get("artist-credit", []) or []:
        if not isinstance(credit, dict):
            continue
        if credit.get("name"):
            phrases.append(str(credit.get("name")).strip())
        artist = credit.get("artist")
        if isinstance(artist, dict):
            name = get_str(artist, "name")
            mbid = get_str(artist, "id")
            if name:
                names.append(name)
            if mbid:
                mbids.append(mbid)
    phrase = get_str(recording, "artist-credit-phrase") or " ".join(phrases)
    return names, mbids, phrase


def recording_date(recording: Dict[str, Any]) -> str:
    for key in ("first-release-date", "date"):
        value = get_str(recording, key)
        if value:
            return value
    return ""


def recording_year(recording: Dict[str, Any]) -> str:
    date_value = recording_date(recording)
    return date_value[:4] if date_value else ""


def candidate_recordings(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return payload.get("recordings", []) if isinstance(payload, dict) else []


def recording_has_seed_artist(recording: Dict[str, Any], artist_row: Dict[str, str]) -> bool:
    names, mbids, phrase = parse_recording_credit(recording)
    seed_names = {
        normalize_name(get_str(artist_row, "input_artist_name")),
        normalize_name(get_str(artist_row, "matched_name")),
    }
    seed_mbid = get_str(artist_row, "mbid")

    if seed_mbid and seed_mbid in mbids:
        return True
    normalized_names = {normalize_name(name) for name in names}
    if seed_names & normalized_names:
        return True
    if any(seed_name and seed_name in normalize_name(phrase) for seed_name in seed_names):
        return True
    return False


def title_similarity(left: str, right: str) -> float:
    left_n = normalize_name(left)
    right_n = normalize_name(right)
    if not left_n or not right_n:
        return 0.0
    if left_n == right_n:
        return 1.0
    if left_n in right_n or right_n in left_n:
        return 0.9
    return 0.0


def choose_best_recording(
    artist_row: Dict[str, str],
    song_title: str,
    candidate_set: List[Dict[str, Any]],
    strategy: str,
) -> Optional[Dict[str, Any]]:
    if not candidate_set:
        return None

    scored: List[Tuple[float, Dict[str, Any]]] = []
    seed_artist_name = get_str(artist_row, "input_artist_name")
    for recording in candidate_set:
        score = safe_int(recording.get("score"), 0)
        candidate_title = get_str(recording, "title")
        title_score = title_similarity(song_title, candidate_title)
        artist_match = recording_has_seed_artist(recording, artist_row)
        if strategy in {"title_only", "clean_title_only"} and not artist_match:
            continue
        combined = score + (20 * title_score) + (15 if artist_match else 0)
        scored.append((combined, recording))

    if not scored:
        return None

    scored.sort(key=lambda item: item[0], reverse=True)
    best = scored[0][1]
    best_score = safe_int(best.get("score"), 0)
    best_title_score = title_similarity(song_title, get_str(best, "title"))
    best_artist_match = recording_has_seed_artist(best, artist_row)

    if strategy in {"exact_artist_title", "clean_artist_title"}:
        if best_score >= 80 and (best_title_score >= 0.9 or best_artist_match):
            return best
        return None

    if strategy in {"title_only", "clean_title_only"}:
        if best_score >= 80 and best_artist_match and best_title_score >= 0.9:
            return best
        return None

    return None


def build_queries(artist_name: str, song_title: str) -> List[Tuple[str, str]]:
    exact_artist = query_literal(artist_name)
    clean_artist = query_literal(clean_text(artist_name))
    exact_title = query_literal(song_title)
    clean_title = query_literal(clean_text(song_title))

    return [
        ("exact_artist_title", f'artist:"{exact_artist}" AND recording:"{exact_title}"'),
        ("clean_artist_title", f'artist:"{clean_artist}" AND recording:"{clean_title}"'),
        ("title_only", f'recording:"{exact_title}"'),
        ("clean_title_only", f'recording:"{clean_title}"'),
    ]


def select_song_rows(song_rows: List[Dict[str, str]], artist_row: Dict[str, str]) -> List[Dict[str, str]]:
    artist_keys = {
        normalize_name(get_str(artist_row, "input_artist_name")),
        normalize_name(get_str(artist_row, "matched_name")),
    }
    rows = [
        row
        for row in song_rows
        if normalize_name(get_str(row, "artist")) in artist_keys
    ]
    rows.sort(
        key=lambda row: (
            safe_int(get_str(row, "year"), 9999),
            normalize_name(get_str(row, "song_title")),
        )
    )

    deduped: List[Dict[str, str]] = []
    seen = set()
    for row in rows:
        key = (normalize_name(get_str(row, "song_title")), get_str(row, "year"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
    return deduped[:MAX_SONGS_PER_ARTIST]


def artist_song_buckets(usable_artists: List[Dict[str, str]], song_rows: List[Dict[str, str]]) -> List[Tuple[Dict[str, str], List[Dict[str, str]]]]:
    buckets: List[Tuple[Dict[str, str], List[Dict[str, str]]]] = []
    for artist_row in usable_artists:
        rows = select_song_rows(song_rows, artist_row)
        if rows:
            buckets.append((artist_row, rows))
    buckets.sort(key=lambda item: (-len(item[1]), get_str(item[0], "input_artist_name").lower()))
    return buckets


def lookup_key(artist_name: str, song_title: str, year: str) -> Tuple[str, str, str]:
    return normalize_name(artist_name), normalize_name(song_title), str(year).strip()


def build_lookup_row(
    artist_row: Dict[str, str],
    song_row: Dict[str, str],
    strategy: str,
    status: str,
    recording: Optional[Dict[str, Any]],
) -> Dict[str, str]:
    row = {
        "input_artist_name": get_str(artist_row, "input_artist_name"),
        "input_song_title": get_str(song_row, "song_title"),
        "seed_artist_mbid": get_str(artist_row, "mbid"),
        "recording_title": "",
        "recording_mbid": "",
        "first_date": "",
        "year": "",
        "credited_artist_names": "",
        "credited_artist_mbids": "",
        "musicbrainz_score": "",
        "lookup_strategy_used": strategy,
        "lookup_status": status,
        "country": get_str(song_row, "country"),
        "period": get_str(song_row, "period"),
    }

    if recording is not None:
        names, mbids, _ = parse_recording_credit(recording)
        row.update(
            {
                "recording_title": get_str(recording, "title"),
                "recording_mbid": get_str(recording, "id"),
                "first_date": recording_date(recording),
                "year": recording_year(recording) or get_str(song_row, "year"),
                "credited_artist_names": " | ".join(names),
                "credited_artist_mbids": " | ".join(mbids),
                "musicbrainz_score": get_str(recording, "score"),
            }
        )
    return row


def load_existing_lookup_rows() -> List[Dict[str, str]]:
    if not LOOKUP_CSV.exists():
        return []
    return read_csv(LOOKUP_CSV)


def rebuild_graph_from_lookup_rows(rows: List[Dict[str, str]]) -> Tuple[nx.Graph, Dict[Tuple[str, str], Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    graph = nx.Graph()
    edge_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
    node_map: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "artist_name": "",
            "artist_mbid": "",
            "recording_count": 0,
            "weighted_degree": 0,
            "degree": 0,
        }
    )

    for row in rows:
        if get_str(row, "lookup_status") != "matched":
            continue
        names = split_delimited(get_str(row, "credited_artist_names"))
        mbids = split_delimited(get_str(row, "credited_artist_mbids"))
        if len(names) < 2:
            continue

        title = get_str(row, "recording_title")
        recording_mbid = get_str(row, "recording_mbid")
        year_value = get_str(row, "year")
        seed_artist = get_str(row, "input_artist_name")
        country = get_str(row, "country")
        period = get_str(row, "period")

        for index, name in enumerate(names):
            key = normalize_name(name)
            node = node_map[key]
            node["artist_name"] = name
            if index < len(mbids) and mbids[index] and not node["artist_mbid"]:
                node["artist_mbid"] = mbids[index]
            node["recording_count"] += 1

        for i, j in combinations(range(len(names)), 2):
            name_a = names[i]
            name_b = names[j]
            mbid_a = mbids[i] if i < len(mbids) else ""
            mbid_b = mbids[j] if j < len(mbids) else ""
            key = tuple(sorted([normalize_name(name_a), normalize_name(name_b)]))
            if key not in edge_map:
                edge_map[key] = {
                    "artist_a_name": name_a if normalize_name(name_a) == key[0] else name_b,
                    "artist_a_mbid": mbid_a if normalize_name(name_a) == key[0] else mbid_b,
                    "artist_b_name": name_b if normalize_name(name_b) == key[1] else name_a,
                    "artist_b_mbid": mbid_b if normalize_name(name_b) == key[1] else mbid_a,
                    "weight": 0,
                    "recordings": [],
                    "recording_mbids": [],
                    "recording_titles": [],
                    "recording_years": [],
                    "source_artists": [],
                    "source_countries": [],
                    "source_periods": [],
                }

            edge = edge_map[key]
            edge["weight"] += 1
            edge["recordings"].append(title)
            edge["recording_mbids"].append(recording_mbid)
            edge["recording_titles"].append(f"{title} ({year_value})" if year_value else title)
            if year_value:
                edge["recording_years"].append(year_value)
            edge["source_artists"].append(seed_artist)
            edge["source_countries"].append(country)
            edge["source_periods"].append(period)

    edge_rows = edge_rows_from_map(edge_map)
    node_rows = node_rows_from_map(node_map, edge_rows)

    for node in node_rows:
        graph.add_node(
            node["artist_name"],
            mbid=node["artist_mbid"],
            recording_count=node["recording_count"],
            weighted_degree=node["weighted_degree"],
            degree=node["degree"],
        )
    for edge in edge_rows:
        graph.add_edge(
            edge["artist_a_name"],
            edge["artist_b_name"],
            weight=edge["weight"],
            recordings=edge["recordings"],
            recording_mbids=edge["recording_mbids"],
            recording_titles=edge["recording_titles"],
            recording_years=edge["recording_years"],
            source_artists=edge["source_artists"],
            source_countries=edge["source_countries"],
            source_periods=edge["source_periods"],
        )

    return graph, edge_map, node_map


def edge_rows_from_map(edge_map: Dict[Tuple[str, str], Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for key, edge in sorted(edge_map.items(), key=lambda item: (-item[1]["weight"], item[0][0], item[0][1])):
        rows.append(
            {
                "artist_a_name": edge["artist_a_name"],
                "artist_a_mbid": edge["artist_a_mbid"],
                "artist_b_name": edge["artist_b_name"],
                "artist_b_mbid": edge["artist_b_mbid"],
                "weight": edge["weight"],
                "recordings": "; ".join(edge["recordings"]),
                "recording_mbids": "; ".join(edge["recording_mbids"]),
                "recording_titles": "; ".join(edge["recording_titles"]),
                "recording_years": "; ".join(edge["recording_years"]),
                "source_artists": "; ".join(sorted(set(filter(None, edge["source_artists"])))),
                "source_countries": "; ".join(sorted(set(filter(None, edge["source_countries"])))),
                "source_periods": "; ".join(sorted(set(filter(None, edge["source_periods"])))),
            }
        )
    return rows


def node_rows_from_map(node_map: Dict[str, Dict[str, Any]], edge_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for key, node in sorted(node_map.items(), key=lambda item: (-item[1]["recording_count"], item[1]["artist_name"].lower())):
        degree = 0
        weighted_degree = 0
        for edge in edge_rows:
            if normalize_name(edge["artist_a_name"]) == key or normalize_name(edge["artist_b_name"]) == key:
                degree += 1
                weighted_degree += safe_int(edge["weight"], 0)
        rows.append(
            {
                "artist_name": node["artist_name"],
                "artist_mbid": node["artist_mbid"],
                "recording_count": node["recording_count"],
                "weighted_degree": weighted_degree,
                "degree": degree,
            }
        )
    return rows


def build_graph_json(node_rows: List[Dict[str, Any]], edge_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "nodes": [
            {
                "id": node["artist_name"],
                "artist_name": node["artist_name"],
                "artist_mbid": node["artist_mbid"],
                "recording_count": node["recording_count"],
                "weighted_degree": node["weighted_degree"],
                "degree": node["degree"],
            }
            for node in node_rows
        ],
        "edges": [
            {
                "source": edge["artist_a_name"],
                "target": edge["artist_b_name"],
                "weight": edge["weight"],
                "recordings": split_delimited(edge["recordings"].replace("; ", "|")) if edge["recordings"] else [],
                "recording_titles": split_delimited(edge["recording_titles"].replace("; ", "|")) if edge["recording_titles"] else [],
                "recording_years": split_delimited(edge["recording_years"].replace("; ", "|")) if edge["recording_years"] else [],
            }
            for edge in edge_rows
        ],
    }


def choose_html_subgraph(graph: nx.Graph, node_rows: List[Dict[str, Any]]) -> nx.Graph:
    if graph.number_of_nodes() == 0:
        return graph
    if graph.number_of_edges() == 0:
        top_nodes = [row["artist_name"] for row in sorted(node_rows, key=lambda row: (-row["recording_count"], row["artist_name"].lower()))[:HTML_NODE_LIMIT]]
        return graph.subgraph(top_nodes).copy()

    components = sorted(nx.connected_components(graph), key=len, reverse=True)
    largest = graph.subgraph(components[0]).copy()
    if largest.number_of_nodes() <= HTML_NODE_LIMIT:
        return largest

    weighted_nodes = sorted(
        largest.nodes(),
        key=lambda name: (
            -largest.nodes[name].get("weighted_degree", 0),
            -largest.nodes[name].get("recording_count", 0),
            name.lower(),
        ),
    )[:HTML_NODE_LIMIT]
    return largest.subgraph(weighted_nodes).copy()


def build_pyvis_html(graph: nx.Graph, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    net = Network(height="850px", width="100%", bgcolor="#111111", font_color="#f1f1f1", notebook=False)
    net.barnes_hut(gravity=-5000, central_gravity=0.25, spring_length=180, spring_strength=0.04, damping=0.09, overlap=0)

    max_weighted_degree = max((graph.nodes[node].get("weighted_degree", 1) for node in graph.nodes), default=1)
    for node, data in graph.nodes(data=True):
        weighted_degree = data.get("weighted_degree", 0)
        recording_count = data.get("recording_count", 0)
        size = 10 + (weighted_degree / max_weighted_degree) * 28 if max_weighted_degree else 10
        title_lines = [
            f"Artist: {node}",
            f"MusicBrainz ID: {data.get('mbid', '')}",
            f"Recordings: {recording_count}",
            f"Weighted degree: {weighted_degree}",
        ]
        net.add_node(
            node,
            label=node,
            title="<br>".join(title_lines),
            value=recording_count,
            size=size,
        )

    for left, right, data in graph.edges(data=True):
        weight = data.get("weight", 1)
        title = "<br>".join(
            [
                f"Weight: {weight}",
                f"Recordings: {data.get('recording_titles', '')}",
                f"Seed artists: {data.get('source_artists', '')}",
            ]
        )
        net.add_edge(left, right, value=weight, width=1 + weight, title=title)

    net.set_options(
        """
        var options = {
          "nodes": {"borderWidth": 1, "font": {"size": 18}},
          "edges": {"smooth": {"type": "dynamic"}, "color": {"inherit": true}},
          "physics": {"stabilization": {"iterations": 250}}
        }
        """
    )
    net.write_html(str(path), open_browser=False)


def recording_credit_count(row: Dict[str, str]) -> int:
    names = split_delimited(get_str(row, "credited_artist_names"))
    mbids = split_delimited(get_str(row, "credited_artist_mbids"))
    if len(names) < 2:
        return 0
    if mbids and any(mbids) and len(mbids) < 2:
        return 0
    return len(names)


def update_outputs(
    lookup_rows: List[Dict[str, str]],
    edge_rows: List[Dict[str, Any]],
    node_rows: List[Dict[str, Any]],
    graph_json: Dict[str, Any],
    summary_text: str,
) -> None:
    write_csv(LOOKUP_CSV, lookup_rows, LOOKUP_COLUMNS)
    write_csv(EDGES_CSV, edge_rows, EDGE_COLUMNS)
    write_csv(NODES_CSV, node_rows, NODE_COLUMNS)
    GRAPH_JSON.write_text(json.dumps(graph_json, ensure_ascii=False, indent=2), encoding="utf-8")
    SUMMARY_TXT.write_text(summary_text, encoding="utf-8")


def summarize_results(
    usable_artists_considered: int,
    artists_with_songs: int,
    lookup_rows: List[Dict[str, str]],
    edge_rows: List[Dict[str, Any]],
    node_rows: List[Dict[str, Any]],
    strategy_attempts: Counter,
    strategy_successes: Counter,
) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    successful_rows = [row for row in lookup_rows if get_str(row, "lookup_status") == "matched"]
    usable_date_rows = [row for row in successful_rows if get_str(row, "first_date") or get_str(row, "year")]
    multi_credit_rows = [row for row in successful_rows if recording_credit_count(row) >= 2]

    top_nodes = sorted(node_rows, key=lambda row: (-row["weighted_degree"], -row["recording_count"], row["artist_name"].lower()))[:20]
    top_edges = sorted(edge_rows, key=lambda row: (-safe_int(row["weight"], 0), row["artist_a_name"].lower(), row["artist_b_name"].lower()))[:20]
    no_match_examples = [row for row in lookup_rows if get_str(row, "lookup_status") != "matched"][:10]

    match_rate = round((len(successful_rows) / len(lookup_rows)) * 100, 1) if lookup_rows else 0.0
    lines = [
        "Selected-song collaboration network summary",
        "",
        f"Usable artists considered: {usable_artists_considered}",
        f"Artists with selected songs: {artists_with_songs}",
        f"Artist-song queries: {len(lookup_rows)}",
        f"Successful recording matches: {len(successful_rows)}",
        f"Match rate: {match_rate}%",
        f"Recordings with 2+ credited artists: {len(multi_credit_rows)}",
        f"Nodes: {len(node_rows)}",
        f"Edges: {len(edge_rows)}",
        f"Matches with usable year/date: {len(usable_date_rows)}",
        "",
        "Lookup success by strategy:",
    ]

    for strategy in ("exact_artist_title", "clean_artist_title", "title_only", "clean_title_only"):
        lines.append(
            f"- {strategy}: attempted={strategy_attempts[strategy]} successful={strategy_successes[strategy]}"
        )

    lines.extend([
        "",
        "Top 20 nodes by weighted degree:",
    ])
    for row in top_nodes:
        lines.append(
            f"- {row['artist_name']} | weighted_degree={row['weighted_degree']} | degree={row['degree']} | recordings={row['recording_count']}"
        )

    lines.extend([
        "",
        "Top 20 edges by weight:",
    ])
    for row in top_edges:
        lines.append(
            f"- {row['artist_a_name']} -- {row['artist_b_name']} | weight={row['weight']} | recordings={row['recording_titles']}"
        )

    lines.extend([
        "",
        "Sample no-match rows:",
    ])
    for row in no_match_examples:
        lines.append(f"- {row['input_artist_name']} / {row['input_song_title']} -> {row['lookup_status']}")

    lines.extend([
        "",
        f"Lookup CSV: {LOOKUP_CSV}",
        f"Edges CSV: {EDGES_CSV}",
        f"Nodes CSV: {NODES_CSV}",
        f"Graph JSON: {GRAPH_JSON}",
        f"HTML: {HTML_PATH}",
    ])

    return "\n".join(lines) + "\n", top_nodes, top_edges, no_match_examples


def main() -> None:
    usable_artists = read_csv(USABLE_MATCHES_CSV)
    song_rows = read_csv(SONG_SOURCE_CSV)

    existing_lookup_rows = load_existing_lookup_rows()
    processed_keys = {
        lookup_key(get_str(row, "input_artist_name"), get_str(row, "input_song_title"), get_str(row, "year"))
        for row in existing_lookup_rows
    }

    graph, edge_map, node_map = rebuild_graph_from_lookup_rows(existing_lookup_rows)
    lookup_rows = list(existing_lookup_rows)

    artist_buckets = artist_song_buckets(usable_artists, song_rows)
    considered_artists = len(usable_artists)
    artists_with_songs = len(artist_buckets)

    strategy_attempts: Counter = Counter()
    strategy_successes: Counter = Counter()
    total_queries = len(lookup_rows)
    matched_queries = sum(1 for row in lookup_rows if get_str(row, "lookup_status") == "matched")

    for artist_index, (artist_row, artist_songs) in enumerate(artist_buckets, start=1):
        artist_name = get_str(artist_row, "input_artist_name")
        print(f"[{artist_index}/{len(artist_buckets)}] Artist: {artist_name} ({len(artist_songs)} songs)")

        artist_added = False
        for song_row in artist_songs:
            song_title = get_str(song_row, "song_title")
            source_year = get_str(song_row, "year")
            key = lookup_key(artist_name, song_title, source_year)
            if key in processed_keys:
                continue

            total_queries += 1
            matched_recording: Optional[Dict[str, Any]] = None
            used_strategy = "none"
            final_status = "no_match"

            for strategy, query in build_queries(artist_name, song_title):
                strategy_attempts[strategy] += 1
                payload = search_musicbrainz_recordings(strategy, query, artist_name, song_title)
                recordings = candidate_recordings(payload)
                best = choose_best_recording(artist_row, song_title, recordings, strategy)
                if best is None:
                    continue

                matched_recording = best
                used_strategy = strategy
                final_status = "matched"
                strategy_successes[strategy] += 1
                break

            lookup_row = build_lookup_row(artist_row, song_row, used_strategy, final_status, matched_recording)
            lookup_rows.append(lookup_row)
            processed_keys.add(key)

            if final_status == "matched" and matched_recording is not None:
                matched_queries += 1
                artist_added = True
                names, mbids, _ = parse_recording_credit(matched_recording)
                if len(names) >= 2:
                    title = get_str(matched_recording, "title")
                    recording_mbid = get_str(matched_recording, "id")
                    year_value = recording_year(matched_recording) or get_str(song_row, "year")
                    country = get_str(song_row, "country")
                    period = get_str(song_row, "period")
                    seed_artist = artist_name

                    for idx, name in enumerate(names):
                        node_key = normalize_name(name)
                        node = node_map[node_key]
                        node["artist_name"] = name
                        if idx < len(mbids) and mbids[idx] and not node["artist_mbid"]:
                            node["artist_mbid"] = mbids[idx]
                        node["recording_count"] += 1

                    for i, j in combinations(range(len(names)), 2):
                        name_a = names[i]
                        name_b = names[j]
                        mbid_a = mbids[i] if i < len(mbids) else ""
                        mbid_b = mbids[j] if j < len(mbids) else ""
                        edge_key = tuple(sorted([normalize_name(name_a), normalize_name(name_b)]))
                        if edge_key not in edge_map:
                            edge_map[edge_key] = {
                                "artist_a_name": name_a if normalize_name(name_a) == edge_key[0] else name_b,
                                "artist_a_mbid": mbid_a if normalize_name(name_a) == edge_key[0] else mbid_b,
                                "artist_b_name": name_b if normalize_name(name_b) == edge_key[1] else name_a,
                                "artist_b_mbid": mbid_b if normalize_name(name_b) == edge_key[1] else mbid_a,
                                "weight": 0,
                                "recordings": [],
                                "recording_mbids": [],
                                "recording_titles": [],
                                "recording_years": [],
                                "source_artists": [],
                                "source_countries": [],
                                "source_periods": [],
                            }

                        edge = edge_map[edge_key]
                        edge["weight"] += 1
                        edge["recordings"].append(title)
                        edge["recording_mbids"].append(recording_mbid)
                        edge["recording_titles"].append(f"{title} ({year_value})" if year_value else title)
                        if year_value:
                            edge["recording_years"].append(year_value)
                        edge["source_artists"].append(seed_artist)
                        edge["source_countries"].append(country)
                        edge["source_periods"].append(period)

            if artist_added and len([row for row in lookup_rows if get_str(row, "input_artist_name") == artist_name]) % 5 == 0:
                edge_rows = edge_rows_from_map(edge_map)
                node_rows = node_rows_from_map(node_map, edge_rows)
                graph_json = build_graph_json(node_rows, edge_rows)
                summary_text, _, _, _ = summarize_results(
                    considered_artists,
                    artists_with_songs,
                    lookup_rows,
                    edge_rows,
                    node_rows,
                    strategy_attempts,
                    strategy_successes,
                )
                update_outputs(lookup_rows, edge_rows, node_rows, graph_json, summary_text)

        # Save after each artist to avoid losing progress.
        edge_rows = edge_rows_from_map(edge_map)
        node_rows = node_rows_from_map(node_map, edge_rows)
        graph_json = build_graph_json(node_rows, edge_rows)
        summary_text, _, _, _ = summarize_results(
            considered_artists,
            artists_with_songs,
            lookup_rows,
            edge_rows,
            node_rows,
            strategy_attempts,
            strategy_successes,
        )
        update_outputs(lookup_rows, edge_rows, node_rows, graph_json, summary_text)

    edge_rows = edge_rows_from_map(edge_map)
    node_rows = node_rows_from_map(node_map, edge_rows)
    graph_json = build_graph_json(node_rows, edge_rows)
    summary_text, top_nodes, top_edges, no_match_examples = summarize_results(
        considered_artists,
        artists_with_songs,
        lookup_rows,
        edge_rows,
        node_rows,
        strategy_attempts,
        strategy_successes,
    )
    update_outputs(lookup_rows, edge_rows, node_rows, graph_json, summary_text)

    graph_for_html = nx.Graph()
    for node in node_rows:
        graph_for_html.add_node(
            node["artist_name"],
            mbid=node["artist_mbid"],
            recording_count=node["recording_count"],
            weighted_degree=node["weighted_degree"],
            degree=node["degree"],
        )
    for edge in edge_rows:
        graph_for_html.add_edge(
            edge["artist_a_name"],
            edge["artist_b_name"],
            weight=edge["weight"],
            recording_titles=edge["recording_titles"],
            source_artists=edge["source_artists"],
        )
    graph_for_html = choose_html_subgraph(graph_for_html, node_rows)
    build_pyvis_html(graph_for_html, HTML_PATH)

    print(f"Usable artists considered: {considered_artists}")
    print(f"Artists with selected songs: {artists_with_songs}")
    print(f"Artist-song queries: {len(lookup_rows)}")
    print(f"Successful recording matches: {sum(1 for row in lookup_rows if get_str(row, 'lookup_status') == 'matched')}")
    print(f"Recordings with 2+ credited artists: {sum(1 for row in lookup_rows if get_str(row, 'lookup_status') == 'matched' and recording_credit_count(row) >= 2)}")
    print(f"Nodes: {len(node_rows)}")
    print(f"Edges: {len(edge_rows)}")
    print("Top 20 edges by weight:")
    for row in top_edges[:20]:
        print(f"- {row['artist_a_name']} -- {row['artist_b_name']} | weight={row['weight']} | recordings={row['recording_titles']}")
    print(f"Output lookup CSV: {LOOKUP_CSV}")
    print(f"Output edges CSV: {EDGES_CSV}")
    print(f"Output nodes CSV: {NODES_CSV}")
    print(f"Output graph JSON: {GRAPH_JSON}")
    print(f"Output summary TXT: {SUMMARY_TXT}")
    print(f"Output HTML: {HTML_PATH}")


if __name__ == "__main__":
    main()