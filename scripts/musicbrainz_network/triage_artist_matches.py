"""Conservatively triage MusicBrainz artist matches for first-network use.

This script reads the completed MusicBrainz matching outputs and creates a
smaller, precision-first seed file that only includes clearly reliable rows.
The first pass keeps all auto-accepted rows and only promotes review-needed
rows when the input and matched names normalize to the same value.
"""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[2]
INPUT_MATCHES_CSV = ROOT / "data" / "network" / "artist_matches.csv"
INPUT_CANDIDATES_CSV = ROOT / "data" / "network" / "artist_match_candidates.csv"
OUTPUT_CSV = ROOT / "data" / "network" / "usable_artist_matches.csv"
SUMMARY_TXT = ROOT / "data" / "network" / "match_triage_summary.txt"

OUTPUT_COLUMNS = [
    "input_artist_name",
    "matched_name",
    "mbid",
    "musicbrainz_country",
    "type",
    "disambiguation",
    "match_status",
    "source_origin_country",
    "source_birth_place",
    "source_current_residence",
    "source_wikidata_id",
    "source_wiki_url",
    "usable_for_network",
    "triage_reason",
]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_name(value: str) -> str:
    text = (value or "").lower().strip()
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def get_str(row: Dict[str, Any], key: str) -> str:
    value = row.get(key)
    if value is None:
        return ""
    return str(value).strip()


def build_output_row(row: Dict[str, str], usable_for_network: bool, triage_reason: str) -> Dict[str, str]:
    output = {column: get_str(row, column) for column in OUTPUT_COLUMNS if column not in {"usable_for_network", "triage_reason"}}
    output["usable_for_network"] = "True" if usable_for_network else "False"
    output["triage_reason"] = triage_reason
    return output


def collect_examples(rows: List[Dict[str, str]], include_status: bool = True, limit: int = 5) -> List[str]:
    examples: List[str] = []
    for row in rows[:limit]:
        if include_status:
            examples.append(
                f"- {row['input_artist_name']} -> {row['matched_name']} | {row['match_status']} | {row['triage_reason']}"
            )
        else:
            examples.append(f"- {row['input_artist_name']} | {row['triage_reason']}")
    return examples


def main() -> None:
    matches = read_csv(INPUT_MATCHES_CSV)
    candidates = read_csv(INPUT_CANDIDATES_CSV)

    usable_rows: List[Dict[str, str]] = []
    excluded_review_rows: List[Dict[str, str]] = []
    excluded_no_match_rows: List[Dict[str, str]] = []

    for row in matches:
        input_name = get_str(row, "input_artist_name")
        matched_name = get_str(row, "matched_name")
        match_status = get_str(row, "match_status")
        exact_normalized_match = bool(
            normalize_name(input_name) and normalize_name(input_name) == normalize_name(matched_name)
        )

        if match_status == "auto_accept":
            triage_reason = "Included: original match was auto_accept."
            usable_rows.append(build_output_row(row, True, triage_reason))
            continue

        if match_status == "review_needed" and exact_normalized_match:
            triage_reason = "Included: review_needed row has an exact normalized name match."
            usable_rows.append(build_output_row(row, True, triage_reason))
            continue

        if match_status == "review_needed":
            triage_reason = "Excluded: review_needed row is not an exact normalized name match."
            excluded_review_rows.append(build_output_row(row, False, triage_reason))
            continue

        if match_status == "no_match":
            triage_reason = "Excluded: original match was no_match."
            excluded_no_match_rows.append(build_output_row(row, False, triage_reason))
            continue

        triage_reason = f"Excluded: unsupported match_status '{match_status}'."
        excluded_review_rows.append(build_output_row(row, False, triage_reason))

    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(usable_rows)

    total_rows = len(matches)
    included_rows = len(usable_rows)
    excluded_review_count = sum(1 for row in matches if get_str(row, "match_status") == "review_needed")
    excluded_no_match_count = sum(1 for row in matches if get_str(row, "match_status") == "no_match")
    promoted_review_count = sum(
        1
        for row in matches
        if get_str(row, "match_status") == "review_needed"
        and normalize_name(get_str(row, "input_artist_name")) == normalize_name(get_str(row, "matched_name"))
    )

    summary_lines = [
        "MusicBrainz artist match triage summary",
        "",
        f"Input matches file: {INPUT_MATCHES_CSV}",
        f"Candidate file: {INPUT_CANDIDATES_CSV}",
        f"Output file: {OUTPUT_CSV}",
        "",
        f"Total rows in artist_matches.csv: {total_rows}",
        f"Number included in usable_artist_matches.csv: {included_rows}",
        f"Number excluded as review_needed: {excluded_review_count}",
        f"Number excluded as no_match: {excluded_no_match_count}",
        f"Review-needed rows promoted by exact normalized name match: {promoted_review_count}",
        f"Candidate rows loaded: {len(candidates)}",
        "",
        "Included examples:",
        *collect_examples(usable_rows, include_status=True, limit=5),
        "",
        "Excluded review_needed examples:",
        *collect_examples(excluded_review_rows, include_status=True, limit=5),
        "",
        "Excluded no_match examples:",
        *collect_examples(excluded_no_match_rows, include_status=False, limit=5),
    ]

    SUMMARY_TXT.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Wrote {len(usable_rows)} usable rows to {OUTPUT_CSV}")
    print(f"Wrote summary to {SUMMARY_TXT}")
    print(f"Total rows in artist_matches.csv: {total_rows}")
    print(f"Included rows: {included_rows}")
    print(f"Excluded review_needed rows: {excluded_review_count}")
    print(f"Excluded no_match rows: {excluded_no_match_count}")


if __name__ == "__main__":
    main()