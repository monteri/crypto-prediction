#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import time

load_dotenv()

def test_kafka_connection():
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    print(f"Testing connection to: {bootstrap_servers}")
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers.split(','),
            client_id='test_producer',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        print("✅ Producer created successfully")
        
        consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers.split(','),
            group_id='test_consumer',
            auto_offset_reset='earliest'
        )
        print("✅ Consumer created successfully")
        
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers.split(','),
            client_id='test_admin'
        )
        print("✅ Admin client created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_topic_creation():
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers.split(','),
            client_id='test_admin'
        )
        
        topic_name = 'test_topic'
        new_topic = NewTopic(
            name=topic_name,
            num_partitions=1,
            replication_factor=1
        )
        
        admin_client.create_topics([new_topic])
        print(f"✅ Topic '{topic_name}' created successfully")
        
        admin_client.delete_topics([topic_name])
        print(f"✅ Topic '{topic_name}' deleted successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Topic creation failed: {e}")
        return False

def test_message_production():
    bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
    topic_name = 'test_producer_topic'
    
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers.split(','),
            client_id='test_admin'
        )
        
        new_topic = NewTopic(
            name=topic_name,
            num_partitions=1,
            replication_factor=1
        )
        admin_client.create_topics([new_topic])
        
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers.split(','),
            client_id='test_producer',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        test_message = {
            'symbol': 'BTCUSDT',
            'price': '50000.00',
            'timestamp': int(time.time() * 1000)
        }
        
        future = producer.send(topic_name, value=test_message)
        record_metadata = future.get(timeout=10)
        
        print(f"✅ Message sent successfully to topic '{topic_name}' partition {record_metadata.partition} offset {record_metadata.offset}")
        
        admin_client.delete_topics([topic_name])
        producer.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Message production failed: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Kafka setup...")
    
    print("\n1. Testing Kafka connection...")
    if not test_kafka_connection():
        print("❌ Kafka connection failed. Make sure Kafka is running.")
        exit(1)
    
    print("\n2. Testing topic creation...")
    if not test_topic_creation():
        print("❌ Topic creation failed.")
        exit(1)
    
    print("\n3. Testing message production...")
    if not test_message_production():
        print("❌ Message production failed.")
        exit(1)
    
    print("\n🎉 All tests passed! Kafka setup is working correctly.") 