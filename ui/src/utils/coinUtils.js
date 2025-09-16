import bitcoinLogo from "../assets/logo-BTC.png";
import ethereumLogo from "../assets/logo-ETH.svg";

export const getPriceRange = (id) => {
  switch (id.toLowerCase()) {
    case "bitcoin":
      return [115000, 118000];
    case "ethereum":
      return [3700, 4100];
    default:
      return [1000, 2000];
  }
};

export const getCoinInfo = (coinId) => {
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

export const getCoinLogo = (coinId) => {
  switch (coinId.toLowerCase()) {
    case "bitcoin":
      return bitcoinLogo;
    case "ethereum":
      return ethereumLogo;
    default:
      return null;
  }
};

export const generatePrice = (min, max) =>
  +(Math.random() * (max - min) + min).toFixed(2);
