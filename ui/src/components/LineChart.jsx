import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

function LineChart({ labels, data, title }) {
  // Determine if data is trending up or down for color
  const isPositive = data.length > 1 ? data[data.length - 1] > data[0] : true;
  const lineColor = isPositive ? "rgba(34, 197, 94, 1)" : "rgba(239, 68, 68, 1)"; // green or red
  
  return (
    <div style={{ backgroundColor: "#333", padding: "20px", borderRadius: "8px" }}>
      <Line
        data={{
          labels,
          datasets: [
            {
              label: title,
              data,
              fill: false,
              borderColor: lineColor,
              backgroundColor: lineColor + "20", // Add transparency
              tension: 0.1,
              pointBackgroundColor: lineColor,
              pointBorderColor: lineColor,
              pointRadius: 3,
              pointHoverRadius: 5,
            },
          ],
        }}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { 
              labels: { color: "white" },
              display: false // Hide legend since title is already shown
            },
            tooltip: {
              backgroundColor: "rgba(0, 0, 0, 0.8)",
              titleColor: "white",
              bodyColor: "white",
              borderColor: lineColor,
              borderWidth: 1,
              callbacks: {
                label: function(context) {
                  return `Price: $${context.parsed.y.toLocaleString(undefined, { 
                    minimumFractionDigits: 2, 
                    maximumFractionDigits: 2 
                  })}`;
                }
              }
            }
          },
          scales: {
            x: { 
              ticks: { color: "white" },
              grid: { color: "rgba(255, 255, 255, 0.1)" }
            },
            y: { 
              ticks: { 
                color: "white",
                callback: function(value) {
                  return '$' + value.toLocaleString(undefined, { 
                    minimumFractionDigits: 0, 
                    maximumFractionDigits: 0 
                  });
                }
              },
              grid: { color: "rgba(255, 255, 255, 0.1)" }
            },
          },
          interaction: {
            intersect: false,
            mode: 'index'
          }
        }}
      />
    </div>
  );
}

export default LineChart;