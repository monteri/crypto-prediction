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


def consume_latest_alerts(limit: int = 100, timeout_ms: int = 300) -> List[Dict]:
    """
    Ultra-optimized consumer for sub-1-second response times
    """
    consumer = KafkaConsumer(
        bootstrap_servers=BOOTSTRAP.split(','),
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        enable_auto_commit=False,
        auto_offset_reset='latest',  # Start from latest messages
        consumer_timeout_ms=timeout_ms,
        group_id='alerts-api-consumer-direct'
    )
    
    try:
        # Check if topic exists and has partitions
        partitions = consumer.partitions_for_topic(ALERT_TOPIC)
        if not partitions:
            return []
        
        parts = [TopicPartition(ALERT_TOPIC, p) for p in partitions]
        consumer.assign(parts)

        # Get end offsets for all partitions
        end_offsets = consumer.end_offsets(parts)
        
        # Calculate how many messages to fetch from each partition
        per_part = max(1, limit // max(1, len(parts)))
        
        # Seek to appropriate positions in each partition
        for tp in parts:
            end = end_offsets[tp]
            start = max(0, end - per_part)
            consumer.seek(tp, start)

        alerts = []
        
        # Single poll with short timeout for maximum speed
        polled = consumer.poll(timeout_ms=timeout_ms)
        
        for records in polled.values():
            for msg in records:
                if msg.value:
                    v = msg.value
                    v['consumed_at'] = int(time.time() * 1000)
                    alerts.append(v)
                    if len(alerts) >= limit:
                        break
            if len(alerts) >= limit:
                break
                    
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
        
        # Direct Kafka query
        alerts = consume_latest_alerts(limit=limit, timeout_ms=300)
        
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