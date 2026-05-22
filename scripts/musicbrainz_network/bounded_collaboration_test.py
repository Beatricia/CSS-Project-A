"""Bounded collaboration lookup/build test using existing selected songs.

The script samples a limited set of usable artists, looks up a small number of
their already-selected songs against MusicBrainz recordings, and converts the
successful multi-credit recordings into a tiny collaboration graph.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import networkx as nx
except ImportError as exc:  # pragma: no cover - handled in script output
    print("NetworkX is required for this script.")
    print("Please run: pip install networkx")
    raise SystemExit(1) from exc

import requests


ROOT = Path(__file__).resolve().parents[2]
USABLE_MATCHES_CSV = ROOT / "data" / "network" / "usable_artist_matches.csv"
SONG_SOURCE_CSV = ROOT / "data" / "lyrics_data" / "lyrics_with_sentiment_translated.csv"
OUTPUT_LOOKUP_CSV = ROOT / "data" / "network" / "bounded_recording_lookup.csv"
OUTPUT_EDGES_CSV = ROOT / "data" / "network" / "bounded_collaboration_edges.csv"
OUTPUT_NODES_CSV = ROOT / "data" / "network" / "bounded_collaboration_nodes.csv"
OUTPUT_GRAPH_JSON = ROOT / "data" / "network" / "bounded_artist_network.json"
OUTPUT_SUMMARY_TXT = ROOT / "data" / "network" / "bounded_collaboration_summary.txt"
CACHE_DIR = ROOT / "data" / "network" / "cache" / "recording_search"

BASE_URL = "https://musicbrainz.org/ws/2/"
USER_AGENT = "CSS-Project-A/1.0"
REQUEST_DELAY_SECONDS = 1
MAX_SAMPLE_ARTISTS = 20
MAX_SONGS_PER_ARTIST = 3
SEARCH_LIMIT = 8

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
    "source_artist_match_name",
    "source_song_year",
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


@dataclass(frozen=True)
class StrategyResult:
    strategy: str
    status: str
    recording: Optional[Dict[str, Any]]


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


def clean_title(value: str) -> str:
    text = (value or "").strip()
    text = text.replace("’", "'").replace("`", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\((feat\.|featuring|ft\.|with).*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\[.*?\]", "", text)
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[\u2010-\u2015\-_/|]+", " ", text)
    text = re.sub(r"[^\w\s]+", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def query_string_literal(value: str) -> str:
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


def save_cached_response(strategy: str, artist_name: str, song_title: str, query: str, payload: Dict[str, Any]) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / cache_key_for_query(strategy, artist_name, song_title, query)
    with cache_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return cache_path


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


def year_from_date(date_value: str) -> str:
    return date_value[:4] if date_value else ""


def candidate_recordings(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    return payload.get("recordings", []) if isinstance(payload, dict) else []


def artist_match_score(artist_name: str, recording: Dict[str, Any]) -> bool:
    names, mbids, phrase = parse_recording_credit(recording)
    normalized_artist = normalize_name(artist_name)
    if any(normalized_artist == normalize_name(name) for name in names):
        return True
    if normalized_artist and normalized_artist in normalize_name(phrase):
        return True
    return False


def title_match_score(query_title: str, candidate_title: str) -> float:
    left = normalize_name(query_title)
    right = normalize_name(candidate_title)
    if not left or not right:
        return 0.0
    if left == right:
        return 1.0
    if left in right or right in left:
        return 0.9
    return 0.0


def choose_best_recording(artist_name: str, song_title: str, recordings: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not recordings:
        return None

    scored: List[Tuple[float, Dict[str, Any]]] = []
    for recording in recordings:
        score = safe_int(recording.get("score"), 0)
        title_score = title_match_score(song_title, get_str(recording, "title"))
        artist_score = 1.0 if artist_match_score(artist_name, recording) else 0.0
        combined = score + (15 * title_score) + (10 * artist_score)
        scored.append((combined, recording))

    scored.sort(key=lambda item: item[0], reverse=True)
    best = scored[0][1]
    if safe_int(best.get("score"), 0) < 70 and not artist_match_score(artist_name, best):
        return None
    return best


def build_queries(artist_name: str, song_title: str) -> List[Tuple[str, str]]:
    exact_artist = query_string_literal(artist_name)
    exact_title = query_string_literal(song_title)
    cleaned_title = query_string_literal(clean_title(song_title))

    return [
        ("exact_artist_title", f'artist:"{exact_artist}" AND recording:"{exact_title}"'),
        ("clean_artist_title", f'artist:"{exact_artist}" AND recording:"{cleaned_title}"'),
        ("title_only", f'recording:"{exact_title}"'),
        ("clean_title_only", f'recording:"{cleaned_title}"'),
    ]


def seeded_artist_song_rows(usable_artists: List[Dict[str, str]], song_rows: List[Dict[str, str]]) -> List[Tuple[Dict[str, str], List[Dict[str, str]]]]:
    artist_index: Dict[str, Dict[str, str]] = {}
    for row in usable_artists:
        for key in ("input_artist_name", "matched_name"):
            name = get_str(row, key)
            if name:
                artist_index[normalize_name(name)] = row

    song_map: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in song_rows:
        song_map[normalize_name(get_str(row, "artist"))].append(row)

    ranked: List[Tuple[int, str, Dict[str, str], List[Dict[str, str]]]] = []
    for key, artist_row in artist_index.items():
        rows = song_map.get(key, [])
        if rows:
            rows_sorted = sorted(
                rows,
                key=lambda row: (
                    safe_int(get_str(row, "year"), 9999),
                    normalize_name(get_str(row, "song_title")),
                ),
            )
            ranked.append((len(rows_sorted), get_str(artist_row, "input_artist_name").lower(), artist_row, rows_sorted[:MAX_SONGS_PER_ARTIST]))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [(artist_row, song_rows_for_artist) for _, _, artist_row, song_rows_for_artist in ranked[:MAX_SAMPLE_ARTISTS]]


def build_lookup_row(
    artist_row: Dict[str, str],
    song_row: Dict[str, str],
    strategy: str,
    status: str,
    recording: Optional[Dict[str, Any]],
) -> Dict[str, str]:
    if recording is None:
        return {
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
            "source_artist_match_name": get_str(artist_row, "matched_name"),
            "source_song_year": get_str(song_row, "year"),
        }

    credited_names, credited_mbids, _ = parse_recording_credit(recording)
    date_value = recording_date(recording)
    year_value = year_from_date(date_value) or get_str(song_row, "year")

    return {
        "input_artist_name": get_str(artist_row, "input_artist_name"),
        "input_song_title": get_str(song_row, "song_title"),
        "seed_artist_mbid": get_str(artist_row, "mbid"),
        "recording_title": get_str(recording, "title"),
        "recording_mbid": get_str(recording, "id"),
        "first_date": date_value,
        "year": year_value,
        "credited_artist_names": " | ".join(credited_names),
        "credited_artist_mbids": " | ".join(credited_mbids),
        "musicbrainz_score": get_str(recording, "score"),
        "lookup_strategy_used": strategy,
        "lookup_status": status,
        "country": get_str(song_row, "country"),
        "period": get_str(song_row, "period"),
        "source_artist_match_name": get_str(artist_row, "matched_name"),
        "source_song_year": get_str(song_row, "year"),
    }


def record_has_two_credited_artists(row: Dict[str, str]) -> bool:
    names = split_delimited(get_str(row, "credited_artist_names").replace(" | ", "|"))
    mbids = split_delimited(get_str(row, "credited_artist_mbids").replace(" | ", "|"))
    if len(names) < 2:
        return False
    if mbids and any(mbids) and len(mbids) < 2:
        return False
    return True


def edge_key(name_a: str, name_b: str) -> Tuple[str, str]:
    return tuple(sorted([normalize_name(name_a), normalize_name(name_b)]))


def main() -> None:
    usable_artists = read_csv(USABLE_MATCHES_CSV)
    song_rows = read_csv(SONG_SOURCE_CSV)

    artist_song_pairs = seeded_artist_song_rows(usable_artists, song_rows)

    lookup_rows: List[Dict[str, str]] = []
    strategy_counts = Counter()
    strategy_success_counts = Counter()
    no_match_examples: List[Dict[str, str]] = []

    for artist_row, songs_for_artist in artist_song_pairs:
        artist_name = get_str(artist_row, "input_artist_name")
        for song_row in songs_for_artist:
            song_title = get_str(song_row, "song_title")

            matched_recording: Optional[Dict[str, Any]] = None
            used_strategy = ""
            final_status = "no_match"

            for strategy, query in build_queries(artist_name, song_title):
                strategy_counts[strategy] += 1
                payload = search_musicbrainz_recordings(strategy, query, artist_name, song_title)
                recordings = candidate_recordings(payload)
                best = choose_best_recording(artist_name, song_title, recordings)

                if best is None:
                    continue

                matched_recording = best
                used_strategy = strategy
                final_status = "matched"
                strategy_success_counts[strategy] += 1
                break

            if matched_recording is None:
                lookup_rows.append(build_lookup_row(artist_row, song_row, "none", final_status, None))
                no_match_examples.append(
                    {
                        "input_artist_name": artist_name,
                        "input_song_title": song_title,
                        "lookup_status": final_status,
                    }
                )
                continue

            lookup_rows.append(build_lookup_row(artist_row, song_row, used_strategy, final_status, matched_recording))

    successful_rows = [row for row in lookup_rows if get_str(row, "lookup_status") == "matched"]
    usable_date_rows = [row for row in successful_rows if get_str(row, "first_date") or get_str(row, "year")]
    multi_credit_rows = [row for row in successful_rows if record_has_two_credited_artists(row)]

    write_csv(OUTPUT_LOOKUP_CSV, lookup_rows, LOOKUP_COLUMNS)

    graph = nx.Graph()
    edge_map: Dict[Tuple[str, str], Dict[str, Any]] = {}
    node_map: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "artist_name": "",
        "artist_mbid": "",
        "recording_count": 0,
        "weighted_degree": 0,
        "degree": 0,
    })

    used_recording_rows = 0
    for row in multi_credit_rows:
        names = split_delimited(get_str(row, "credited_artist_names").replace(" | ", "|"))
        mbids = split_delimited(get_str(row, "credited_artist_mbids").replace(" | ", "|"))
        if len(names) < 2:
            continue
        used_recording_rows += 1

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
            key = edge_key(name_a, name_b)

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

    edge_rows: List[Dict[str, Any]] = []
    for key, edge in sorted(edge_map.items(), key=lambda item: (-item[1]["weight"], item[0][0], item[0][1])):
        edge_rows.append(
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
                "source_artists": "; ".join(sorted(set(edge["source_artists"]))),
                "source_countries": "; ".join(sorted(set(filter(None, edge["source_countries"])))),
                "source_periods": "; ".join(sorted(set(filter(None, edge["source_periods"])))),
            }
        )

    node_rows: List[Dict[str, Any]] = []
    for key, node in sorted(node_map.items(), key=lambda item: (-item[1]["recording_count"], item[1]["artist_name"].lower())):
        degree = 0
        weighted_degree = 0
        for edge in edge_rows:
            if normalize_name(edge["artist_a_name"]) == key or normalize_name(edge["artist_b_name"]) == key:
                degree += 1
                weighted_degree += safe_int(edge["weight"], 0)

        graph.add_node(node["artist_name"], mbid=node["artist_mbid"], recording_count=node["recording_count"], weighted_degree=weighted_degree, degree=degree)
        node_rows.append(
            {
                "artist_name": node["artist_name"],
                "artist_mbid": node["artist_mbid"],
                "recording_count": node["recording_count"],
                "weighted_degree": weighted_degree,
                "degree": degree,
            }
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

    graph_json = {
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
                "recordings": edge["recordings"].split("; ") if edge["recordings"] else [],
                "recording_titles": edge["recording_titles"].split("; ") if edge["recording_titles"] else [],
                "recording_years": edge["recording_years"].split("; ") if edge["recording_years"] else [],
            }
            for edge in edge_rows
        ],
    }

    write_csv(OUTPUT_EDGES_CSV, edge_rows, EDGE_COLUMNS)
    write_csv(OUTPUT_NODES_CSV, node_rows, NODE_COLUMNS)
    OUTPUT_GRAPH_JSON.write_text(json.dumps(graph_json, ensure_ascii=False, indent=2), encoding="utf-8")

    top_nodes = sorted(node_rows, key=lambda row: (-row["weighted_degree"], -row["recording_count"], row["artist_name"].lower()))[:10]
    top_edges = sorted(edge_rows, key=lambda row: (-safe_int(row["weight"], 0), row["artist_a_name"].lower(), row["artist_b_name"].lower()))[:10]

    summary_lines = [
        "Bounded MusicBrainz collaboration test summary",
        "",
        f"Sampled artists: {len(artist_song_pairs)}",
        f"Artist-song queries: {len(lookup_rows)}",
        f"Successful recording matches: {len(successful_rows)}",
        f"Match rate: {round((len(successful_rows) / len(lookup_rows)) * 100, 1) if lookup_rows else 0.0}%",
        f"Matches with usable year/date: {len(usable_date_rows)}",
        f"Rows with 2+ credited artists: {len(multi_credit_rows)}",
        f"Nodes: {len(node_rows)}",
        f"Edges: {len(edge_rows)}",
        "",
        "Lookup success by strategy:",
    ]

    for strategy in ("exact_artist_title", "clean_artist_title", "title_only", "clean_title_only"):
        summary_lines.append(f"- {strategy}: attempted={strategy_counts[strategy]} successful={strategy_success_counts[strategy]}")

    summary_lines.extend([
        "",
        "Top 10 nodes by weighted degree:",
    ])

    for node in top_nodes:
        summary_lines.append(
            f"- {node['artist_name']} | weighted_degree={node['weighted_degree']} | degree={node['degree']} | recordings={node['recording_count']}"
        )

    summary_lines.extend([
        "",
        "Top 10 edges by weight:",
    ])

    for edge in top_edges:
        summary_lines.append(
            f"- {edge['artist_a_name']} -- {edge['artist_b_name']} | weight={edge['weight']} | recordings={edge['recording_titles']}"
        )

    summary_lines.extend([
        "",
        "Sample no-match rows:",
    ])

    for example in no_match_examples[:10]:
        summary_lines.append(f"- {example['input_artist_name']} / {example['input_song_title']} -> {example['lookup_status']}")

    OUTPUT_SUMMARY_TXT.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Sampled artists: {len(artist_song_pairs)}")
    print(f"Artist-song queries: {len(lookup_rows)}")
    print(f"Successful recording matches: {len(successful_rows)}")
    print(f"Match rate: {round((len(successful_rows) / len(lookup_rows)) * 100, 1) if lookup_rows else 0.0}%")
    print(f"Matches with usable year/date: {len(usable_date_rows)}")
    print(f"Rows with 2+ credited artists: {len(multi_credit_rows)}")
    print(f"Nodes: {len(node_rows)}")
    print(f"Edges: {len(edge_rows)}")
    print("Lookup success by strategy:")
    for strategy in ("exact_artist_title", "clean_artist_title", "title_only", "clean_title_only"):
        print(f"- {strategy}: attempted={strategy_counts[strategy]} successful={strategy_success_counts[strategy]}")
    print("Top 10 edges by weight:")
    for edge in top_edges[:10]:
        print(f"- {edge['artist_a_name']} -- {edge['artist_b_name']} | weight={edge['weight']} | recordings={edge['recording_titles']}")
    print(f"Output lookup CSV: {OUTPUT_LOOKUP_CSV}")
    print(f"Edges CSV: {OUTPUT_EDGES_CSV}")
    print(f"Nodes CSV: {OUTPUT_NODES_CSV}")
    print(f"Graph JSON: {OUTPUT_GRAPH_JSON}")
    print(f"Summary TXT: {OUTPUT_SUMMARY_TXT}")


if __name__ == "__main__":
    main()