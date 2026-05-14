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
            Wikipedia pageviews serve as a measure of global attention. 
            We tracked how conflict events affected artist visibility worldwide.
          </p>

          <div className="pageview-chart">
            <img 
              src={`${import.meta.env.BASE_URL}pageviews_by_conflict.png`}
              alt="Wikipedia Pageviews by Conflict Region" 
              className="chart-image"
            />
          </div>
          
          <div className="insights-boxes">
            <div className="insight-box wide">
              <h4>⚠️ Note on Syria & Palestine</h4>
              <p>
                The Wikipedia Pageviews API only provides data from July 2015 onwards. 
                Since the Syrian Civil War began in March 2011, we cannot capture pre-conflict pageview data for Syrian artists. 
                The Syria chart shows pageview trends during the ongoing conflict period (2015-2020), but lacks a true 
                "before vs after" comparison. Similarly, Palestine shows "No data" due to insufficient pageview records 
                for the limited number of Palestinian artists in our dataset - many Palestinian musicians have minimal or no English Wiki articles.
              </p>
            </div>
            <div className="insight-box">
              <h4>🇮🇱 Israel: Clearest Pattern</h4>
              <p>
                Visible spike immediately after Oct 7, 2023 (~65,000 views vs ~10,000 baseline). 
                Higher interest throughout 2024-2025 suggests global audiences actively 
                sought cultural context about Israel during the conflict. 
              </p>
            </div>
            <div className="insight-box">
              <h4>🇷🇺 Russia: Moderate Spike, Then Decline</h4>
              <p>
                Peak around ~35,000 views right after Feb 24, 2022, followed by gradual decline 
                to below pre-conflict levels (~10,000-15,000). May reflect international attention 
                followed by cultural sanctions reducing visibility.
              </p>
            </div>
            <div className="insight-box">
              <h4>🇺🇦 Ukraine: High Baseline, No Dramatic Spike</h4>
              <p>
                Consistently high pageviews (~250,000-400,000/month) throughout with no sudden surge 
                after the invasion. Suggests Ukrainian artists were already well-known internationally.
              </p>
            </div>
            <div className="insight-box">
              <h4>📊 Overall Conclusion</h4>
              <p>
                Conflict events can significantly boost global attention to artists from affected regions, 
                particularly visible in the Israel case. However, the effect varies by country, pre-existing 
                international recognition, geopolitical context, and media coverage all influence the pattern.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Trends;
