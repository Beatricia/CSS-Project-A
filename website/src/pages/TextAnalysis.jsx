import './TextAnalysis.css';

const TOP_POSITIVE = [
  { title: "Stefania", artist: "Kalush Orchestra", country: "🇺🇦 Ukraine", score: "+0.98" },
  { title: "Varta", artist: "Ruslana", country: "🇺🇦 Ukraine", score: "+0.95" },
  { title: "Lena Chamamyan", artist: "Lena Chamamyan", country: "🇸🇾 Syria", score: "+0.98" },
  { title: "Shadia Mansour", artist: "Shadia Mansour", country: "🇵🇸 Palestine", score: "+0.98" },
  { title: "David Broza", artist: "David Broza", country: "🇮🇱 Israel", score: "+0.92" },
];

const TOP_NEGATIVE = [
  { title: "Post-conflict track", artist: "Pussy Riot", country: "🇷🇺 Russia", score: "−0.97" },
  { title: "Post-conflict track", artist: "Bulat Okudzhava", country: "🇷🇺 Russia", score: "−0.97" },
  { title: "Post-conflict track", artist: "Oxxxymiron", country: "🇷🇺 Russia", score: "−0.87" },
  { title: "Post-conflict track", artist: "Noize MC", country: "🇷🇺 Russia", score: "−0.83" },
  { title: "Mahmoud Darwish", artist: "Mahmoud Darwish", country: "🇵🇸 Palestine", score: "−0.64" },
];

function TextAnalysis() {
  return (
    <div className="text-analysis-page">
      <section className="page-header">
        <h1>Text Analysis</h1>
        <p>Exploring sentiment and themes in lyrics from conflict regions</p>
      </section>

      {/* Methodology */}
      <section className="section">
        <div className="container">
          <h2>Sentiment Analysis Overview</h2>
          <p className="section-intro">
            We analysed lyrics from 50 artists across 5 conflict-affected countries —
            Ukraine, Russia, Syria, Palestine, and Israel — covering 739 songs in total.
            Because most artists sing in non-English languages, we first translated all
            lyrics to English using Google Translate before running VADER sentiment scoring.
            This step was essential: without translation, over 80% of songs would have
            returned a near-zero score simply due to language mismatch, not actual sentiment.
          </p>

          <div className="method-card">
            <h3>🔬 Methodology</h3>
            <p>
              We used <strong>VADER (Valence Aware Dictionary and sEntiment Reasoner)</strong>,
              a lexicon and rule-based sentiment analysis tool. Each song receives a
              compound score from −1 (very negative) to +1 (very positive).
              Songs are classified as <em>pre-conflict</em> or <em>post-conflict </em>
              based on release year versus each country's conflict start year
              (Ukraine &amp; Russia: 2022, Syria: 2011, Palestine &amp; Israel: 2023).
            </p>
            <div className="method-metrics">
              <div className="metric">
                <span className="metric-label">Positive</span>
                <span className="metric-desc">Proportion of positive sentiment</span>
              </div>
              <div className="metric">
                <span className="metric-label">Negative</span>
                <span className="metric-desc">Proportion of negative sentiment</span>
              </div>
              <div className="metric">
                <span className="metric-label">Neutral</span>
                <span className="metric-desc">Proportion of neutral sentiment</span>
              </div>
              <div className="metric">
                <span className="metric-label">Compound</span>
                <span className="metric-desc">Overall sentiment score (−1 to +1)</span>
              </div>
            </div>
          </div>

          {/* Language distribution */}
          <h2 style={{ marginTop: "2rem" }}>Why Translation Was Necessary</h2>
          <p className="section-intro">
            The chart below shows how few songs per country were originally in English.
            Syria and Israel had over 90% non-English lyrics — making translation
            a critical pre-processing step rather than an optional one.
          </p>
          <div className="chart-container">
            <img src="/CSS-Project-A/language_distribution.png" alt="Language distribution by country" className="chart-img" />
          </div>
        </div>
      </section>

      {/* Pre/Post conflict */}
      <section className="section alt-bg">
        <div className="container">
          <h2>Sentiment Before and After Conflict</h2>
          <p className="section-intro">
            Russia is the only country where lyrical sentiment clearly dropped after conflict onset,
            falling from +0.02 pre-war to −0.16 post-war. Israel showed the largest positive shift
            (+0.28), possibly reflecting a surge in nationally resilient or patriotic music.
            Ukraine remained relatively stable with a slight decrease (−0.01).
          </p>
          <div className="chart-container">
            <img src="/CSS-Project-A/prepost_conflict.png" alt="Pre and post conflict sentiment by country" className="chart-img" />
          </div>

          <h2 style={{ marginTop: "2.5rem" }}>Sentiment Change Ranking</h2>
          <p className="section-intro">
            A direct comparison of how much each country's average lyrical sentiment
            shifted after conflict. Negative values indicate music became darker;
            positive values indicate music became more emotionally uplifting.
          </p>
          <div className="chart-container">
            <img src="/CSS-Project-A/sentiment_change_ranking.png" alt="Sentiment change ranking" className="chart-img" />
          </div>
        </div>
      </section>

      {/* Artist heatmap */}
      <section className="section">
        <div className="container">
          <h2>Artist-level Sentiment Heatmap</h2>
          <p className="section-intro">
            Each column represents one artist. Green cells indicate positive sentiment,
            red indicates negative. Grey means no songs were available for that period.
            Russia's post-conflict artists (Pussy Riot, Oxxxymiron, Noize MC) stand out
            as the most consistently negative — reflecting overt anti-war sentiment.
          </p>
          <div className="chart-container">
            <img src="/CSS-Project-A/artist_heatmap.png" alt="Artist level sentiment heatmap" className="chart-img" />
          </div>
        </div>
      </section>

      {/* Sentiment over time */}
      <section className="section alt-bg">
        <div className="container">
          <h2>Sentiment Over Time</h2>
          <p className="section-intro">
            Tracking how the emotional tone of music shifts in relation to conflict start years
            (shown as dashed vertical lines). Russia shows a sharp decline after 2022.
            Syria's trajectory remains relatively stable despite conflict beginning in 2011,
            possibly because many post-2011 songs are from artists who continued
            making celebratory or traditional music abroad.
          </p>
          <div className="chart-container">
            <img src="/CSS-Project-A/sentiment_over_time.png" alt="Sentiment over time by country" className="chart-img" />
          </div>
        </div>
      </section>

      {/* Notable songs */}
      <section className="section">
        <div className="container">
          <h2>Notable Songs</h2>

          <div className="songs-section">
            <h3 className="songs-heading">🎵 Most Positive Artists (Pre-conflict)</h3>
            <div className="songs-grid">
              {TOP_POSITIVE.map((s, i) => (
                <div key={i} className="song-card positive-song">
                  <div className="song-info">
                    <span className="song-artist">{s.artist}</span>
                    <span className="song-country">{s.country}</span>
                  </div>
                  <div className="song-score">{s.score}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="songs-section" style={{ marginTop: "2rem" }}>
            <h3 className="songs-heading">🎵 Most Negative Artists (Post-conflict)</h3>
            <div className="songs-grid">
              {TOP_NEGATIVE.map((s, i) => (
                <div key={i} className="song-card negative-song">
                  <div className="song-info">
                    <span className="song-artist">{s.artist}</span>
                    <span className="song-country">{s.country}</span>
                  </div>
                  <div className="song-score">{s.score}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Featured song */}
      <section className="section alt-bg">
        <div className="container">
          <h2>Featured Song Analysis</h2>

          <div className="featured-song">
            <div className="song-header">
              <h3>"1944" by Jamala</h3>
              <span className="country-tag">🇺🇦 Ukraine</span>
            </div>
            <div className="lyrics-excerpt">
              <p>
                <em>"When strangers are coming<br />
                They come to your house<br />
                They kill you all<br />
                And say we're not guilty, not guilty..."</em>
              </p>
            </div>
            <div className="song-analysis">
              <p>
                This Eurovision-winning song tells the story of the 1944 deportation
                of Crimean Tatars under Soviet rule. Written and released in 2016,
                long before the 2022 invasion, it demonstrates how music preserves
                collective memory and serves as quiet resistance. Jamala's pre-conflict
                average compound score of +0.54 reflects an emotionally complex
                catalogue — not purely dark, but carrying weight.
              </p>
              <div className="analysis-scores">
                <div className="score-item">
                  <span className="score-label">Pre-conflict avg</span>
                  <span className="score-value">+0.54</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Post-conflict avg</span>
                  <span className="score-value">+0.22</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Change</span>
                  <span className="score-value negative">−0.32</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default TextAnalysis;