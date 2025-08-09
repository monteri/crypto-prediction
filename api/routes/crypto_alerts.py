from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from consumers.alert_consumer import get_alert_consumer
import threading
import time

router = APIRouter()

# Start alert consumer when module is imported
alert_consumer = get_alert_consumer()

def ensure_consumer_running():
    """Ensure alert consumer is running"""
    if not alert_consumer.consumer:
        def consumer_worker():
            try:
                if alert_consumer.create_consumer():
                    alert_consumer.start_consuming()
            except Exception as e:
                print(f"❌ Error starting alert consumer: {e}")
        
        # Start consumer in daemon thread
        consumer_thread = threading.Thread(target=consumer_worker, daemon=True)
        consumer_thread.start()
        time.sleep(2)  # Give it a moment to initialize

@router.get("/alerts", summary="Get Recent Crypto Alerts")
async def get_alerts(
    symbol: Optional[str] = Query(None, description="Filter by crypto symbol (e.g., BTCUSDT)"),
    limit: int = Query(100, ge=1, le=1000, description="Number of alerts to return")
) -> Dict:
    """
    Get recent crypto price alerts
    
    - **symbol**: Optional filter by crypto symbol
    - **limit**: Maximum number of alerts to return (1-1000)
    """
    try:
        ensure_consumer_running()
        alerts = alert_consumer.get_recent_alerts(symbol=symbol, limit=limit)
        
        return {
            "success": True,
            "data": alerts,
            "count": len(alerts),
            "filters": {
                "symbol": symbol,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")

@router.get("/alerts/summary", summary="Get Alert Summary Statistics")
async def get_alert_summary() -> Dict:
    """
    Get summary statistics of crypto alerts
    
    Returns:
    - Total number of alerts
    - List of symbols with alerts
    - Alert type distribution
    - Latest alert information
    """
    try:
        ensure_consumer_running()
        summary = alert_consumer.get_alert_summary()
        
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alert summary: {str(e)}")

@router.get("/alerts/symbols", summary="Get Available Symbols with Alerts")
async def get_alert_symbols() -> Dict:
    """
    Get list of crypto symbols that have generated alerts
    """
    try:
        ensure_consumer_running()
        summary = alert_consumer.get_alert_summary()
        
        return {
            "success": True,
            "data": {
                "symbols": summary.get("symbols", []),
                "count": len(summary.get("symbols", []))
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving symbols: {str(e)}")

@router.get("/alerts/{symbol}", summary="Get Alerts for Specific Symbol")
async def get_symbol_alerts(
    symbol: str,
    limit: int = Query(50, ge=1, le=500, description="Number of alerts to return")
) -> Dict:
    """
    Get alerts for a specific crypto symbol
    
    - **symbol**: Crypto symbol (e.g., BTCUSDT, ETHUSDT)
    - **limit**: Maximum number of alerts to return
    """
    try:
        ensure_consumer_running()
        symbol = symbol.upper()
        alerts = alert_consumer.get_recent_alerts(symbol=symbol, limit=limit)
        
        if not alerts:
            return {
                "success": True,
                "message": f"No alerts found for symbol {symbol}",
                "data": [],
                "count": 0,
                "symbol": symbol
            }
        
        return {
            "success": True,
            "data": alerts,
            "count": len(alerts),
            "symbol": symbol
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts for {symbol}: {str(e)}")

@router.get("/alerts/health", summary="Check Alert Consumer Health")
async def check_alert_health() -> Dict:
    """
    Check the health status of the alert consumer
    """
    try:
        consumer_status = "running" if alert_consumer.consumer else "stopped"
        alerts_count = len(alert_consumer.alert_store)
        
        return {
            "success": True,
            "data": {
                "consumer_status": consumer_status,
                "alerts_in_memory": alerts_count,
                "max_alerts_capacity": alert_consumer.max_alerts,
                "memory_usage_percent": (alerts_count / alert_consumer.max_alerts) * 100
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking health: {str(e)}")

@router.post("/alerts/reset", summary="Reset Alert Consumer")
async def reset_alert_consumer() -> Dict:
    """
    Reset the alert consumer and clear stored alerts
    
    Warning: This will clear all in-memory alerts
    """
    try:
        # Clear alerts
        alert_consumer.alert_store.clear()
        
        # Close existing consumer if running
        if alert_consumer.consumer:
            alert_consumer.consumer.close()
            alert_consumer.consumer = None
        
        return {
            "success": True,
            "message": "Alert consumer reset successfully",
            "data": {
                "alerts_cleared": True,
                "consumer_status": "stopped"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting consumer: {str(e)}")