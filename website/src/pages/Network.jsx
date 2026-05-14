import './Network.css';

function Network() {
  return (
    <div className="network-page">
      <section className="page-header">
        <h1>Network Analysis</h1>
        <p>Analyzing artistic collaborations and connections</p>
      </section>

      <section className="section">
        <div className="container">
          <h2>Artist Collaboration Network</h2>
          <p className="section-intro">
            We analyze collaboration patterns among artists from conflict regions to understand 
            how musical connections form across borders and how conflict affects these networks.
          </p>

          <div className="coming-soon-banner">
            <span className="banner-icon">🚧</span>
            <div className="banner-content">
              <h3>Coming Soon</h3>
              <p>We are currently collecting collaboration data to build the artist network.</p>
            </div>
          </div>

          <div className="network-preview">
            <h3>What We're Building</h3>
            <div className="preview-grid">
              <div className="preview-card">
                <span className="preview-icon">🎤</span>
                <h4>Collaboration Network</h4>
                <p>Interactive graph showing which artists have worked together on songs, albums, or live performances.</p>
              </div>
              <div className="preview-card">
                <span className="preview-icon">📊</span>
                <h4>Centrality Analysis</h4>
                <p>Identifying the most influential and well-connected artists using network metrics like degree and betweenness centrality.</p>
              </div>
              <div className="preview-card">
                <span className="preview-icon">🔗</span>
                <h4>Cross-Border Connections</h4>
                <p>Examining how artists from different conflict regions collaborate and form musical bridges.</p>
              </div>
              <div className="preview-card">
                <span className="preview-icon">👥</span>
                <h4>Community Detection</h4>
                <p>Discovering clusters of artists who frequently collaborate, revealing genre and regional groupings.</p>
              </div>
            </div>
          </div>

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
                Interactive network visualization will appear here once data collection is complete.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Network;
