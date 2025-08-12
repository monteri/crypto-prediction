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


def consume_latest_alerts(limit: int = 100, timeout_ms: int = 5000) -> List[Dict]:
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP.split(','),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=False
    )
    try:
        parts = [TopicPartition(ALERT_TOPIC, p) for p in consumer.partitions_for_topic(ALERT_TOPIC) or []]
        if not parts:
            return []

        consumer.assign(parts)

        # Compute start offsets ~tail
        end_offsets = consumer.end_offsets(parts)
        per_part = max(1, limit // max(1, len(parts)))
        for tp in parts:
            end = end_offsets[tp]
            start = max(0, end - per_part)
            consumer.seek(tp, start)

        alerts = []
        end_time = time.time() + (timeout_ms / 1000.0)
        while time.time() < end_time and len(alerts) < limit:
            polled = consumer.poll(timeout_ms=200)
            for records in polled.values():
                for msg in records:
                    if msg.value:
                        v = msg.value
                        v['consumed_at'] = int(time.time() * 1000)
                        alerts.append(v)
                        if len(alerts) >= limit:
                            break
        alerts.sort(key=lambda x: x.get('alert_time', 0), reverse=True)
        return alerts[:limit]
    finally:
        consumer.close()


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