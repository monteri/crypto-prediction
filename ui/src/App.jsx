import { Link } from "react-router-dom";
import { memo, useMemo, useState, useEffect } from "react";
import CryptoTable from "./components/CryptoTable.jsx";
import { cryptoAnalyticsApi } from "./api";

import "./App.scss";

const App = memo(function App() {
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [usdUah, setUsdUah] = useState(null);
  const [fxError, setFxError] = useState(null);

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

  // Fetch USD -> UAH from open.exchangerate-api.com
  useEffect(() => {
    let cancelled = false;

    const fetchUsdUah = async () => {
      try {
        setFxError(null);
        const res = await fetch('https://open.exchangerate-api.com/v6/latest');
        if (!res.ok) throw new Error(`FX HTTP ${res.status}`);
        const json = await res.json();
        const rate = json?.rates?.UAH;
        if (typeof rate === 'number' && !cancelled) {
          setUsdUah(rate);
        }
      } catch (e) {
        if (!cancelled) setFxError(e.message || 'FX fetch failed');
      }
    };

    fetchUsdUah();
  }, []);

  // Removed BTC/ETH fetch; using $ → USDT static badge

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
      <div className="app-header">
        <div></div>
        <h2 className="app-title">Crypto Prediction</h2>
        <div className="header-right" style={{ justifySelf: 'end', alignSelf: 'start' }}>
          <span className="fx-badge">
            <span className="fx-badge__label">USD → UAH</span>
            <strong>{usdUah ? usdUah.toFixed(2) : fxError ? '—' : '...'}</strong>
          </span>
          <span className="coin-badge coin-badge--usdt">
            <span className="coin-badge__label">USD → USDT</span>
            <strong>1.00</strong>
          </span>
        </div>
      </div>
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