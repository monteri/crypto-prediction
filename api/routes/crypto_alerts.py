import os
import json
import time
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
ALERT_TOPIC = os.getenv('KAFKA_ALERT_TOPIC', 'crypto_alerts')

def consume_latest_alerts(limit: int = 100, timeout_ms: int = 5000) -> List[Dict]:
    """Consume latest alerts directly from Kafka topic"""
    try:
        consumer = KafkaConsumer(
            ALERT_TOPIC,
            bootstrap_servers=BOOTSTRAP.split(','),
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=False,
            consumer_timeout_ms=timeout_ms
        )
        
        alerts = []
        for message in consumer:
            if message.value:
                alert = message.value
                alert['consumed_at'] = int(time.time() * 1000)
                alerts.append(alert)
                
                if len(alerts) >= limit:
                    break
        
        consumer.close()
        return sorted(alerts, key=lambda x: x.get('alert_time', 0), reverse=True)
        
    except Exception as e:
        print(f"Error consuming alerts: {e}")
        return []

@router.get("/alerts")
async def get_alerts(limit: int = Query(50, ge=1, le=200)) -> Dict:
    """Get latest crypto price alerts"""
    try:
        alerts = consume_latest_alerts(limit=limit)
        
        return {
            "success": True,
            "data": alerts,
            "count": len(alerts),
            "timestamp": int(time.time() * 1000)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))