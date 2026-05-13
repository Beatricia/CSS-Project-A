import { useState } from 'react';
import './Trends.css';

function Trends() {
  const [selectedCountry, setSelectedCountry] = useState('world');
  const [mapType, setMapType] = useState('migration');

  const countries = [
    { id: 'world', name: 'Global View', flag: '🌍' },
    { id: 'ukraine', name: 'Ukraine', flag: '🇺🇦' },
    { id: 'russia', name: 'Russia', flag: '🇷🇺' },
    { id: 'israel', name: 'Israel', flag: '🇮🇱' },
    { id: 'syria', name: 'Syria', flag: '🇸🇾' },
    { id: 'palestine', name: 'Palestine', flag: '🇵🇸' },
  ];

  const getMapSrc = () => {
    if (selectedCountry === 'world') {
      if (mapType === 'migration') return 'maps/migration_comparison.html';
      if (mapType === 'birth') return 'maps/world_map_birth_place.html';
      return 'maps/world_map_current_residence.html';
    }
    if (mapType === 'migration') return `maps/${selectedCountry}_migration.html`;
    if (mapType === 'birth') return `maps/${selectedCountry}_birth_place.html`;
    return `maps/${selectedCountry}_current_residence.html`;
  };

  return (
    <div className="trends-page">
      <section className="page-header">
        <h1>Trends</h1>
        <p>Tracking artist migration and global attention patterns</p>
      </section>

      <section className="section">
        <div className="container">
          <h2>Artist Migration Map</h2>
          <p className="section-intro">
            This interactive map shows where artists from conflict regions have relocated.
            The connections reveal patterns of cultural exchange and displacement.
          </p>
          
          <div className="map-controls">
            <div className="country-selector">
              {countries.map(country => (
                <button
                  key={country.id}
                  className={`country-btn ${selectedCountry === country.id ? 'active' : ''}`}
                  onClick={() => setSelectedCountry(country.id)}
                >
                  {country.flag} {country.name}
                </button>
              ))}
            </div>
            
            <div className="map-type-selector">
              <button 
                className={`type-btn ${mapType === 'migration' ? 'active' : ''}`}
                onClick={() => setMapType('migration')}
              >
                Migration Flow
              </button>
              <button 
                className={`type-btn ${mapType === 'birth' ? 'active' : ''}`}
                onClick={() => setMapType('birth')}
              >
                Birth Place
              </button>
              <button 
                className={`type-btn ${mapType === 'residence' ? 'active' : ''}`}
                onClick={() => setMapType('residence')}
              >
                Current Residence
              </button>
            </div>
          </div>

          <div className="map-container">
            <iframe 
              src={getMapSrc()}
              title="Artist Migration Map"
              className="map-iframe"
            />
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Migration Patterns</h2>
          <div className="patterns-grid">
            <div className="pattern-card global-card">
              <h3>🌍 Global Overview</h3>
              <p>
                Artists from conflict regions tend to migrate towards Western Europe and North America, 
                with secondary flows to neighboring countries. The data reveals how cultural displacement 
                follows geopolitical events, creating new artistic diasporas worldwide.
              </p>
            </div>

            <div className="pattern-card">
              <h3>🇺🇦 Ukrainian Artists</h3>
              <p>
                Following the 2022 invasion, many Ukrainian artists relocated to 
                Western Europe and the United States - being more present in Poland, Germany, and the UK.
              </p>
            </div>

            <div className="pattern-card">
              <h3>🇸🇾 Syrian Artists</h3>
              <p>
                Due to limited data on Syrian artists, there is not enough information to draw major conclusions. 
                With the data available, it can be seen that many seek refuge in neighbouring countries 
                and Europe. 
              </p>
            </div>

            <div className="pattern-card">
              <h3>🇷🇺 Russian Artists</h3>
              <p>
                Some Russian artists left following the 2022 invasion, 
                often relocating to countries with existing Russian communities.
              </p>
            </div>

            <div className="pattern-card">
              <h3>🇮🇱 Israeli Artists</h3>
              <p>
                It can be seen clearly that artists from Israel relocate to North America, with most of them moving to Europe.
              </p>
            </div>

            <div className="pattern-card">
              <h3>🇵🇸 Palestinian Artists</h3>
              <p>
                Due to limited data, conclusions on artists from Palestine could not be drawn.
              </p>
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
    </div>
  );
}

export default Trends;
