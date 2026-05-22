"""Minimal MusicBrainz API test for the artist collaboration network phase.

This script performs one search request against the MusicBrainz artist search
endpoint and prints a few readable results.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List

import requests

BASE_URL = "https://musicbrainz.org/ws/2/"
USER_AGENT = "CSS-Project-A/1.0 (https://github.com/Beatricia/CSS-Project-A)"
DEFAULT_QUERY = "Jamala"
TOP_RESULTS = 5
REQUEST_DELAY_SECONDS = 1


def rate_limit_pause(seconds: float = REQUEST_DELAY_SECONDS) -> None:
    """Respect the MusicBrainz rate limit."""
    time.sleep(seconds)


def search_artists(query: str) -> Dict[str, Any]:
    """Search MusicBrainz artists and return the parsed JSON response."""
    url = f"{BASE_URL}artist/"
    params = {"query": query, "fmt": "json"}
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=20)
    except requests.RequestException as exc:
        print(f"Connection error while contacting MusicBrainz: {exc}")
        return {}

    rate_limit_pause()

    if response.status_code != 200:
        print(f"Bad status code from MusicBrainz: {response.status_code}")
        print(response.text[:500])
        return {}

    try:
        return response.json()
    except ValueError:
        print("Could not decode MusicBrainz response as JSON.")
        return {}


def format_field(value: Any, fallback: str = "Unknown") -> str:
    """Return a readable string for possibly missing MusicBrainz fields."""
    if value is None:
        return fallback
    if isinstance(value, str) and not value.strip():
        return fallback
    return str(value)


def print_artist_results(results: Iterable[Dict[str, Any]], limit: int = TOP_RESULTS) -> None:
    """Print the top search results in a readable format."""
    print(f"Top {limit} MusicBrainz artist search results:\n")

    for index, artist in enumerate(results, start=1):
        if index > limit:
            break

        name = format_field(artist.get("name"))
        mbid = format_field(artist.get("id"))
        country = format_field(artist.get("country"))
        artist_type = format_field(artist.get("type"))
        disambiguation = format_field(artist.get("disambiguation"))
        score = format_field(artist.get("score"))

        print(f"{index}. {name}")
        print(f"   MusicBrainz ID: {mbid}")
        print(f"   Country: {country}")
        print(f"   Type: {artist_type}")
        print(f"   Disambiguation: {disambiguation}")
        print(f"   Score: {score}")
        print()


def main() -> None:
    print(f"Searching MusicBrainz for: {DEFAULT_QUERY}")
    data = search_artists(DEFAULT_QUERY)

    artists: List[Dict[str, Any]] = data.get("artists", []) if isinstance(data, dict) else []
    if not artists:
        print("No artist results found.")
        return

    print_artist_results(artists)


if __name__ == "__main__":
    main()
