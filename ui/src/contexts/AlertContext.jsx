import React, { createContext, useContext, useState, useCallback } from 'react';
import { ToastNotification, InlineNotification } from '@carbon/react';

const AlertContext = createContext();

export const useAlert = () => {
  const context = useContext(AlertContext);
  if (!context) {
    throw new Error('useAlert must be used within an AlertProvider');
  }
  return context;
};

export const AlertProvider = ({ children }) => {
  const [alerts, setAlerts] = useState([]);

  const show = useCallback(({ 
    title = 'Notification', 
    message, 
    kind = 'info', 
    timeout = 5000,
    position = 'top-right' 
  }) => {
    const id = Date.now() + Math.random();
    const newAlert = {
      id,
      title,
      message,
      kind,
      timeout,
      position
    };

    setAlerts(prev => [...prev, newAlert]);

    // Auto remove after timeout
    if (timeout > 0) {
      setTimeout(() => {
        remove(id);
      }, timeout);
    }

    return id;
  }, []);

  const remove = useCallback((id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  }, []);

  const success = useCallback((message, title = 'Success') => {
    return show({ title, message, kind: 'success' });
  }, [show]);

  const error = useCallback((message, title = 'Error') => {
    return show({ title, message, kind: 'error' });
  }, [show]);

  const warning = useCallback((message, title = 'Warning') => {
    return show({ title, message, kind: 'warning' });
  }, [show]);

  const info = useCallback((message, title = 'Info') => {
    return show({ title, message, kind: 'info' });
  }, [show]);

  const value = {
    show,
    success,
    error,
    warning,
    info,
    remove,
    alerts
  };

  return (
    <AlertContext.Provider value={value}>
      {children}
      <AlertContainer />
    </AlertContext.Provider>
  );
};

const AlertContainer = () => {
  const { alerts, remove } = useAlert();

  const getPositionStyles = (position) => {
    const baseStyles = {
      position: 'fixed',
      zIndex: 9999,
      maxWidth: '400px',
      width: '100%',
      margin: '16px'
    };

    switch (position) {
      case 'top-right':
        return { ...baseStyles, top: 0, right: 0 };
      case 'top-left':
        return { ...baseStyles, top: 0, left: 0 };
      case 'bottom-right':
        return { ...baseStyles, bottom: 0, right: 0 };
      case 'bottom-left':
        return { ...baseStyles, bottom: 0, left: 0 };
      case 'top-center':
        return { ...baseStyles, top: 0, left: '50%', transform: 'translateX(-50%)' };
      case 'bottom-center':
        return { ...baseStyles, bottom: 0, left: '50%', transform: 'translateX(-50%)' };
      default:
        return { ...baseStyles, top: 0, right: 0 };
    }
  };

  return (
    <div style={{ position: 'relative' }}>
      {alerts.map((alert) => (
        <div key={alert.id} style={getPositionStyles(alert.position)}>
          <ToastNotification
            title={alert.title}
            subtitle={alert.message}
            kind={alert.kind}
            onClose={() => remove(alert.id)}
            timeout={alert.timeout}
            lowContrast={false}
          />
        </div>
      ))}
    </div>
  );
};
