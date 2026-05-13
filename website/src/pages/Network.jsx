import './Network.css';

function Network() {
  return (
    <div className="network-page">
      <section className="page-header">
        <h1>Network Analysis</h1>
        <p>Analyzing artistic collaborations and genre connections</p>
      </section>

      <section className="section">
        <div className="container">
          <h2>Network Connections</h2>
          <p className="section-intro">
            We analyze artistic collaborations and genre connections 
            among artists from conflict regions.
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
