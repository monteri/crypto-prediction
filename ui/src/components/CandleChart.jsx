import React, { useEffect, useRef, useState } from "react";
import { createChart } from "lightweight-charts";

const CandleChart = ({ coinName = "Bitcoin" }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const seriesRef = useRef();
  const [range, setRange] = useState("24h"); // 24h или 30d

  // Тестовые данные
  const getTestData = (type) => {
    const data = [];
    let basePrice = type === "24h" ? 116500 : 116000;
    let count = type === "24h" ? 24 : 30;

    for (let i = 0; i < count; i++) {
      const open = basePrice + Math.random() * 200 - 100;
      const close = open + Math.random() * 200 - 100;
      const high = Math.max(open, close) + Math.random() * 100;
      const low = Math.min(open, close) - Math.random() * 100;
      data.push({
        time: i + 1,
        open: parseFloat(open.toFixed(2)),
        high: parseFloat(high.toFixed(2)),
        low: parseFloat(low.toFixed(2)),
        close: parseFloat(close.toFixed(2)),
      });
    }
    return data;
  };

  useEffect(() => {
    // создаём график
    chartRef.current = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: "#1e1e1e" },
        textColor: "#d1d4dc",
      },
      grid: {
        vertLines: { color: "#2b2b43" },
        horzLines: { color: "#2b2b43" },
      },
    });

    // создаём серию свечей
    seriesRef.current = chartRef.current.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderDownColor: "#ef5350",
      borderUpColor: "#26a69a",
      wickDownColor: "#ef5350",
      wickUpColor: "#26a69a",
    });

    // первичная загрузка данных
    seriesRef.current.setData(getTestData(range));

    // ресайз
    const handleResize = () => {
      chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chartRef.current.remove();
    };
  }, []);

  // обновление данных при смене диапазона
  useEffect(() => {
    if (seriesRef.current) {
      seriesRef.current.setData(getTestData(range));
    }
  }, [range]);

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto" }}>
      <h2 style={{ color: "#fff", textAlign: "center", marginBottom: "10px" }}>
        {coinName} — Candlestick Chart
      </h2>
      <div style={{ textAlign: "center", marginBottom: "10px" }}>
        <button
          onClick={() => setRange("24h")}
          style={{
            marginRight: "10px",
            padding: "5px 10px",
            background: range === "24h" ? "#26a69a" : "#333",
            color: "#fff",
            border: "none",
            cursor: "pointer",
          }}
        >
          24h
        </button>
        <button
          onClick={() => setRange("30d")}
          style={{
            padding: "5px 10px",
            background: range === "30d" ? "#26a69a" : "#333",
            color: "#fff",
            border: "none",
            cursor: "pointer",
          }}
        >
          30d
        </button>
      </div>
      <div ref={chartContainerRef} />
    </div>
  );
};

export default CandleChart;


