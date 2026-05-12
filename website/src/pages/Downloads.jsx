import './Downloads.css';

function Downloads() {
  const datasets = [
    {
      name: 'artists_data.csv',
      description: 'Complete database of 1,583 artists from conflict regions including name, origin, birth place, and current residence.',
      size: '148 KB',
      rows: '1,583',
      format: 'CSV'
    },
    {
      name: 'monthly_pageviews.csv',
      description: 'Monthly Wikipedia pageview data for artists, tracking global attention over time.',
      size: '~500 KB',
      rows: '10,350+',
      format: 'CSV'
    },
    {
      name: 'lyrics_with_sentiment.csv',
      description: 'Song lyrics with VADER sentiment analysis scores (compound, positive, negative, neutral).',
      size: '280 KB',
      rows: '130+',
      format: 'CSV'
    },
    {
      name: 'raw_lyrics.json',
      description: 'Raw lyrics data in JSON format from the Genius API.',
      size: '292 KB',
      rows: '-',
      format: 'JSON'
    },
    {
      name: 'top_positive_songs.csv',
      description: 'Subset of songs with the highest positive sentiment scores.',
      size: '-',
      rows: '-',
      format: 'CSV'
    },
    {
      name: 'top_negative_songs.csv',
      description: 'Subset of songs with the highest negative sentiment scores.',
      size: '-',
      rows: '-',
      format: 'CSV'
    }
  ];

  return (
    <div className="downloads-page">
      <section className="page-header">
        <h1>Downloads</h1>
        <p>Access our datasets and explore the data yourself</p>
      </section>

      <section className="section">
        <div className="container">
          <h2>Available Datasets</h2>
          <p className="section-intro">
            All datasets used in this analysis are available for download. 
            Feel free to explore, visualize, and build upon our work.
          </p>

          <div className="datasets-grid">
            {datasets.map((dataset, index) => (
              <div key={index} className="dataset-card">
                <div className="dataset-icon">
                  {dataset.format === 'CSV' ? '📊' : '📄'}
                </div>
                <div className="dataset-info">
                  <h3>{dataset.name}</h3>
                  <p>{dataset.description}</p>
                  <div className="dataset-meta">
                    <span className="meta-item">
                      <strong>Format:</strong> {dataset.format}
                    </span>
                    <span className="meta-item">
                      <strong>Size:</strong> {dataset.size}
                    </span>
                    <span className="meta-item">
                      <strong>Rows:</strong> {dataset.rows}
                    </span>
                  </div>
                </div>
                <a 
                  href={`${import.meta.env.BASE_URL}data/${dataset.name.includes('lyrics') || dataset.name.includes('top_') ? 'lyrics_data/' : ''}${dataset.name}`}
                  className="download-btn"
                  download
                >
                  ⬇️ Download
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Explainer Notebook</h2>
          <p className="section-intro">
            For a detailed walkthrough of our methodology, including data collection, 
            preprocessing, and analysis techniques, check out our Jupyter notebook.
          </p>

          <div className="notebook-card">
            <div className="notebook-icon">📓</div>
            <div className="notebook-info">
              <h3>conflict_music_analysis.ipynb</h3>
              <p>
                This notebook contains the complete analysis pipeline including:
              </p>
              <ul>
                <li>Data collection from Wikidata, Wikipedia, and Genius APIs</li>
                <li>Data cleaning and preprocessing</li>
                <li>VADER sentiment analysis implementation</li>
                <li>Visualization code for all charts</li>
                <li>Statistical analysis and findings</li>
              </ul>
            </div>
            <div className="notebook-links">
              <a 
                href="https://nbviewer.org/github/Beatricia/CSS-Project-A/blob/main/conflict_music_analysis.ipynb"
                className="notebook-btn primary"
                target="_blank"
                rel="noopener noreferrer"
              >
                📖 View on nbviewer
              </a>
              <a 
                href="https://github.com/Beatricia/CSS-Project-A/blob/main/conflict_music_analysis.ipynb"
                className="notebook-btn secondary"
                target="_blank"
                rel="noopener noreferrer"
              >
                💻 View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <h2>GitHub Repository</h2>
          <p className="section-intro">
            Access the complete project repository including all code, data, and documentation.
          </p>

          <div className="repo-card">
            <div className="repo-header">
              <span className="repo-icon">🐙</span>
              <div>
                <h3>Beatricia/CSS-Project-A</h3>
                <p>Conflict & Music Culture Analysis</p>
              </div>
            </div>
            <div className="repo-stats">
              <span className="stat">📂 Python, JavaScript</span>
              <span className="stat">📊 CSS Project</span>
            </div>
            <a 
              href="https://github.com/Beatricia/CSS-Project-A"
              className="repo-btn"
              target="_blank"
              rel="noopener noreferrer"
            >
              View Repository →
            </a>
          </div>
        </div>
      </section>

      <section className="section alt-bg">
        <div className="container">
          <h2>Data Usage & Citation</h2>
          <div className="usage-info">
            <div className="usage-card">
              <h3>📝 License</h3>
              <p>
                This project and its data are available for academic and research purposes. 
                Please cite appropriately if you use our data in your work.
              </p>
            </div>
            <div className="usage-card">
              <h3>📚 Citation</h3>
              <div className="citation-box">
                <code>
                  @misc{'{'}conflict_music_2024,{'\n'}
                  {'  '}title = {'{'}Conflict & Music Culture Analysis{'}'},\n
                  {'  '}author = {'{'}Your Name{'}'},\n
                  {'  '}year = {'{'}2024{'}'},\n
                  {'  '}url = {'{'}https://github.com/Beatricia/CSS-Project-A{'}'}\n
                  {'}'}
                </code>
              </div>
            </div>
            <div className="usage-card">
              <h3>🔗 Data Sources</h3>
              <ul>
                <li><a href="https://www.wikidata.org/" target="_blank" rel="noopener noreferrer">Wikidata</a></li>
                <li><a href="https://wikimedia.org/api/rest_v1/" target="_blank" rel="noopener noreferrer">Wikipedia Pageviews API</a></li>
                <li><a href="https://genius.com/developers" target="_blank" rel="noopener noreferrer">Genius API</a></li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Downloads;
