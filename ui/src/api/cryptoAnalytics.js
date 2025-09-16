import axios from 'axios';

const API_BASE_URL = 'http://localhost:8080';
const CRYPTO_ANALYTICS_PATH = '/crypto/analytics'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const cryptoAnalyticsApi = {
  getAllSymbolsSummary: async () => {
    try {
      const response = await apiClient.get(`${CRYPTO_ANALYTICS_PATH}/summary`);
      return response.data;
    } catch (error) {
      console.error('Error fetching all symbols summary:', error);
      throw error;
    }
  },

  getSymbolSummary: async (symbol) => {
    try {
      const response = await apiClient.get(`${CRYPTO_ANALYTICS_PATH}/summary/${symbol}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching summary for ${symbol}:`, error);
      throw error;
    }
  },

  getDailyStats: async (symbol, limit = 30) => {
    try {
      const response = await apiClient.get(`${CRYPTO_ANALYTICS_PATH}/daily/${symbol}?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching daily stats for ${symbol}:`, error);
      throw error;
    }
  },

  getMonthlyStats: async (symbol, limit = 12) => {
    try {
      const response = await apiClient.get(`${CRYPTO_ANALYTICS_PATH}/monthly/${symbol}?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching monthly stats for ${symbol}:`, error);
      throw error;
    }
  },

  getHourlyStats: async (symbol, limit = 24) => {
    try {
      const response = await apiClient.get(`${CRYPTO_ANALYTICS_PATH}/hourly/${symbol}?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching hourly stats for ${symbol}:`, error);
      throw error;
    }
  },

  getAlerts: async (limit = 2) => {
    try {
      const response = await apiClient.get(`/alerts?limit=${limit}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching alerts:', error);
      throw error;
    }
  },
};
