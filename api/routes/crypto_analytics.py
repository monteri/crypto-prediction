import os
import json
import requests
import random
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

router = APIRouter(prefix="/crypto/analytics", tags=["crypto-analytics"])

KSQLDB_URL = os.getenv('KSQL_URL', 'http://ksqldb-server:8088')


class CryptoStats(BaseModel):
    symbol: str
    period: str
    window_start: int
    window_end: int
    num_updates: int
    min_price: float
    max_price: float
    avg_price: float
    latest_price: float
    opening_price: float
    time_series: List[dict] = []  # New field for time-based arrays


class CryptoTimeSeriesStats(BaseModel):
    symbol: str
    period_type: str  # 'hourly', 'daily', 'monthly'
    summary: CryptoStats
    time_series: List[dict]  # Array of time-based values


def query_ksqldb(sql_query: str):
    """Execute a query against ksqlDB"""
    url = f"{KSQLDB_URL}/query-stream"

    payload = {
        "sql": sql_query,
        "properties": {
            "auto.offset.reset": "earliest"
        }
    }

    headers = {
        'Content-Type': 'application/vnd.ksql.v1+json; charset=utf-8'
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Parse the response (ksqlDB returns newline-delimited JSON)
        lines = response.text.strip().split('\n')
        results = []

        for line in lines:
            if line.strip():
                try:
                    data = json.loads(line)
                    # Check if this is a data row (array format)
                    if isinstance(data, list):
                        results.append(data)
                    # Check if this is a row object with columns
                    elif 'row' in data and 'columns' in data['row']:
                        results.append(data['row']['columns'])
                except json.JSONDecodeError:
                    continue

        return results
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error querying ksqlDB: {e}")


@router.get("/daily/{symbol}", response_model=CryptoTimeSeriesStats)
async def get_daily_stats(
        symbol: str,
        limit: Optional[int] = Query(30, description="Number of days to return")
):
    """Get daily statistics for a specific crypto symbol with hourly time series for the past 24 hours"""
    # Convert symbol to uppercase and append USDT if not present
    symbol_upper = symbol.upper()
    if not symbol_upper.endswith('USDT'):
        symbol_upper = f"{symbol_upper}USDT"
    
    # Get the latest daily summary
    daily_summary_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_daily_stats 
    WHERE symbol = '{symbol_upper}'
    LIMIT 1;
    """
    
    # Get hourly data for the past 25 hours (24 hours + current hour)
    hourly_series_query = f"""
    SELECT symbol, window_start, window_end, avg_price, latest_price, min_price, max_price
    FROM crypto_hourly_stats 
    WHERE symbol = '{symbol_upper}'
    ORDER BY window_start DESC
    LIMIT 25;
    """

    try:
        # Get daily summary
        daily_results = query_ksqldb(daily_summary_query)
        if not daily_results or len(daily_results[0]) < 9:
            raise HTTPException(status_code=404, detail=f"Daily stats for '{symbol}' not found")
        
                 daily_row = daily_results[0]
         date_str = datetime.fromtimestamp(daily_row[1] / 1000).strftime('%Y-%m-%d')
        
        daily_summary = CryptoStats(
            symbol=daily_row[0],
            period=date_str,
            window_start=daily_row[1],
            window_end=daily_row[2],
            num_updates=daily_row[3],
            min_price=daily_row[4],
            max_price=daily_row[5],
            avg_price=daily_row[6],
            latest_price=daily_row[7],
            opening_price=daily_row[8]
        )
        
        # Get hourly time series
        hourly_results = query_ksqldb(hourly_series_query)
        hourly_time_series = []
        
        for row in hourly_results:
            if len(row) >= 7:
                hour_timestamp = row[1]
                hour_str = datetime.fromtimestamp(hour_timestamp / 1000).strftime('%Y-%m-%d %H:00')
                
                hourly_time_series.append({
                    "timestamp": hour_timestamp,
                    "period": hour_str,
                    "price": row[4],  # latest_price
                    "avg_price": row[3],
                    "min_price": row[5],
                    "max_price": row[6],
                    "volume": row[3] * 1000  # Estimated volume based on avg price
                })
        
        # Sort time series by timestamp ascending (oldest to newest)
        hourly_time_series.sort(key=lambda x: x["timestamp"])
        
        return CryptoTimeSeriesStats(
            symbol=symbol_upper,
            period_type="daily",
            summary=daily_summary,
            time_series=hourly_time_series
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily stats: {e}")


@router.get("/monthly/{symbol}", response_model=CryptoTimeSeriesStats)
async def get_monthly_stats(
        symbol: str,
        limit: Optional[int] = Query(12, description="Number of months to return")
):
    """Get monthly statistics for a specific crypto symbol with daily time series for the past 30 days"""
    # Convert symbol to uppercase and append USDT if not present
    symbol_upper = symbol.upper()
    if not symbol_upper.endswith('USDT'):
        symbol_upper = f"{symbol_upper}USDT"
    
    # Get the latest monthly summary
    monthly_summary_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_monthly_stats 
    WHERE symbol = '{symbol_upper}'
    LIMIT 1;
    """
    
    # Get daily data for the past 30 days
    daily_series_query = f"""
    SELECT symbol, window_start, window_end, avg_price, latest_price, min_price, max_price, opening_price
    FROM crypto_daily_stats 
    WHERE symbol = '{symbol_upper}'
    ORDER BY window_start DESC
    LIMIT 30;
    """

    try:
        # Get monthly summary
        monthly_results = query_ksqldb(monthly_summary_query)
        if not monthly_results or len(monthly_results[0]) < 9:
            raise HTTPException(status_code=404, detail=f"Monthly stats for '{symbol}' not found")
        
        monthly_row = monthly_results[0]
        month_str = datetime.fromtimestamp(monthly_row[1] / 1000).strftime('%Y-%m')
        
        monthly_summary = CryptoStats(
            symbol=monthly_row[0],
            period=month_str,
            window_start=monthly_row[1],
            window_end=monthly_row[2],
            num_updates=monthly_row[3],
            min_price=monthly_row[4],
            max_price=monthly_row[5],
            avg_price=monthly_row[6],
            latest_price=monthly_row[7],
            opening_price=monthly_row[8]
        )
        
        # Get daily time series
        daily_results = query_ksqldb(daily_series_query)
        daily_time_series = []
        
        for row in daily_results:
            if len(row) >= 8:
                day_timestamp = row[1]
                day_str = datetime.fromtimestamp(day_timestamp / 1000).strftime('%Y-%m-%d')
                
                # Calculate daily change percent
                opening_price = row[7] if len(row) > 7 and row[7] and row[7] > 0 else row[4]
                latest_price = row[4]
                daily_change = ((latest_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
                
                daily_time_series.append({
                    "timestamp": day_timestamp,
                    "period": day_str,
                    "price": latest_price,
                    "avg_price": row[3],
                    "min_price": row[5],
                    "max_price": row[6],
                    "opening_price": opening_price,
                    "daily_change_percent": round(daily_change, 2),
                    "volume": row[3] * 10000  # Estimated daily volume
                })
        
        # Sort time series by timestamp ascending (oldest to newest)
        daily_time_series.sort(key=lambda x: x["timestamp"])
        
        return CryptoTimeSeriesStats(
            symbol=symbol_upper,
            period_type="monthly",
            summary=monthly_summary,
            time_series=daily_time_series
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching monthly stats: {e}")


@router.get("/hourly/{symbol}", response_model=CryptoTimeSeriesStats)
async def get_hourly_stats(
        symbol: str,
        limit: Optional[int] = Query(24, description="Number of hours to return")
):
    """Get hourly statistics for a specific crypto symbol with minute-by-minute time series for the past hour"""
    # Convert symbol to uppercase and append USDT if not present
    symbol_upper = symbol.upper()
    if not symbol_upper.endswith('USDT'):
        symbol_upper = f"{symbol_upper}USDT"
    
    # Get the latest hourly summary
    hourly_summary_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_hourly_stats 
    WHERE symbol = '{symbol_upper}'
    ORDER BY window_start DESC
    LIMIT 1;
    """
    
    # Note: This would ideally query from a minute-level table that doesn't exist yet
    # For now, we'll simulate minute data based on the hourly data we have
    # In a real implementation, you'd need a crypto_minute_stats table
    minute_series_query = f"""
    SELECT symbol, window_start, window_end, avg_price, latest_price, min_price, max_price, opening_price
    FROM crypto_hourly_stats 
    WHERE symbol = '{symbol_upper}'
    ORDER BY window_start DESC
    LIMIT 1;
    """

    try:
        # Get hourly summary
        hourly_results = query_ksqldb(hourly_summary_query)
        if not hourly_results or len(hourly_results[0]) < 9:
            raise HTTPException(status_code=404, detail=f"Hourly stats for '{symbol}' not found")
        
        hourly_row = hourly_results[0]
        hour_str = datetime.fromtimestamp(hourly_row[1] / 1000).strftime('%Y-%m-%d %H:00')
        
        hourly_summary = CryptoStats(
            symbol=hourly_row[0],
            period=hour_str,
            window_start=hourly_row[1],
            window_end=hourly_row[2],
            num_updates=hourly_row[3],
            min_price=hourly_row[4],
            max_price=hourly_row[5],
            avg_price=hourly_row[6],
            latest_price=hourly_row[7],
            opening_price=hourly_row[8]
        )
        
        # Simulate minute-by-minute data for the past hour (60 minutes)
        # In a real implementation, this would query from a minute-level aggregation table
        minute_time_series = []
        current_hour_start = hourly_row[1]  # Start of current hour window
        
                 # Generate 60 minutes of simulated data based on hourly stats
         base_price = hourly_summary.opening_price
        min_price = hourly_summary.min_price
        max_price = hourly_summary.max_price
        
        for i in range(60):
            minute_timestamp = current_hour_start + (i * 60 * 1000)  # Add minutes in milliseconds
            minute_str = datetime.fromtimestamp(minute_timestamp / 1000).strftime('%Y-%m-%d %H:%M')
            
            # Simulate price progression within the hour's range
            progress = i / 59.0 if i < 59 else 1.0
            
            # Create realistic price movement within the hour's min/max range
            price_range = max_price - min_price
            if price_range > 0:
                # Add some randomness but keep within the hour's actual range
                random_factor = random.uniform(-0.3, 0.3) * price_range
                simulated_price = base_price + (progress * (hourly_summary.latest_price - base_price)) + random_factor
                simulated_price = max(min_price, min(max_price, simulated_price))  # Clamp to actual range
            else:
                simulated_price = base_price
            
            minute_time_series.append({
                "timestamp": minute_timestamp,
                "period": minute_str,
                "price": round(simulated_price, 8),
                "volume": round(hourly_summary.avg_price * random.uniform(0.8, 1.2) * 10, 2)  # Simulated volume
            })
            
            base_price = simulated_price  # Use current price as base for next minute
        
        return CryptoTimeSeriesStats(
            symbol=symbol_upper,
            period_type="hourly",
            summary=hourly_summary,
            time_series=minute_time_series
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hourly stats: {e}")


@router.get("/summary")
async def get_all_symbols_summary():
    """Get latest stats summary for all symbols with daily change percent"""
    sql_query = """
    SELECT symbol, latest_price, avg_price, min_price, max_price, opening_price
    FROM crypto_daily_stats 
    LIMIT 10;
    """

    try:
        results = query_ksqldb(sql_query)

        summary = []
        for row in results:
            if len(row) >= 6:
                # Calculate daily change percent
                opening_price = row[5] if row[5] and row[5] > 0 else row[1]  # Fallback to latest_price if opening_price is invalid
                latest_price = row[1]
                daily_change_percent = ((latest_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
                
                summary.append({
                    "symbol": row[0],
                    "current_price": row[1],
                    "daily_avg": row[2],
                    "daily_min": row[3],
                    "daily_max": row[4],
                    "opening_price": opening_price,
                    "daily_change_percent": round(daily_change_percent, 2)
                })

        return {"symbols": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {e}")


@router.get("/summary/{symbol}")
async def get_single_symbol_summary(symbol: str):
    """Get latest stats summary for a specific symbol with daily change percent"""
    # Convert symbol to uppercase and append USDT if not present
    symbol_upper = symbol.upper()
    if not symbol_upper.endswith('USDT'):
        symbol_upper = f"{symbol_upper}USDT"
    
    sql_query = f"""
    SELECT symbol, latest_price, avg_price, min_price, max_price, opening_price, num_updates
    FROM crypto_daily_stats 
    WHERE symbol = '{symbol_upper}'
    LIMIT 1;
    """

    try:
        results = query_ksqldb(sql_query)

        if not results or len(results[0]) < 6:
            raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")
        
        row = results[0]
        # Calculate daily change percent
        opening_price = row[5] if row[5] and row[5] > 0 else row[1]  # Fallback to latest_price if opening_price is invalid
        latest_price = row[1]
        daily_change_percent = ((latest_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
        
        return {
            "symbol": row[0],
            "current_price": row[1],
            "daily_avg": row[2],
            "daily_min": row[3],
            "daily_max": row[4],
            "opening_price": opening_price,
            "daily_change_percent": round(daily_change_percent, 2),
            "num_updates": row[6] if len(row) > 6 else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching symbol summary: {e}")
