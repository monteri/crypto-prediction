import os
import json
import requests
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

router = APIRouter(prefix="/crypto/analytics", tags=["crypto-analytics"])

KSQLDB_URL = os.getenv('KSQL_URL', 'http://ksqldb-server:8088')


class TimeSeriesDataPoint(BaseModel):
    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    period: str = Field(..., description="Formatted period string (YYYY-MM-DD, YYYY-MM, or YYYY-MM-DD HH:00)")
    price: float = Field(..., description="Latest price for the period")
    avg_price: float = Field(..., description="Average price for the period")
    min_price: float = Field(..., description="Minimum price for the period")
    max_price: float = Field(..., description="Maximum price for the period")
    opening_price: float = Field(..., description="Opening price for the period")
    daily_change_percent: Optional[float] = Field(None, description="Daily change percentage")
    monthly_change_percent: Optional[float] = Field(None, description="Monthly change percentage")
    hourly_change_percent: Optional[float] = Field(None, description="Hourly change percentage")
    num_updates: int = Field(..., description="Number of price updates in the period")
    volume: float = Field(..., description="Simulated trading volume")


class CryptoTimeSeriesStats(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTCUSDT)")
    period_type: str = Field(..., description="Type of time period: 'hourly', 'daily', or 'monthly'")
    time_series: List[TimeSeriesDataPoint] = Field(..., description="Array of time-based price data")


# Response Models for Summary Data
class SymbolSummary(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTCUSDT)")
    current_price: float = Field(..., description="Current/latest price")
    daily_avg: float = Field(..., description="Daily average price")
    daily_min: float = Field(..., description="Daily minimum price")
    daily_max: float = Field(..., description="Daily maximum price")
    opening_price: float = Field(..., description="Opening price for the day")
    daily_change_percent: float = Field(..., description="Daily price change percentage")


class AllSymbolsSummary(BaseModel):
    symbols: List[SymbolSummary] = Field(..., description="List of summary data for all symbols")


class SingleSymbolSummary(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTCUSDT)")
    current_price: float = Field(..., description="Current/latest price")
    daily_avg: float = Field(..., description="Daily average price")
    daily_min: float = Field(..., description="Daily minimum price")
    daily_max: float = Field(..., description="Daily maximum price")
    opening_price: float = Field(..., description="Opening price for the day")
    daily_change_percent: float = Field(..., description="Daily price change percentage")
    num_updates: int = Field(..., description="Number of price updates")


# Error Response Models
class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Error message")


def query_ksqldb_pull(sql_query: str):
    """
    Execute a transient PULL query against ksqlDB (/query).
    Use for fetching current state without streaming.
    """
    url = f"{KSQLDB_URL}/query"
    payload = {"sql": sql_query, "properties": {"auto.offset.reset": "earliest"}}
    headers = {"Content-Type": "application/vnd.ksql.v1+json; charset=utf-8"}

    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        
        if "data" in data and "data" in data["data"]:
            return data["data"]["data"]
        return []
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error querying ksqlDB: {e}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing ksqlDB response: {e}")


def normalize_symbol(symbol: str) -> str:
    """Normalize symbol to uppercase with USDT suffix"""
    symbol_upper = symbol.upper()
    if not symbol_upper.endswith('USDT'):
        symbol_upper = f"{symbol_upper}USDT"
    return symbol_upper


@router.get("/daily/{symbol}", response_model=CryptoTimeSeriesStats, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_daily_stats(
        symbol: str,
        limit: Optional[int] = Query(30, description="Number of days to return")
):
    """Get daily statistics for a specific crypto symbol for the past month (30 days)"""
    symbol_upper = normalize_symbol(symbol)
    limit = min(max(limit or 30, 1), 200)
    
    sql_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_daily_stats 
    WHERE symbol = '{symbol_upper}'
    ORDER BY window_start DESC
    LIMIT {limit};
    """

    try:
        results = query_ksqldb_pull(sql_query)
        if not results:
            raise HTTPException(status_code=404, detail=f"Daily stats for '{symbol}' not found")
        
        # Data is already sorted by window_start DESC from the query
        sorted_results = results
        
        time_series = []
        for row in sorted_results:
            if len(row) >= 9:
                day_timestamp = row[1]
                day_str = datetime.fromtimestamp(day_timestamp / 1000).strftime('%Y-%m-%d')
                
                opening_price = row[8] if row[8] and row[8] > 0 else row[7]
                latest_price = row[7]
                daily_change = ((latest_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
                
                time_series.append(TimeSeriesDataPoint(
                    timestamp=day_timestamp,
                    period=day_str,
                    price=latest_price,
                    avg_price=row[6],
                    min_price=row[4],
                    max_price=row[5],
                    opening_price=opening_price,
                    daily_change_percent=round(daily_change, 2),
                    num_updates=row[3],
                    volume=row[6] * 10000  # Simulated volume based on avg price
                ))
        
        # Sort chronologically for chart display
        time_series.sort(key=lambda x: x.timestamp)
        
        return CryptoTimeSeriesStats(
            symbol=symbol_upper,
            period_type="daily",
            time_series=time_series
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily stats: {e}")


@router.get("/monthly/{symbol}", response_model=CryptoTimeSeriesStats, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_monthly_stats(
        symbol: str,
        limit: Optional[int] = Query(12, description="Number of months to return")
):
    """Get monthly statistics for a specific crypto symbol for the past 12 months"""
    symbol_upper = normalize_symbol(symbol)
    limit = min(max(limit or 12, 1), 200)
    
    sql_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_monthly_stats 
    WHERE symbol = '{symbol_upper}'
    ORDER BY window_start DESC
    LIMIT {limit};
    """

    try:
        results = query_ksqldb_pull(sql_query)
        if not results:
            raise HTTPException(status_code=404, detail=f"Monthly stats for '{symbol}' not found")
        
        # Data is already sorted by window_start DESC from the query
        sorted_results = results
        
        time_series = []
        for row in sorted_results:
            if len(row) >= 9:
                month_timestamp = row[1]
                month_str = datetime.fromtimestamp(month_timestamp / 1000).strftime('%Y-%m')
                
                opening_price = row[8] if row[8] and row[8] > 0 else row[7]
                latest_price = row[7]
                monthly_change = ((latest_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
                
                time_series.append(TimeSeriesDataPoint(
                    timestamp=month_timestamp,
                    period=month_str,
                    price=latest_price,
                    avg_price=row[6],
                    min_price=row[4],
                    max_price=row[5],
                    opening_price=opening_price,
                    monthly_change_percent=round(monthly_change, 2),
                    num_updates=row[3],
                    volume=row[6] * 100000  # Simulated volume based on avg price
                ))
        
        # Sort chronologically for chart display
        time_series.sort(key=lambda x: x.timestamp)
        
        return CryptoTimeSeriesStats(
            symbol=symbol_upper,
            period_type="monthly",
            time_series=time_series
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching monthly stats: {e}")


@router.get("/hourly/{symbol}", response_model=CryptoTimeSeriesStats, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_hourly_stats(
        symbol: str,
        limit: Optional[int] = Query(24, description="Number of hours to return")
):
    """Get hourly statistics for a specific crypto symbol for the past 24 hours"""
    symbol_upper = normalize_symbol(symbol)
    limit = min(max(limit or 24, 1), 200)
    
    sql_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_hourly_stats 
    WHERE symbol = '{symbol_upper}'
    ORDER BY window_start DESC
    LIMIT {limit};
    """

    try:
        results = query_ksqldb_pull(sql_query)
        if not results:
            raise HTTPException(status_code=404, detail=f"Hourly stats for '{symbol}' not found")
        
        # Data is already sorted by window_start DESC from the query
        sorted_results = results
        
        time_series = []
        for row in sorted_results:
            if len(row) >= 9:
                hour_timestamp = row[1]
                hour_str = datetime.fromtimestamp(hour_timestamp / 1000).strftime('%Y-%m-%d %H:00')
                
                opening_price = row[8] if row[8] and row[8] > 0 else row[7]
                latest_price = row[7]
                hourly_change = ((latest_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
                
                time_series.append(TimeSeriesDataPoint(
                    timestamp=hour_timestamp,
                    period=hour_str,
                    price=latest_price,
                    avg_price=row[6],
                    min_price=row[4],
                    max_price=row[5],
                    opening_price=opening_price,
                    hourly_change_percent=round(hourly_change, 2),
                    num_updates=row[3],
                    volume=row[6] * 1000  # Simulated volume based on avg price
                ))
        
        # Sort chronologically for chart display
        time_series.sort(key=lambda x: x.timestamp)
        
        return CryptoTimeSeriesStats(
            symbol=symbol_upper,
            period_type="hourly",
            time_series=time_series
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hourly stats: {e}")


@router.get("/summary", response_model=AllSymbolsSummary, responses={500: {"model": ErrorResponse}})
async def get_all_symbols_summary():
    """Get latest stats summary for all symbols with daily change percent"""
    sql_query = """
    SELECT symbol, latest_price, avg_price, min_price, max_price, opening_price
    FROM crypto_daily_stats 
    LIMIT 10;
    """

    try:
        results = query_ksqldb_pull(sql_query)

        summary = []
        for row in results:
            if len(row) >= 6:
                opening_price = row[5] if row[5] and row[5] > 0 else row[1]
                latest_price = row[1]
                daily_change_percent = ((latest_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
                
                summary.append(SymbolSummary(
                    symbol=row[0],
                    current_price=row[1],
                    daily_avg=row[2],
                    daily_min=row[3],
                    daily_max=row[4],
                    opening_price=opening_price,
                    daily_change_percent=round(daily_change_percent, 2)
                ))

        return AllSymbolsSummary(symbols=summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {e}")


@router.get("/summary/{symbol}", response_model=SingleSymbolSummary, responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def get_single_symbol_summary(symbol: str):
    """Get latest stats summary for a specific symbol with daily change percent"""
    symbol_upper = normalize_symbol(symbol)
    
    sql_query = f"""
    SELECT symbol, window_start, latest_price, avg_price, min_price, max_price, opening_price, num_updates
    FROM crypto_daily_stats 
    WHERE symbol = '{symbol_upper}'
    ORDER BY window_start DESC
    LIMIT 1;
    """

    try:
        results = query_ksqldb_pull(sql_query)

        if not results:
            raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found")
        
        # Get the first (and only) row since we limited to 1
        row = results[0]
        opening_price = row[6] if row[6] and row[6] > 0 else row[2]
        latest_price = row[2]
        daily_change_percent = ((latest_price - opening_price) / opening_price * 100) if opening_price > 0 else 0
        
        return SingleSymbolSummary(
            symbol=row[0],
            current_price=row[2],
            daily_avg=row[3],
            daily_min=row[4],
            daily_max=row[5],
            opening_price=opening_price,
            daily_change_percent=round(daily_change_percent, 2),
            num_updates=row[7] if len(row) > 7 else 0
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching symbol summary: {e}")
