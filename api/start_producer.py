#!/usr/bin/env python3
import os
import sys
import time
from dotenv import load_dotenv
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from producers.crypto_binance import *

load_dotenv()

def ensure_topic_exists():
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    topic_name = 'crypto_prices'
    max_retries = 30
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            print(f"🔄 Attempt {attempt + 1}/{max_retries}: Connecting to Kafka at {bootstrap_servers}...")
            
            admin_client = KafkaAdminClient(
                bootstrap_servers=bootstrap_servers.split(','),
                client_id='startup_admin',
                request_timeout_ms=10000,
                retry_backoff_ms=500
            )
            
            new_topic = NewTopic(
                name=topic_name,
                num_partitions=3,
                replication_factor=1
            )
            
            admin_client.create_topics([new_topic])
            print(f"✅ Topic '{topic_name}' created successfully")
            admin_client.close()
            return
            
        except TopicAlreadyExistsError:
            print(f"ℹ️ Topic '{topic_name}' already exists")
            admin_client.close()
            return
        except Exception as e:
            print(f"❌ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {retry_delay} seconds before retry...")
                time.sleep(retry_delay)
            else:
                print(f"💥 Failed to create topic after {max_retries} attempts")
                raise

def main():
    print("🚀 Starting Binance Crypto Producer...")
    
    print("📋 Ensuring topic exists...")
    ensure_topic_exists()
    
    time.sleep(2)
    
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
    
    try:
        ws.run_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down producer...")
        ws.close()
        producer.close()
        print("✅ Producer shutdown complete")

if __name__ == '__main__':
    main() 