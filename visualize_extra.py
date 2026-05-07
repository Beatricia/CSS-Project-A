import json
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

CONFLICT_YEARS = {
    "Ukraine": 2022,
    "Russia": 2022,
    "Syria": 2011,
    "Palestine": 2023,
    "Israel": 2023,
}

with open("lyrics_data/raw_lyrics.json", "r", encoding="utf-8") as f:
    results = json.load(f)

analyzer = SentimentIntensityAnalyzer()
for item in results:
    scores = analyzer.polarity_scores(item['lyrics'])
    item['compound'] = scores['compound']
    conflict_year = CONFLICT_YEARS.get(item['country'], 2022)
    try:
        year = int(str(item['year'])[:4]) if item['year'] else None
        item['period'] = 'pre' if year and year < conflict_year else 'post'
        item['year_int'] = year
    except:
        item['period'] = 'unknown'
        item['year_int'] = None

df = pd.DataFrame(results)

# ===== 1. WORD CLOUD =====
fig, axes = plt.subplots(1, 5, figsize=(25, 5))
fig.patch.set_facecolor('#1a1a2e')
fig.suptitle('Most Common Words by Country', color='white', fontsize=16, fontweight='bold')

country_colors = {
    'Ukraine': '#FFD700', 'Russia': '#E63946',
    'Israel': '#3A86FF', 'Syria': '#FF6B35', 'Palestine': '#2DC653'
}

for idx, country in enumerate(['Ukraine', 'Russia', 'Israel', 'Syria', 'Palestine']):
    country_df = df[df['country'] == country]
    text = ' '.join(country_df['lyrics'].tolist())
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower()
    
    wc = WordCloud(
        width=400, height=400,
        background_color='#16213e',
        colormap='Blues' if country == 'Russia' else 'YlOrRd',
        max_words=50
    ).generate(text)
    
    axes[idx].imshow(wc, interpolation='bilinear')
    axes[idx].axis('off')
    axes[idx].set_title(country, color=country_colors[country], fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('lyrics_data/wordcloud.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.show()
print("Word cloud saved!")

# ===== 2. SENTIMENT OVER TIME =====
df_year = df[df['year_int'].notna() & (df['year_int'] > 1990) & (df['year_int'] <= 2026)]
df_year['year_int'] = df_year['year_int'].astype(int)

fig, ax = plt.subplots(figsize=(14, 6))
fig.patch.set_facecolor('#1a1a2e')
ax.set_facecolor('#16213e')

for country, color in country_colors.items():
    country_df = df_year[df_year['country'] == country]
    if not country_df.empty:
        yearly = country_df.groupby('year_int')['compound'].mean()
        ax.plot(yearly.index, yearly.values, marker='o', label=country, 
                color=color, linewidth=2, markersize=5)
        
        conflict_year = CONFLICT_YEARS[country]
        ax.axvline(conflict_year, color=color, linestyle='--', alpha=0.3)

ax.axhline(0, color='white', linewidth=0.8, linestyle='--', alpha=0.5)
ax.set_xlabel('Year', color='white')
ax.set_ylabel('Sentiment Score', color='white')
ax.set_title('Sentiment Over Time by Country', color='white', fontsize=14, fontweight='bold')
ax.tick_params(colors='white')
ax.legend(facecolor='#0f3460', labelcolor='white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#555')
ax.spines['left'].set_color('#555')

plt.tight_layout()
plt.savefig('lyrics_data/sentiment_over_time.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.show()
print("Sentiment over time saved!")

# ===== 3. TOP POSITIVE/NEGATIVE SONGS =====
print("\n=== TOP 5 MOST POSITIVE SONGS ===")
top_positive = df.nlargest(5, 'compound')[['artist', 'country', 'song_title', 'compound', 'year_int']]
print(top_positive.to_string(index=False))

print("\n=== TOP 5 MOST NEGATIVE SONGS ===")
top_negative = df.nsmallest(5, 'compound')[['artist', 'country', 'song_title', 'compound', 'year_int']]
print(top_negative.to_string(index=False))

# Save as CSV
top_positive.to_csv('lyrics_data/top_positive_songs.csv', index=False)
top_negative.to_csv('lyrics_data/top_negative_songs.csv', index=False)
print("\nSaved to CSV!")