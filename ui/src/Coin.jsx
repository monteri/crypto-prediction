import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import LineChart from "./components/LineChart";
import bitcoinLogo from "./assets/logo-BTC.png";
import ethereumLogo from "./assets/logo-ETH.svg";

function Coin() {
  const { id } = useParams();

  const [isCardOpen, setIsCardOpen] = useState(false);

  const generatePrice = (min, max) => {
    return +(Math.random() * (max - min) + min).toFixed(2);
  };

  const getPriceRange = (id) => {
    switch (id.toLowerCase()) {
      case "bitcoin":
        return [115000, 118000];
      case "ethereum":
        return [3700, 4100];
      default:
        return [1000, 2000];
    }
  };

  const getCoinInfo = (coinId) => {
    const info = {
      bitcoin: {
        marketCap: "$1.2T",
        volume24h: "$30B",
        totalSupply: "19.5M",
      },
      ethereum: {
        marketCap: "$450B",
        volume24h: "$15B",
        totalSupply: "120M",
      },
      default: {
        marketCap: "N/A",
        volume24h: "N/A",
        totalSupply: "N/A",
      },
    };
    return info[coinId.toLowerCase()] || info.default;
  };

  // 🆕 Новая функция для выбора логотипа
  const getCoinLogo = (coinId) => {
    switch (coinId.toLowerCase()) {
      case "bitcoin":
        return bitcoinLogo;
      case "ethereum":
        return ethereumLogo;
      default:
        return null; // Возвращаем null, если логотипа нет
    }
  };

  const [min, max] = getPriceRange(id);
  const [currentValue, setCurrentValue] = useState(generatePrice(min, max));
  const [dayData, setDayData] = useState([]);
  const [monthData, setMonthData] = useState([]);

  useEffect(() => {
    const [min, max] = getPriceRange(id);
    setCurrentValue(generatePrice(min, max));
    setDayData(Array.from({ length: 24 }, () => generatePrice(min, max)));
    setMonthData(Array.from({ length: 30 }, () => generatePrice(min, max)));
  }, [id]);

  const changePercent = +(Math.random() * 10 - 5).toFixed(2);
  const getChangeColor = () => {
    if (changePercent > 0) return "limegreen";
    if (changePercent < 0) return "red";
    return "gold";
  };

  const coinInfo = getCoinInfo(id);
  const coinLogo = getCoinLogo(id);

  const dayLabels = Array.from({ length: 24 }, (_, i) => `${i}:00`);
  const monthLabels = Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`);

  return (
    <div style={{ backgroundColor: "#222", minHeight: "100vh", width: "900px", padding: "40px 0", color: "white" }}>
      <div style={{ maxWidth: "900px", margin: "0 auto", padding: "0 20px" }}>
        {/* 🆕 Обновленный заголовок с условным рендерингом логотипа */}
        <h2 style={{ marginBottom: "30px", display: "flex", alignItems: "center", gap: "10px", justifyContent: "center"}}>
          {id.toUpperCase()}
          {coinLogo && (
            <img src={coinLogo} alt={`${id} logo`} style={{ width: "32px", height: "32px" }} />
          )}
        </h2>

        <button
          onClick={() => setIsCardOpen(!isCardOpen)}
          style={{
            marginBottom: "20px",
            padding: "10px 20px",
            backgroundColor: "#444",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer",
          }}
        >
          {isCardOpen ? "Hide the information" : "About crypto-coin"}
        </button>

        {isCardOpen && (
          <div style={{
            backgroundColor: "#333",
            padding: "20px",
            borderRadius: "8px",
            marginBottom: "40px"
          }}>
            <p><strong>Market capitalization:</strong> {coinInfo.marketCap}</p>
            <p><strong>Volume in 24 hours:</strong> {coinInfo.volume24h}</p>
            <p><strong>General offer:</strong> {coinInfo.totalSupply}</p>
          </div>
        )}

        <div style={{ display: "flex", gap: "40px", marginBottom: "40px", alignItems: "center" }}>
          <div>
            <strong>Name:</strong> {id.toUpperCase()}
          </div>
          <div>
            <strong>Current Value:</strong> ${currentValue.toLocaleString()}
          </div>
          <div>
            <strong>Change:</strong>{" "}
            <span style={{ color: getChangeColor() }}>
              {changePercent > 0 ? "+" : ""}
              {changePercent}%
            </span>
          </div>
        </div>

        <div style={{ marginBottom: "50px" }}>
          <h3 style={{ marginBottom: "15px" }}>📅 Monthly Chart (30 Days)</h3>
          <LineChart
            labels={monthLabels}
            data={monthData}
            title={`${id} - Monthly Price`}
          />
        </div>

        <div>
          <h3 style={{ marginBottom: "15px" }}>🕐 Daily Chart (24 Hours)</h3>
          <LineChart
            labels={dayLabels}
            data={dayData}
            title={`${id} - Daily Price`}
          />
        </div>
      </div>
    </div>
  );
}

export default Coin;