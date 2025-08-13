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
              borderColor: "rgba(75,192,192,1)",
              tension: 0.1,
            },
          ],
        }}
        options={{
          responsive: true,
          plugins: {
            legend: { labels: { color: "white" } },
          },
          scales: {
            x: { ticks: { color: "white" } },
            y: { ticks: { color: "white" } },
          },
        }}
      />
    </div>
  );
}

export default LineChart;