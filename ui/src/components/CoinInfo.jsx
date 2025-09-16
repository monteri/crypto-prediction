import React from "react";

const CoinInfo = ({ 
  id, 
  isCardOpen, 
  setIsCardOpen, 
  coinInfo, 
  symbolData 
}) => {
  return (
    <>
      {/* About Coin Button */}
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

      {/* Info Card */}
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
          {symbolData && (
            <>
              <p>
                <strong>Daily Average:</strong> ${symbolData.dailyAvg.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p>
                <strong>Daily Min:</strong> ${symbolData.dailyMin.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p>
                <strong>Daily Max:</strong> ${symbolData.dailyMax.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p>
                <strong>Opening Price:</strong> ${symbolData.openingPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </p>
              <p>
                <strong>Number of Updates:</strong> {symbolData.numUpdates}
              </p>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default CoinInfo;
