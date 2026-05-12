import './TextAnalysis.css';

function TextAnalysis() {
  return (
    <div className="text-analysis-page">
      <section className="page-header">
        <h1>Text Analysis</h1>
        <p>Exploring sentiment and themes in lyrics from conflict regions</p>
      </section>

      <section className="section">
        <div className="container">
          <h2>Sentiment Analysis Overview</h2>
          <p className="section-intro">
            Using VADER sentiment analysis, we examined the emotional content of songs 
            from artists in conflict regions. The analysis reveals how artists process 
            and express experiences of war, displacement, and resilience.
          </p>

          <div className="method-card">
            <h3>🔬 Methodology</h3>
            <p>
              We used <strong>VADER (Valence Aware Dictionary and sEntiment Reasoner)</strong>, 
              a lexicon and rule-based sentiment analysis tool specifically attuned to 
              sentiments expressed in social media and informal text.
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
                <span className="metric-desc">Overall sentiment score (-1 to +1)</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Sentiment Distribution</h2>
          
          <div className="visualization-placeholder">
            <div className="placeholder-content">
              <span className="placeholder-icon">📊</span>
              <h3>Sentiment Analysis Chart</h3>
              <p>
                Sentiment distribution visualization will be embedded here.
                <br />
                <em>(Replace with your sentiment_analysis.png or interactive chart)</em>
              </p>
            </div>
          </div>

          <div className="sentiment-summary">
            <div className="sentiment-card positive">
              <h4>😊 Positive Songs</h4>
              <p>
                Songs expressing hope, love, resilience, and celebration of cultural identity.
                Often found in folk traditions and contemporary pop.
              </p>
            </div>
            <div className="sentiment-card negative">
              <h4>😢 Negative Songs</h4>
              <p>
                Songs expressing grief, loss, anger, and protest. Common themes include 
                separation, destruction, and injustice.
              </p>
            </div>
            <div className="sentiment-card neutral">
              <h4>😐 Neutral Songs</h4>
              <p>
                Songs with balanced or matter-of-fact content, including narrative 
                storytelling and observational lyrics.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <h2>Word Cloud Analysis</h2>
          <p className="section-intro">
            The most frequent words in lyrics from conflict regions reveal 
            common themes and emotional touchpoints.
          </p>

          <div className="visualization-placeholder">
            <div className="placeholder-content">
              <span className="placeholder-icon">☁️</span>
              <h3>Word Cloud</h3>
              <p>
                Word frequency visualization will be embedded here.
                <br />
                <em>(Replace with your wordcloud.png)</em>
              </p>
            </div>
          </div>

          <div className="themes-grid">
            <div className="theme-card">
              <h4>🏠 Home & Homeland</h4>
              <p>Words related to home, country, land, and belonging appear frequently.</p>
            </div>
            <div className="theme-card">
              <h4>❤️ Love & Loss</h4>
              <p>Universal themes of love, relationships, and separation.</p>
            </div>
            <div className="theme-card">
              <h4>💪 Resistance & Hope</h4>
              <p>Expressions of strength, perseverance, and hope for the future.</p>
            </div>
            <div className="theme-card">
              <h4>🕊️ Peace & Freedom</h4>
              <p>Aspirations for peace, freedom, and an end to conflict.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Sentiment Over Time</h2>
          <p className="section-intro">
            Tracking how the emotional tone of music changes in relation to conflict events.
          </p>

          <div className="visualization-placeholder">
            <div className="placeholder-content">
              <span className="placeholder-icon">📈</span>
              <h3>Sentiment Timeline</h3>
              <p>
                Temporal sentiment visualization will be embedded here.
                <br />
                <em>(Replace with your sentiment_over_time.png)</em>
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <h2>Notable Songs</h2>
          
          <div className="songs-section">
            <h3 className="songs-heading">🎵 Most Positive Songs</h3>
            <div className="songs-grid">
              <div className="song-card positive-song">
                <div className="song-info">
                  <span className="song-title">Song Title</span>
                  <span className="song-artist">Artist Name</span>
                  <span className="song-country">Country</span>
                </div>
                <div className="song-score">+0.XX</div>
              </div>
              {/* Add more song cards dynamically */}
              <p className="placeholder-note">
                <em>Top positive songs from your analysis will appear here</em>
              </p>
            </div>
          </div>

          <div className="songs-section">
            <h3 className="songs-heading">🎵 Most Negative Songs</h3>
            <div className="songs-grid">
              <div className="song-card negative-song">
                <div className="song-info">
                  <span className="song-title">Song Title</span>
                  <span className="song-artist">Artist Name</span>
                  <span className="song-country">Country</span>
                </div>
                <div className="song-score">-0.XX</div>
              </div>
              {/* Add more song cards dynamically */}
              <p className="placeholder-note">
                <em>Top negative songs from your analysis will appear here</em>
              </p>
            </div>
          </div>
        </div>
      </section>

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
                <em>"When strangers are coming<br/>
                They come to your house<br/>
                They kill you all<br/>
                And say we're not guilty, not guilty..."</em>
              </p>
            </div>
            <div className="song-analysis">
              <p>
                This Eurovision-winning song tells the story of the 1944 deportation 
                of Crimean Tatars. The song connects historical trauma to contemporary 
                events, demonstrating how music preserves collective memory and serves 
                as a form of resistance and remembrance.
              </p>
              <div className="analysis-scores">
                <div className="score-item">
                  <span className="score-label">Compound Score</span>
                  <span className="score-value negative">-0.XX</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Negative %</span>
                  <span className="score-value">XX%</span>
                </div>
                <div className="score-item">
                  <span className="score-label">Positive %</span>
                  <span className="score-value">XX%</span>
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
