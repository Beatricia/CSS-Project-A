import './Dataset.css';

function Dataset() {
  return (
    <div className="dataset-page">
      <section className="page-header">
        <h1>The Dataset</h1>
        <p>Understanding our data sources and collection methodology</p>
      </section>

      <section className="section">
        <div className="container">
          <h2>Data Sources</h2>
          <div className="sources-grid">
            <div className="source-card">
              <div className="source-icon">🔗</div>
              <h3>Wikidata SPARQL API</h3>
              <p className="source-type">Artist Database</p>
              <p>
                We queried musicians by birth place, citizenship, and ethnicity 
                to build a comprehensive database of artists from conflict regions.
              </p>
              <ul className="data-fields">
                <li>Name</li>
                <li>Wikidata ID</li>
                <li>Origin Country</li>
                <li>Birth Place</li>
                <li>Current Residence</li>
                <li>Wikipedia URL</li>
              </ul>
            </div>

            <div className="source-card">
              <div className="source-icon">📊</div>
              <h3>Wikipedia Pageviews API</h3>
              <p className="source-type">Popularity Data</p>
              <p>
                Monthly pageview counts for each artist's Wikipedia article, 
                serving as a proxy for global interest and attention.
              </p>
              <ul className="data-fields">
                <li>Artist Name</li>
                <li>Monthly Views</li>
                <li>Date Range</li>
                <li>Country</li>
              </ul>
            </div>

            <div className="source-card">
              <div className="source-icon">🎵</div>
              <h3>Genius API</h3>
              <p className="source-type">Lyrics & Sentiment</p>
              <p>
                Song lyrics scraped for top artists, analyzed using VADER 
                sentiment analysis to understand emotional content.
              </p>
              <ul className="data-fields">
                <li>Song Title</li>
                <li>Lyrics</li>
                <li>Sentiment Scores</li>
                <li>Release Year</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Dataset Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <span className="stat-number">1,583</span>
              <span className="stat-label">Artists</span>
              <span className="stat-detail">From 5 conflict regions</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">10,350+</span>
              <span className="stat-label">Pageview Records</span>
              <span className="stat-detail">Monthly tracking data</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">130+</span>
              <span className="stat-label">Songs Analyzed</span>
              <span className="stat-detail">With sentiment scores</span>
            </div>
            <div className="stat-card">
              <span className="stat-number">5</span>
              <span className="stat-label">Conflict Regions</span>
              <span className="stat-detail">Ukraine, Russia, Syria, Israel, Palestine</span>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <h2>Artists by Country</h2>
          <div className="country-breakdown">
            <div className="country-bar">
              <span className="country-name">Ukraine</span>
              <div className="bar-container">
                <div className="bar ukraine-bar" style={{width: '31%'}}></div>
                <span className="bar-value">494 artists</span>
              </div>
            </div>
            <div className="country-bar">
              <span className="country-name">Russia</span>
              <div className="bar-container">
                <div className="bar russia-bar" style={{width: '31%'}}></div>
                <span className="bar-value">490 artists</span>
              </div>
            </div>
            <div className="country-bar">
              <span className="country-name">Israel</span>
              <div className="bar-container">
                <div className="bar israel-bar" style={{width: '31%'}}></div>
                <span className="bar-value">490 artists</span>
              </div>
            </div>
            <div className="country-bar">
              <span className="country-name">Syria</span>
              <div className="bar-container">
                <div className="bar syria-bar" style={{width: '5%'}}></div>
                <span className="bar-value">86 artists</span>
              </div>
            </div>
            <div className="country-bar">
              <span className="country-name">Palestine</span>
              <div className="bar-container">
                <div className="bar palestine-bar" style={{width: '1.5%'}}></div>
                <span className="bar-value">23 artists</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Data Pipeline</h2>
          <div className="pipeline">
            <div className="pipeline-step">
              <div className="step-number">1</div>
              <h3>Query Artists</h3>
              <p>SPARQL queries to Wikidata for musicians from each region</p>
            </div>
            <div className="pipeline-arrow">→</div>
            <div className="pipeline-step">
              <div className="step-number">2</div>
              <h3>Fetch Pageviews</h3>
              <p>Wikipedia API for monthly view counts per artist</p>
            </div>
            <div className="pipeline-arrow">→</div>
            <div className="pipeline-step">
              <div className="step-number">3</div>
              <h3>Scrape Lyrics</h3>
              <p>Genius API for song lyrics from top artists</p>
            </div>
            <div className="pipeline-arrow">→</div>
            <div className="pipeline-step">
              <div className="step-number">4</div>
              <h3>Analyze Sentiment</h3>
              <p>VADER sentiment analysis on all lyrics</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dataset;
