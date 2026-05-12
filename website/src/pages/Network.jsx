import './Network.css';

function Network() {
  return (
    <div className="network-page">
      <section className="page-header">
        <h1>Network Analysis</h1>
        <p>Mapping artist connections and migration patterns</p>
      </section>

      <section className="section">
        <div className="container">
          <h2>Artist Migration Map</h2>
          <p className="section-intro">
            This interactive map shows where artists from conflict regions have relocated.
            The connections reveal patterns of cultural exchange and displacement.
          </p>
          
          <div className="visualization-placeholder">
            <div className="placeholder-content">
              <span className="placeholder-icon">🗺️</span>
              <h3>Interactive World Map</h3>
              <p>
                Artist migration visualization will be embedded here.
                <br />
                <em>(Replace with your artists_world_map.html or an embedded visualization)</em>
              </p>
            </div>
          </div>

          <div className="map-legend">
            <h4>Map Legend</h4>
            <div className="legend-items">
              <div className="legend-item">
                <span className="legend-dot origin"></span>
                <span>Origin Country</span>
              </div>
              <div className="legend-item">
                <span className="legend-dot destination"></span>
                <span>Current Residence</span>
              </div>
              <div className="legend-item">
                <span className="legend-line"></span>
                <span>Migration Path</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Migration Patterns</h2>
          <div className="patterns-grid">
            <div className="pattern-card">
              <h3>🇺🇦 Ukrainian Artists</h3>
              <p>
                Following the 2022 invasion, many Ukrainian artists relocated to 
                Western Europe and the United States, with notable concentrations 
                in Poland, Germany, and the UK.
              </p>
              <div className="pattern-destinations">
                <span className="dest-tag">Poland</span>
                <span className="dest-tag">Germany</span>
                <span className="dest-tag">UK</span>
                <span className="dest-tag">USA</span>
              </div>
            </div>

            <div className="pattern-card">
              <h3>🇸🇾 Syrian Artists</h3>
              <p>
                The Syrian civil war led to significant artist displacement, 
                with many seeking refuge in neighboring countries and Europe.
              </p>
              <div className="pattern-destinations">
                <span className="dest-tag">Turkey</span>
                <span className="dest-tag">Lebanon</span>
                <span className="dest-tag">Germany</span>
                <span className="dest-tag">Sweden</span>
              </div>
            </div>

            <div className="pattern-card">
              <h3>🇷🇺 Russian Artists</h3>
              <p>
                Some Russian artists left following the 2022 invasion, 
                often relocating to countries with existing Russian communities.
              </p>
              <div className="pattern-destinations">
                <span className="dest-tag">Georgia</span>
                <span className="dest-tag">Armenia</span>
                <span className="dest-tag">Israel</span>
                <span className="dest-tag">USA</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <h2>Pageview Analysis</h2>
          <p className="section-intro">
            Wikipedia pageviews serve as a proxy for global attention. 
            We tracked how conflict events affected artist visibility worldwide.
          </p>

          <div className="visualization-placeholder">
            <div className="placeholder-content">
              <span className="placeholder-icon">📈</span>
              <h3>Pre/Post Conflict Comparison</h3>
              <p>
                Pageview trends visualization will be embedded here.
                <br />
                <em>(Replace with your prepost_conflict chart)</em>
              </p>
            </div>
          </div>

          <div className="insights-boxes">
            <div className="insight-box">
              <h4>Key Finding</h4>
              <p>
                Artists from conflict regions often see a spike in global attention 
                immediately following major conflict events, as international audiences 
                seek to understand the cultural context.
              </p>
            </div>
            <div className="insight-box">
              <h4>Sustained Interest</h4>
              <p>
                Some artists maintain elevated pageviews long after initial spikes, 
                suggesting lasting cultural impact and continued international interest.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Network Connections</h2>
          <p className="section-intro">
            Beyond geographic migration, we analyze artistic collaborations and 
            genre connections among artists from conflict regions.
          </p>

          <div className="network-stats">
            <div className="network-stat">
              <span className="stat-value">—</span>
              <span className="stat-label">Network Nodes</span>
            </div>
            <div className="network-stat">
              <span className="stat-value">—</span>
              <span className="stat-label">Connections</span>
            </div>
            <div className="network-stat">
              <span className="stat-value">—</span>
              <span className="stat-label">Communities</span>
            </div>
          </div>

          <div className="visualization-placeholder">
            <div className="placeholder-content">
              <span className="placeholder-icon">🕸️</span>
              <h3>Artist Network Graph</h3>
              <p>
                Network visualization will be embedded here.
                <br />
                <em>(Add your network graph visualization)</em>
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Network;
