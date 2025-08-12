import os
import json
import time
import requests
from dotenv import load_dotenv

load_dotenv()

KSQLDB_URL = os.getenv("KSQL_URL", "http://ksqldb-server:8088")
CRYPTO_TOPIC = os.getenv("KAFKA_CRYPTO_TOPIC", "crypto_prices")


def execute_ksql(statement, stream_properties=None):
    """Execute a ksqlDB statement with detailed error logging."""
    url = f"{KSQLDB_URL}/ksql"
    payload = {"ksql": statement, "streamsProperties": stream_properties or {}}
    headers = {"Content-Type": "application/vnd.ksql.v1+json; charset=utf-8"}

    try:
        r = requests.post(url, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        print("❌ Error executing ksqlDB statement.")
        print("---- KSQL SENT ----")
        print(statement.strip())
        if getattr(e, "response", None) is not None:
            print(f"HTTP {e.response.status_code}")
            try:
                err = e.response.json()
                print("---- KSQL ERROR (JSON) ----")
                print(json.dumps(err, indent=2))
                if isinstance(err, list):
                    for item in err:
                        if "error_message" in item:
                            print("error_message:", item.get("error_message"))
                        if "message" in item:
                            print("message:", item.get("message"))
                        if "statementText" in item:
                            print("statementText:", item.get("statementText"))
                elif isinstance(err, dict):
                    print("message:", err.get("message") or err.get("error_message"))
                    print("statementText:", err.get("statementText"))
            except Exception:
                print("---- KSQL ERROR (TEXT) ----")
                print(e.response.text[:4000])
        else:
            print(str(e))
        return None


def wait_for_ksqldb():
    """Wait for ksqlDB to be ready."""
    max_retries, retry_delay = 30, 2
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{KSQLDB_URL}/info", timeout=3)
            if response.status_code == 200:
                print("✅ ksqlDB is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"⏳ Waiting for ksqlDB... (attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_delay)
    print("❌ ksqlDB not available after maximum retries")
    return False


def exec_with_retry(stmt, tries=3, delay=3):
    """Retry wrapper for occasionally flaky CTAS/CSAS statements."""
    for i in range(tries):
        res = execute_ksql(stmt)
        if res is not None:
            return res
        print(f"🔁 Retry {i+1}/{tries} in {delay}s")
        time.sleep(delay)
    return None


def list_queries():
    """Return parsed SHOW QUERIES output."""
    res = execute_ksql("SHOW QUERIES;")
    if not res:
        return []
    # Find the object containing 'queries'
    for item in res:
        if isinstance(item, dict) and "queries" in item:
            return item.get("queries", [])
    return []


def terminate_queries_touching(names_upper):
    """Terminate any running queries whose sink or sources match names_upper."""
    queries = list_queries()
    for qi in queries:
        qid = qi.get("id")
        sink = (qi.get("sink") or "").upper()
        sources = [s.upper() for s in (qi.get("sources") or [])]
        if sink in names_upper or any(s in names_upper for s in sources):
            execute_ksql(f"TERMINATE {qid};")
            print(f"🛑 TERMINATED {qid} (sink={sink} sources={sources})")


def create_price_changes_table():
    statement = """
    CREATE TABLE IF NOT EXISTS crypto_price_changes
    WITH (KAFKA_TOPIC='crypto_price_changes', PARTITIONS=3, REPLICAS=1) AS
    SELECT 
        symbol,
        WINDOWSTART AS window_start,
        WINDOWEND   AS window_end,
        EARLIEST_BY_OFFSET(price_numeric) AS start_price,
        LATEST_BY_OFFSET(price_numeric)   AS end_price,
        CASE 
          WHEN EARLIEST_BY_OFFSET(price_numeric) = 0 THEN NULL
          ELSE (LATEST_BY_OFFSET(price_numeric) - EARLIEST_BY_OFFSET(price_numeric))
                 / EARLIEST_BY_OFFSET(price_numeric) * 100
        END AS price_change_percent,
        COUNT(*) AS data_points,
        LATEST_BY_OFFSET(event_time) AS latest_timestamp
    FROM crypto_enriched 
    WINDOW HOPPING (SIZE 10 MINUTES, ADVANCE BY 60 SECONDS)
    GROUP BY symbol
    EMIT CHANGES;
    """
    return exec_with_retry(statement)


def create_price_changes_source_stream():
    statement = """
    CREATE STREAM IF NOT EXISTS crypto_price_changes_s (
      symbol VARCHAR,
      window_start BIGINT,
      window_end BIGINT,
      start_price DOUBLE,
      end_price DOUBLE,
      price_change_percent DOUBLE,
      data_points BIGINT,
      latest_timestamp BIGINT
    ) WITH (
      KAFKA_TOPIC='crypto_price_changes',
      VALUE_FORMAT='JSON',
      TIMESTAMP='latest_timestamp',
      PARTITIONS=3
    );
    """
    return exec_with_retry(statement)


def create_significant_alerts_stream():
    statement = """
    CREATE STREAM IF NOT EXISTS crypto_significant_alerts
    WITH (KAFKA_TOPIC='crypto_significant_alerts', PARTITIONS=3, REPLICAS=1) AS
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
        WHEN price_change_percent >=  5.0 THEN 'INCREASE'
        WHEN price_change_percent <= -5.0 THEN 'DECREASE'
      END AS alert_type,
      ROWTIME AS alert_time
    FROM crypto_price_changes_s
    WHERE ABS(price_change_percent) >= 5.0
    EMIT CHANGES;
    """
    return exec_with_retry(statement)


def create_alert_dedup_table():
    statement = """
    CREATE TABLE IF NOT EXISTS crypto_alert_dedup_store
    WITH (KAFKA_TOPIC='crypto_alert_dedup_store', PARTITIONS=3, REPLICAS=1) AS
    SELECT 
      symbol,
      LATEST_BY_OFFSET(alert_time) AS last_alert_time,
      LATEST_BY_OFFSET(alert_type) AS last_alert_type,
      COUNT(*) AS alert_count
    FROM crypto_significant_alerts
    GROUP BY symbol
    EMIT CHANGES;
    """
    return exec_with_retry(statement)


def create_deduplicated_alerts_stream():
    statement = """
    CREATE STREAM IF NOT EXISTS crypto_alerts
    WITH (KAFKA_TOPIC='crypto_alerts', PARTITIONS=3, REPLICAS=1) AS
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
    WHERE d.last_alert_time IS NULL
       OR (a.alert_time - d.last_alert_time) > 120000
    EMIT CHANGES;
    """
    return exec_with_retry(statement)


def drop_existing_alert_streams():
    """
    Dependency-safe teardown:
      1) crypto_alerts (sink)
      2) crypto_alert_dedup_store (reads from significant_alerts)
      3) crypto_significant_alerts (reads from price_changes_s)
      4) crypto_price_changes_s (source over table topic)  [NO DELETE TOPIC]
    """
    objs_upper = {
        "CRYPTO_ALERTS",
        "CRYPTO_ALERT_DEDUP_STORE",
        "CRYPTO_SIGNIFICANT_ALERTS",
        "CRYPTO_PRICE_CHANGES_S",
    }
    terminate_queries_touching(objs_upper)

    # Drop in correct order
    cmds = [
        ("STREAM", "crypto_alerts", True),
        ("TABLE",  "crypto_alert_dedup_store", True),
        ("STREAM", "crypto_significant_alerts", True),
        ("STREAM", "crypto_price_changes_s", False),  # do NOT delete topic
    ]
    for kind, name, delete_topic in cmds:
        if kind == "STREAM":
            stmt = f"DROP STREAM IF EXISTS {name}" + (" DELETE TOPIC;" if delete_topic else ";")
        else:
            stmt = f"DROP TABLE IF EXISTS {name}" + (" DELETE TOPIC;" if delete_topic else ";")
        res = execute_ksql(stmt)
        print(("✅ Dropped" if res else "⚠️  Could not drop"), kind.lower(), name)


def main():
    print("Starting ksqlDB setup for crypto price alerting...")

    if not wait_for_ksqldb():
        print("❌ Cannot proceed without ksqlDB")
        return False

    print("🗑️  Dropping existing alert streams...")
    drop_existing_alert_streams()

    # Give the command runner a moment to settle
    time.sleep(6)

    success = True
    success &= create_price_changes_table() is not None
    success &= create_price_changes_source_stream() is not None
    success &= create_significant_alerts_stream() is not None
    success &= create_alert_dedup_table() is not None
    success &= create_deduplicated_alerts_stream() is not None

    if success:
        print("✅ All alert streams created successfully!")
    else:
        print("❌ Some alert streams failed to create")
        return False

    return True


if __name__ == "__main__":
    main()
