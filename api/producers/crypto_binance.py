import os
import json
import time
import threading
from dotenv import load_dotenv
from kafka import KafkaProducer
from websocket import WebSocketApp

load_dotenv()
BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
TOPIC = os.getenv('KAFKA_CRYPTO_TOPIC', 'crypto_prices')

def create_producer():
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}: Initializing Kafka producer...")
            
            producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP.split(','),
                client_id=os.getenv('KAFKA_PRODUCER_CLIENT_ID'),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3,
                acks='all',
                request_timeout_ms=10000,
                retry_backoff_ms=500
            )
            print(f"✅ Kafka producer initialized successfully")
            return producer
            
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                print(f"💥 Failed to initialize Kafka producer after {max_retries} attempts")
                raise

try:
    producer = create_producer()
except Exception as e:
    print(f"❌ Failed to initialize Kafka producer: {e}")
    raise

COINS = ['btcusdt', 'ethusdt', 'bnbusdt']
streams = '/'.join(f"{coin}@ticker" for coin in COINS)
SOCKET = f"wss://stream.binance.com:9443/stream?streams={streams}"
latest_data = {}
running = True


def on_message(ws, message):
    payload = json.loads(message)['data']
    latest_data[payload['s']] = {
        'symbol': payload['s'],
        'price': payload['c'],
        'timestamp': payload['E']
    }


def on_error(ws, error):
    print("WebSocket error:", error)


def on_close(ws, code, reason):
    print("WebSocket closed:", code, reason)
    global running
    running = False


def on_open(ws):
    print("🔌 WebSocket connection opened")
    # Start periodic sending in a separate thread
    threading.Thread(target=periodic_send_worker, daemon=True).start()


def periodic_send_worker():
    """Worker thread for periodic sending of data to Kafka"""
    global running
    while running:
        try:
            if latest_data:
                for msg in latest_data.values():
                    future = producer.send(TOPIC, value=msg)
                    record_metadata = future.get(timeout=10)
                    print(f"✅ Sent to Kafka topic '{TOPIC}' partition {record_metadata.partition} offset {record_metadata.offset}: {msg}")
                producer.flush()
            time.sleep(5)  # Send every 5 seconds
        except Exception as e:
            print(f"❌ Error sending message to Kafka: {e}")
            time.sleep(5)  # Wait before retrying


if __name__ == '__main__':
    print("🔌 Starting WebSocket connection to Binance...")
    print(f"📊 Monitoring: {', '.join(COINS)}")
    print(f"📨 Producing to topic: {TOPIC}")
    print("⏱️ Sending messages every 5 seconds...")
    print("=" * 50)
    
    ws = WebSocketApp(
        SOCKET,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
