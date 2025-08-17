import React from 'react';
import { Button, ButtonSet } from '@carbon/react';
import { useAlert } from '../contexts/AlertContext.jsx';

const AlertExample = () => {
  const { success, error, warning, info, show } = useAlert();

  const handleSuccess = () => {
    success('Operation completed successfully!');
  };

  const handleError = () => {
    error('Something went wrong. Please try again.');
  };

  const handleWarning = () => {
    warning('This action cannot be undone.');
  };

  const handleInfo = () => {
    info('Here is some useful information.');
  };

  const handleCustom = () => {
    show({
      title: 'Custom Alert',
      message: 'This is a custom alert with different position',
      kind: 'info',
      timeout: 3000,
      position: 'bottom-right'
    });
  };

  return (
    <div style={{ padding: '20px' }}>
      <h3>Alert Examples</h3>
      <p>Click the buttons below to see different types of alerts:</p>
      
      <ButtonSet>
        <Button kind="tertiary" onClick={handleSuccess}>
          Show Success
        </Button>
        <Button kind="tertiary" onClick={handleError}>
          Show Error
        </Button>
        <Button kind="tertiary" onClick={handleWarning}>
          Show Warning
        </Button>
        <Button kind="tertiary" onClick={handleInfo}>
          Show Info
        </Button>
        <Button kind="tertiary" onClick={handleCustom}>
          Custom Alert
        </Button>
      </ButtonSet>
    </div>
  );
};

export default AlertExample;
