import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1>Conflict & Music Culture</h1>
          <p className="hero-subtitle">How War Shapes the Music We Listen To</p>
          <p className="hero-description">
            An exploration of how armed conflicts affect music culture in affected regions, 
            examining artist migration, popularity shifts, and lyrical themes.
          </p>
          <div className="hero-buttons">
            <Link to="/dataset" className="btn btn-primary">Explore the Data</Link>
            <Link to="/text-analysis" className="btn btn-secondary">View Analysis</Link>
          </div>
        </div>
      </section>

      {/* Research Question */}
      <section className="section research-question">
        <div className="container">
          <h2>Our Research Question</h2>
          <div className="question-card">
            <p className="big-question">
              How does armed conflict affect music culture in affected regions?
            </p>
          </div>
          <div className="dimensions-grid">
            <div className="dimension-card">
              <span className="dimension-icon">🌍</span>
              <h3>Artist Migration</h3>
              <p>Where do artists flee during conflict?</p>
            </div>
            <div className="dimension-card">
              <span className="dimension-icon">📈</span>
              <h3>Popularity Shifts</h3>
              <p>Do artists gain or lose listeners during war?</p>
            </div>
            <div className="dimension-card">
              <span className="dimension-icon">🎤</span>
              <h3>Lyrical Themes</h3>
              <p>How does conflict appear in song lyrics?</p>
            </div>
          </div>
        </div>
      </section>

      {/* Conflict Regions */}
      <section className="section regions">
        <div className="container">
          <h2>Conflict Regions Studied</h2>
          <div className="regions-grid">
            <div className="region-card ukraine">
              <h3>🇺🇦 Ukraine</h3>
              <p>Russian Invasion</p>
              <span className="date">Feb 2022 - Ongoing</span>
            </div>
            <div className="region-card russia">
              <h3>🇷🇺 Russia</h3>
              <p>Aggressor Side</p>
              <span className="date">Feb 2022 - Ongoing</span>
            </div>
            <div className="region-card syria">
              <h3>🇸🇾 Syria</h3>
              <p>Civil War</p>
              <span className="date">Mar 2011 - Ongoing</span>
            </div>
            <div className="region-card israel">
              <h3>🇮🇱 Israel</h3>
              <p>Gaza War</p>
              <span className="date">Oct 2023 - Ongoing</span>
            </div>
            <div className="region-card palestine">
              <h3>🇵🇸 Palestine</h3>
              <p>Gaza War</p>
              <span className="date">Oct 2023 - Ongoing</span>
            </div>
          </div>
        </div>
      </section>

      {/* Key Insights Preview */}
      <section className="section insights">
        <div className="container">
          <h2>Key Insights</h2>
          <div className="insights-grid">
            <div className="insight-card">
              <h3>Global Attention</h3>
              <p>
                Wikipedia pageviews serve as a proxy for global attention. 
                We found significant spikes in artist visibility following conflict events.
              </p>
            </div>
            <div className="insight-card">
              <h3>Sentiment in Lyrics</h3>
              <p>
                VADER sentiment analysis reveals how artists process trauma, 
                resistance, and hope through their music.
              </p>
            </div>
            <div className="insight-card">
              <h3>Cultural Identity</h3>
              <p>
                Music reflects cultural identity and political sentiment. 
                Artists become voices of resistance and shared experience.
              </p>
            </div>
          </div>
          <div className="cta-center">
            <Link to="/text-analysis" className="btn btn-primary">
              Dive into the Analysis →
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
