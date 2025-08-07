# Crypto Analytics with Kafka Views

This guide explains how to use the automated Kafka and ksqlDB setup for crypto price analytics with daily and monthly aggregations.

## Overview

The system provides:
- **Real-time crypto price streaming** from Binance
- **Automated topic and view creation**
- **Hourly, daily, and monthly aggregations** using ksqlDB
- **REST API endpoints** to query the aggregated data

## Architecture

```
Binance WebSocket → Kafka Topic → ksqlDB Streams/Tables → FastAPI Endpoints
```

### Components

1. **Kafka Topics**: Raw crypto price data
2. **ksqlDB Streams**: 
   - `crypto_prices_stream`: Raw price stream
   - `crypto_enriched`: Enriched stream with numeric prices
3. **ksqlDB Tables**:
   - `crypto_hourly_stats`: Hourly aggregations
   - `crypto_daily_stats`: Daily aggregations  
   - `crypto_monthly_stats`: Monthly aggregations

## Directory Structure

```
api/
├── bootstrap/              # Bootstrap scripts and configuration
│   ├── bootstrap_complete.py    # Main bootstrap orchestrator
│   ├── bootstrap_topics.py      # Kafka topics creation
│   ├── bootstrap_ksql.py        # ksqlDB views creation
│   ├── start_bootstrap.sh       # Bootstrap shell script
│   └── topics.yaml              # Topic configuration
├── routes/                 # API routes
│   ├── crypto_analytics.py     # Analytics endpoints
│   └── crypto_coins.py          # Coin data endpoints
├── producers/              # Kafka producers
└── consumers/              # Kafka consumers
```

## Quick Start

### 1. Setup Environment

Copy the environment file:
```bash
cp .env.example .env
```

### 2. Start the Complete System

Option A: Start everything at once (recommended)
```bash
make start-all
```

Option B: Start step by step
```bash
# Start Kafka infrastructure first
make start-kafka

# Wait a moment, then start the app services
make start-app
```

### 3. Verify Bootstrap

The bootstrap process will automatically:
- ✅ Create Kafka topics
- ✅ Create ksqlDB streams and tables
- ✅ Set up hourly, daily, and monthly aggregations

Check logs:
```bash
docker logs kafka_bootstrap
```

### 4. Access the API

The FastAPI server will be available at: `http://localhost:8000`

## API Endpoints

### Analytics Endpoints

#### Get Daily Statistics
```http
GET /crypto/analytics/daily/{symbol}?limit=30
```

Example:
```bash
curl "http://localhost:8000/crypto/analytics/daily/BTCUSDT?limit=7"
```

Response:
```json
[
  {
    "symbol": "BTCUSDT",
    "period": "2024-01-15",
    "window_start": 1705276800000,
    "window_end": 1705363200000,
    "num_updates": 17280,
    "min_price": 42150.50,
    "max_price": 43200.75,
    "avg_price": 42675.32,
    "latest_price": 43100.25,
    "opening_price": 42200.10
  }
]
```

#### Get Monthly Statistics
```http
GET /crypto/analytics/monthly/{symbol}?limit=12
```

#### Get Hourly Statistics
```http
GET /crypto/analytics/hourly/{symbol}?limit=24
```

#### Get Summary for All Symbols
```http
GET /crypto/analytics/summary
```

### Health Check
```http
GET /health
```

## Supported Crypto Symbols

Currently monitored symbols:
- `BTCUSDT` (Bitcoin)
- `ETHUSDT` (Ethereum)  
- `BNBUSDT` (Binance Coin)

## Data Fields Explained

Each aggregation includes:

- **symbol**: Crypto symbol (e.g., "BTCUSDT")
- **period**: Time period (date/hour/month string)
- **window_start/end**: Timestamp range for the aggregation
- **num_updates**: Number of price updates in the period
- **min_price**: Lowest price in the period
- **max_price**: Highest price in the period
- **avg_price**: Average price in the period
- **latest_price**: Most recent price (close price)
- **opening_price**: First price in the period (open price)

## ksqlDB Views Details

### Raw Stream
```sql
-- Raw crypto prices
SELECT * FROM crypto_prices_stream;
```

### Daily Aggregations
```sql
-- Daily stats for Bitcoin
SELECT * FROM crypto_daily_stats 
WHERE symbol = 'BTCUSDT'
ORDER BY window_start DESC;
```

### Custom Queries

You can access ksqlDB directly at `http://localhost:8088` to run custom queries:

```sql
-- Get hourly price volatility
SELECT symbol, hour_str, 
       (max_price - min_price) AS volatility,
       (max_price - min_price) / avg_price * 100 AS volatility_pct
FROM crypto_hourly_stats
WHERE symbol = 'BTCUSDT'
ORDER BY window_start DESC
LIMIT 24;
```

## Management Commands

### Stop Services
```bash
make stop
```

### Clean Everything
```bash
make clean
```

### Run Bootstrap Manually
If you need to recreate topics/views:
```bash
make bootstrap
```

### View Logs
```bash
# All services
docker-compose -f compose.yml logs -f

# Specific service
docker logs kafka_producer -f
docker logs kafka_consumer -f
docker logs fastapi_app -f
```

## Configuration

### Environment Variables

Key configurations in `.env`:

```env
# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka1:19092
KAFKA_CRYPTO_TOPIC=crypto_prices
KAFKA_TOPIC_CONFIG_FILE=bootstrap/topics.yaml

# ksqlDB
KSQL_URL=http://ksqldb-server:8088

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000
```

### Topic Configuration

Edit `api/bootstrap/topics.yaml` to modify topic settings:

```yaml
topics:
  - name: crypto_prices
    partitions: 3
    replication: 1
```

## Troubleshooting

### Common Issues

1. **Bootstrap fails**: Check if Kafka and ksqlDB are running
   ```bash
   docker-compose -f kafka.yaml ps
   ```

2. **No data in views**: Verify producer is running
   ```bash
   docker logs kafka_producer
   ```

3. **API returns empty**: Wait for data to accumulate or check ksqlDB
   ```bash
   curl http://localhost:8088/info
   ```

### Useful ksqlDB Commands

Access ksqlDB CLI:
```bash
docker exec -it ksqldb-server ksql http://localhost:8088
```

List streams and tables:
```sql
SHOW STREAMS;
SHOW TABLES;
```

Check data:
```sql
SELECT * FROM crypto_daily_stats EMIT CHANGES LIMIT 5;
```

## Performance Notes

- **Data Retention**: Tables automatically maintain windowed data
- **Scaling**: Increase topic partitions for higher throughput
- **Memory**: ksqlDB tables are stored in memory and backed by Kafka topics
- **Latency**: Real-time aggregations update as new data arrives

## Next Steps

1. **Add More Coins**: Modify `COINS` list in `api/producers/crypto_binance.py`
2. **Custom Aggregations**: Create new ksqlDB queries in `api/bootstrap/bootstrap_ksql.py`
3. **Alerting**: Add endpoints for price change alerts
4. **UI Dashboard**: Build a frontend to visualize the data

---

For more details, see the individual component documentation in the `api/` directory.