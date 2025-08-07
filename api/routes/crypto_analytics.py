import os
import json
import requests
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv

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


@router.get("/daily/{symbol}", response_model=List[CryptoStats])
async def get_daily_stats(
        symbol: str,
        limit: Optional[int] = Query(30, description="Number of days to return")
):
    """Get daily statistics for a specific crypto symbol"""
    # Convert symbol to uppercase and append USDT if not present
    symbol_upper = symbol.upper()
    if not symbol_upper.endswith('USDT'):
        symbol_upper = f"{symbol_upper}USDT"
    
    sql_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_daily_stats 
    WHERE symbol = '{symbol_upper}'
    LIMIT {limit};
    """

    try:
        results = query_ksqldb(sql_query)

        stats = []
        for row in results:
            if len(row) >= 9:
                # Convert window_start timestamp to date string
                from datetime import datetime
                date_str = datetime.fromtimestamp(row[1] / 1000).strftime('%Y-%m-%d')
                
                stats.append(CryptoStats(
                    symbol=row[0],
                    period=date_str,
                    window_start=row[1],
                    window_end=row[2],
                    num_updates=row[3],
                    min_price=row[4],
                    max_price=row[5],
                    avg_price=row[6],
                    latest_price=row[7],
                    opening_price=row[8]
                ))

        # Sort by window_start in descending order in Python
        stats.sort(key=lambda x: x.window_start, reverse=True)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching daily stats: {e}")


@router.get("/monthly/{symbol}", response_model=List[CryptoStats])
async def get_monthly_stats(
        symbol: str,
        limit: Optional[int] = Query(12, description="Number of months to return")
):
    """Get monthly statistics for a specific crypto symbol"""
    # Convert symbol to uppercase and append USDT if not present
    symbol_upper = symbol.upper()
    if not symbol_upper.endswith('USDT'):
        symbol_upper = f"{symbol_upper}USDT"
    
    sql_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_monthly_stats 
    WHERE symbol = '{symbol_upper}'
    LIMIT {limit};
    """

    try:
        results = query_ksqldb(sql_query)

        stats = []
        for row in results:
            if len(row) >= 9:
                # Convert window_start timestamp to month string
                from datetime import datetime
                month_str = datetime.fromtimestamp(row[1] / 1000).strftime('%Y-%m')
                
                stats.append(CryptoStats(
                    symbol=row[0],
                    period=month_str,
                    window_start=row[1],
                    window_end=row[2],
                    num_updates=row[3],
                    min_price=row[4],
                    max_price=row[5],
                    avg_price=row[6],
                    latest_price=row[7],
                    opening_price=row[8]
                ))

        # Sort by window_start in descending order in Python
        stats.sort(key=lambda x: x.window_start, reverse=True)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching monthly stats: {e}")


@router.get("/hourly/{symbol}", response_model=List[CryptoStats])
async def get_hourly_stats(
        symbol: str,
        limit: Optional[int] = Query(24, description="Number of hours to return")
):
    """Get hourly statistics for a specific crypto symbol"""
    # Convert symbol to uppercase and append USDT if not present
    symbol_upper = symbol.upper()
    if not symbol_upper.endswith('USDT'):
        symbol_upper = f"{symbol_upper}USDT"
    
    sql_query = f"""
    SELECT symbol, window_start, window_end, num_updates, 
           min_price, max_price, avg_price, latest_price, opening_price
    FROM crypto_hourly_stats 
    WHERE symbol = '{symbol_upper}'
    LIMIT {limit};
    """

    try:
        results = query_ksqldb(sql_query)

        stats = []
        for row in results:
            if len(row) >= 9:
                # Convert window_start timestamp to hour string
                from datetime import datetime
                hour_str = datetime.fromtimestamp(row[1] / 1000).strftime('%Y-%m-%d %H:00')
                
                stats.append(CryptoStats(
                    symbol=row[0],
                    period=hour_str,
                    window_start=row[1],
                    window_end=row[2],
                    num_updates=row[3],
                    min_price=row[4],
                    max_price=row[5],
                    avg_price=row[6],
                    latest_price=row[7],
                    opening_price=row[8]
                ))

        # Sort by window_start in descending order in Python
        stats.sort(key=lambda x: x.window_start, reverse=True)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hourly stats: {e}")


@router.get("/summary")
async def get_all_symbols_summary():
    """Get latest stats summary for all symbols"""
    sql_query = """
    SELECT symbol, latest_price, avg_price, min_price, max_price
    FROM crypto_daily_stats 
    LIMIT 10;
    """

    try:
        results = query_ksqldb(sql_query)

        summary = []
        for row in results:
            if len(row) >= 5:
                summary.append({
                    "symbol": row[0],
                    "current_price": row[1],
                    "daily_avg": row[2],
                    "daily_min": row[3],
                    "daily_max": row[4]
                })

        return {"symbols": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching summary: {e}")
