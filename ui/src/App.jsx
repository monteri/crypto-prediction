import { Link } from "react-router-dom";
import CryptoTable from "./components/CryptoTable.jsx";
import Balance from './Balance.jsx';

import "./App.scss";


function App() {
  return (
    <div className="app-container" style={{ backgroundColor: "#222", height: "100vh", padding: "20px" }}>
      <Balance />
      <h2 style={{ color: "white" }}>Crypto Prediction</h2>
        <nav>
        <Link to="/" className="nav-link">Home</Link>{" | "}
        <Link to="/about" className="nav-link">About</Link>{" | "}
        <Link to="/coin/bitcoin" className="nav-link">Bitcoin</Link>{" | "}
        <Link to="/coin/ethereum" className="nav-link">Ethereum</Link>
      </nav>
      <CryptoTable />
    </div>
  );
}


export default App;