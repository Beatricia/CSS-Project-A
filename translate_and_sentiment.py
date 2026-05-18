import json
import time
import csv
from langdetect import detect
from deep_translator import GoogleTranslator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ── Config ──────────────────────────────────────────────────────────────────
INPUT_JSON  = "data/lyrics_data/raw_lyrics.json"
OUTPUT_CSV  = "data/lyrics_data/lyrics_with_sentiment_translated.csv"
LOG_FILE    = "data/lyrics_data/translation_log.txt"

CONFLICT_YEARS = {
    "Ukraine":   2022,
    "Russia":    2022,
    "Syria":     2011,
    "Palestine": 2023,
    "Israel":    2023,
}

MAX_CHARS = 4500   # Google Translate free limit per request
SLEEP_SEC = 1.5    # pause between API calls to avoid rate-limit

# ── Helpers ──────────────────────────────────────────────────────────────────
analyzer = GoogleTranslator(source="auto", target="en")
vader    = SentimentIntensityAnalyzer()

def detect_lang(text):
    try:
        return detect(text[:500])
    except Exception:
        return "unknown"

def translate_text(text):
    """Translate a block of text to English, chunking if needed."""
    if not text or len(text.strip()) < 10:
        return text
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + MAX_CHARS])
        start += MAX_CHARS
    translated_chunks = []
    for chunk in chunks:
        try:
            result = GoogleTranslator(source="auto", target="en").translate(chunk)
            translated_chunks.append(result or chunk)
            time.sleep(SLEEP_SEC)
        except Exception as e:
            print(f"  [translate error] {e}")
            translated_chunks.append(chunk)   # fallback: keep original
    return " ".join(translated_chunks)

def get_period(year, country):
    if year is None:
        return "post"   # default as before
    conflict = CONFLICT_YEARS.get(country)
    if conflict is None:
        return "unknown"
    return "pre" if int(year) < conflict else "post"

# ── Main ─────────────────────────────────────────────────────────────────────
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Loaded {len(data)} songs.\n")

results = []
log_lines = []

for i, song in enumerate(data):
    artist  = song.get("artist", "")
    country = song.get("country", "")
    title   = song.get("song_title", "")
    year    = song.get("year")
    lyrics  = song.get("lyrics") or ""

    print(f"[{i+1}/{len(data)}] {artist} — {title}", end=" ")

    # detect language
    lang = detect_lang(lyrics)
    translated = False

    if lang != "en" and len(lyrics.strip()) >= 50:
        print(f"({lang} → translating...)", end=" ")
        lyrics_for_vader = translate_text(lyrics)
        translated = True
    else:
        lyrics_for_vader = lyrics
        print(f"({lang}, keeping)", end=" ")

    # VADER on (possibly translated) lyrics
    scores = vader.polarity_scores(lyrics_for_vader)
    compound = scores["compound"]
    period   = get_period(year, country)

    print(f"→ compound={compound:.3f}")

    results.append({
        "artist":          artist,
        "country":         country,
        "song_title":      title,
        "year":            year,
        "original_lang":   lang,
        "translated":      translated,
        "compound":        compound,
        "positive":        scores["pos"],
        "negative":        scores["neg"],
        "neutral":         scores["neu"],
        "period":          period,
    })

    log_lines.append(f"{'TRANSLATED' if translated else 'KEPT      '} | {lang:8} | {country:10} | {artist} — {title}")

# ── Save CSV ──────────────────────────────────────────────────────────────────
fieldnames = ["artist","country","song_title","year","original_lang",
              "translated","compound","positive","negative","neutral","period"]

with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

# ── Save log ──────────────────────────────────────────────────────────────────
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

# ── Summary ───────────────────────────────────────────────────────────────────
total      = len(results)
translated = sum(1 for r in results if r["translated"])
print(f"\nDone! {total} songs processed, {translated} translated.")
print(f"CSV  → {OUTPUT_CSV}")
print(f"Log  → {LOG_FILE}")