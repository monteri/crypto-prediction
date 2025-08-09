#!/usr/bin/env python3
"""
Starts the crypto alert consumer
This service processes crypto price alerts and stores them for API access
"""
import os
import threading
import time
from consumers.alert_consumer import alert_consumer_instance

def start_alert_consumer():
    """Start the alert consumer in a separate thread"""
    def consumer_worker():
        try:
            # Initialize the consumer
            if alert_consumer_instance.create_consumer():
                # Start consuming alerts
                alert_consumer_instance.start_consuming()
            else:
                print("❌ Failed to create alert consumer")
        except Exception as e:
            print(f"❌ Error in alert consumer: {e}")
    
    # Start consumer in daemon thread
    consumer_thread = threading.Thread(target=consumer_worker, daemon=True)
    consumer_thread.start()
    print("✅ Alert consumer started in background thread")
    return consumer_thread

if __name__ == '__main__':
    print("🚨 Starting Crypto Alert Consumer Service...")
    print("=" * 50)
    
    try:
        # Start the consumer
        thread = start_alert_consumer()
        
        # Keep the main thread alive
        print("🔍 Alert consumer is running...")
        print("Press Ctrl+C to stop")
        
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping alert consumer...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("✅ Alert consumer service stopped")