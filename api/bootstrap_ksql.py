import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

KSQLDB_URL = os.getenv('KSQLDB_URL', 'http://ksqldb-server:8088')
CRYPTO_TOPIC = os.getenv('KAFKA_CRYPTO_TOPIC', 'crypto_prices')

def execute_ksql(statement, stream_properties=None):
    """Execute a ksqlDB statement"""
    url = f"{KSQLDB_URL}/ksql"
    
    payload = {
        "ksql": statement,
        "streamsProperties": stream_properties or {}
    }
    
    headers = {
        'Content-Type': 'application/vnd.ksql.v1+json; charset=utf-8'
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error executing ksqlDB statement: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")
        return None

def wait_for_ksqldb():
    """Wait for ksqlDB to be ready"""
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{KSQLDB_URL}/info")
            if response.status_code == 200:
                print("✅ ksqlDB is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Waiting for ksqlDB... (attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)
    
    print("❌ ksqlDB not available after maximum retries")
    return False

def create_crypto_stream():
    """Create the main crypto prices stream"""
    statement = f"""
    CREATE STREAM IF NOT EXISTS crypto_prices_stream (
        symbol VARCHAR,
        price VARCHAR,
        timestamp BIGINT
    ) WITH (
        KAFKA_TOPIC='{CRYPTO_TOPIC}',
        VALUE_FORMAT='JSON'
    );
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_prices_stream")
    else:
        print("❌ Failed to create crypto_prices_stream")
    return result

def create_crypto_enriched_stream():
    """Create enriched stream with proper timestamp and numeric price"""
    statement = """
    CREATE STREAM IF NOT EXISTS crypto_enriched AS
    SELECT 
        symbol,
        CAST(price AS DOUBLE) AS price_numeric,
        timestamp AS price_timestamp,
        ROWTIME AS event_time
    FROM crypto_prices_stream
    EMIT CHANGES;
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_enriched stream")
    else:
        print("❌ Failed to create crypto_enriched stream")
    return result

def create_daily_aggregates_table():
    """Create daily price aggregates table"""
    statement = """
    CREATE TABLE IF NOT EXISTS crypto_daily_stats AS
    SELECT 
        symbol,
        FORMAT_DATE(FROM_UNIXTIME(WINDOWSTART/1000), 'yyyy-MM-dd') AS date_str,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end,
        COUNT(*) AS num_updates,
        MIN(price_numeric) AS min_price,
        MAX(price_numeric) AS max_price,
        AVG(price_numeric) AS avg_price,
        LATEST_BY_OFFSET(price_numeric) AS latest_price,
        EARLIEST_BY_OFFSET(price_numeric) AS opening_price
    FROM crypto_enriched 
    WINDOW TUMBLING (SIZE 1 DAY)
    GROUP BY symbol
    EMIT CHANGES;
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_daily_stats table")
    else:
        print("❌ Failed to create crypto_daily_stats table")
    return result

def create_monthly_aggregates_table():
    """Create monthly price aggregates table"""
    statement = """
    CREATE TABLE IF NOT EXISTS crypto_monthly_stats AS
    SELECT 
        symbol,
        FORMAT_DATE(FROM_UNIXTIME(WINDOWSTART/1000), 'yyyy-MM') AS month_str,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end,
        COUNT(*) AS num_updates,
        MIN(price_numeric) AS min_price,
        MAX(price_numeric) AS max_price,
        AVG(price_numeric) AS avg_price,
        LATEST_BY_OFFSET(price_numeric) AS latest_price,
        EARLIEST_BY_OFFSET(price_numeric) AS opening_price
    FROM crypto_enriched 
    WINDOW TUMBLING (SIZE 30 DAYS)
    GROUP BY symbol
    EMIT CHANGES;
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_monthly_stats table")
    else:
        print("❌ Failed to create crypto_monthly_stats table")
    return result

def create_hourly_aggregates_table():
    """Create hourly price aggregates table for more granular data"""
    statement = """
    CREATE TABLE IF NOT EXISTS crypto_hourly_stats AS
    SELECT 
        symbol,
        FORMAT_DATE(FROM_UNIXTIME(WINDOWSTART/1000), 'yyyy-MM-dd HH') AS hour_str,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end,
        COUNT(*) AS num_updates,
        MIN(price_numeric) AS min_price,
        MAX(price_numeric) AS max_price,
        AVG(price_numeric) AS avg_price,
        LATEST_BY_OFFSET(price_numeric) AS latest_price,
        EARLIEST_BY_OFFSET(price_numeric) AS opening_price
    FROM crypto_enriched 
    WINDOW TUMBLING (SIZE 1 HOUR)
    GROUP BY symbol
    EMIT CHANGES;
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_hourly_stats table")
    else:
        print("❌ Failed to create crypto_hourly_stats table")
    return result

def main():
    print("🚀 Starting ksqlDB setup for crypto price views...")
    
    # Wait for ksqlDB to be ready
    if not wait_for_ksqldb():
        print("❌ Cannot proceed without ksqlDB")
        return False
    
    # Create streams and tables
    success = True
    success &= create_crypto_stream() is not None
    success &= create_crypto_enriched_stream() is not None
    success &= create_hourly_aggregates_table() is not None
    success &= create_daily_aggregates_table() is not None
    success &= create_monthly_aggregates_table() is not None
    
    if success:
        print("✅ All ksqlDB views created successfully!")
        print("\n📊 Available views:")
        print("  - crypto_prices_stream: Raw crypto price stream")
        print("  - crypto_enriched: Enriched stream with numeric prices")
        print("  - crypto_hourly_stats: Hourly aggregated statistics")
        print("  - crypto_daily_stats: Daily aggregated statistics")
        print("  - crypto_monthly_stats: Monthly aggregated statistics")
    else:
        print("❌ Some ksqlDB views failed to create")
        return False
    
    return True

if __name__ == '__main__':
    main()