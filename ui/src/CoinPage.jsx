import React, { useState } from "react";
import CandleChart from "../components/CandleChart";

const CoinPage = () => {
  const [selectedCoin, setSelectedCoin] = useState("Bitcoin");

  return (
    <div style={{ background: "#121212", minHeight: "100vh", padding: "20px" }}>
      {/* Выбор монеты */}
      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <button
          onClick={() => setSelectedCoin("Bitcoin")}
          style={{
            marginRight: "10px",
            padding: "8px 14px",
            background: selectedCoin === "Bitcoin" ? "#26a69a" : "#333",
            color: "#fff",
            border: "none",
            cursor: "pointer",
          }}
        >
          BTC
        </button>
        <button
          onClick={() => setSelectedCoin("Ethereum")}
          style={{
            padding: "8px 14px",
            background: selectedCoin === "Ethereum" ? "#26a69a" : "#333",
            color: "#fff",
            border: "none",
            cursor: "pointer",
          }}
        >
          ETH
        </button>
      </div>

      {/* График */}
      <CandleChart coinName={selectedCoin} />
    </div>
  );
};

export default CoinPage;