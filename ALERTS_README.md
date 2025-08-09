# Crypto Alerts - Simplified

Simple crypto price alerting system that detects price changes ≥5% using KSQL hopping windows.

## System Overview

- **KSQL Streams**: Detect price changes with 10-minute hopping windows (30-second advance)
- **Deduplication**: Prevent duplicate alerts within 2 minutes per symbol  
- **Direct Consumption**: API endpoint consumes directly from Kafka on request

## Configuration

Environment variables:
```
KAFKA_ALERT_TOPIC=crypto_alerts
KAFKA_BOOTSTRAP_SERVERS=kafka1:19092
```

## API Endpoint

**GET /alerts**
```bash
curl "http://localhost:8000/alerts?limit=50"
```

Response:
```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTCUSDT",
      "start_price": 45000.0,
      "end_price": 47250.0,
      "price_change_percent": 5.0,
      "alert_type": "INCREASE",
      "alert_time": 1640995500000,
      "consumed_at": 1640995800000
    }
  ],
  "count": 1,
  "timestamp": 1640995800000
}
```

## Frontend Polling

Poll every 30 seconds:
```javascript
async function checkAlerts() {
    const response = await fetch('/alerts?limit=20');
    const data = await response.json();
    
    if (data.success && data.count > 0) {
        // Process new alerts
        data.data.forEach(alert => {
            console.log(`${alert.symbol}: ${alert.price_change_percent}%`);
        });
    }
}

setInterval(checkAlerts, 30000);
```

## Alert Logic

- **Window**: 10 minutes, advancing every 30 seconds
- **Threshold**: ±5% price change
- **Deduplication**: 2-minute window per symbol
- **Types**: INCREASE or DECREASE