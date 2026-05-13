import lyricsgenius
import pandas as pd
import matplotlib.pyplot as plt
import json
import time
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

GENIUS_TOKEN = "vsGycUlc8-swa6gJf5TkETdfWD1QP1MUkbrqaVY21ngIcZ02H3Kl0dHlZWtGmDRf"

CONFLICT_YEARS = {
    "Ukraine": 2022,
    "Russia": 2022,
    "Syria": 2011,
    "Palestine": 2023,
    "Israel": 2023,
}

TOP_ARTISTS = {
    
    "Ukraine": [
        "Jamala", "Kalush Orchestra", "Okean Elzy", "Antytila",
        "Boombox", "Alyona Alyona", "Jerry Heil", "Ruslana",
        "Skofka", "Khrystyna Soloviy"
    ],
     "Russia": [
         "Viktor Tsoi", "Bulat Okudzhava", "Vladimir Vysotsky",
         "Zemfira", "Oxxxymiron", "Noize MC", "Pussy Riot",
         "DDT", "Aquarium", "Yuri Shevchuk"
     ],
     "Israel": [
         "Mira Awad", "David Broza", "Yehuda Poliker", "Subliminal",
         "Tamer Nafar", "Noa", "Aviv Geffen", "Idan Raichel",
         "Yasmin Levy", "Arik Einstein"
    ],
     "Syria": [
         "Omar Souleyman", "Kinan Azmeh", "Lena Chamamyan", "Fairuz",
        "Farid al-Atrash", "Abed Azrie", "Faia Younan",
         "Nassif Zeytoun", "George Wassouf", "Waed Bouhassoun"
    ],
     "Palestine": [
         "DAM", "Shadia Mansour", "Tamer Nafar", "Mohammed Assaf",
         "Saint Levant", "Elyanna", "Bashar Murad", "Remi Kanazi",
         "Mahmoud Darwish", "Kamilya Jubran"
     ]
}

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
    os.makedirs("../data/lyrics_data", exist_ok=True)

    for country, artists in TOP_ARTISTS.items():
        print(f"\n{'='*40}")
        print(f"Scraping: {country}")
        print(f"{'='*40}")

        for artist_name in artists:
            print(f"  -> {artist_name}...", end=" ")
            try:
                artist = genius.search_artist(artist_name, max_songs=20, sort="popularity")
                if artist and artist.songs:
                    for song in artist.songs:
                        if song.lyrics:
                            results.append({
                                "artist": artist_name,
                                "country": country,
                                "song_title": song.title,
                                "year": song.to_dict().get("release_date_components", {}).get("year") if song.to_dict().get("release_date_components") else None,
                                "lyrics": song.lyrics[:3000]
                            })
                    print(f"Got {len(artist.songs)} songs")
                else:
                    print("No songs found")
                time.sleep(1)
            except Exception as e:
                print(f"Error: {e}")
                print("Waiting 60 seconds before continuing...")
                time.sleep(60)
                try:
                    artist = genius.search_artist(artist_name, max_songs=20, sort="popularity")
                    if artist and artist.songs:
                        for song in artist.songs:
                            if song.lyrics:
                                country_results.append({
                                    "artist": artist_name,
                                    "country": country,
                                    "song_title": song.title,
                                    "year": song.to_dict().get("release_date_components", {}).get("year") if song.to_dict().get("release_date_components") else None,
                                    "lyrics": song.lyrics[:3000]
                                })
                        print(f"Got {len(artist.songs)} songs")
                    else:
                        print("No songs found")
                except Exception as e2:
                    print(f"Retry failed: {e2}, skipping...")
                continue

    with open("../data/lyrics_data/raw_lyrics.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nTotal songs: {len(results)}")
    return results

def analyze_sentiment(results):
    analyzer = SentimentIntensityAnalyzer()

    for item in results:
        scores = analyzer.polarity_scores(item['lyrics'])
        item['compound'] = scores['compound']
        item['positive'] = scores['pos']
        item['negative'] = scores['neg']
        item['neutral'] = scores['neu']

        conflict_year = CONFLICT_YEARS.get(item['country'], 2022)
        try:
            year = int(str(item['year'])[:4]) if item['year'] else None
            item['period'] = 'pre' if year and year < conflict_year else 'post'
        except:
            item['period'] = 'unknown'

    df = pd.DataFrame(results)
    df.to_csv("../data/lyrics_data/lyrics_with_sentiment.csv", index=False)
    print("Sentiment analysis done!")
    return df

def visualize(df):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('#1a1a2e')

    country_colors = {
        'Ukraine': '#FFD700', 'Russia': '#E63946',
        'Israel': '#3A86FF', 'Syria': '#FF6B35', 'Palestine': '#2DC653'
    }

    ax1 = axes[0]
    ax1.set_facecolor('#16213e')
    sentiment = df.groupby('country')['compound'].mean().sort_values()
    colors = [country_colors.get(c, '#888') for c in sentiment.index]
    bars = ax1.barh(sentiment.index, sentiment.values, color=colors, alpha=0.85)
    ax1.axvline(0, color='white', linewidth=0.8, linestyle='--', alpha=0.5)
    ax1.set_xlabel('Average Sentiment', color='white', fontsize=10)
    ax1.set_title('Overall Sentiment by Country', color='white', fontsize=12, fontweight='bold')
    ax1.tick_params(colors='white')
    for bar, val in zip(bars, sentiment.values):
        ax1.text(val + 0.01 if val >= 0 else val - 0.01,
                 bar.get_y() + bar.get_height()/2,
                 f'{val:.2f}', va='center',
                 ha='left' if val >= 0 else 'right',
                 color='white', fontsize=9, fontweight='bold')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_color('#555')
    ax1.spines['left'].set_color('#555')

    ax2 = axes[1]
    ax2.set_facecolor('#16213e')
    df_filtered = df[df['period'].isin(['pre', 'post'])]
    pre_post = df_filtered.groupby(['country', 'period'])['compound'].mean().unstack(fill_value=0)

    x = range(len(pre_post))
    width = 0.35
    if 'pre' in pre_post.columns:
        ax2.bar([i - width/2 for i in x], pre_post['pre'], width,
                label='Pre-conflict', color='#3A86FF', alpha=0.85)
    if 'post' in pre_post.columns:
        ax2.bar([i + width/2 for i in x], pre_post['post'], width,
                label='Post-conflict', color='#E63946', alpha=0.85)
    ax2.axhline(0, color='white', linewidth=0.8, linestyle='--', alpha=0.5)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(pre_post.index, color='white', fontsize=9)
    ax2.set_ylabel('Sentiment Score', color='white', fontsize=10)
    ax2.set_title('Pre vs Post Conflict\nSentiment Change', color='white',
                  fontsize=12, fontweight='bold')
    ax2.tick_params(colors='white')
    ax2.legend(facecolor='#0f3460', labelcolor='white', fontsize=9)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_color('#555')
    ax2.spines['left'].set_color('#555')

    plt.tight_layout(pad=3)
    plt.savefig('../data/lyrics_data/sentiment_analysis.png', dpi=150,
                bbox_inches='tight', facecolor='#1a1a2e')
    plt.show()
    print("Chart saved!")
    print("\n=== SENTIMENT SUMMARY ===")
    print(df.groupby('country')['compound'].agg(['mean', 'count']).round(3))
    print("\n=== PRE vs POST ===")
    if not df_filtered.empty:
        print(df_filtered.groupby(['country', 'period'])['compound'].mean().round(3))

if __name__ == "__main__":
    print("Scraping lyrics...")
    results = scrape_lyrics()
    if results:
        print("\nAnalyzing sentiment...")
        df = analyze_sentiment(results)
        print("\nCreating charts...")
        visualize(df)
    else:
        print("No lyrics found.")