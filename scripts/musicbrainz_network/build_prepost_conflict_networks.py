"""Build conflict-specific pre/post collaboration networks from selected songs.

This script does not call MusicBrainz. It uses the already-built selected-song
recording lookup and collaboration outputs, plus the lyrics dataset, to split
collaboration edges into conflict-specific pre/post graphs.
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import networkx as nx

try:
    from pyvis.network import Network
except ImportError as exc:  # pragma: no cover - surfaced at runtime
    print("PyVis is required for this script.")
    print("Please run: pip install pyvis")
    raise SystemExit(1) from exc


ROOT = Path(__file__).resolve().parents[2]
LOOKUP_CSV = ROOT / "data" / "network" / "selected_song_recording_lookup.csv"
EDGES_CSV = ROOT / "data" / "network" / "selected_song_collaboration_edges.csv"
NODES_CSV = ROOT / "data" / "network" / "selected_song_collaboration_nodes.csv"
GRAPH_JSON = ROOT / "data" / "network" / "selected_song_artist_network.json"
LYRICS_CSV = ROOT / "data" / "lyrics_data" / "lyrics_with_sentiment_translated.csv"

OUTPUT_DIR = ROOT / "data" / "network" / "prepost"
HTML_DIR = ROOT / "website" / "public" / "network" / "prepost"
SUMMARY_TXT = OUTPUT_DIR / "prepost_network_summary.txt"

BASE_URL = "https://musicbrainz.org/ws/2/"
HTML_NODE_LIMIT = 200

CONFLICTS = {
    "ukraine_russia": {
        "countries": {"Ukraine", "Russia"},
        "start_year": 2022,
        "display_name": "Ukraine/Russia",
    },
    "israel_palestine": {
        "countries": {"Israel", "Palestine"},
        "start_year": 2023,
        "display_name": "Israel/Palestine",
    },
    "syria": {
        "countries": {"Syria"},
        "start_year": 2011,
        "display_name": "Syria",
    },
}

PERIODS = ("pre", "post")

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
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("’", "'").replace("`", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def split_delimited(value: str) -> List[str]:
    if not value:
        return []
    parts = [part.strip() for part in value.split("|")]
    return [part for part in parts if part]


def parse_year(value: str) -> Optional[int]:
    value = (value or "").strip()
    if not value:
        return None
    match = re.search(r"(\d{4})", value)
    if not match:
        return None
    return int(match.group(1))


def build_lyrics_artist_map(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    mapping: Dict[str, Dict[str, str]] = {}
    for row in rows:
        artist = get_str(row, "artist")
        if not artist:
            continue
        mapping[normalize_name(artist)] = {
            "artist": artist,
            "country": get_str(row, "country"),
            "period": get_str(row, "period"),
            "year": get_str(row, "year"),
            "song_title": get_str(row, "song_title"),
        }
    return mapping


def classify_conflict(country: str) -> Optional[str]:
    for key, conflict in CONFLICTS.items():
        if country in conflict["countries"]:
            return key
    return None


def edge_template() -> Dict[str, Any]:
    return {
        "artist_a_name": "",
        "artist_a_mbid": "",
        "artist_b_name": "",
        "artist_b_mbid": "",
        "weight": 0,
        "recordings": [],
        "recording_mbids": [],
        "recording_titles": [],
        "recording_years": [],
        "source_artists": [],
        "source_countries": [],
        "source_periods": [],
    }


def add_edge_instance(
    edge_map: Dict[Tuple[str, str], Dict[str, Any]],
    name_a: str,
    mbid_a: str,
    name_b: str,
    mbid_b: str,
    recording_title: str,
    recording_mbid: str,
    recording_year: Optional[int],
    source_artist: str,
    source_country: str,
    source_period: str,
) -> None:
    key = tuple(sorted([normalize_name(name_a), normalize_name(name_b)]))
    if key not in edge_map:
        edge_map[key] = edge_template()
        edge_map[key]["artist_a_name"] = name_a if normalize_name(name_a) == key[0] else name_b
        edge_map[key]["artist_a_mbid"] = mbid_a if normalize_name(name_a) == key[0] else mbid_b
        edge_map[key]["artist_b_name"] = name_b if normalize_name(name_b) == key[1] else name_a
        edge_map[key]["artist_b_mbid"] = mbid_b if normalize_name(name_b) == key[1] else mbid_a

    edge = edge_map[key]
    edge["weight"] += 1
    edge["recordings"].append(recording_title)
    edge["recording_mbids"].append(recording_mbid)
    edge["recording_titles"].append(f"{recording_title} ({recording_year})" if recording_year else recording_title)
    if recording_year:
        edge["recording_years"].append(str(recording_year))
    edge["source_artists"].append(source_artist)
    edge["source_countries"].append(source_country)
    edge["source_periods"].append(source_period)


def rows_to_edge_csv_rows(edge_map: Dict[Tuple[str, str], Dict[str, Any]]) -> List[Dict[str, Any]]:
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


def rows_to_node_csv_rows(edge_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    node_map: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "artist_name": "",
            "artist_mbid": "",
            "recordings": set(),
            "weighted_degree": 0,
            "degree": 0,
        }
    )
    for edge in edge_rows:
        name_a = edge["artist_a_name"]
        name_b = edge["artist_b_name"]
        mbid_a = edge["artist_a_mbid"]
        mbid_b = edge["artist_b_mbid"]
        weight = safe_int(edge["weight"], 0)
        recording_mbids = [item.strip() for item in edge["recording_mbids"].split(";") if item.strip()]

        for name, mbid in ((name_a, mbid_a), (name_b, mbid_b)):
            key = normalize_name(name)
            node = node_map[key]
            node["artist_name"] = name
            if mbid and not node["artist_mbid"]:
                node["artist_mbid"] = mbid
            node["recordings"].update(recording_mbids)
            node["weighted_degree"] += weight
            node["degree"] += 1

    rows: List[Dict[str, Any]] = []
    for key, node in sorted(node_map.items(), key=lambda item: (-item[1]["weighted_degree"], item[1]["artist_name"].lower())):
        rows.append(
            {
                "artist_name": node["artist_name"],
                "artist_mbid": node["artist_mbid"],
                "recording_count": len(node["recordings"]),
                "weighted_degree": node["weighted_degree"],
                "degree": node["degree"],
            }
        )
    return rows


def build_graph(edge_rows: List[Dict[str, Any]], node_rows: List[Dict[str, Any]]) -> nx.Graph:
    graph = nx.Graph()
    node_lookup = {row["artist_name"]: row for row in node_rows}
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
    return graph


def graph_json(node_rows: List[Dict[str, Any]], edge_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "nodes": [
            {
                "id": row["artist_name"],
                "artist_name": row["artist_name"],
                "artist_mbid": row["artist_mbid"],
                "recording_count": row["recording_count"],
                "weighted_degree": row["weighted_degree"],
                "degree": row["degree"],
            }
            for row in node_rows
        ],
        "edges": [
            {
                "source": row["artist_a_name"],
                "target": row["artist_b_name"],
                "weight": row["weight"],
                "recordings": split_delimited(row["recordings"].replace("; ", "|")) if row["recordings"] else [],
                "recording_titles": split_delimited(row["recording_titles"].replace("; ", "|")) if row["recording_titles"] else [],
                "recording_years": split_delimited(row["recording_years"].replace("; ", "|")) if row["recording_years"] else [],
            }
            for row in edge_rows
        ],
    }


def choose_html_subgraph(graph: nx.Graph) -> nx.Graph:
    if graph.number_of_nodes() == 0:
        return graph
    if graph.number_of_nodes() <= HTML_NODE_LIMIT:
        return graph
    components = sorted(nx.connected_components(graph), key=len, reverse=True)
    largest = graph.subgraph(components[0]).copy()
    if largest.number_of_nodes() <= HTML_NODE_LIMIT:
        return largest
    top_nodes = sorted(
        largest.nodes(),
        key=lambda name: (-largest.nodes[name].get("weighted_degree", 0), -largest.nodes[name].get("recording_count", 0), name.lower()),
    )[:HTML_NODE_LIMIT]
    return largest.subgraph(top_nodes).copy()


def build_pyvis_html(graph: nx.Graph, path: Path, title: str) -> None:
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
        net.add_node(node, label=node, title="<br>".join(title_lines), value=recording_count, size=size)

    for left, right, data in graph.edges(data=True):
        weight = data.get("weight", 1)
        title_text = "<br>".join(
            [
                f"Weight: {weight}",
                f"Recordings: {data.get('recording_titles', '')}",
                f"Seed artists: {data.get('source_artists', '')}",
            ]
        )
        net.add_edge(left, right, value=weight, width=1 + weight, title=title_text)

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


def main() -> None:
    lyrics_rows = read_csv(LYRICS_CSV)
    lookup_rows = read_csv(LOOKUP_CSV)

    lyrics_map = build_lyrics_artist_map(lyrics_rows)

    # One record per matched recording, used to split the selected-song collaborations.
    recording_rows: List[Dict[str, Any]] = []
    assigned_rows: List[Dict[str, Any]] = []
    unassigned_rows: List[Dict[str, Any]] = []

    for row in lookup_rows:
        if get_str(row, "lookup_status") != "matched":
            continue

        input_artist = get_str(row, "input_artist_name")
        input_key = normalize_name(input_artist)
        lyrics_meta = lyrics_map.get(input_key)
        if not lyrics_meta:
            unassigned_rows.append({"reason": "artist_not_found_in_lyrics_csv", **row})
            continue

        conflict_key = classify_conflict(get_str(lyrics_meta, "country"))
        if not conflict_key:
            unassigned_rows.append({"reason": "artist_country_not_in_target_conflicts", **row})
            continue

        recording_year = parse_year(get_str(row, "year"))
        if recording_year is None:
            unassigned_rows.append({"reason": "missing_recording_year", **row})
            continue

        recording_rows.append({**row, "conflict_key": conflict_key, "recording_year": recording_year})
        assigned_rows.append({**row, "conflict_key": conflict_key, "recording_year": recording_year})

    grouped: Dict[Tuple[str, str], Dict[str, Dict[str, Any]]] = defaultdict(lambda: defaultdict(dict))
    for conflict_key in CONFLICTS:
        for period in PERIODS:
            grouped[(conflict_key, period)] = {"edge_map": {}, "recording_count": 0, "unassigned_notes": []}

    for row in assigned_rows:
        conflict_key = row["conflict_key"]
        start_year = CONFLICTS[conflict_key]["start_year"]
        period = "pre" if row["recording_year"] < start_year else "post"

        names = split_delimited(get_str(row, "credited_artist_names"))
        mbids = split_delimited(get_str(row, "credited_artist_mbids"))
        if len(names) < 2:
            continue

        group_bucket = grouped[(conflict_key, period)]
        group_bucket["recording_count"] += 1

        for i, j in combinations(range(len(names)), 2):
            name_a = names[i]
            name_b = names[j]
            mbid_a = mbids[i] if i < len(mbids) else ""
            mbid_b = mbids[j] if j < len(mbids) else ""
            add_edge_instance(
                group_bucket["edge_map"],
                name_a,
                mbid_a,
                name_b,
                mbid_b,
                get_str(row, "recording_title"),
                get_str(row, "recording_mbid"),
                row["recording_year"],
                get_str(row, "input_artist_name"),
                get_str(row, "country"),
                get_str(row, "period"),
            )

    summary_lines = ["Pre/post collaboration network summary", ""]
    generated_html: List[str] = []

    for conflict_key, conflict in CONFLICTS.items():
        for period in PERIODS:
            bucket = grouped[(conflict_key, period)]
            edge_rows = rows_to_edge_csv_rows(bucket["edge_map"])
            node_rows = rows_to_node_csv_rows(edge_rows)
            graph = build_graph(edge_rows, node_rows)
            graph_json_data = graph_json(node_rows, edge_rows)

            prefix = f"{conflict_key}_{period}"
            edges_path = OUTPUT_DIR / f"{prefix}_edges.csv"
            nodes_path = OUTPUT_DIR / f"{prefix}_nodes.csv"
            json_path = OUTPUT_DIR / f"{prefix}_network.json"
            html_path = HTML_DIR / f"{prefix}_network.html"

            write_csv(edges_path, edge_rows, EDGE_COLUMNS)
            write_csv(nodes_path, node_rows, NODE_COLUMNS)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(json.dumps(graph_json_data, ensure_ascii=False, indent=2), encoding="utf-8")

            if graph.number_of_nodes() > 0 and graph.number_of_edges() > 0:
                html_graph = choose_html_subgraph(graph)
                build_pyvis_html(html_graph, html_path, f"{conflict['display_name']} {period.title()}")
                generated_html.append(str(html_path))

            top_nodes = sorted(node_rows, key=lambda row: (-row["weighted_degree"], -row["recording_count"], row["artist_name"].lower()))[:10]
            top_edges = sorted(edge_rows, key=lambda row: (-safe_int(row["weight"], 0), row["artist_a_name"].lower(), row["artist_b_name"].lower()))[:10]

            summary_lines.extend(
                [
                    f"Conflict group: {conflict['display_name']}",
                    f"Period: {period}",
                    f"Conflict start year used: {conflict['start_year']}",
                    f"Nodes: {len(node_rows)}",
                    f"Edges: {len(edge_rows)}",
                    f"Recordings represented: {bucket['recording_count']}",
                ]
            )

            if edge_rows:
                summary_lines.append("Top nodes by weighted degree:")
                for row in top_nodes:
                    summary_lines.append(
                        f"- {row['artist_name']} | weighted_degree={row['weighted_degree']} | degree={row['degree']} | recordings={row['recording_count']}"
                    )
                summary_lines.append("Top edges by weight:")
                for row in top_edges:
                    summary_lines.append(
                        f"- {row['artist_a_name']} -- {row['artist_b_name']} | weight={row['weight']} | recordings={row['recording_titles']}"
                    )
            else:
                summary_lines.append("Top nodes by weighted degree: none")
                summary_lines.append("Top edges by weight: none")
                summary_lines.append("Note: graph is empty or too sparse for visualization.")

            summary_lines.append("")

    summary_lines.extend(
        [
            "Unassigned summary:",
            f"Unassigned matched recordings: {len(unassigned_rows)}",
        ]
    )
    for row in unassigned_rows[:20]:
        summary_lines.append(
            f"- {row.get('reason', 'unassigned')} | {get_str(row, 'input_artist_name')} / {get_str(row, 'input_song_title')}"
        )
    summary_lines.extend([
        "",
        f"HTML files generated: {len(generated_html)}",
    ])
    for path in generated_html:
        summary_lines.append(f"- {path}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_TXT.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Assigned matched recordings: {len(assigned_rows)}")
    print(f"Unassigned matched recordings: {len(unassigned_rows)}")
    print(f"HTML files generated: {len(generated_html)}")
    for path in generated_html:
        print(f"- {path}")
    print(f"Summary: {SUMMARY_TXT}")


if __name__ == "__main__":
    main()