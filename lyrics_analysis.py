import lyricsgenius
import pandas as pd
import matplotlib.pyplot as plt
import json
import time
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ============================================================
# CONFIG
# ============================================================
GENIUS_TOKEN = "vsGycUlc8-swa6gJf5TkETdfWD1QP1MUkbrqaVY21ngIcZ02H3Kl0dHlZWtGmDRf"

TOP_ARTISTS = {
    "Ukraine": [
        "Jamala",           # 2016 Eurovision winner, song about Crimea deportation
        "Kalush Orchestra", # 2022 Eurovision winner, performed during invasion
        "Okean Elzy",       # Iconic Ukrainian rock, anti-war statements
        "Antytila",         # Joined Ukrainian army in 2022
        "Boombox",          # Lead singer joined army 2022
        "Alyona Alyona",    # Ukrainian hip-hop, identity themes
        "Jerry Heil",       # Released war-themed songs 2022
        "Ruslana",          # Eurovision 2004, vocal pro-Ukraine activist
        "Skofka",           # Ukrainian rap, war themes post 2022
        "Khrystyna Soloviy" # Ukrainian folk, cultural resistance
    ],
    "Russia": [
        "Viktor Tsoi",      # Soviet rock legend, anti-authoritarian themes
        "Bulat Okudzhava",  # WWII protest songs
        "Vladimir Vysotsky",# Soviet-era protest singer
        "Zemfira",          # Left Russia after 2022, anti-war
        "Oxxxymiron",       # Cancelled Russian shows, anti-war
        "Noize MC",         # Openly anti-war statements
        "Pussy Riot",       # Political protest group
        "DDT",              # Yuri Shevchuk criticised Putin directly
        "Aquarium",         # Boris Grebenshchikov, left Russia
        "Yuri Shevchuk"     # Called war a catastrophe publicly
    ],
    "Israel": [
        "Mira Awad",        # Arab-Israeli artist, sings about coexistence
        "David Broza",      # Peace activist, Israeli-Palestinian themes
        "Yehuda Poliker",   # Holocaust and conflict themes
        "Subliminal",       # Israeli rap, conflict themes
        "Tamer Nafar",      # Palestinian-Israeli rapper, DAM founder
        "Noa",              # Peace activist, collaboration with Arabs
        "Aviv Geffen",      # Wrote song after Rabin assassination
        "Idan Raichel",     # Multicultural themes, coexistence
        "Yasmin Levy",      # Sephardic identity and displacement
        "Arik Einstein"     # Classic Israeli, songs about war and peace
    ],
    "Syria": [
        "Omar Souleyman",   # Active during civil war, fled Syria
        "Kinan Azmeh",      # Left Syria, performs for refugees
        "Lena Chamamyan",   # Left Damascus, sings in Arabic/Armenian
        "Fairuz",           # Voice of Arab world, sung about displacement
        "Farid al-Atrash",  # Classic Syrian, themes of longing and exile
        "Abed Azrie",       # Syrian exile in France
        "Faia Younan",      # Fled to Sweden during civil war
        "Nassif Zeytoun",   # Rose to fame during Syrian civil war
        "George Wassouf",   # Syrian icon, themes of loss
        "Waed Bouhassoun"   # Traditional Syrian music, exile themes
    ],
    "Palestine": [
        "DAM",              # First Palestinian rap group, occupation themes
        "Shadia Mansour",   # "First Lady of Arabic Hip Hop", resistance
        "Tamer Nafar",      # Raps about Palestinian identity
        "Mohammed Assaf",   # Gaza singer, symbol of Palestinian hope
        "Saint Levant",     # Gaza-born, sings about conflict
        "Elyanna",          # Palestinian-Israeli, cultural identity
        "Bashar Murad",     # Queer Palestinian artist, resistance themes
        "Remi Kanazi",      # Palestinian-American spoken word
        "Mahmoud Darwish",  # Palestine's national poet, set to music
        "Kamilya Jubran"    # Palestinian oud player, exile themes
    ]
}

# ============================================================
# STEP 1: SCRAPE LYRICS
# ============================================================
def scrape_lyrics():
    genius = lyricsgenius.Genius(
    GENIUS_TOKEN,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)"],
    timeout=30,
    retries=2
)
    genius.verbose = False

    results = []
    os.makedirs("lyrics_data", exist_ok=True)

    for country, artists in TOP_ARTISTS.items():
        print(f"\n{'='*40}")
        print(f"Scraping: {country}")
        print(f"{'='*40}")

        for artist_name in artists:
            print(f"  -> {artist_name}...", end=" ")
            try:
                artist = genius.search_artist(artist_name, max_songs=3, sort="popularity")
                if artist and artist.songs:
                    for song in artist.songs:
                        if song.lyrics:
                            results.append({
                                "artist": artist_name,
                                "country": country,
                                "song_title": song.title,
                                "lyrics": song.lyrics[:3000]
                            })
                    print(f"Got {len(artist.songs)} songs")
                else:
                    print("No songs found")
                time.sleep(1)
            except Exception as e:
                print(f"Error: {e}")
                continue

    with open("lyrics_data/raw_lyrics.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nTotal songs collected: {len(results)}")
    return results

# ============================================================
# STEP 2: VADER SENTIMENT ANALYSIS
# ============================================================
def analyze_sentiment(results):
    analyzer = SentimentIntensityAnalyzer()

    for item in results:
        scores = analyzer.polarity_scores(item['lyrics'])
        item['compound'] = scores['compound']
        item['positive'] = scores['pos']
        item['negative'] = scores['neg']
        item['neutral'] = scores['neu']

    df = pd.DataFrame(results)
    df.to_csv("lyrics_data/lyrics_with_sentiment.csv", index=False)
    print("Sentiment analysis done!")
    return df

# ============================================================
# STEP 3: VISUALIZE
# ============================================================
def visualize(df):
    country_sentiment = df.groupby('country')['compound'].mean().sort_values()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#1a1a2e')

    country_colors = {
        'Ukraine': '#FFD700',
        'Russia': '#E63946',
        'Israel': '#3A86FF',
        'Syria': '#FF6B35',
        'Palestine': '#2DC653'
    }

    # Plot 1: Average sentiment
    ax1 = axes[0]
    ax1.set_facecolor('#16213e')
    colors = [country_colors.get(c, '#888') for c in country_sentiment.index]
    bars = ax1.barh(country_sentiment.index, country_sentiment.values,
                    color=colors, alpha=0.85, edgecolor='#0f3460')
    ax1.axvline(0, color='white', linewidth=0.8, linestyle='--', alpha=0.5)
    ax1.set_xlabel('Average Sentiment (VADER compound score)', color='white', fontsize=10)
    ax1.set_title('Average Music Sentiment\nby Conflict Country', color='white',
                  fontsize=12, fontweight='bold')
    ax1.tick_params(colors='white')
    for bar, val in zip(bars, country_sentiment.values):
        ax1.text(val + 0.01 if val >= 0 else val - 0.01,
                 bar.get_y() + bar.get_height()/2,
                 f'{val:.2f}', va='center',
                 ha='left' if val >= 0 else 'right',
                 color='white', fontsize=9, fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_color('#555')
    ax1.spines['left'].set_color('#555')

    # Plot 2: Positive vs Negative breakdown
    ax2 = axes[1]
    ax2.set_facecolor('#16213e')
    country_avg = df.groupby('country')[['positive', 'negative', 'neutral']].mean()
    x = range(len(country_avg))
    width = 0.25
    ax2.bar([i - width for i in x], country_avg['positive'],
            width, label='Positive', color='#2DC653', alpha=0.85)
    ax2.bar(x, country_avg['neutral'],
            width, label='Neutral', color='#8E8EA0', alpha=0.85)
    ax2.bar([i + width for i in x], country_avg['negative'],
            width, label='Negative', color='#E63946', alpha=0.85)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(country_avg.index, color='white', fontsize=9)
    ax2.set_ylabel('Score', color='white', fontsize=10)
    ax2.set_title('Positive / Neutral / Negative\nBreakdown by Country', color='white',
                  fontsize=12, fontweight='bold')
    ax2.tick_params(colors='white')
    ax2.legend(facecolor='#0f3460', labelcolor='white', fontsize=9)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_color('#555')
    ax2.spines['left'].set_color('#555')

    plt.tight_layout(pad=3)
    plt.savefig('lyrics_data/sentiment_analysis.png', dpi=150,
                bbox_inches='tight', facecolor='#1a1a2e')
    plt.show()
    print("Chart saved to lyrics_data/sentiment_analysis.png")

    print("\n=== SENTIMENT SUMMARY (for presentation) ===")
    print(df.groupby('country')['compound'].agg(['mean', 'count']).round(3))

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("Step 1: Scraping lyrics from Genius...")
    results = scrape_lyrics()

    if results:
        print("\nStep 2: Running VADER sentiment analysis...")
        df = analyze_sentiment(results)

        print("\nStep 3: Creating visualizations...")
        visualize(df)
    else:
        print("No lyrics collected — check your token or artist names.")