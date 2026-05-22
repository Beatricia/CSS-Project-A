"""Read-only inspector for candidate MusicBrainz seed artist sources.

This script only summarizes existing files. It does not modify any data and
does not call MusicBrainz.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[2]


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def unique_nonempty(values: Iterable[Any]) -> List[Any]:
    seen = []
    for value in values:
        if value in (None, ""):
            continue
        if value not in seen:
            seen.append(value)
    return seen


def summarize_csv(path: Path, name_field: str | None = None) -> None:
    rows = read_csv(path)
    fields = list(rows[0].keys()) if rows else []
    print(f"FILE: {path.relative_to(ROOT)}")
    print(f"rows: {len(rows)}")
    print(f"fields: {', '.join(fields) if fields else 'none'}")

    if name_field and rows:
        names = unique_nonempty(row.get(name_field) for row in rows)
        print(f"unique {name_field}s: {len(names)}")
        print(f"sample {name_field}s: {', '.join(str(name) for name in names[:5])}")

    if rows and "country" in fields:
        countries = Counter(row.get("country") for row in rows if row.get("country"))
        print(f"countries: {', '.join(f'{country} ({count})' for country, count in countries.most_common())}")

    if rows and "period" in fields:
        periods = Counter(row.get("period") for row in rows if row.get("period"))
        print(f"periods: {', '.join(f'{period} ({count})' for period, count in periods.most_common())}")

    if rows and "original_lang" in fields:
        langs = Counter(row.get("original_lang") for row in rows if row.get("original_lang"))
        print(f"languages: {', '.join(f'{lang} ({count})' for lang, count in langs.most_common())}")

    print()


def summarize_json(path: Path) -> None:
    rows = read_json(path)
    fields = list(rows[0].keys()) if rows else []
    print(f"FILE: {path.relative_to(ROOT)}")
    print(f"rows: {len(rows)}")
    print(f"fields: {', '.join(fields) if fields else 'none'}")

    if rows:
        artists = unique_nonempty(row.get("artist") for row in rows)
        countries = Counter(row.get("country") for row in rows if row.get("country"))
        years = unique_nonempty(row.get("year") for row in rows)
        print(f"unique artists: {len(artists)}")
        print(f"sample artists: {', '.join(str(artist) for artist in artists[:5])}")
        print(f"countries: {', '.join(f'{country} ({count})' for country, count in countries.most_common())}")
        print(f"has year field: {'yes' if years else 'no'}")

    print()


def summarize_hardcoded_artists(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    countries = []
    artists_by_country: Dict[str, List[str]] = {}
    current_country = None

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('"') and stripped.endswith('": ['):
            current_country = stripped.split('"')[1]
            countries.append(current_country)
            artists_by_country[current_country] = []
            continue
        if current_country and stripped.startswith('"'):
            artist = stripped.strip(',').strip('"')
            if artist:
                artists_by_country[current_country].append(artist)
        if current_country and stripped == '],':
            current_country = None

    total = sum(len(items) for items in artists_by_country.values())
    print(f"FILE: {path.relative_to(ROOT)}")
    print(f"countries: {', '.join(countries)}")
    print(f"total hardcoded artists: {total}")
    for country, items in artists_by_country.items():
        print(f"{country}: {len(items)} artists")
        print(f"  sample: {', '.join(items[:5])}")
    print()


def main() -> None:
    summarize_csv(ROOT / "data" / "artists_data.csv", name_field="name")
    summarize_json(ROOT / "data" / "lyrics_data" / "raw_lyrics.json")
    summarize_csv(ROOT / "data" / "lyrics_data" / "lyrics_with_sentiment.csv", name_field="artist")
    summarize_csv(ROOT / "data" / "lyrics_data" / "lyrics_with_sentiment_translated.csv", name_field="artist")
    summarize_csv(ROOT / "data" / "lyrics_data" / "top_positive_songs.csv", name_field="artist")
    summarize_csv(ROOT / "data" / "lyrics_data" / "top_negative_songs.csv", name_field="artist")
    summarize_hardcoded_artists(ROOT / "scripts" / "lyrics_analysis.py")


if __name__ == "__main__":
    main()