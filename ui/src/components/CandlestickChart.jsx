import { Chart as ChartJS } from "chart.js";
import { CandlestickController, CandlestickElement } from "chartjs-chart-financial";
import { Chart } from "react-chartjs-2";

// Регистрируем необходимые элементы
ChartJS.register(CandlestickController, CandlestickElement);

function CandlestickChart({ labels, data, title }) {
  const chartData = {
    labels,
    datasets: [
      {
        label: title,
        data,
        borderColor: "rgba(255, 255, 255, 0.5)",
        backgroundColor: "rgba(255, 255, 255, 0.2)",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
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

  return <Chart type="candlestick" data={chartData} options={options} />;
}

export default CandlestickChart;