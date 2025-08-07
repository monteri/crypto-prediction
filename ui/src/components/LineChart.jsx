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
  const chartData = {
    labels,
    datasets: [
      {
        label: title,
        data,
        borderColor: "#4bc0c0",
        backgroundColor: "rgba(75,192,192,0.2)",
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: true },
    },
    scales: {
      y: {
        ticks: { color: "#fff" },
      },
      x: {
        ticks: { color: "#fff" },
      },
    },
  };

  return <Line data={chartData} options={options} />;
}

export default LineChart;