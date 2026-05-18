import csv
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

# ── Config ───────────────────────────────────────────────────────────────────
CSV_FILE = "data/lyrics_data/lyrics_with_sentiment_translated.csv"
OUT_DIR  = "data/lyrics_data/"

CONFLICT_YEARS = {
    "Ukraine":   2022,
    "Russia":    2022,
    "Syria":     2011,
    "Palestine": 2023,
    "Israel":    2023,
}

COUNTRY_COLORS = {
    "Ukraine":   "#4A90D9",
    "Russia":    "#E05C5C",
    "Syria":     "#F0A500",
    "Palestine": "#2ECC71",
    "Israel":    "#9B59B6",
}

COUNTRIES = ["Ukraine", "Russia", "Syria", "Palestine", "Israel"]

rows = list(csv.DictReader(open(CSV_FILE, encoding="utf-8")))

# ── 1. Pre/Post Conflict Bar Chart ───────────────────────────────────────────
print("Building chart 1: Pre/Post Conflict Bar Chart...")

by_country = defaultdict(lambda: {"pre": [], "post": []})
for row in rows:
    c = row["country"]
    p = row["period"]
    s = float(row["compound"])
    if p in ("pre", "post"):
        by_country[c][p].append(s)

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(COUNTRIES))
width = 0.35

pre_avgs  = [sum(by_country[c]["pre"])  / len(by_country[c]["pre"])  if by_country[c]["pre"]  else 0 for c in COUNTRIES]
post_avgs = [sum(by_country[c]["post"]) / len(by_country[c]["post"]) if by_country[c]["post"] else 0 for c in COUNTRIES]

bars1 = ax.bar(x - width/2, pre_avgs,  width, label="Pre-conflict",  color=[COUNTRY_COLORS[c] for c in COUNTRIES], alpha=0.45, edgecolor="white", linewidth=1.2)
bars2 = ax.bar(x + width/2, post_avgs, width, label="Post-conflict", color=[COUNTRY_COLORS[c] for c in COUNTRIES], alpha=1.0,  edgecolor="white", linewidth=1.2)

for bar in bars1:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.015, f"{h:.2f}", ha="center", va="bottom", fontsize=9)
for bar in bars2:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.015, f"{h:.2f}", ha="center", va="bottom", fontsize=9)

ax.set_xlabel("Country", fontsize=12)
ax.set_ylabel("Average Sentiment Score (VADER Compound)", fontsize=12)
ax.set_title("Lyrical Sentiment Before and After Conflict Onset\n(Translated Lyrics, VADER Analysis)", fontsize=13, fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(COUNTRIES, fontsize=11)
ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.4)
ax.legend(fontsize=11)
ax.set_ylim(-0.3, 0.85)
fig.patch.set_facecolor("#F9F9F9")
ax.set_facecolor("#F9F9F9")
plt.tight_layout()
plt.savefig(OUT_DIR + "prepost_conflict.png", dpi=150)
plt.close()
print("  Saved prepost_conflict.png")

# ── 2. Sentiment Over Time (smoothed) ────────────────────────────────────────
print("Building chart 2: Sentiment Over Time...")

MIN_SONGS = 3
by_year_country = defaultdict(lambda: defaultdict(list))
for row in rows:
    year = row["year"]
    if not year or not year.strip().isdigit():
        continue
    by_year_country[row["country"]][int(year)].append(float(row["compound"]))

fig, ax = plt.subplots(figsize=(14, 6))

for country in COUNTRIES:
    year_data = by_year_country[country]
    years = sorted(y for y in year_data if len(year_data[y]) >= MIN_SONGS)
    if len(years) < 2:
        continue
    avgs = [sum(year_data[y]) / len(year_data[y]) for y in years]
    smoothed = []
    for i in range(len(avgs)):
        window = avgs[max(0, i-1):i+2]
        smoothed.append(sum(window) / len(window))
    ax.plot(years, smoothed, color=COUNTRY_COLORS[country],
            label=country, linewidth=2.5, marker="o", markersize=4)
    cy = CONFLICT_YEARS[country]
    ax.axvline(x=cy, color=COUNTRY_COLORS[country], linestyle="--", linewidth=1.2, alpha=0.7)
    label_y = {"Ukraine": 0.92, "Russia": 0.80, "Syria": 0.92,
                "Palestine": 0.68, "Israel": 0.56}
    ax.text(cy + 0.3, label_y[country], country[:3], color=COUNTRY_COLORS[country],
            fontsize=8, transform=ax.get_xaxis_transform(), va="top")

ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Average Sentiment Score (3-yr smoothed)", fontsize=12)
ax.set_title("Lyrical Sentiment Over Time by Country\n(3-year rolling average, dashed lines = conflict start)", fontsize=13, fontweight="bold")
ax.axhline(0, color="black", linewidth=0.8, linestyle=":", alpha=0.4)
ax.legend(fontsize=10, loc="lower left")
ax.set_ylim(-1.1, 1.1)
fig.patch.set_facecolor("#F9F9F9")
ax.set_facecolor("#F9F9F9")
plt.tight_layout()
plt.savefig(OUT_DIR + "sentiment_over_time.png", dpi=150)
plt.close()
print("  Saved sentiment_over_time.png")

# ── 3. Box Plot (fixed margins) ───────────────────────────────────────────────
print("Building chart 3: Box Plot Distribution...")

fig, axes = plt.subplots(1, len(COUNTRIES), figsize=(16, 7), sharey=True)
fig.subplots_adjust(left=0.08, right=0.97, top=0.88, bottom=0.12, wspace=0.05)

for i, country in enumerate(COUNTRIES):
    pre_scores  = by_country[country]["pre"]
    post_scores = by_country[country]["post"]
    bp = axes[i].boxplot([pre_scores, post_scores], patch_artist=True, widths=0.5,
                         medianprops=dict(color="black", linewidth=2),
                         flierprops=dict(marker="o", markersize=4, alpha=0.5))
    bp["boxes"][0].set_facecolor(COUNTRY_COLORS[country])
    bp["boxes"][0].set_alpha(0.35)
    bp["boxes"][1].set_facecolor(COUNTRY_COLORS[country])
    bp["boxes"][1].set_alpha(0.9)
    axes[i].set_title(country, fontsize=11, fontweight="bold", color=COUNTRY_COLORS[country], pad=8)
    axes[i].set_xticks([1, 2])
    axes[i].set_xticklabels(["Pre", "Post"], fontsize=10)
    axes[i].axhline(0, color="black", linewidth=0.7, linestyle="--", alpha=0.4)
    axes[i].set_facecolor("#F9F9F9")
    axes[i].set_ylim(-1.15, 1.15)

axes[0].set_ylabel("Compound Sentiment Score", fontsize=11)
fig.suptitle("Distribution of Lyrical Sentiment Before and After Conflict\n(Translated Lyrics, VADER)", fontsize=13, fontweight="bold")
fig.patch.set_facecolor("#F9F9F9")
plt.savefig(OUT_DIR + "sentiment_distribution.png", dpi=150)
plt.close()
print("  Saved sentiment_distribution.png")

# ── 4. Language Distribution (cleaner) ───────────────────────────────────────
print("Building chart 4: Language Distribution...")

LANG_COLORS = {
    "English":    "#4A90D9",
    "Arabic":     "#E05C5C",
    "Hebrew":     "#9B59B6",
    "Russian":    "#E67E22",
    "Ukrainian":  "#2ECC71",
    "French":     "#1ABC9C",
    "German":     "#34495E",
    "Spanish":    "#F39C12",
    "Other":      "#BDC3C7",
}

lang_map = {
    "en": "English", "ar": "Arabic",   "he": "Hebrew",
    "ru": "Russian", "uk": "Ukrainian","fr": "French",
    "de": "German",  "es": "Spanish",  "tr": "Other",
    "id": "Other",   "so": "Other",    "no": "Other",
    "et": "Other",   "bg": "Other",    "unknown": "Other",
}

lang_by_country = defaultdict(lambda: defaultdict(int))
for row in rows:
    lang = row.get("original_lang", "unknown")
    lang_label = lang_map.get(lang, "Other")
    lang_by_country[row["country"]][lang_label] += 1

LANG_ORDER = ["English", "Arabic", "Hebrew", "Russian", "Ukrainian", "French", "German", "Spanish", "Other"]

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(COUNTRIES))
bottom = np.zeros(len(COUNTRIES))

for lang in LANG_ORDER:
    counts = [lang_by_country[c].get(lang, 0) for c in COUNTRIES]
    if sum(counts) == 0:
        continue
    bars = ax.bar(x, counts, bottom=bottom, label=lang,
                  color=LANG_COLORS.get(lang, "#BDC3C7"), edgecolor="white", linewidth=0.8)
    for j, (bar, count) in enumerate(zip(bars, counts)):
        total = sum(lang_by_country[COUNTRIES[j]].values())
        pct = count / total * 100 if total > 0 else 0
        if pct >= 8:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bottom[j] + count/2,
                    f"{lang}\n{pct:.0f}%",
                    ha="center", va="center", fontsize=8, color="white", fontweight="bold")
    bottom += np.array(counts)

ax.set_xticks(x)
ax.set_xticklabels(COUNTRIES, fontsize=11)
ax.set_ylabel("Number of Songs", fontsize=12)
ax.set_title("Language Distribution of Songs by Country\n(Why Translation Was Necessary)", fontsize=13, fontweight="bold")
ax.legend(fontsize=9, bbox_to_anchor=(1.01, 1), loc="upper left", title="Language")
fig.patch.set_facecolor("#F9F9F9")
ax.set_facecolor("#F9F9F9")
plt.tight_layout()
plt.savefig(OUT_DIR + "language_distribution.png", dpi=150, bbox_inches="tight")
plt.close()
print("  Saved language_distribution.png")

# ── 5. Sentiment Change Ranking ───────────────────────────────────────────────
print("Building chart 5: Sentiment Change Ranking...")

changes = {}
for c in COUNTRIES:
    pre  = by_country[c]["pre"]
    post = by_country[c]["post"]
    pre_avg  = sum(pre)  / len(pre)  if pre  else 0
    post_avg = sum(post) / len(post) if post else 0
    changes[c] = {"pre": pre_avg, "post": post_avg, "change": post_avg - pre_avg}

sorted_countries = sorted(changes, key=lambda c: changes[c]["change"])

fig, ax = plt.subplots(figsize=(10, 6))
y = np.arange(len(sorted_countries))
change_vals = [changes[c]["change"] for c in sorted_countries]
colors = [COUNTRY_COLORS[c] for c in sorted_countries]

bars = ax.barh(y, change_vals, color=colors, edgecolor="white", linewidth=1.2, height=0.55)

for bar, val in zip(bars, change_vals):
    xpos = val + 0.005 if val >= 0 else val - 0.005
    ha = "left" if val >= 0 else "right"
    ax.text(xpos, bar.get_y() + bar.get_height()/2, f"{val:+.3f}",
            va="center", ha=ha, fontsize=11, fontweight="bold")

ax.set_yticks(y)
ax.set_yticklabels(sorted_countries, fontsize=12)
ax.axvline(0, color="black", linewidth=1, linestyle="-", alpha=0.6)
ax.set_xlabel("Sentiment Change (Post − Pre Conflict)", fontsize=12)
ax.set_title("How Much Did Lyrical Sentiment Change After Conflict?\n(Positive = more positive post-conflict)", fontsize=13, fontweight="bold")
ax.set_xlim(-0.28, 0.42)
fig.patch.set_facecolor("#F9F9F9")
ax.set_facecolor("#F9F9F9")
plt.tight_layout()
plt.savefig(OUT_DIR + "sentiment_change_ranking.png", dpi=150)
plt.close()
print("  Saved sentiment_change_ranking.png")

print(f"\nAll 5 charts saved to {OUT_DIR}")