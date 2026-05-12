import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          🎵 Conflict & Music
        </Link>
        
        <ul className="nav-menu">
          <li className="nav-item">
            <Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>
              Home
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/dataset" className={`nav-link ${isActive('/dataset') ? 'active' : ''}`}>
              Dataset
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/network" className={`nav-link ${isActive('/network') ? 'active' : ''}`}>
              Network Analysis
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/text-analysis" className={`nav-link ${isActive('/text-analysis') ? 'active' : ''}`}>
              Text Analysis
            </Link>
          </li>
          <li className="nav-item">
            <Link to="/downloads" className={`nav-link ${isActive('/downloads') ? 'active' : ''}`}>
              Downloads
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;
