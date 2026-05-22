"""Build a tiny collaboration graph from the recording smoke test output.

This script stays intentionally small and conservative. It only uses the
existing smoke-test recording lookup output and turns recordings with 2+ credited
artists into pairwise collaboration edges.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import networkx as nx
except ImportError as exc:  # pragma: no cover - handled in script output
    print("NetworkX is required for this script.")
    print("Please run: pip install networkx")
    raise SystemExit(1) from exc


ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = ROOT / "data" / "network" / "recording_lookup_smoke_test.csv"
EDGES_CSV = ROOT / "data" / "network" / "smoke_test_collaboration_edges.csv"
NODES_CSV = ROOT / "data" / "network" / "smoke_test_collaboration_nodes.csv"
GRAPH_JSON = ROOT / "data" / "network" / "smoke_test_artist_network.json"
SUMMARY_TXT = ROOT / "data" / "network" / "smoke_test_edge_summary.txt"

INPUT_COLUMNS = [
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
    "lookup_status",
    "source_country",
    "source_period",
    "source_year",
    "source_song_title",
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
    "source_seed_artists",
    "source_countries",
    "source_periods",
]

NODE_COLUMNS = [
    "artist_name",
    "artist_mbid",
    "degree_weight",
    "weighted_degree",
    "recording_count",
    "seed_artist_count",
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


def split_delimited(value: str) -> List[str]:
    parts = [part.strip() for part in value.split("|")]
    return [part for part in parts if part]


def normalize_name(value: str) -> str:
    text = (value or "").lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def parse_credit_lists(row: Dict[str, str]) -> Tuple[List[str], List[str]]:
    names = split_delimited(get_str(row, "credited_artist_names"))
    mbids = split_delimited(get_str(row, "credited_artist_mbids"))
    if mbids and len(mbids) == len(names):
        return names, mbids
    return names, [""] * len(names)


def is_usable_match(row: Dict[str, str]) -> bool:
    if get_str(row, "lookup_status") != "matched":
        return False
    if not get_str(row, "recording_mbid"):
        return False
    names, mbids = parse_credit_lists(row)
    if len(names) < 2:
        return False
    if mbids and any(mbids) and len(mbids) < 2:
        return False
    return True


def first_year(row: Dict[str, str]) -> str:
    first_date = get_str(row, "first_date")
    if first_date:
        return first_date[:4]
    year = get_str(row, "year")
    return year[:4] if year else ""


def main() -> None:
    rows = read_csv(INPUT_CSV)
    matched_rows = [row for row in rows if get_str(row, "lookup_status") == "matched"]
    usable_rows = [row for row in matched_rows if is_usable_match(row)]

    graph = nx.Graph()
    edge_details: Dict[Tuple[str, str], Dict[str, Any]] = {}
    node_details: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
        "artist_name": "",
        "artist_mbid": "",
        "degree_weight": 0,
        "weighted_degree": 0,
        "recording_count": 0,
        "seed_artist_count": 0,
    })

    recording_rows_used = 0

    for row in usable_rows:
        names, mbids = parse_credit_lists(row)
        if len(names) < 2:
            continue

        recording_rows_used += 1
        recording_title = get_str(row, "recording_title")
        recording_mbid = get_str(row, "recording_mbid")
        recording_year = first_year(row)
        seed_artist = get_str(row, "input_artist_name")
        source_country = get_str(row, "source_country")
        source_period = get_str(row, "source_period")

        for name, mbid in zip(names, mbids):
            normalized = normalize_name(name)
            node = node_details[normalized]
            node["artist_name"] = name
            if mbid and not node["artist_mbid"]:
                node["artist_mbid"] = mbid
            node["recording_count"] += 1
            node["seed_artist_count"] += 1 if normalize_name(seed_artist) == normalized else 0

        for left_name, right_name in combinations(names, 2):
            left_mbid = mbids[names.index(left_name)] if mbids else ""
            right_mbid = mbids[names.index(right_name)] if mbids else ""
            left_key = normalize_name(left_name)
            right_key = normalize_name(right_name)
            edge_key = tuple(sorted([left_key, right_key]))

            if edge_key not in edge_details:
                edge_details[edge_key] = {
                    "artist_a_name": left_name if edge_key[0] == left_key else right_name,
                    "artist_a_mbid": left_mbid if edge_key[0] == left_key else right_mbid,
                    "artist_b_name": right_name if edge_key[1] == right_key else left_name,
                    "artist_b_mbid": right_mbid if edge_key[1] == right_key else left_mbid,
                    "weight": 0,
                    "recordings": [],
                    "recording_mbids": [],
                    "recording_titles": [],
                    "recording_years": [],
                    "source_seed_artists": [],
                    "source_countries": [],
                    "source_periods": [],
                }

            edge = edge_details[edge_key]
            edge["weight"] += 1
            edge["recordings"].append(recording_title)
            edge["recording_mbids"].append(recording_mbid)
            edge["recording_titles"].append(f"{recording_title} ({recording_year})" if recording_year else recording_title)
            edge["recording_years"].append(recording_year)
            edge["source_seed_artists"].append(seed_artist)
            edge["source_countries"].append(source_country)
            edge["source_periods"].append(source_period)

    edge_rows: List[Dict[str, Any]] = []
    for edge_key, edge in sorted(edge_details.items(), key=lambda item: (-item[1]["weight"], item[0][0], item[0][1])):
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
                "recording_years": "; ".join([year for year in edge["recording_years"] if year]),
                "source_seed_artists": "; ".join(sorted(set(edge["source_seed_artists"]))),
                "source_countries": "; ".join(sorted(set(filter(None, edge["source_countries"])))),
                "source_periods": "; ".join(sorted(set(filter(None, edge["source_periods"])))),
            }
        )

    node_rows: List[Dict[str, Any]] = []
    for normalized_name, node in sorted(node_details.items(), key=lambda item: (-item[1]["recording_count"], item[1]["artist_name"].lower())):
        graph.add_node(node["artist_name"], mbid=node["artist_mbid"], recording_count=node["recording_count"], seed_artist_count=node["seed_artist_count"])
        node_rows.append(
            {
                "artist_name": node["artist_name"],
                "artist_mbid": node["artist_mbid"],
                "degree_weight": 0,
                "weighted_degree": 0,
                "recording_count": node["recording_count"],
                "seed_artist_count": node["seed_artist_count"],
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
        )

    for node_row in node_rows:
        artist_name = node_row["artist_name"]
        degree = graph.degree(artist_name)
        weighted_degree = sum(data.get("weight", 0) for _, _, data in graph.edges(artist_name, data=True))
        node_row["degree_weight"] = degree
        node_row["weighted_degree"] = weighted_degree

    graph_json = {
        "nodes": [
            {
                "id": node_row["artist_name"],
                "artist_name": node_row["artist_name"],
                "artist_mbid": node_row["artist_mbid"],
                "degree_weight": node_row["degree_weight"],
                "weighted_degree": node_row["weighted_degree"],
                "recording_count": node_row["recording_count"],
                "seed_artist_count": node_row["seed_artist_count"],
            }
            for node_row in node_rows
        ],
        "edges": [
            {
                "source": edge["artist_a_name"],
                "target": edge["artist_b_name"],
                "weight": edge["weight"],
                "recordings": edge["recordings"].split("; ") if edge["recordings"] else [],
                "recording_titles": edge["recording_titles"].split("; ") if edge["recording_titles"] else [],
                "recording_mbids": edge["recording_mbids"].split("; ") if edge["recording_mbids"] else [],
            }
            for edge in edge_rows
        ],
    }

    write_csv(EDGES_CSV, edge_rows, EDGE_COLUMNS)
    write_csv(NODES_CSV, node_rows, NODE_COLUMNS)
    GRAPH_JSON.write_text(json.dumps(graph_json, ensure_ascii=False, indent=2), encoding="utf-8")

    top_nodes = sorted(node_rows, key=lambda row: (-row["weighted_degree"], -row["recording_count"], row["artist_name"].lower()))[:10]
    sample_edges = edge_rows[:10]

    summary_lines = [
        "MusicBrainz smoke-test collaboration edge summary",
        "",
        f"Input recording rows: {len(rows)}",
        f"Matched rows: {len(matched_rows)}",
        f"Rows with 2+ credited artists: {len(usable_rows)}",
        f"Nodes: {len(node_rows)}",
        f"Edges: {len(edge_rows)}",
        f"Recording rows used for graph: {recording_rows_used}",
        "",
        "Top nodes by weighted degree:",
    ]

    for node in top_nodes:
        summary_lines.append(
            f"- {node['artist_name']} | weighted_degree={node['weighted_degree']} | degree={node['degree_weight']} | recordings={node['recording_count']}"
        )

    summary_lines.extend([
        "",
        "Sample edges:",
    ])

    for edge in sample_edges:
        summary_lines.append(
            f"- {edge['artist_a_name']} -- {edge['artist_b_name']} | weight={edge['weight']} | recordings={edge['recording_titles']}"
        )

    SUMMARY_TXT.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Input recording rows: {len(rows)}")
    print(f"Matched rows: {len(matched_rows)}")
    print(f"Rows with 2+ credited artists: {len(usable_rows)}")
    print(f"Nodes: {len(node_rows)}")
    print(f"Edges: {len(edge_rows)}")
    print("Top nodes by weighted degree:")
    for node in top_nodes[:5]:
        print(f"- {node['artist_name']} | weighted_degree={node['weighted_degree']} | degree={node['degree_weight']}")
    print("Sample edges:")
    for edge in sample_edges[:5]:
        print(f"- {edge['artist_a_name']} -- {edge['artist_b_name']} | weight={edge['weight']} | recordings={edge['recording_titles']}")
    print(f"Edges CSV: {EDGES_CSV}")
    print(f"Nodes CSV: {NODES_CSV}")
    print(f"Graph JSON: {GRAPH_JSON}")
    print(f"Summary TXT: {SUMMARY_TXT}")


if __name__ == "__main__":
    main()