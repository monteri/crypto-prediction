import { Link } from "react-router-dom";
import "./App.css";
import Balance from './Balance.jsx';

function App() {
  return (
    <div style={{ backgroundColor: "#222", height: "100vh", padding: "20px" }}>
      <Balance />
      <h2 style={{ color: "white" }}>Crypto Prediction</h2>
        <nav>
        <Link to="/" className="nav-link">Home</Link>{" | "}
        <Link to="/about" className="nav-link">About</Link>{" | "}
        <Link to="/coin/bitcoin" className="nav-link">Bitcoin</Link>{" | "}
        <Link to="/coin/ethereum" className="nav-link">Ethereum</Link>
      </nav>
    </div>
  );
}


export default App;