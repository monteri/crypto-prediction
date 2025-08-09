import os
import json
import time
from datetime import datetime
from typing import Dict, List
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
ALERT_TOPIC = os.getenv('KAFKA_ALERT_TOPIC', 'crypto_alerts')
CONSUMER_GROUP = os.getenv('KAFKA_ALERT_CONSUMER_GROUP', 'alert-processor-group')

class CryptoAlertConsumer:
    def __init__(self):
        self.consumer = None
        self.alert_store: List[Dict] = []  # Store alerts in memory
        self.max_alerts = 1000  # Keep last 1000 alerts
        
    def create_consumer(self):
        """Create Kafka consumer for alerts"""
        max_retries = 30
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                print(f"🔄 Attempt {attempt + 1}/{max_retries}: Initializing alert consumer...")
                
                self.consumer = KafkaConsumer(
                    ALERT_TOPIC,
                    bootstrap_servers=BOOTSTRAP.split(','),
                    group_id=CONSUMER_GROUP,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    key_deserializer=lambda m: m.decode('utf-8') if m else None,
                    auto_offset_reset='latest',  # Start from latest alerts
                    enable_auto_commit=True,
                    auto_commit_interval_ms=1000,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000
                )
                
                print(f"✅ Alert consumer initialized successfully")
                print(f"📨 Consuming from topic: {ALERT_TOPIC}")
                print(f"👥 Consumer group: {CONSUMER_GROUP}")
                return True
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"⏳ Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                else:
                    print(f"💥 Failed to initialize alert consumer after {max_retries} attempts")
                    raise
        
        return False
    
    def process_alert(self, alert_data: Dict) -> None:
        """Process a single crypto alert"""
        try:
            # Enrich alert with processing timestamp
            enriched_alert = {
                **alert_data,
                'processed_at': datetime.utcnow().isoformat() + 'Z',
                'alert_id': f"{alert_data.get('symbol', 'UNKNOWN')}_{alert_data.get('alert_time', int(time.time() * 1000))}"
            }
            
            # Add to in-memory store
            self.alert_store.append(enriched_alert)
            
            # Keep only the most recent alerts
            if len(self.alert_store) > self.max_alerts:
                self.alert_store = self.alert_store[-self.max_alerts:]
            
            # Log the alert
            symbol = enriched_alert.get('symbol', 'UNKNOWN')
            change_percent = enriched_alert.get('price_change_percent', 0)
            alert_type = enriched_alert.get('alert_type', 'UNKNOWN')
            start_price = enriched_alert.get('start_price', 0)
            end_price = enriched_alert.get('end_price', 0)
            
            print(f"🚨 CRYPTO ALERT: {symbol}")
            print(f"   📊 Type: {alert_type}")
            print(f"   📈 Change: {change_percent:.2f}%")
            print(f"   💰 Price: ${start_price:.4f} → ${end_price:.4f}")
            print(f"   🕐 Time: {enriched_alert['processed_at']}")
            print(f"   🆔 Alert ID: {enriched_alert['alert_id']}")
            print("   " + "="*50)
            
        except Exception as e:
            print(f"❌ Error processing alert: {e}")
            print(f"Alert data: {alert_data}")
    
    def get_recent_alerts(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """Get recent alerts, optionally filtered by symbol"""
        alerts = self.alert_store.copy()
        
        if symbol:
            alerts = [alert for alert in alerts if alert.get('symbol') == symbol.upper()]
        
        # Sort by alert time (most recent first)
        alerts.sort(key=lambda x: x.get('alert_time', 0), reverse=True)
        
        return alerts[:limit]
    
    def get_alert_summary(self) -> Dict:
        """Get summary statistics of alerts"""
        if not self.alert_store:
            return {
                'total_alerts': 0,
                'symbols': [],
                'alert_types': {},
                'latest_alert': None
            }
        
        symbols = list(set(alert.get('symbol') for alert in self.alert_store))
        alert_types = {}
        
        for alert in self.alert_store:
            alert_type = alert.get('alert_type', 'UNKNOWN')
            alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
        
        # Get latest alert
        latest_alert = max(self.alert_store, key=lambda x: x.get('alert_time', 0))
        
        return {
            'total_alerts': len(self.alert_store),
            'symbols': sorted(symbols),
            'alert_types': alert_types,
            'latest_alert': latest_alert
        }
    
    def start_consuming(self):
        """Start consuming alerts"""
        if not self.consumer:
            if not self.create_consumer():
                print("❌ Failed to create consumer")
                return
        
        print("🚀 Starting crypto alert consumer...")
        print("🔍 Listening for price alerts...")
        print("=" * 60)
        
        try:
            for message in self.consumer:
                if message.value:
                    self.process_alert(message.value)
                    
        except KeyboardInterrupt:
            print("\n⏹️  Consumer stopped by user")
        except Exception as e:
            print(f"❌ Error in consumer loop: {e}")
        finally:
            if self.consumer:
                self.consumer.close()
                print("✅ Consumer closed")

# Global instance for API access
alert_consumer_instance = CryptoAlertConsumer()

def get_alert_consumer():
    """Get the global alert consumer instance"""
    return alert_consumer_instance

if __name__ == '__main__':
    consumer = CryptoAlertConsumer()
    consumer.start_consuming()