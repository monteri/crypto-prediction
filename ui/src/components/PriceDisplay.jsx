import React from "react";

const PriceDisplay = ({ id, currentValue, changePercent }) => {
  const getChangeColor = () =>
    changePercent > 0 ? "limegreen" : changePercent < 0 ? "red" : "gold";

  return (
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
        <strong>Current Value:</strong> ${currentValue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </div>
      <div>
        <strong>Change:</strong>{" "}
        <span style={{ color: getChangeColor() }}>
          {changePercent > 0 ? "+" : ""}
          {changePercent}%
        </span>
      </div>
    </div>
  );
};

export default PriceDisplay;
