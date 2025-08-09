import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

KSQLDB_URL = os.getenv('KSQL_URL', 'http://ksqldb-server:8088')
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
            print(f"Response status: {e.response.status_code}")
            print(f"Response text: {e.response.text}")
            try:
                error_json = e.response.json()
                print(f"Error details: {json.dumps(error_json, indent=2)}")
            except:
                pass
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

def create_price_changes_stream():
    """Create stream to track price changes using hopping window (10 min window, 30 sec hop)"""
    statement = """
    CREATE STREAM IF NOT EXISTS crypto_price_changes AS
    SELECT 
        symbol,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end,
        EARLIEST_BY_OFFSET(price_numeric) AS start_price,
        LATEST_BY_OFFSET(price_numeric) AS end_price,
        (LATEST_BY_OFFSET(price_numeric) - EARLIEST_BY_OFFSET(price_numeric)) / EARLIEST_BY_OFFSET(price_numeric) * 100 AS price_change_percent,
        COUNT(*) AS data_points,
        LATEST_BY_OFFSET(event_time) AS latest_timestamp
    FROM crypto_enriched 
    WINDOW HOPPING (SIZE 10 MINUTES, ADVANCE BY 30 SECONDS)
    GROUP BY symbol
    HAVING COUNT(*) > 1
    EMIT CHANGES;
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_price_changes stream with hopping window")
    else:
        print("❌ Failed to create crypto_price_changes stream")
    return result

def create_significant_alerts_stream():
    """Create stream for significant price changes (>=5%)"""
    statement = """
    CREATE STREAM IF NOT EXISTS crypto_significant_alerts AS
    SELECT 
        symbol,
        window_start,
        window_end,
        start_price,
        end_price,
        price_change_percent,
        data_points,
        latest_timestamp,
        CASE 
            WHEN price_change_percent >= 5.0 THEN 'INCREASE'
            WHEN price_change_percent <= -5.0 THEN 'DECREASE'
        END AS alert_type,
        ROWTIME AS alert_time
    FROM crypto_price_changes
    WHERE ABS(price_change_percent) >= 5.0
    EMIT CHANGES;
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_significant_alerts stream")
    else:
        print("❌ Failed to create crypto_significant_alerts stream")
    return result

def create_alert_dedup_table():
    """Create table to track recent alerts for deduplication (2 minute window)"""
    statement = """
    CREATE TABLE IF NOT EXISTS crypto_alert_dedup_store AS
    SELECT 
        symbol,
        LATEST_BY_OFFSET(alert_time) AS last_alert_time,
        LATEST_BY_OFFSET(alert_type) AS last_alert_type,
        COUNT(*) AS alert_count
    FROM crypto_significant_alerts
    WINDOW TUMBLING (SIZE 2 MINUTES)
    GROUP BY symbol
    EMIT CHANGES;
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_alert_dedup_store table")
    else:
        print("❌ Failed to create crypto_alert_dedup_store table")
    return result

def create_deduplicated_alerts_stream():
    """Create final alerts stream with deduplication logic"""
    statement = """
    CREATE STREAM IF NOT EXISTS crypto_alerts AS
    SELECT 
        a.symbol,
        a.window_start,
        a.window_end,
        a.start_price,
        a.end_price,
        a.price_change_percent,
        a.alert_type,
        a.alert_time,
        a.data_points,
        'DEDUPLICATED' AS processing_status
    FROM crypto_significant_alerts a
    LEFT JOIN crypto_alert_dedup_store d 
    ON a.symbol = d.symbol
    WHERE d.symbol IS NULL 
       OR (a.alert_time - d.last_alert_time) > 120000
    EMIT CHANGES;
    """
    
    result = execute_ksql(statement)
    if result:
        print("✅ Created crypto_alerts stream with deduplication")
    else:
        print("❌ Failed to create crypto_alerts stream")
    return result

def drop_existing_alert_streams():
    """Drop existing alert streams to ensure clean recreation"""
    streams_to_drop = [
        "crypto_alerts",
        "crypto_significant_alerts",
        "crypto_price_changes",
        "crypto_alert_dedup_store"
    ]
    
    for stream in streams_to_drop:
        statement = f"DROP STREAM IF EXISTS {stream} DELETE TOPIC;"
        result = execute_ksql(statement)
        if result:
            print(f"✅ Dropped stream {stream}")
        else:
            print(f"⚠️  Could not drop stream {stream} (may not exist)")
            

        statement = f"DROP TABLE IF EXISTS {stream} DELETE TOPIC;"
        result = execute_ksql(statement)
        if result:
            print(f"✅ Dropped table {stream}")

def main():
    print("🚨 Starting ksqlDB setup for crypto price alerting...")
    
    # Wait for ksqlDB to be ready
    if not wait_for_ksqldb():
        print("❌ Cannot proceed without ksqlDB")
        return False
    
    print("🗑️  Dropping existing alert streams...")
    drop_existing_alert_streams()
    
    time.sleep(3)
    
    success = True
    success &= create_price_changes_stream() is not None
    success &= create_significant_alerts_stream() is not None
    success &= create_alert_dedup_table() is not None
    success &= create_deduplicated_alerts_stream() is not None
    
    if success:
        print("✅ All alert streams created successfully!")
        print("\n🚨 Available alert streams:")
        print("  - crypto_price_changes: Hopping window price changes (10min/30sec)")
        print("  - crypto_significant_alerts: Price changes >=5%")
        print("  - crypto_alert_dedup_store: Deduplication tracking table")
        print("  - crypto_alerts: Final deduplicated alerts")
        print("\n⚙️  Alert Configuration:")
        print("  - Window: 10 minutes hopping, 30 second advance")
        print("  - Threshold: ±5% price change")
        print("  - Deduplication: 2 minutes per symbol")
    else:
        print("❌ Some alert streams failed to create")
        return False
    
    return True

if __name__ == '__main__':
    main()