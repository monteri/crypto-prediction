import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { ActionableNotification } from "@carbon/react";
import LineChart from "./components/LineChart";

import bitcoinLogo from "./assets/logo-BTC.png";
import ethereumLogo from "./assets/logo-ETH.svg";

function Coin() {
  const { id } = useParams();
  const [isCardOpen, setIsCardOpen] = useState(false);
  const [timeRange, setTimeRange] = useState("1d");
  const [showAlert, setShowAlert] = useState(false);

  const generatePrice = (min, max) =>
    +(Math.random() * (max - min) + min).toFixed(2);

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
      default: { marketCap: "N/A", volume24h: "N/A", totalSupply: "N/A" },
    };
    return info[coinId.toLowerCase()] || info.default;
  };

  const getCoinLogo = (coinId) => {
    switch (coinId.toLowerCase()) {
      case "bitcoin":
        return bitcoinLogo;
      case "ethereum":
        return ethereumLogo;
      default:
        return null;
    }
  };

  const [min, max] = getPriceRange(id);
  const [currentValue, setCurrentValue] = useState(generatePrice(min, max));
  const [chartData, setChartData] = useState([]);
  const [chartLabels, setChartLabels] = useState([]);
  const [changePercent, setChangePercent] = useState(
    +(Math.random() * 10 - 5).toFixed(2)
  );

  const generateChartData = (range) => {
    const [min, max] = getPriceRange(id);

    if (range === "15m") {
      return {
        labels: Array.from({ length: 15 }, (_, i) => `${i + 1}m`),
        data: Array.from({ length: 15 }, () => generatePrice(min, max)),
      };
    }
    if (range === "1d") {
      return {
        labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
        data: Array.from({ length: 24 }, () => generatePrice(min, max)),
      };
    }
    if (range === "1w") {
      return {
        labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        data: Array.from({ length: 7 }, () => generatePrice(min, max)),
      };
    }
    if (range === "1m") {
      return {
        labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`),
        data: Array.from({ length: 30 }, () => generatePrice(min, max)),
      };
    }
    return { labels: [], data: [] };
  };

  const getChangeColor = () =>
    changePercent > 0 ? "limegreen" : changePercent < 0 ? "red" : "gold";

  useEffect(() => {
    const [min, max] = getPriceRange(id);
    setCurrentValue(generatePrice(min, max));
    setChangePercent(+(Math.random() * 10 - 5).toFixed(2));

    const { labels, data } = generateChartData(timeRange);
    setChartLabels(labels);
    setChartData(data);
  }, [id, timeRange]);

  useEffect(() => {
    if (Math.abs(changePercent) >= 4) {
      setShowAlert(true);
      const timer = setTimeout(() => setShowAlert(false), 30000);
      return () => clearTimeout(timer);
    }
  }, [changePercent]);

  const coinInfo = getCoinInfo(id);
  const coinLogo = getCoinLogo(id);

  return (
    <div
      style={{
        backgroundColor: "#222",
        minHeight: "100vh",
        width: "900px",
        padding: "40px 0",
        color: "white",
      }}
    >
      <div
        style={{
          maxWidth: "900px",
          margin: "0 auto",
          padding: "0 20px",
        }}
      >
        {/* Заголовок */}
        <h2
          style={{
            marginBottom: "30px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "10px",
          }}
        >
          {id.toUpperCase()}
          {coinLogo && (
            <img
              src={coinLogo}
              alt={`${id} logo`}
              style={{ width: "32px", height: "32px" }}
            />
          )}
        </h2>

        {/* Кнопка "О монете" */}
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

        {/* Инфо карточка */}
        {isCardOpen && (
          <div
            style={{
              backgroundColor: "#333",
              padding: "20px",
              borderRadius: "8px",
              marginBottom: "40px",
            }}
          >
            <p>
              <strong>Market capitalization:</strong> {coinInfo.marketCap}
            </p>
            <p>
              <strong>Volume in 24 hours:</strong> {coinInfo.volume24h}
            </p>
            <p>
              <strong>General offer:</strong> {coinInfo.totalSupply}
            </p>
          </div>
        )}

        {/* Блок с Name / Current Value / Change */}
        <div
          style={{
            display: "flex",
            gap: "40px",
            marginBottom: "20px",
            alignItems: "center",
          }}
        >
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

        {/* Переключатели + уведомление */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: "20px",
          }}
        >
          <div
            style={{
              backgroundColor: "#111",
              padding: "8px",
              borderRadius: "6px",
              display: "inline-block",
            }}
          >
            {["15m", "1d", "1w", "1m"].map((range) => (
              <button
                key={range}
                onClick={() => setTimeRange(range)}
                style={{
                  padding: "8px 16px",
                  margin: "0 2px",
                  backgroundColor:
                    timeRange === range ? "#f0b90b" : "#111",
                  color: timeRange === range ? "#000" : "#aaa",
                  fontWeight: "bold",
                  border: "1px solid #333",
                  borderRadius: "4px",
                  cursor: "pointer",
                  transition: "all 0.2s ease",
                }}
                onMouseEnter={(e) => {
                  if (timeRange !== range) e.target.style.color = "#f0b90b";
                }}
                onMouseLeave={(e) => {
                  if (timeRange !== range) e.target.style.color = "#aaa";
                }}
              >
                {range.toUpperCase()}
              </button>
            ))}
          </div>

          {/* Уведомление */}
          {showAlert && (
            <div style={{ width: "300px" }}>
              <ActionableNotification
                kind={changePercent > 0 ? "success" : "error"}
                title="Price Alert"
                subtitle={`${changePercent}% change`}
                actionButtonLabel="OK"
                onClose={() => setShowAlert(false)}
                inline
              />
            </div>
          )}
        </div>

        {/* График */}
        <LineChart
          labels={chartLabels}
          data={chartData}
          title={`${id} - ${timeRange.toUpperCase()} Price`}
        />
      </div>
    </div>
  );
}

export default Coin;

