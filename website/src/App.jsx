import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Dataset from './pages/Dataset';
import Trends from './pages/Trends';
import Network from './pages/Network';
import TextAnalysis from './pages/TextAnalysis';
import Downloads from './pages/Downloads';
import './App.css';

function App() {
  return (
    <div className="app">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dataset" element={<Dataset />} />
          <Route path="/trends" element={<Trends />} />
          <Route path="/network" element={<Network />} />
          <Route path="/text-analysis" element={<TextAnalysis />} />
          <Route path="/downloads" element={<Downloads />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
