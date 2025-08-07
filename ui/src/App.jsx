import { Link } from "react-router-dom";
import { memo, useMemo } from "react";
import CryptoTable from "./components/CryptoTable.jsx";

import "./App.scss";

const App = memo(function App() {
  // Memoize the navigation links to prevent re-renders
  const navigationLinks = useMemo(() => [
    { to: "/", label: "Home" },
    { to: "/coin/bitcoin", label: "Bitcoin" },
    { to: "/coin/ethereum", label: "Ethereum" },
  ], []);

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
      <Balance />
      <CryptoTable />
    </div>
  );
});

export default App;