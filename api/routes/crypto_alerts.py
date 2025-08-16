import os
import json
import time
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from kafka import KafkaConsumer, TopicPartition
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS')
ALERT_TOPIC = os.getenv('KAFKA_ALERT_TOPIC', 'crypto_alerts')


def consume_new_alerts(limit: int = 10, timeout_ms: int = 1500) -> List[Dict]:
    """
    Consume only new alerts using consumer group offsets to avoid duplicates
    """
    consumer = KafkaConsumer(
        ALERT_TOPIC,
        bootstrap_servers=BOOTSTRAP.split(','),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=False,              # we'll commit explicitly
        auto_offset_reset='earliest',
        group_id='alerts-api-consumer-persistent',
        consumer_timeout_ms=timeout_ms,
        max_poll_records=limit                 # cap per poll
    )
    
    alerts = []
    try:
        end = time.time() + (timeout_ms / 1000.0)
        while len(alerts) < limit and time.time() < end:
            records = consumer.poll(timeout_ms=timeout_ms)
            for _tp, msgs in records.items():
                for msg in msgs:
                    v = msg.value
                    if v:
                        v['consumed_at'] = int(time.time() * 1000)
                        alerts.append(v)
                        if len(alerts) >= limit:
                            break
                if len(alerts) >= limit:
                    break
        
        # commit what we actually consumed
        if alerts:
            consumer.commit()
        
        # Sort by alert time (most recent first)
        alerts.sort(key=lambda x: x.get('alert_time', 0), reverse=True)
        return alerts[:limit]
        
    except Exception as e:
        print(f"Error consuming alerts: {e}")
        return []
    finally:
        consumer.close()


@router.get("/alerts")
async def get_alerts(limit: int = Query(50, ge=1, le=200)) -> Dict:
    """Get latest crypto price alerts with sub-1-second performance for frontend"""
    try:
        start_time = time.time()
        
        # Direct Kafka query - only new alerts, no duplicates
        alerts = consume_new_alerts(limit=limit, timeout_ms=300)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            "success": True,
            "data": alerts,
            "count": len(alerts),
            "timestamp": int(time.time() * 1000),
            "processing_time_ms": round(processing_time, 2),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))