# MusicBrainz Network Test Setup

This folder is the isolated starting point for the MusicBrainz-only artist collaboration network work.

## What this is for

The goal of this phase is to verify that we can talk to the MusicBrainz API cleanly before building any network logic.
This folder only contains a minimal API test script and its notes.

## API notes

MusicBrainz does not require an API key for basic public requests.
For this project we are using the following User-Agent exactly:

CSS-Project-A/1.0

MusicBrainz asks clients to respect a rate limit of one request per second.
Future scripts in this folder should follow that rule.

## Files

- `test_musicbrainz_api.py`: one small search test against the MusicBrainz artist endpoint.

## How to run

From the repo root, run:

python scripts/musicbrainz_network/test_musicbrainz_api.py

If Python reports that `requests` is missing, install it with:

pip install requests
