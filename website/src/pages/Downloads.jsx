import './Downloads.css';

function Downloads() {
  const datasets = [
    {
      name: 'artists_data.csv',
      description: 'Complete database of 1,637 artists from conflict regions including name, origin, birth place, and current residence.',
      size: '148 KB',
      rows: '1,637',
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
      name: 'lyrics_with_sentiment_translated.csv',
      description: 'Song lyrics with VADER sentiment analysis scores after Google Translate preprocessing. Covers 739 songs across 5 countries (compound, positive, negative, neutral scores).',
      size: '~350 KB',
      rows: '739',
      format: 'CSV'
    },
    {
      name: 'raw_lyrics.json',
      description: 'Raw lyrics data in JSON format from the Genius API.',
      size: '292 KB',
      rows: '739',
      format: 'JSON'
    },
    {
      name: 'top_positive_songs.csv',
      description: 'Top 20 songs with the highest positive sentiment scores after translation.',
      size: '~5 KB',
      rows: '20',
      format: 'CSV'
    },
    {
      name: 'top_negative_songs.csv',
      description: 'Top 20 songs with the lowest (most negative) sentiment scores after translation.',
      size: '~5 KB',
      rows: '20',
      format: 'CSV'
    },
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
              <h3>explainer_notebook.ipynb</h3>
              <p>
                This notebook contains the complete analysis pipeline including:
              </p>
              <ul>
                <li>Motivation: Why we chose this dataset and our research goals</li>
                <li>Basic Stats: Data cleaning, preprocessing, and dataset statistics</li>
                <li>Tools & Analysis: Text processing, VADER sentiment, geographic analysis</li>
                <li>Discussion: What worked well and areas for improvement</li>
              </ul>
            </div>
            <div className="notebook-links">
              <a 
                href="https://nbviewer.org/github/Beatricia/CSS-Project-A/blob/main/notebooks/explainer_notebook.ipynb"
                className="notebook-btn primary"
                target="_blank"
                rel="noopener noreferrer"
              >
                📖 View on nbviewer
              </a>
              <a 
                href="https://github.com/Beatricia/CSS-Project-A/blob/main/notebooks/explainer_notebook.ipynb"
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
    </div>
  );
}

export default Downloads;
