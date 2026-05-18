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
              <a href="https://nbviewer.org/github/Beatricia/CSS-Project-A/blob/main/notebooks/explainer_notebook.ipynb" target="_blank" rel="noopener noreferrer">
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
      </div>
    </footer>
  );
}

export default Footer;
