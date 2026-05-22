"""Match artists from the seed dataset to MusicBrainz search results.

This script is isolated to the MusicBrainz network preparation phase. It reads
the existing artist dataset, queries MusicBrainz artist search, caches raw API
responses, and writes both candidate matches and the best selected match per
artist.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests


ROOT = Path(__file__).resolve().parents[2]
INPUT_CSV = ROOT / "data" / "artists_data.csv"
OUTPUT_DIR = ROOT / "data" / "network"
CACHE_DIR = OUTPUT_DIR / "cache" / "artist_search"
CANDIDATES_CSV = OUTPUT_DIR / "artist_match_candidates.csv"
MATCHES_CSV = OUTPUT_DIR / "artist_matches.csv"

BASE_URL = "https://musicbrainz.org/ws/2/"
USER_AGENT = "CSS-Project-A/1.0"
REQUEST_DELAY_SECONDS = 1
MB_SEARCH_LIMIT = 10

SOURCE_COLUMNS = ["name", "wikidata_id", "origin_country", "birth_place", "current_residence", "wiki_url"]


def read_seed_artists(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    unique_rows: List[Dict[str, str]] = []
    seen_names = set()
    for row in rows:
        artist_name = (row.get("name") or "").strip()
        if not artist_name or artist_name in seen_names:
            continue
        seen_names.add(artist_name)
        unique_rows.append(row)
    return unique_rows


def normalize_name(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"\(.*?\)", "", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_name(left), normalize_name(right)).ratio()


def cache_key_for_artist(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", normalize_name(name))[:60] or "artist"
    digest = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    return f"{slug}_{digest}.json"


def load_cached_response(artist_name: str) -> Optional[Dict[str, Any]]:
    cache_path = CACHE_DIR / cache_key_for_artist(artist_name)
    if not cache_path.exists():
        return None
    with cache_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_cached_response(artist_name: str, payload: Dict[str, Any]) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / cache_key_for_artist(artist_name)
    with cache_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return cache_path


def search_musicbrainz_artist(artist_name: str) -> Dict[str, Any]:
    cached = load_cached_response(artist_name)
    if cached is not None:
        return cached

    url = f"{BASE_URL}artist/"
    params = {"query": artist_name, "fmt": "json", "limit": MB_SEARCH_LIMIT}
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
    except requests.RequestException as exc:
        return {"error": f"connection_error: {exc}", "artists": []}

    time.sleep(REQUEST_DELAY_SECONDS)

    if response.status_code != 200:
        return {
            "error": f"bad_status_code: {response.status_code}",
            "status_code": response.status_code,
            "response_text": response.text[:1000],
            "artists": [],
        }

    try:
        payload = response.json()
    except ValueError:
        return {"error": "json_decode_error", "artists": []}

    save_cached_response(artist_name, payload)
    return payload


def get_str(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    return text if text else fallback


def has_usable_candidate(candidate: Dict[str, Any]) -> bool:
    return bool(get_str(candidate.get("id")) and get_str(candidate.get("name")))


def candidate_notes(input_name: str, candidate: Dict[str, Any], top_score: int, second_score: Optional[int], candidate_count: int) -> Tuple[str, str]:
    matched_name = get_str(candidate.get("name"))
    score_raw = candidate.get("score")
    score = int(score_raw) if str(score_raw).isdigit() else 0
    name_similarity = similarity(input_name, matched_name)
    disambiguation = get_str(candidate.get("disambiguation"), "")

    if candidate_count == 0:
        return "no_match", "MusicBrainz returned no usable artist results."

    if score >= 95 and name_similarity >= 0.95:
        return "auto_accept", "Very high score and near-exact name match."

    score_gap = top_score - second_score if second_score is not None else 999

    if score >= 90 and name_similarity >= 0.85:
        if score_gap <= 5 and candidate_count > 1:
            return "review_needed", "High score but other candidates look plausible."
        return "auto_accept", "High score and strong name similarity."

    if score >= 80 and name_similarity >= 0.9 and not disambiguation:
        return "auto_accept", "Strong match with clean name similarity."

    if score < 80:
        return "review_needed", "Score is below the auto-accept threshold."

    if disambiguation:
        return "review_needed", "Candidate is disambiguated and should be checked manually."

    return "review_needed", "Candidate needs manual review."


def build_source_payload(row: Dict[str, str]) -> Dict[str, str]:
    return {f"source_{column}": get_str(row.get(column)) for column in SOURCE_COLUMNS}


def select_best_candidate(input_name: str, candidates: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], str, str]:
    usable = [candidate for candidate in candidates if has_usable_candidate(candidate)]
    if not usable:
        return None, "no_match", "MusicBrainz returned no usable artist results."

    usable.sort(
        key=lambda candidate: (
            int(candidate.get("score") or 0),
            similarity(input_name, get_str(candidate.get("name"))),
        ),
        reverse=True,
    )
    best = usable[0]
    score = int(best.get("score") or 0)
    top_score = score
    if len(usable) > 1:
        top_score = int(usable[0].get("score") or 0)

    second_score = int(usable[1].get("score") or 0) if len(usable) > 1 else None
    status, notes = candidate_notes(input_name, best, top_score, second_score, len(usable))
    return best, status, notes


def candidate_row(input_row: Dict[str, str], input_name: str, rank: int, candidate: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "input_artist_name": input_name,
        "candidate_rank": rank,
        "matched_name": get_str(candidate.get("name")),
        "mbid": get_str(candidate.get("id")),
        "musicbrainz_country": get_str(candidate.get("country")),
        "type": get_str(candidate.get("type")),
        "disambiguation": get_str(candidate.get("disambiguation")),
        "score": get_str(candidate.get("score")),
        "match_status": "candidate",
        "notes": "Returned by MusicBrainz search.",
    }
    row.update(build_source_payload(input_row))
    return row


def best_match_row(input_row: Dict[str, str], input_name: str, best: Optional[Dict[str, Any]], status: str, notes: str) -> Dict[str, Any]:
    row = {
        "input_artist_name": input_name,
        "matched_name": get_str(best.get("name")) if best else "",
        "mbid": get_str(best.get("id")) if best else "",
        "musicbrainz_country": get_str(best.get("country")) if best else "",
        "type": get_str(best.get("type")) if best else "",
        "disambiguation": get_str(best.get("disambiguation")) if best else "",
        "score": get_str(best.get("score")) if best else "",
        "match_status": status,
        "notes": notes,
    }
    row.update(build_source_payload(input_row))
    return row


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Match seed artists to MusicBrainz search results.")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit for seed artists, for smoke tests.")
    args = parser.parse_args()

    seed_rows = read_seed_artists(INPUT_CSV)
    if args.limit is not None:
        seed_rows = seed_rows[: max(args.limit, 0)]

    candidate_rows: List[Dict[str, Any]] = []
    best_rows: List[Dict[str, Any]] = []
    counts = Counter()

    for index, row in enumerate(seed_rows, start=1):
        input_name = get_str(row.get("name"))
        print(f"[{index}/{len(seed_rows)}] Matching: {input_name}")

        payload = search_musicbrainz_artist(input_name)
        search_results = payload.get("artists", []) if isinstance(payload, dict) else []
        usable_results = [candidate for candidate in search_results if has_usable_candidate(candidate)]

        if not usable_results:
            status = "no_match"
            notes = payload.get("error", "No usable result returned by MusicBrainz.") if isinstance(payload, dict) else "No usable result returned by MusicBrainz."
            best_rows.append(best_match_row(row, input_name, None, status, notes))
            counts[status] += 1
            continue

        for rank, candidate in enumerate(usable_results, start=1):
            candidate_rows.append(candidate_row(row, input_name, rank, candidate))

        best_candidate, status, notes = select_best_candidate(input_name, usable_results)
        best_rows.append(best_match_row(row, input_name, best_candidate, status, notes))
        counts[status] += 1

    candidate_fieldnames = [
        "input_artist_name",
        "candidate_rank",
        "matched_name",
        "mbid",
        "musicbrainz_country",
        "type",
        "disambiguation",
        "score",
        "match_status",
        "notes",
        *[f"source_{column}" for column in SOURCE_COLUMNS],
    ]
    match_fieldnames = [
        "input_artist_name",
        "matched_name",
        "mbid",
        "musicbrainz_country",
        "type",
        "disambiguation",
        "score",
        "match_status",
        "notes",
        *[f"source_{column}" for column in SOURCE_COLUMNS],
    ]

    write_csv(CANDIDATES_CSV, candidate_rows, candidate_fieldnames)
    write_csv(MATCHES_CSV, best_rows, match_fieldnames)

    total_seed_artists = len(seed_rows)
    print()
    print(f"total seed artists: {total_seed_artists}")
    print(f"auto accepted: {counts['auto_accept']}")
    print(f"review needed: {counts['review_needed']}")
    print(f"no match: {counts['no_match']}")
    print(f"artist_matches.csv: {MATCHES_CSV}")
    print(f"artist_match_candidates.csv: {CANDIDATES_CSV}")


if __name__ == "__main__":
    main()