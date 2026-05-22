"""Quickly promote additional usable MusicBrainz artist matches for lyric artists.

This script does not call MusicBrainz. It only uses the existing CSV outputs to
promote a small number of additional lyric artists into a conservative expanded
seed file for the selected-song collaboration network.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[2]
LYRICS_CSV = ROOT / "data" / "lyrics_data" / "lyrics_with_sentiment_translated.csv"
ARTIST_MATCHES_CSV = ROOT / "data" / "network" / "artist_matches.csv"
ARTIST_CANDIDATES_CSV = ROOT / "data" / "network" / "artist_match_candidates.csv"
USABLE_MATCHES_CSV = ROOT / "data" / "network" / "usable_artist_matches.csv"
EXPANDED_USABLE_CSV = ROOT / "data" / "network" / "expanded_usable_artist_matches.csv"
PROMO_CANDIDATES_CSV = ROOT / "data" / "network" / "quick_promotion_candidates.csv"
SUMMARY_TXT = ROOT / "data" / "network" / "quick_promotion_summary.txt"


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


def normalize_name(value: str) -> str:
    text = (value or "").lower().strip()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace("’", "'").replace("`", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    text = re.sub(r"\(.*?\)", "", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity(left: str, right: str) -> float:
    return SequenceMatcher(None, normalize_name(left), normalize_name(right)).ratio()


def is_generic_single_word(name: str) -> bool:
    normalized = normalize_name(name)
    return len(normalized.split()) == 1 and normalized not in {
        "jamala",
        "alyona",
        "jerry",
        "bashar",
        "saint",
        "monika",
        "ela",
        "subliminal",
        "yasmin",
    }


def song_counts_by_artist(rows: List[Dict[str, str]]) -> Dict[str, int]:
    counts: Counter = Counter()
    for row in rows:
        artist = get_str(row, "artist")
        if artist:
            counts[normalize_name(artist)] += 1
    return dict(counts)


def best_usable_artist_set(rows: List[Dict[str, str]]) -> set[str]:
    usable = set()
    for row in rows:
        for key in ("input_artist_name", "matched_name"):
            artist = get_str(row, key)
            if artist:
                usable.add(normalize_name(artist))
    return usable


def build_lookup_maps(
    artist_matches_rows: List[Dict[str, str]],
    candidate_rows: List[Dict[str, str]],
) -> Tuple[Dict[str, Dict[str, str]], Dict[str, List[Dict[str, str]]]]:
    best_rows_by_artist: Dict[str, Dict[str, str]] = {}
    for row in artist_matches_rows:
        artist_key = normalize_name(get_str(row, "input_artist_name"))
        if not artist_key:
            continue
        if row.get("match_status") != "review_needed":
            continue
        existing = best_rows_by_artist.get(artist_key)
        if existing is None:
            best_rows_by_artist[artist_key] = row
            continue
        existing_score = int(get_str(existing, "score") or 0)
        current_score = int(get_str(row, "score") or 0)
        if current_score > existing_score:
            best_rows_by_artist[artist_key] = row

    candidates_by_artist: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in candidate_rows:
        artist_key = normalize_name(get_str(row, "input_artist_name"))
        if artist_key:
            candidates_by_artist[artist_key].append(row)
    for rows in candidates_by_artist.values():
        rows.sort(key=lambda row: int(get_str(row, "candidate_rank") or 9999))

    return best_rows_by_artist, candidates_by_artist


def row_score(row: Dict[str, str]) -> int:
    try:
        return int(float(get_str(row, "score") or 0))
    except ValueError:
        return 0


def type_mismatch_ok(lyrics_artist: str, matched_name: str, row_type: str) -> bool:
    if not row_type:
        return True
    normalized_artist = normalize_name(lyrics_artist)
    normalized_matched = normalize_name(matched_name)
    if row_type.lower() == "person":
        if is_generic_single_word(lyrics_artist) and normalized_artist != normalized_matched:
            return False
    if row_type.lower() in {"group", "choir", "orchestra"}:
        if normalized_artist == normalized_matched:
            return True
    return True


def candidate_row_for_promotion(
    lyric_artist: str,
    best_match_row: Dict[str, str],
    candidate_rows: List[Dict[str, str]],
) -> Optional[Tuple[Dict[str, str], str]]:
    if not best_match_row:
        return None

    matched_name = get_str(best_match_row, "matched_name")
    matched_type = get_str(best_match_row, "type")
    norm_lyric = normalize_name(lyric_artist)
    norm_matched = normalize_name(matched_name)
    if not norm_lyric or not norm_matched:
        return None

    exact_norm = norm_lyric == norm_matched
    if not exact_norm:
        if similarity(lyric_artist, matched_name) < 0.94:
            return None
        if is_generic_single_word(lyric_artist) or is_generic_single_word(matched_name):
            return None

    if not type_mismatch_ok(lyric_artist, matched_name, matched_type):
        return None

    if get_str(best_match_row, "match_status") != "review_needed":
        return None

    if row_score(best_match_row) < 90:
        return None

    # Require the candidate list to agree with the selected row or show a very
    # strong top-1 signal for the same matched artist.
    candidate_rank1 = candidate_rows[0] if candidate_rows else None
    if candidate_rank1 is not None:
        rank1_name = normalize_name(get_str(candidate_rank1, "matched_name"))
        rank1_score = int(get_str(candidate_rank1, "score") or 0)
        if rank1_name and rank1_name != norm_matched and candidate_rank1.get("matched_name"):
            return None
        if rank1_score and rank1_score < 90 and not exact_norm:
            return None

    if not exact_norm and row_score(best_match_row) < 95:
        return None

    return best_match_row, ("Exact normalized match" if exact_norm else "Very close normalized match")


def promotion_row_from_usable(row: Dict[str, str]) -> Dict[str, str]:
    promoted = dict(row)
    promoted["promotion_source"] = "original_usable"
    promoted["promotion_reason"] = "Original high-confidence usable match"
    promoted["usable_for_network"] = row.get("usable_for_network", "True") or "True"
    return promoted


def promotion_row_from_match(row: Dict[str, str], reason: str) -> Dict[str, str]:
    promoted = {
        "input_artist_name": get_str(row, "input_artist_name"),
        "matched_name": get_str(row, "matched_name"),
        "mbid": get_str(row, "mbid"),
        "musicbrainz_country": get_str(row, "musicbrainz_country"),
        "type": get_str(row, "type"),
        "disambiguation": get_str(row, "disambiguation"),
        "match_status": get_str(row, "match_status"),
        "score": get_str(row, "score"),
        "notes": get_str(row, "notes"),
        "source_name": get_str(row, "source_name"),
        "source_wikidata_id": get_str(row, "source_wikidata_id"),
        "source_origin_country": get_str(row, "source_origin_country"),
        "source_birth_place": get_str(row, "source_birth_place"),
        "source_current_residence": get_str(row, "source_current_residence"),
        "source_wiki_url": get_str(row, "source_wiki_url"),
        "usable_for_network": "True",
        "triage_reason": get_str(row, "notes") or "Quickly promoted from lyric artist cross-check",
        "promotion_source": "quick_promoted_lyrics_artist",
        "promotion_reason": reason,
    }
    return promoted


def main() -> None:
    lyrics_rows = read_csv(LYRICS_CSV)
    usable_rows = read_csv(USABLE_MATCHES_CSV)
    artist_matches_rows = read_csv(ARTIST_MATCHES_CSV)
    candidate_rows = read_csv(ARTIST_CANDIDATES_CSV)

    lyric_counts = song_counts_by_artist(lyrics_rows)
    lyric_artists = sorted(lyric_counts.keys(), key=lambda key: (-lyric_counts[key], key))
    usable_set = best_usable_artist_set(usable_rows)
    artists_already_usable = sorted([artist for artist in lyric_artists if artist in usable_set])
    lyric_artists_not_usable = [artist for artist in lyric_artists if artist not in usable_set]

    best_match_rows_by_artist, candidates_by_artist = build_lookup_maps(artist_matches_rows, candidate_rows)

    promoted_rows: List[Dict[str, str]] = [promotion_row_from_usable(row) for row in usable_rows]
    quick_promotion_rows: List[Dict[str, str]] = []
    unresolved_artists: List[str] = []

    considered_artists = lyric_artists_not_usable[:]
    for artist_key in considered_artists:
        lyric_name = next((row.get("artist", "").strip() for row in lyrics_rows if normalize_name(get_str(row, "artist")) == artist_key), "")
        if not lyric_name:
            continue

        best_match = best_match_rows_by_artist.get(artist_key)
        candidate_rows_for_artist = candidates_by_artist.get(artist_key, [])
        promotion = candidate_row_for_promotion(lyric_name, best_match or {}, candidate_rows_for_artist)
        if promotion is None:
            unresolved_artists.append(artist_key)
            continue

        row, reason = promotion
        promoted_rows.append(promotion_row_from_match(row, reason))
        quick_promotion_rows.append(
            {
                "lyric_artist": lyric_name,
                "lyrics_song_count": lyric_counts[artist_key],
                "matched_name": get_str(row, "matched_name"),
                "mbid": get_str(row, "mbid"),
                "score": get_str(row, "score"),
                "type": get_str(row, "type"),
                "promotion_reason": reason,
            }
        )

    fieldnames = list(promoted_rows[0].keys()) if promoted_rows else []
    if "promotion_source" not in fieldnames:
        fieldnames.append("promotion_source")
    if "promotion_reason" not in fieldnames:
        fieldnames.append("promotion_reason")
    write_csv(EXPANDED_USABLE_CSV, promoted_rows, fieldnames)

    promo_candidate_fieldnames = [
        "lyric_artist",
        "lyrics_song_count",
        "matched_name",
        "mbid",
        "score",
        "type",
        "promotion_reason",
    ]
    write_csv(PROMO_CANDIDATES_CSV, quick_promotion_rows, promo_candidate_fieldnames)

    top_unresolved = sorted(
        unresolved_artists,
        key=lambda artist_key: (-lyric_counts[artist_key], artist_key),
    )[:20]

    summary_lines = [
        "Quick promotion summary",
        "",
        f"Unique artists in lyrics CSV: {len(lyric_artists)}",
        f"Artists already usable: {len(artists_already_usable)}",
        f"Lyric artists not currently usable: {len(lyric_artists_not_usable)}",
        f"Newly promoted artists: {len(quick_promotion_rows)}",
        f"Still unresolved lyric artists: {len(unresolved_artists)}",
        f"Total rows in expanded_usable_artist_matches.csv: {len(promoted_rows)}",
        "",
        "Top unresolved lyric artists by song_count:",
    ]

    for artist_key in top_unresolved:
        lyric_name = next((row.get("artist", "").strip() for row in lyrics_rows if normalize_name(get_str(row, "artist")) == artist_key), artist_key)
        summary_lines.append(f"- {lyric_name} | song_count={lyric_counts[artist_key]}")

    summary_lines.extend([
        "",
        "Promoted examples:",
    ])
    for row in quick_promotion_rows[:10]:
        summary_lines.append(
            f"- {row['lyric_artist']} -> {row['matched_name']} | score={row['score']} | {row['promotion_reason']}"
        )

    summary_lines.extend([
        "",
        f"Expanded usable file: {EXPANDED_USABLE_CSV}",
        f"Promotion candidates file: {PROMO_CANDIDATES_CSV}",
    ])
    SUMMARY_TXT.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Unique artists in lyrics CSV: {len(lyric_artists)}")
    print(f"Artists already usable: {len(artists_already_usable)}")
    print(f"Lyric artists not currently usable: {len(lyric_artists_not_usable)}")
    print(f"Newly promoted artists: {len(quick_promotion_rows)}")
    print(f"Still unresolved lyric artists: {len(unresolved_artists)}")
    print(f"Total rows in expanded_usable_artist_matches.csv: {len(promoted_rows)}")
    print(f"Expanded usable file: {EXPANDED_USABLE_CSV}")
    print(f"Promotion candidates file: {PROMO_CANDIDATES_CSV}")
    print(f"Summary file: {SUMMARY_TXT}")
    if quick_promotion_rows:
        print("Promoted examples:")
        for row in quick_promotion_rows[:5]:
            print(f"- {row['lyric_artist']} -> {row['matched_name']} | score={row['score']} | {row['promotion_reason']}")


if __name__ == "__main__":
    main()