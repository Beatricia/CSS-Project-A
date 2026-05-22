"""Smoke test MusicBrainz recording lookup for a small artist-song sample.

The goal is to verify that the repo's already-selected songs can be matched to
MusicBrainz recordings with usable metadata for a later collaboration network.
This script is intentionally conservative and limited in scope.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests


ROOT = Path(__file__).resolve().parents[2]
USABLE_MATCHES_CSV = ROOT / "data" / "network" / "usable_artist_matches.csv"
SONG_SOURCE_CSV = ROOT / "data" / "lyrics_data" / "lyrics_with_sentiment_translated.csv"
OUTPUT_CSV = ROOT / "data" / "network" / "recording_lookup_smoke_test.csv"
SUMMARY_TXT = ROOT / "data" / "network" / "recording_lookup_smoke_test_summary.txt"
CACHE_DIR = ROOT / "data" / "network" / "cache" / "recording_search"

BASE_URL = "https://musicbrainz.org/ws/2/"
USER_AGENT = "CSS-Project-A/1.0"
REQUEST_DELAY_SECONDS = 1
SEARCH_LIMIT = 5
ARTIST_SAMPLE_SIZE = 10
SONGS_PER_ARTIST = 3

USABLE_MATCH_COLUMNS = [
    "input_artist_name",
    "matched_name",
    "mbid",
    "source_origin_country",
    "source_current_residence",
    "source_wikidata_id",
]

OUTPUT_COLUMNS = [
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


def safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return fallback


def cache_key_for_query(artist_name: str, song_title: str) -> str:
    slug_artist = re.sub(r"[^a-z0-9]+", "_", normalize_name(artist_name))[:40] or "artist"
    slug_song = re.sub(r"[^a-z0-9]+", "_", normalize_name(song_title))[:40] or "song"
    digest = hashlib.sha1(f"{artist_name}\n{song_title}".encode("utf-8")).hexdigest()[:12]
    return f"{slug_artist}__{slug_song}__{digest}.json"


def load_cached_response(artist_name: str, song_title: str) -> Optional[Dict[str, Any]]:
    cache_path = CACHE_DIR / cache_key_for_query(artist_name, song_title)
    if not cache_path.exists():
        return None
    with cache_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_cached_response(artist_name: str, song_title: str, payload: Dict[str, Any]) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = CACHE_DIR / cache_key_for_query(artist_name, song_title)
    with cache_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    return cache_path


def search_musicbrainz_recording(artist_name: str, song_title: str) -> Dict[str, Any]:
    cached = load_cached_response(artist_name, song_title)
    if cached is not None:
        return cached

    url = f"{BASE_URL}recording/"
    query = f'artist:"{artist_name}" AND recording:"{song_title}"'
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
    save_cached_response(artist_name, song_title, payload)
    return payload


def split_artist_credits(recording: Dict[str, Any]) -> Tuple[str, str]:
    names: List[str] = []
    mbids: List[str] = []
    for credit in recording.get("artist-credit", []) or []:
        artist = credit.get("artist") if isinstance(credit, dict) else None
        if not isinstance(artist, dict):
            continue
        name = get_str(artist, "name")
        mbid = get_str(artist, "id")
        if name:
            names.append(name)
        if mbid:
            mbids.append(mbid)
    return " | ".join(names), " | ".join(mbids)


def build_output_row(
    artist_row: Dict[str, str],
    song_row: Dict[str, str],
    recording: Optional[Dict[str, Any]],
    status: str,
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
            "lookup_status": status,
            "source_country": get_str(song_row, "country"),
            "source_period": get_str(song_row, "period"),
            "source_year": get_str(song_row, "year"),
            "source_song_title": get_str(song_row, "song_title"),
        }

    credited_names, credited_mbids = split_artist_credits(recording)
    first_date = get_str(recording, "first-release-date")
    year = first_date[:4] if first_date else ""
    if not year:
        year = get_str(song_row, "year")

    return {
        "input_artist_name": get_str(artist_row, "input_artist_name"),
        "input_song_title": get_str(song_row, "song_title"),
        "seed_artist_mbid": get_str(artist_row, "mbid"),
        "recording_title": get_str(recording, "title"),
        "recording_mbid": get_str(recording, "id"),
        "first_date": first_date,
        "year": year,
        "credited_artist_names": credited_names,
        "credited_artist_mbids": credited_mbids,
        "musicbrainz_score": get_str(recording, "score"),
        "lookup_status": status,
        "source_country": get_str(song_row, "country"),
        "source_period": get_str(song_row, "period"),
        "source_year": get_str(song_row, "year"),
        "source_song_title": get_str(song_row, "song_title"),
    }


def is_usably_matched(artist_name: str, song_title: str, recording: Dict[str, Any]) -> bool:
    recording_title = get_str(recording, "title")
    score = safe_int(recording.get("score"), 0)
    title_similarity = 1.0 if normalize_name(recording_title) == normalize_name(song_title) else 0.0
    artist_similarity = 1.0 if normalize_name(artist_name) in normalize_name(recording.get("artist-credit-phrase", "")) else 0.0
    return score >= 90 and (title_similarity >= 1.0 or artist_similarity >= 1.0)


def select_song_rows(song_rows: List[Dict[str, str]], artist_name: str, limit: int = SONGS_PER_ARTIST) -> List[Dict[str, str]]:
    matching_rows = [row for row in song_rows if normalize_name(get_str(row, "artist")) == normalize_name(artist_name)]
    matching_rows.sort(key=lambda row: (safe_int(get_str(row, "year"), 9999), normalize_name(get_str(row, "song_title"))))
    return matching_rows[:limit]


def choose_artist_sample(usable_artists: List[Dict[str, str]], song_rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    songs_by_artist = defaultdict(int)
    for row in song_rows:
        songs_by_artist[normalize_name(get_str(row, "artist"))] += 1

    ranked: List[Tuple[int, str, Dict[str, str]]] = []
    for artist_row in usable_artists:
        artist_name = get_str(artist_row, "input_artist_name")
        count = songs_by_artist.get(normalize_name(artist_name), 0)
        if count > 0:
            ranked.append((count, artist_name.lower(), artist_row))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [row for _, _, row in ranked[:ARTIST_SAMPLE_SIZE]]


def write_csv(path: Path, rows: List[Dict[str, str]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    usable_artists = read_csv(USABLE_MATCHES_CSV)
    song_rows = read_csv(SONG_SOURCE_CSV)

    sample_artists = choose_artist_sample(usable_artists, song_rows)
    lookup_rows: List[Dict[str, str]] = []
    matched_rows: List[Dict[str, str]] = []
    collaborator_preview: List[Dict[str, str]] = []

    artist_song_queries = 0
    successful_matches = 0
    multi_credit_matches = 0
    dateful_matches = 0

    for artist_row in sample_artists:
        artist_name = get_str(artist_row, "input_artist_name")
        selected_songs = select_song_rows(song_rows, artist_name)
        for song_row in selected_songs:
            artist_song_queries += 1
            song_title = get_str(song_row, "song_title")
            payload = search_musicbrainz_recording(artist_name, song_title)
            recordings = payload.get("recordings", []) if isinstance(payload, dict) else []

            if not recordings:
                lookup_rows.append(build_output_row(artist_row, song_row, None, "no_match"))
                continue

            best = sorted(
                recordings,
                key=lambda rec: (safe_int(rec.get("score"), 0), normalize_name(get_str(rec, "title")) == normalize_name(song_title)),
                reverse=True,
            )[0]

            if not is_usably_matched(artist_name, song_title, best):
                lookup_rows.append(build_output_row(artist_row, song_row, best, "ambiguous"))
                continue

            row = build_output_row(artist_row, song_row, best, "matched")
            lookup_rows.append(row)
            matched_rows.append(row)
            successful_matches += 1

            credited_names = get_str(row, "credited_artist_names")
            credited_mbids = get_str(row, "credited_artist_mbids")
            if credited_names and " | " in credited_names:
                multi_credit_matches += 1
                collaborator_preview.append(
                    {
                        "input_artist_name": row["input_artist_name"],
                        "input_song_title": row["input_song_title"],
                        "credited_artist_names": credited_names,
                        "credited_artist_mbids": credited_mbids,
                        "recording_title": row["recording_title"],
                    }
                )
            if get_str(row, "first_date") or get_str(row, "year"):
                dateful_matches += 1

    write_csv(OUTPUT_CSV, lookup_rows, OUTPUT_COLUMNS)

    summary_lines = [
        "MusicBrainz recording lookup smoke test summary",
        "",
        f"Usable artist seed file: {USABLE_MATCHES_CSV}",
        f"Song source: {SONG_SOURCE_CSV}",
        f"Cache dir: {CACHE_DIR}",
        f"Output file: {OUTPUT_CSV}",
        "",
        f"Sampled artists: {len(sample_artists)}",
        f"Artist-song queries: {artist_song_queries}",
        f"Successful recording matches: {successful_matches}",
        f"Matches with 2+ credited artists: {multi_credit_matches}",
        f"Matches with usable date/year: {dateful_matches}",
        "",
        "Sample collaborators:",
    ]

    for row in collaborator_preview[:5]:
        summary_lines.append(
            f"- {row['input_artist_name']} / {row['input_song_title']} -> {row['credited_artist_names']}"
        )

    summary_lines.extend([
        "",
        "Sample no-match or ambiguous rows:",
    ])

    for row in lookup_rows:
        if row["lookup_status"] in {"no_match", "ambiguous"}:
            summary_lines.append(
                f"- {row['input_artist_name']} / {row['input_song_title']} -> {row['lookup_status']}"
            )
        if len(summary_lines) > 40:
            break

    SUMMARY_TXT.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Sampled artists: {len(sample_artists)}")
    print(f"Artist-song queries: {artist_song_queries}")
    print(f"Successful recording matches: {successful_matches}")
    print(f"Matches with 2+ credited artists: {multi_credit_matches}")
    print(f"Matches with usable date/year: {dateful_matches}")
    print(f"Output CSV: {OUTPUT_CSV}")
    print(f"Summary TXT: {SUMMARY_TXT}")
    if collaborator_preview:
        print("Collaborator preview:")
        for row in collaborator_preview[:5]:
            print(f"- {row['input_artist_name']} / {row['input_song_title']} -> {row['credited_artist_names']}")


if __name__ == "__main__":
    main()