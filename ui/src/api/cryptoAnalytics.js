import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';
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
      const response = await apiClient.get(`${CRYPTO_ANALYTICS_PATH}/summary/`);
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
};
