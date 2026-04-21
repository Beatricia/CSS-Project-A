# Conflict & Music Culture Analysis
## Presentation Outline

---

## SLIDE 1: Title Slide
**Conflict & Music Culture Analysis**
*How war shapes the music we listen to*

- Your Name
- Course: Computational Social Science
- Date

---

## SLIDE 2: Central Idea

### Research Question
**How does armed conflict affect music culture in affected regions?**

We investigate three key dimensions:
1. **Artist Migration**: Where do artists flee during conflict?
2. **Popularity Shifts**: Do artists gain or lose listeners during war?
3. **Lyrical Themes**: How does conflict appear in song lyrics?

### Why is this interesting?
- Music reflects cultural identity and political sentiment
- War can create both cultural destruction AND international visibility
- Artists become voices of resistance, trauma, and hope
- Wikipedia pageviews = proxy for global attention/interest

---

## SLIDE 3: Conflict Regions Studied

| Region | Conflict | Start Date | Status |
|--------|----------|------------|--------|
| Ukraine | Russian Invasion | Feb 2022 | Ongoing |
| Russia | (Aggressor side) | Feb 2022 | Ongoing |
| Syria | Civil War | Mar 2011 | Ongoing |
| Israel | Gaza War | Oct 2023 | Ongoing |
| Palestine | Gaza War | Oct 2023 | Ongoing |

---

## SLIDE 4: Data Sources & Collection

### Dataset 1: Artist Database (Wikidata)
- **Source**: Wikidata SPARQL API
- **Method**: Query musicians by birth place + citizenship + ethnicity
- **Fields**: name, wikidata_id, origin_country, birth_place, current_residence, wiki_url

### Dataset 2: Popularity Data (Wikipedia Pageviews)
- **Source**: Wikimedia REST API
- **Method**: Monthly pageview counts per artist article
- **Date ranges**: Country-specific (2021-2024 for Ukraine, 2015-2020 for Syria, etc.)

### Dataset 3: Lyrics & Sentiment (Genius + VADER)
- **Source**: Genius API (lyrics scraping)
- **Analysis**: VADER sentiment analysis
- **Scope**: Top 10 artists per country (50 artists total)

---

## SLIDE 5: Data Collection Pipeline

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Wikidata      │     │  Wikipedia       │     │  Genius API     │
│   SPARQL API    │     │  Pageviews API   │     │  (Lyrics)       │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ artists_data.csv│     │ monthly_df       │     │ lyrics_with_    │
│ (1,583 artists) │     │ (19,869 records) │     │ sentiment.csv   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## SLIDE 6: Dataset Statistics

### Total Data Size

| Dataset | Rows | Columns | Size |
|---------|------|---------|------|
| artists_data.csv | 1,583 | 6 | 148 KB |
| monthly_pageviews.csv | 10,350 | 5 | ~500 KB |
| lyrics_with_sentiment.csv | 130 | 8 | 280 KB |
| raw_lyrics.json | - | - | 292 KB |

### Artists per Country
| Country | Artists Found | Unique Artists with Pageviews |
|---------|---------------|------------------------------|
| Ukraine | 494 | ~10 |
| Russia | 490 | ~290 |
| Israel | 490 | (to collect) |
| Syria | 86 | (to collect) |
| Palestine | 23 | (to collect) |

**Total Pageviews Collected**: 26,214,451

---

## SLIDE 7: Network Analysis Plan

### Network Structure: Artist Collaboration & Influence Network

**Nodes**: Artists (n = 1,583)
- **Attributes**: origin_country, birth_place, current_residence, total_views, sentiment scores

**Edges** (to be extracted):
1. **Collaboration links**: Artists who collaborated on songs
2. **Genre links**: Artists in same musical genre
3. **Migration links**: Artists who moved to same exile cities
4. **Influence links**: Based on Wikipedia "influences" property

### Network Metrics to Calculate:
- Degree distribution (who collaborates most?)
- Clustering by country
- Community detection (do conflict-region artists cluster?)
- Centrality (who are the "bridge" artists?)

---

## SLIDE 8: Text Analysis Plan

### Lyrics Data Structure
- **50 curated artists** (top 10 per country, selected for conflict relevance)
- **130 songs** with full lyrics
- **8 variables**: artist, country, song_title, lyrics, compound, positive, negative, neutral

### Curated Artists Include:
- **Ukraine**: Kalush Orchestra (Eurovision 2022), Go_A, Jamala
- **Russia**: Zemfira (exiled), Nogu Svelo, Kino
- **Israel**: Idan Raichel, Subliminal, Noa
- **Palestine**: DAM, Rim Banna, El Far3i
- **Syria**: Omar Souleyman, Assala Nasri, George Wassouf

### Analysis Methods:
1. **Sentiment Analysis** (VADER scores computed)
   - Compare sentiment between aggressor vs victim nations
   - Identify outlier emotions in lyrics

2. **Topic Modeling** (LDA/BERTopic)
   - Extract war-related themes
   - Track theme emergence over time

3. **Word Frequency Analysis**
   - Keywords: "war", "peace", "home", "exile", "freedom"
   - Language of resistance vs trauma

---

## SLIDE 9: Connecting Network + Text

### The Integration Strategy

```
         NETWORK                           TEXT
    ┌─────────────────┐              ┌──────────────────┐
    │  Artist Graph   │◄────────────►│  Lyrics Corpus   │
    │  (collaborations│   JOIN on    │  (sentiment per  │
    │   migrations)   │   artist_id  │   song/artist)   │
    └─────────────────┘              └──────────────────┘
              │                              │
              ▼                              ▼
    ┌─────────────────────────────────────────────────┐
    │ COMBINED ANALYSIS:                              │
    │ - Do artists with anti-war lyrics have higher   │
    │   pageview spikes during conflict?              │
    │ - Do collaboration networks predict spread of   │
    │   resistance themes?                            │
    │ - Does migration (node attribute) correlate     │
    │   with negative sentiment in lyrics?            │
    └─────────────────────────────────────────────────┘
```

---

## SLIDE 10: Preliminary Results - Pageview Analysis

### Russia (Feb 2022 War with Ukraine)
- **BEFORE** (3,635 records): 9,071,512 total views, avg 2,496/month
- **AFTER** (6,609 records): 17,120,169 total views, avg 2,590/month
- **Change**: +3.8% average monthly views

### Ukraine (Feb 2022 Russian Invasion)
- **BEFORE** (32 records): 6,931 total views, avg 217/month
- **AFTER** (74 records): 15,839 total views, avg 214/month
- **Change**: -1.2% average monthly views

### Sentiment by Country (from Lyrics Analysis)
| Country | Compound | Positive | Negative | Interpretation |
|---------|----------|----------|----------|----------------|
| Russia | -0.228 | 0.042 | 0.059 | Most negative sentiment |
| Israel | -0.016 | 0.005 | 0.011 | Slightly negative |
| Palestine | +0.055 | 0.038 | 0.031 | Slightly positive |
| Syria | +0.143 | 0.057 | 0.025 | Positive/hopeful |
| Ukraine | +0.158 | 0.032 | 0.021 | Most positive sentiment |

### Key Finding:
*Artists from invaded countries (Ukraine, Palestine, Syria) show MORE POSITIVE sentiment than aggressors (Russia) - possibly reflecting themes of hope and resistance*

---

## SLIDE 11: Preliminary Results - Visualization

[INSERT: pageviews_by_conflict.png]

**Figure**: Monthly Wikipedia pageviews for artists from each conflict region. Red dashed line = conflict start date.

---

## SLIDE 12: Preliminary Results - Sentiment

[INSERT: sentiment_analysis.png from lyrics_data/]

**Key observations**:
- Country A shows higher negative sentiment
- Sentiment trends correlate with conflict periods
- Resistance themes appear in lyrics from X country

---

## SLIDE 13: Implementation Plan

### Phase 1: Data Collection ✅ DONE
- [x] Extract artists from Wikidata
- [x] Collect Wikipedia pageviews
- [x] Scrape lyrics from Genius
- [x] Run sentiment analysis

### Phase 2: Network Construction 🔄 IN PROGRESS
- [ ] Extract collaboration data from Wikidata
- [ ] Build artist network graph
- [ ] Calculate network metrics
- [ ] Visualize network

### Phase 3: Integrated Analysis 📋 PLANNED
- [ ] Topic modeling on lyrics
- [ ] Correlate network centrality with sentiment
- [ ] Time-series analysis of pageviews + sentiment
- [ ] Final visualizations

---

## SLIDE 14: Challenges & Limitations

### Data Challenges:
1. **Wikipedia bias**: Many artists only on local-language Wikipedia (Russian, Arabic, Hebrew)
2. **Syria conflict date**: Pre-dates Wikipedia Pageviews API (2015)
3. **Lyrics availability**: Not all artists on Genius

### Methodological Considerations:
- Wikipedia pageviews ≠ actual listenership
- Sentiment analysis may miss nuance in non-English lyrics
- Correlation ≠ causation

---

## SLIDE 15: Expected Outcomes

1. **Quantified "conflict attention effect"**: How much do pageviews spike during war?

2. **Migration patterns**: Where do artists from conflict zones relocate?

3. **Sentiment timeline**: How does lyrical sentiment change around conflict?

4. **Network insights**: Do anti-war artists form communities?

---

## SLIDE 16: Questions?

**Repository**: github.com/Beatricia/CSS-Project-A

**Data files**:
- `artists_data.csv` - Artist metadata
- `lyrics_data/` - Lyrics and sentiment
- `conflict_music_analysis.ipynb` - Analysis notebook
