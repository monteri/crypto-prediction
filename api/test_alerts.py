#!/usr/bin/env python3
"""
Test script to generate crypto price alerts for testing purposes.
This script produces messages with significant price changes to trigger alerts.
"""

import os
import json
import time
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
CRYPTO_TOPIC = os.getenv('KAFKA_CRYPTO_TOPIC', 'crypto_prices')

def create_producer():
    """Create Kafka producer for sending test messages"""
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP.split(','),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )

def generate_test_alerts():
    """Generate test alerts with significant price changes"""
    producer = create_producer()
    
    # Test scenarios with significant price changes
    test_scenarios = [
        {
            "symbol": "BTCUSDT",
            "base_price": 45000.0,
            "changes": [0.05, 0.06, 0.07, 0.08, 0.09, 0.10],  # 5% to 10% changes
            "direction": "up"
        },
        {
            "symbol": "ETHUSDT", 
            "base_price": 3200.0,
            "changes": [-0.05, -0.06, -0.07, -0.08, -0.09, -0.10],  # -5% to -10% changes
            "direction": "down"
        },
        {
            "symbol": "BNBUSDT",
            "base_price": 830.0,
            "changes": [0.05, 0.06, 0.07, 0.08, 0.09, 0.10],  # 5% to 10% changes
            "direction": "up"
        }
    ]
    
    print("🚀 Generating test alerts with significant price changes...")
    
    for scenario in test_scenarios:
        symbol = scenario["symbol"]
        base_price = scenario["base_price"]
        changes = scenario["changes"]
        
        print(f"\n📈 Testing {symbol} with {scenario['direction']} price movements...")
        
        # Send initial price
        initial_msg = {
            "symbol": symbol,
            "price": f"{base_price:.8f}",
            "timestamp": int(time.time() * 1000)
        }
        producer.send(CRYPTO_TOPIC, key=symbol, value=initial_msg)
        print(f"  Initial price: ${base_price}")
        
        # Send price changes
        for i, change_pct in enumerate(changes):
            time.sleep(2)  # Wait 2 seconds between messages
            
            if scenario["direction"] == "up":
                new_price = base_price * (1 + change_pct)
            else:
                new_price = base_price * (1 + change_pct)  # change_pct is already negative
            
            msg = {
                "symbol": symbol,
                "price": f"{new_price:.8f}",
                "timestamp": int(time.time() * 1000)
            }
            
            producer.send(CRYPTO_TOPIC, key=symbol, value=msg)
            print(f"  Price change {i+1}: ${new_price:.2f} ({change_pct*100:+.1f}%)")
    
    producer.flush()
    producer.close()
    print("\n✅ Test alerts generated! Check the alerts endpoint in 30-60 seconds.")

if __name__ == "__main__":
    generate_test_alerts()
