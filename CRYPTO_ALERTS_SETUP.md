# Crypto Price Alerts System

This document describes the crypto price alerts system that has been implemented to monitor significant price changes in real-time.

## Overview

The alerting system uses KSQL hopping windows to detect significant price changes (>=5%) and implements deduplication to prevent alert spam.

## Architecture

### Components

1. **Alert Streams (KSQL)**
   - `crypto_price_changes`: Hopping window stream (10 min window, 30 sec hop)
   - `crypto_significant_alerts`: Filters for price changes >=5%
   - `crypto_alert_dedup_store`: Deduplication table (2 min window)
   - `crypto_alerts`: Final deduplicated alerts

2. **Alert Consumer** (`alert_consumer.py`)
   - Consumes alerts from `crypto_alerts` topic
   - Stores alerts in memory for API access
   - Provides real-time alert processing

3. **API Endpoints** (`crypto_alerts.py`)
   - `/alerts/poll` - **Frontend polling endpoint (recommended)**
   - `/alerts/since/{timestamp}` - Get alerts since timestamp
   - `/alerts` - Get recent alerts
   - `/alerts/summary` - Get alert statistics
   - `/alerts/{symbol}` - Get alerts for specific symbol
   - `/alerts/health` - Check consumer health

## Configuration

### Environment Variables

```bash
# Alert-specific configuration
KAFKA_ALERT_TOPIC=crypto_alerts
KAFKA_ALERT_CONSUMER_GROUP=alert-processor-group
```

### Topics Created

- `crypto_alerts` - Final alert messages
- `_crypto_price_changes` - Internal: Price change calculations
- `_crypto_alert_dedup_store` - Internal: Deduplication state

## Alert Logic

### Detection Window
- **Window Size**: 10 minutes
- **Hop Interval**: 30 seconds
- **Threshold**: ±5% price change

### Deduplication
- **Window**: 2 minutes per symbol
- **Logic**: Prevents alerts for the same symbol within 2 minutes

### Alert Structure

```json
{
  "symbol": "BTCUSDT",
  "start_price": 45000.0,
  "end_price": 47250.0,
  "price_change_percent": 5.0,
  "alert_type": "INCREASE",
  "alert_time": 1640995200000,
  "window_start": 1640995200000,
  "window_end": 1640995800000,
  "data_points": 15,
  "processing_status": "DEDUPLICATED",
  "processed_at": "2024-01-01T12:00:00Z",
  "alert_id": "BTCUSDT_1640995200000"
}
```

## Running the System

### 1. Bootstrap (includes alert streams)
```bash
# Run complete bootstrap
docker-compose up bootstrap

# Or manually
python api/bootstrap/bootstrap_complete.py
```

### 2. Start Services
```bash
# Start all services including alert consumer
docker-compose up

# Or start alert consumer separately
python api/start_alert_consumer.py
```

### 3. API Usage

#### Frontend Polling (Recommended)
```bash
# First poll - get alerts from last 10 minutes
curl "http://localhost:8000/alerts/poll?minutes_back=10"

# Subsequent polls - use timestamp from previous response
curl "http://localhost:8000/alerts/poll?since=1640995200000"
```

#### Get Alerts Since Timestamp
```bash
curl "http://localhost:8000/alerts/since/1640995200000"
```

#### Get Recent Alerts
```bash
curl "http://localhost:8000/alerts?limit=10"
```

#### Get Alerts for Specific Symbol
```bash
curl "http://localhost:8000/alerts/BTCUSDT?limit=5"
```

#### Get Alert Summary
```bash
curl "http://localhost:8000/alerts/summary"
```

#### Check Health
```bash
curl "http://localhost:8000/alerts/health"
```

### Frontend Integration

For frontend applications, use the provided JavaScript polling class:

```javascript
// Initialize the poller
const alertPoller = new CryptoAlertPoller('http://localhost:8000');

// Set up alert handling
alertPoller.onNewAlerts((alertData) => {
    console.log(`Received ${alertData.new_alerts_count} new alerts`);
    // Update your UI here
});

// Start polling every 30 seconds
alertPoller.startPolling();
```

See `frontend-polling-example.js` for a complete implementation example.

### Polling Response Structure

The `/alerts/poll` endpoint returns optimized data for frontend consumption:

```json
{
  "success": true,
  "data": {
    "polling_timestamp": 1640995800000,
    "since_timestamp": 1640995200000,
    "new_alerts_count": 2,
    "has_new_alerts": true,
    "new_alerts": [
      {
        "symbol": "BTCUSDT",
        "start_price": 45000.0,
        "end_price": 47250.0,
        "price_change_percent": 5.0,
        "alert_type": "INCREASE",
        "alert_time": 1640995500000,
        "alert_id": "BTCUSDT_1640995500000"
      }
    ],
    "alerts_by_symbol": {
      "BTCUSDT": [/* alerts for BTC */],
      "ETHUSDT": [/* alerts for ETH */]
    },
    "alert_type_counts": {
      "INCREASE": 1,
      "DECREASE": 1
    },
    "symbols_with_alerts": ["BTCUSDT", "ETHUSDT"]
  },
  "polling_info": {
    "recommended_poll_interval": "30 seconds",
    "next_poll_timestamp": 1640995800000
  }
}
```

**Key fields for frontend:**
- `has_new_alerts`: Quick boolean check
- `new_alerts_count`: Number for badges/counters
- `polling_timestamp`: Use for next poll request
- `alerts_by_symbol`: Pre-grouped data for UI components

## Monitoring

### Consumer Health
The alert consumer provides health endpoints to monitor:
- Consumer status (running/stopped)
- Alerts in memory
- Memory usage percentage

### Alert Statistics
Track alert patterns through the summary endpoint:
- Total alerts generated
- Alert distribution by symbol
- Alert type distribution (INCREASE/DECREASE)
- Latest alert information

## Performance Considerations

### Memory Usage
- Alerts are stored in memory (max 1000 alerts)
- Automatic cleanup of old alerts
- Configurable via `max_alerts` parameter

### Throughput
- Hopping window processes every 30 seconds
- Deduplication prevents alert storms
- Consumer can handle high-frequency updates

## Troubleshooting

### Common Issues

1. **No Alerts Generated**
   - Check if price changes exceed 5% threshold
   - Verify KSQL streams are running
   - Ensure enough data points in window

2. **Consumer Not Starting**
   - Check Kafka connectivity
   - Verify topic exists
   - Check environment variables

3. **Alert Deduplication**
   - Alerts within 2 minutes are filtered
   - Check deduplication table status
   - Verify alert timestamps

### Debug Commands

```bash
# Check KSQL streams status
curl -X POST "http://localhost:8088/ksql" \
  -H "Content-Type: application/vnd.ksql.v1+json" \
  -d '{"ksql": "SHOW STREAMS;"}'

# Check alert topic
kafka-console-consumer --bootstrap-server localhost:29092 \
  --topic crypto_alerts --from-beginning

# Consumer health
curl "http://localhost:8000/alerts/health"
```

## Future Enhancements

1. **Configurable Thresholds**: Make 5% threshold configurable per symbol
2. **Notification Integration**: Add email/SMS/Slack notifications
3. **Historical Storage**: Persist alerts to database
4. **Advanced Filters**: Add volume-based filtering
5. **Alert Subscriptions**: User-specific alert preferences