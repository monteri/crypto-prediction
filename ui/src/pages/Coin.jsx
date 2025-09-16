import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import LineChart from "../components/LineChart";
import ChartControls from "../components/ChartControls";
import CoinInfo from "../components/CoinInfo";
import PriceDisplay from "../components/PriceDisplay";
import { cryptoAnalyticsApi } from "../api";
import { useChartData } from "../hooks/useChartData";
import { getCoinInfo, getCoinLogo, getPriceRange, generatePrice } from "../utils/coinUtils";

function Coin() {
  const { id } = useParams();
  const [isCardOpen, setIsCardOpen] = useState(false);
  const [timeRange, setTimeRange] = useState("1d");
  const [symbolData, setSymbolData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);


  const [min, max] = getPriceRange(id);
  const [currentValue, setCurrentValue] = useState(generatePrice(min, max));
  const [changePercent, setChangePercent] = useState(0.0);

  // Use the custom hook for chart data
  const { chartData, chartLabels, loading: chartLoading, error: chartError } = useChartData(id, timeRange);

  // Fetch symbol data from API
  useEffect(() => {
    const fetchSymbolData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await cryptoAnalyticsApi.getSymbolSummary(id);
        setSymbolData(data);
        
        // Update current value and change percent from API data
        setCurrentValue(data.currentPrice);
        setChangePercent(data.dailyChangePercent);
      } catch (err) {
        console.error('Error fetching symbol data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSymbolData();
  }, [id]);


  const coinInfo = getCoinInfo(id);
  const coinLogo = getCoinLogo(id);

  if (loading) {
    return (
      <div
        style={{
          backgroundColor: "#222",
          minHeight: "100vh",
          width: "900px",
          padding: "40px 0",
          color: "white",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div>Loading {id.toUpperCase()} data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          backgroundColor: "#222",
          minHeight: "100vh",
          width: "900px",
          padding: "40px 0",
          color: "#b51633",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <div>Error loading {id.toUpperCase()}: {error}</div>
      </div>
    );
  }

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

        {/* Coin Information */}
        <CoinInfo
          id={id}
          isCardOpen={isCardOpen}
          setIsCardOpen={setIsCardOpen}
          coinInfo={coinInfo}
          symbolData={symbolData}
        />

        {/* Price Display */}
        <PriceDisplay
          id={id}
          currentValue={currentValue}
          changePercent={changePercent}
        />

        {/* Chart Controls */}
        <ChartControls
          timeRange={timeRange}
          setTimeRange={setTimeRange}
        />

        {/* Chart */}
        {chartLoading ? (
          <div style={{ textAlign: "center", padding: "40px", color: "#aaa" }}>
            Loading chart data...
          </div>
        ) : chartError ? (
          <div style={{ textAlign: "center", padding: "40px", color: "#b51633" }}>
            Error loading chart data: {chartError}
          </div>
        ) : (
          <LineChart
            labels={chartLabels}
            data={chartData}
            title={`${id} - ${timeRange.toUpperCase()} Price`}
          />
        )}
      </div>
    </div>
  );
}

export default Coin;

