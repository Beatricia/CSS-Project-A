import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

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

country_colors = {
    'Ukraine': '#FFD700', 'Russia': '#E63946',
    'Israel': '#3A86FF', 'Syria': '#FF6B35', 'Palestine': '#2DC653'
}

countries = ['Ukraine', 'Russia', 'Israel', 'Syria', 'Palestine']

fig, axes = plt.subplots(1, 5, figsize=(20, 7), sharey=True)
fig.patch.set_facecolor('#1a1a2e')
fig.suptitle('Sentiment Tone Change: Before vs After Conflict', 
             color='white', fontsize=16, fontweight='bold', y=1.02)

for idx, country in enumerate(countries):
    ax = axes[idx]
    ax.set_facecolor('#16213e')
    
    country_df = df[(df['country'] == country) & (df['period'].isin(['pre', 'post']))]
    pre = country_df[country_df['period'] == 'pre']['compound'].mean()
    post = country_df[country_df['period'] == 'post']['compound'].mean()
    
    color = country_colors[country]
    conflict_year = CONFLICT_YEARS[country]
    
    # bars
    bars = ax.bar(['Pre\n(before {})'.format(conflict_year), 
                   'Post\n(after {})'.format(conflict_year)], 
                  [pre, post], 
                  color=[color, '#ff4444' if post < pre else '#44ff44'],
                  alpha=0.85, width=0.5)
    
    # value labels
    for bar, val in zip(bars, [pre, post]):
        ax.text(bar.get_x() + bar.get_width()/2, 
                val + 0.005 if val >= 0 else val - 0.015,
                f'{val:.3f}', ha='center', va='bottom' if val >= 0 else 'top',
                color='white', fontsize=11, fontweight='bold')
    
    # arrow showing change
    ax.annotate('', xy=(1, post), xytext=(0, pre),
                arrowprops=dict(arrowstyle='->', color='white', lw=2))
    
    # change label
    change = post - pre
    ax.text(0.5, max(pre, post) + 0.03, 
            f'{"↑" if change > 0 else "↓"} {abs(change):.3f}',
            ha='center', color='#44ff44' if change > 0 else '#ff4444',
            fontsize=12, fontweight='bold', transform=ax.transData)
    
    ax.axhline(0, color='white', linewidth=0.8, linestyle='--', alpha=0.5)
    ax.set_title(country, color=color, fontsize=13, fontweight='bold')
    ax.tick_params(colors='white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#555')
    ax.spines['left'].set_color('#555')
    ax.set_ylim(-0.35, 0.45)

axes[0].set_ylabel('Sentiment Score', color='white', fontsize=11)

plt.tight_layout()
plt.savefig('lyrics_data/prepost_conflict.png', dpi=150, 
            bbox_inches='tight', facecolor='#1a1a2e')
plt.show()
print("Pre/Post conflict chart saved!")