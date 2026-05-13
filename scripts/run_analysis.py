import json
import pandas as pd
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

CONFLICT_YEARS = {
    "Ukraine": 2022,
    "Russia": 2022,
    "Syria": 2011,
    "Palestine": 2023,
    "Israel": 2023,
}

with open("../data/lyrics_data/raw_lyrics.json", "r", encoding="utf-8") as f:
    results = json.load(f)

print(f"Loaded {len(results)} songs")

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
print(df.groupby('country')['compound'].agg(['mean', 'count']).round(3))
print("\n=== PRE vs POST ===")
df_filtered = df[df['period'].isin(['pre', 'post'])]
print(df_filtered.groupby(['country', 'period'])['compound'].mean().round(3))

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
ax1.set_xlabel('Average Sentiment', color='white')
ax1.set_title('Overall Sentiment by Country', color='white', fontweight='bold')
ax1.tick_params(colors='white')
for bar, val in zip(bars, sentiment.values):
    ax1.text(val + 0.01 if val >= 0 else val - 0.01,
             bar.get_y() + bar.get_height()/2,
             f'{val:.2f}', va='center',
             ha='left' if val >= 0 else 'right',
             color='white', fontsize=9)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

ax2 = axes[1]
ax2.set_facecolor('#16213e')
pre_post = df_filtered.groupby(['country', 'period'])['compound'].mean().unstack(fill_value=0)
x = range(len(pre_post))
width = 0.35
ax2.bar([i - width/2 for i in x], pre_post['pre'], width, label='Pre-conflict', color='#3A86FF', alpha=0.85)
ax2.bar([i + width/2 for i in x], pre_post['post'], width, label='Post-conflict', color='#E63946', alpha=0.85)
ax2.axhline(0, color='white', linewidth=0.8, linestyle='--', alpha=0.5)
ax2.set_xticks(list(x))
ax2.set_xticklabels(pre_post.index, color='white')
ax2.set_ylabel('Sentiment Score', color='white')
ax2.set_title('Pre vs Post Conflict Sentiment', color='white', fontweight='bold')
ax2.tick_params(colors='white')
ax2.legend(facecolor='#0f3460', labelcolor='white')
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

plt.tight_layout(pad=3)
plt.savefig('../data/lyrics_data/sentiment_analysis.png', dpi=150, bbox_inches='tight', facecolor='#1a1a2e')
plt.show()
print("Chart saved!")