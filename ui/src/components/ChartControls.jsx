import React from "react";

const ChartControls = ({ 
  timeRange, 
  setTimeRange,
}) => {
  return (
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
        {["1y", "1m", "1d"].map((range) => (
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
    </div>
  );
};

export default ChartControls;
