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
    <div className="app-container">
      <h2>Coin Page 🪙</h2>
      <p>Selected coin ID: {id}</p>
    </div>
  );
}

export default Coin;