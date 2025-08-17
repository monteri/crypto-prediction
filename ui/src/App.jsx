import { Link } from "react-router-dom";
import { memo, useMemo, useState, useEffect } from "react";
import CryptoTable from "./components/CryptoTable.jsx";
import { cryptoAnalyticsApi } from "./api";

import "./App.scss";

const App = memo(function App() {
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        setLoading(true);
        const data = await cryptoAnalyticsApi.getAllSymbolsSummary();
        setSymbols(data.symbols || []);
      } catch (err) {
        console.error('Error fetching symbols:', err);
        // Fallback to default symbols if API fails
        setSymbols([]);
      } finally {
        setLoading(false);
      }
    };

    fetchSymbols();
  }, []);

  const navigationLinks = useMemo(() => {
    const links = [{ to: "/", label: "Home" }];
    
    // Add up to 5 most popular symbols to navigation
    const popularSymbols = symbols.slice(0, 5);
    popularSymbols.forEach((symbol) => {
      const symbolName = symbol.symbol.replace('USDT', '').toLowerCase();
      const displayName = symbol.symbol.replace('USDT', '');
      links.push({ to: `/coin/${symbolName}`, label: displayName });
    });

    return links;
  }, [symbols]);

  return (
    <div className="app-container">
      <h2 style={{ color: "white" }}>Crypto Prediction</h2>
      <nav>
        {navigationLinks.map((link, index) => (
          <span key={link.to}>
            <Link to={link.to} className="nav-link">{link.label}</Link>
            {index < navigationLinks.length - 1 && " | "}
          </span>
        ))}
      </nav>
      <CryptoTable />
    </div>
  );
});

export default App;