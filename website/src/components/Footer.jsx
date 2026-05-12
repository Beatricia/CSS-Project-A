import './Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-section">
          <h3>Conflict & Music Culture Analysis</h3>
          <p>A Computational Social Science project exploring how armed conflict affects music culture.</p>
        </div>
        
        <div className="footer-section">
          <h4>Resources</h4>
          <ul>
            <li>
              <a href="https://nbviewer.org/" target="_blank" rel="noopener noreferrer">
                📓 Explainer Notebook
              </a>
            </li>
            <li>
              <a href="https://github.com/Beatricia/CSS-Project-A" target="_blank" rel="noopener noreferrer">
                💻 GitHub Repository
              </a>
            </li>
          </ul>
        </div>
        
        <div className="footer-section">
          <h4>Data Sources</h4>
          <ul>
            <li>Wikidata SPARQL API</li>
            <li>Wikipedia Pageviews API</li>
            <li>Genius Lyrics API</li>
          </ul>
        </div>
      </div>
      
      <div className="footer-bottom">
        <p>© 2024 Computational Social Science - DTU</p>
      </div>
    </footer>
  );
}

export default Footer;
