import os
import json
import time
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()

class CryptoConsumer:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.topic = os.getenv('KAFKA_CRYPTO_TOPIC', 'crypto_prices')
        self.group_id = os.getenv('KAFKA_CONSUMER_GROUP_ID', 'crypto_consumer_group')
        self.consumer = None
        
    def create_consumer(self):
        """Create and configure Kafka consumer"""
        max_retries = 30
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{max_retries}: Initializing Kafka consumer...")
                
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=self.bootstrap_servers.split(','),
                    group_id=self.group_id,
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                    consumer_timeout_ms=10000
                )
                print(f"✅ Kafka consumer initialized successfully")
                print(f"📊 Listening to topic: {self.topic}")
                print(f"👥 Consumer group: {self.group_id}")
                return True
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    print(f"💥 Failed to initialize Kafka consumer after {max_retries} attempts")
                    return False
    
    def consume_messages(self):
        """Consume messages from Kafka topic"""
        if not self.consumer:
            print("❌ Consumer not initialized")
            return
            
        print("🚀 Starting to consume messages...")
        print("=" * 50)
        
        try:
            for message in self.consumer:
                print(f"📨 Received message from partition {message.partition} at offset {message.offset}")
                print(f"🔑 Key: {message.key}")
                print(f"📊 Value: {message.value}")
                print(f"⏰ Timestamp: {message.timestamp}")
                print("-" * 30)
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopping consumer...")
        except Exception as e:
            print(f"❌ Error consuming messages: {e}")
        finally:
            self.close()
    
    def close(self):
        """Close the consumer connection"""
        if self.consumer:
            self.consumer.close()
            print("🔌 Consumer connection closed")


def main():
    consumer = CryptoConsumer()
    if consumer.create_consumer():
        consumer.consume_messages()
    else:
        print("❌ Failed to start consumer")


if __name__ == '__main__':
    main() 