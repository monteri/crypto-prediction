/**
 * Frontend Alert Polling Example
 * This example shows how to poll for crypto alerts every 30 seconds
 */

class CryptoAlertPoller {
    constructor(apiBaseUrl = 'http://localhost:8000') {
        this.apiBaseUrl = apiBaseUrl;
        this.lastPollTimestamp = null;
        this.pollingInterval = null;
        this.pollIntervalMs = 30000; // 30 seconds
        this.isPolling = false;
        this.alertCallbacks = [];
    }

    /**
     * Start polling for alerts
     */
    startPolling() {
        if (this.isPolling) {
            console.log('Alert polling is already running');
            return;
        }

        console.log('Starting crypto alert polling every 30 seconds...');
        this.isPolling = true;
        
        // Poll immediately on start
        this.pollForAlerts();
        
        // Set up recurring polling
        this.pollingInterval = setInterval(() => {
            this.pollForAlerts();
        }, this.pollIntervalMs);
    }

    /**
     * Stop polling for alerts
     */
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
        this.isPolling = false;
        console.log('Alert polling stopped');
    }

    /**
     * Add callback function to be called when new alerts are received
     */
    onNewAlerts(callback) {
        this.alertCallbacks.push(callback);
    }

    /**
     * Poll for new alerts
     */
    async pollForAlerts() {
        try {
            const url = this.buildPollUrl();
            console.log(`Polling for alerts: ${url}`);
            
            const response = await fetch(url);
            const result = await response.json();
            
            if (result.success) {
                const alertData = result.data;
                
                // Update our last poll timestamp for next request
                this.lastPollTimestamp = alertData.polling_timestamp;
                
                // Check if there are new alerts
                if (alertData.has_new_alerts) {
                    console.log(`🚨 ${alertData.new_alerts_count} new alerts received!`);
                    this.handleNewAlerts(alertData);
                } else {
                    console.log('No new alerts');
                }
                
                // Log polling info
                console.log(`Next poll in ${this.pollIntervalMs / 1000} seconds`);
                
            } else {
                console.error('Failed to poll alerts:', result);
            }
            
        } catch (error) {
            console.error('Error polling for alerts:', error);
        }
    }

    /**
     * Build the polling URL with appropriate parameters
     */
    buildPollUrl() {
        const endpoint = `${this.apiBaseUrl}/alerts/poll`;
        const params = new URLSearchParams();
        
        if (this.lastPollTimestamp) {
            params.append('since', this.lastPollTimestamp.toString());
        } else {
            // First poll - get alerts from last 10 minutes
            params.append('minutes_back', '10');
        }
        
        return `${endpoint}?${params.toString()}`;
    }

    /**
     * Handle new alerts received from polling
     */
    handleNewAlerts(alertData) {
        // Log alert summary
        console.log('Alert Summary:', {
            count: alertData.new_alerts_count,
            symbols: alertData.symbols_with_alerts,
            types: alertData.alert_type_counts
        });
        
        // Process each alert
        alertData.new_alerts.forEach(alert => {
            this.processAlert(alert);
        });
        
        // Call registered callbacks
        this.alertCallbacks.forEach(callback => {
            try {
                callback(alertData);
            } catch (error) {
                console.error('Error in alert callback:', error);
            }
        });
    }

    /**
     * Process a single alert
     */
    processAlert(alert) {
        const { symbol, price_change_percent, alert_type, start_price, end_price } = alert;
        
        console.log(`🚨 ALERT: ${symbol} ${alert_type}`);
        console.log(`   📈 Change: ${price_change_percent.toFixed(2)}%`);
        console.log(`   💰 Price: $${start_price} → $${end_price}`);
        
        // You can add more alert processing logic here:
        // - Show browser notifications
        // - Update UI components
        // - Play sounds
        // - Send to analytics
    }

    /**
     * Get current polling status
     */
    getStatus() {
        return {
            isPolling: this.isPolling,
            lastPollTimestamp: this.lastPollTimestamp,
            pollInterval: this.pollIntervalMs,
            callbackCount: this.alertCallbacks.length
        };
    }
}

// Usage Example:
const alertPoller = new CryptoAlertPoller();

// Add callback to handle new alerts
alertPoller.onNewAlerts((alertData) => {
    // Update your UI with new alerts
    updateAlertUI(alertData);
    
    // Show browser notification if supported
    if ('Notification' in window && Notification.permission === 'granted') {
        if (alertData.new_alerts_count > 0) {
            new Notification(`${alertData.new_alerts_count} Crypto Alert(s)`, {
                body: `New price alerts for: ${alertData.symbols_with_alerts.join(', ')}`,
                icon: '/crypto-icon.png'
            });
        }
    }
});

// Start polling when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Request notification permission
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
    
    // Start alert polling
    alertPoller.startPolling();
});

// Stop polling when page unloads
window.addEventListener('beforeunload', () => {
    alertPoller.stopPolling();
});

/**
 * Example UI update function
 */
function updateAlertUI(alertData) {
    // Example: Update alert count badge
    const alertBadge = document.getElementById('alert-badge');
    if (alertBadge && alertData.new_alerts_count > 0) {
        alertBadge.textContent = alertData.new_alerts_count;
        alertBadge.style.display = 'block';
    }
    
    // Example: Add alerts to alert list
    const alertList = document.getElementById('alert-list');
    if (alertList) {
        alertData.new_alerts.forEach(alert => {
            const alertElement = createAlertElement(alert);
            alertList.insertBefore(alertElement, alertList.firstChild);
        });
    }
}

/**
 * Create HTML element for an alert
 */
function createAlertElement(alert) {
    const div = document.createElement('div');
    div.className = `alert alert-${alert.alert_type.toLowerCase()}`;
    div.innerHTML = `
        <div class="alert-header">
            <span class="alert-symbol">${alert.symbol}</span>
            <span class="alert-type">${alert.alert_type}</span>
            <span class="alert-time">${new Date(alert.alert_time).toLocaleTimeString()}</span>
        </div>
        <div class="alert-details">
            <span class="price-change ${alert.price_change_percent > 0 ? 'positive' : 'negative'}">
                ${alert.price_change_percent > 0 ? '+' : ''}${alert.price_change_percent.toFixed(2)}%
            </span>
            <span class="price-range">
                $${alert.start_price} → $${alert.end_price}
            </span>
        </div>
    `;
    return div;
}

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CryptoAlertPoller;
}