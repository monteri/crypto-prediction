import React, { useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { useAlert } from './contexts/AlertContext.jsx';
import { cryptoAnalyticsApi } from './api';
import Dashboard from './pages/Dashboard.jsx';

// Lazy load components
const Coin = lazy(() => import('./pages/Coin.jsx'));

// Loading component
const LoadingSpinner = () => (
  <div style={{ 
    display: 'flex', 
    justifyContent: 'center', 
    alignItems: 'center', 
    height: '100vh',
    backgroundColor: '#222',
    color: 'white'
  }}>
    <div>Loading...</div>
  </div>
);

const Router = () => {
  const { show } = useAlert();

  useEffect(() => {
    let isCancelled = false;

    const fetchAlerts = async () => {
      try {
        const response = await cryptoAnalyticsApi.getAlerts(2);
        
        if (isCancelled) return;

        // Only show alerts if we have data and success is true
        if (response.success && response.data && response.data.length > 0) {
          response.data.forEach((alert) => {
            const alertKind = getAlertKind(alert.severity);
            show({
              title: `${alert.symbol} Alert`,
              message: alert.message,
              kind: alertKind,
              timeout: 8000,
              position: 'bottom-right'
            });
          });
        }
      } catch (error) {
        console.error('Error fetching alerts:', error);
        // Don't show error alerts to avoid spam
      }
    };

    // Fetch alerts immediately
    fetchAlerts();

    // Set up interval to fetch alerts every 30 seconds
    const intervalId = setInterval(fetchAlerts, 30000);

    return () => {
      isCancelled = true;
      clearInterval(intervalId);
    };
  }, [show]);

  const getAlertKind = (severity) => {
    switch (severity?.toLowerCase()) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'info';
    }
  };

  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/coin/:id" element={<Coin />} />
      </Routes>
    </Suspense>
  );
};

export default Router;
