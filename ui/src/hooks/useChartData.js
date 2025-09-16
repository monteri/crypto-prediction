import { useState, useEffect, useCallback } from 'react';
import { cryptoAnalyticsApi } from '../api';

export const useChartData = (symbol, timeRange) => {
  const [chartData, setChartData] = useState([]);
  const [chartLabels, setChartLabels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchChartData = useCallback(async () => {
    if (!symbol) return;

    setLoading(true);
    setError(null);

    try {
      let response;
      let labels = [];
      let data = [];

      switch (timeRange) {
        case '1y': {
          // For yearly, we'll use monthly data with last 12 months
          response = await cryptoAnalyticsApi.getMonthlyStats(symbol, 12);
          // Sort by timestamp to ensure oldest to newest order
          const sortedYearlyData = response.timeSeries.sort((a, b) => a.timestamp - b.timestamp);
          labels = sortedYearlyData.map(point => {
            const date = new Date(point.timestamp);
            return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
          });
          data = sortedYearlyData.map(point => point.price);
          break;
        }

        case '1m': {
          // For monthly, we'll use daily data with last 30 days
          response = await cryptoAnalyticsApi.getDailyStats(symbol, 30);
          // Sort by timestamp to ensure oldest to newest order
          const sortedMonthlyData = response.timeSeries.sort((a, b) => a.timestamp - b.timestamp);
          labels = sortedMonthlyData.map(point => {
            const date = new Date(point.timestamp);
            return `${date.getMonth() + 1}/${date.getDate()}`;
          });
          data = sortedMonthlyData.map(point => point.price);
          break;
        }

        case '1d': {
          // For daily, we'll use hourly data with last 24 hours
          response = await cryptoAnalyticsApi.getHourlyStats(symbol, 24);
          // Sort by timestamp to ensure oldest to newest order
          const sortedDailyData = response.timeSeries.sort((a, b) => a.timestamp - b.timestamp);
          labels = sortedDailyData.map(point => {
            const date = new Date(point.timestamp);
            return `${date.getHours()}:00`;
          });
          data = sortedDailyData.map(point => point.price);
          break;
        }

        default:
          throw new Error(`Unsupported time range: ${timeRange}`);
      }

      setChartLabels(labels);
      setChartData(data);
    } catch (err) {
      console.error('Error fetching chart data:', err);
      setError(err.message);
      // Fallback to empty data
      setChartLabels([]);
      setChartData([]);
    } finally {
      setLoading(false);
    }
  }, [symbol, timeRange]);

  useEffect(() => {
    fetchChartData();
  }, [fetchChartData]);

  return {
    chartData,
    chartLabels,
    loading,
    error,
    refetch: fetchChartData
  };
};
