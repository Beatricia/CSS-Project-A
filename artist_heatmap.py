import csv
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

CSV_FILE = "data/lyrics_data/lyrics_with_sentiment_translated.csv"
OUT_DIR  = "data/lyrics_data/"

COUNTRY_COLORS = {
    "Ukraine":   "#4A90D9",
    "Russia":    "#E05C5C",
    "Syria":     "#F0A500",
    "Palestine": "#2ECC71",
    "Israel":    "#9B59B6",
}

COUNTRIES = ["Ukraine", "Russia", "Syria", "Palestine", "Israel"]

rows = list(csv.DictReader(open(CSV_FILE, encoding="utf-8")))

# ── Build artist pre/post averages ────────────────────────────────────────────
artist_data = defaultdict(lambda: {"country": "", "pre": [], "post": []})
for row in rows:
    a = row["artist"]
    artist_data[a]["country"] = row["country"]
    p = row["period"]
    if p in ("pre", "post"):
        artist_data[a][p].append(float(row["compound"]))

# build rows: artist, country, pre_avg, post_avg, change
records = []
for artist, d in artist_data.items():
    pre  = d["pre"]
    post = d["post"]
    if not pre or not post:
        continue
    pre_avg  = sum(pre)  / len(pre)
    post_avg = sum(post) / len(post)
    records.append({
        "artist":   artist,
        "country":  d["country"],
        "pre":      pre_avg,
        "post":     post_avg,
        "change":   post_avg - pre_avg,
    })

# sort by country then by change
records.sort(key=lambda r: (COUNTRIES.index(r["country"]) if r["country"] in COUNTRIES else 99, r["change"]))

artists   = [r["artist"]  for r in records]
countries = [r["country"] for r in records]
pre_vals  = [r["pre"]     for r in records]
post_vals = [r["post"]    for r in records]

n = len(artists)
data_matrix = np.array([pre_vals, post_vals])  # shape (2, n)

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(18, 7))

cmap = plt.cm.RdYlGn
norm = mcolors.Normalize(vmin=-1, vmax=1)

im = ax.imshow(data_matrix, cmap=cmap, norm=norm, aspect="auto")

# x-axis: artist names
ax.set_xticks(range(n))
ax.set_xticklabels(artists, rotation=45, ha="right", fontsize=8)

# y-axis: Pre / Post
ax.set_yticks([0, 1])
ax.set_yticklabels(["Pre-conflict", "Post-conflict"], fontsize=11, fontweight="bold")

# color score values inside cells
for col in range(n):
    for row_i, val in enumerate([pre_vals[col], post_vals[col]]):
        text_color = "black" if -0.5 < val < 0.5 else "white"
        ax.text(col, row_i, f"{val:.2f}", ha="center", va="center",
                fontsize=7, color=text_color, fontweight="bold")

# country separator lines + labels
current_country = None
country_start = 0
for i, country in enumerate(countries):
    if country != current_country:
        if current_country is not None:
            ax.axvline(x=i - 0.5, color="white", linewidth=2.5)
        mid = (country_start + i) / 2 - 0.5
        if current_country:
            ax.text(mid, -0.7, current_country, ha="center", va="top",
                    fontsize=10, fontweight="bold",
                    color=COUNTRY_COLORS.get(current_country, "black"),
                    transform=ax.transData)
        current_country = country
        country_start = i

# last country label
mid = (country_start + n) / 2 - 0.5
ax.text(mid, -0.7, current_country, ha="center", va="top",
        fontsize=10, fontweight="bold",
        color=COUNTRY_COLORS.get(current_country, "black"),
        transform=ax.transData)

# colorbar
cbar = plt.colorbar(im, ax=ax, orientation="vertical", pad=0.01, fraction=0.015)
cbar.set_label("Sentiment Score", fontsize=10)
cbar.set_ticks([-1, -0.5, 0, 0.5, 1])
cbar.set_ticklabels(["−1\n(Very Negative)", "−0.5", "0\n(Neutral)", "0.5", "+1\n(Very Positive)"])

ax.set_title("Artist-level Sentiment Before and After Conflict\n(Green = Positive, Red = Negative)", 
             fontsize=13, fontweight="bold", pad=20)

fig.patch.set_facecolor("#F9F9F9")
ax.set_facecolor("#F9F9F9")
plt.tight_layout()
plt.savefig(OUT_DIR + "artist_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved artist_heatmap.png")