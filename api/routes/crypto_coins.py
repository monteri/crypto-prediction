from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


SAMPLE_CRYPTO_DATA = [
    {
        "id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "current_price": 45000.00,
        "market_cap": 850000000000,
        "volume_24h": 25000000000,
        "price_change_24h": 2.5,
        "price_change_percentage_24h": 5.8,
        "last_updated": "2024-01-15T10:30:00Z"
    },
    {
        "id": "ethereum",
        "symbol": "ETH",
        "name": "Ethereum",
        "current_price": 3200.00,
        "market_cap": 380000000000,
        "volume_24h": 15000000000,
        "price_change_24h": -150.00,
        "price_change_percentage_24h": -4.5,
        "last_updated": "2024-01-15T10:30:00Z"
    },
    {
        "id": "binancecoin",
        "symbol": "BNB",
        "name": "BNB",
        "current_price": 320.00,
        "market_cap": 48000000000,
        "volume_24h": 1200000000,
        "price_change_24h": 5.00,
        "price_change_percentage_24h": 1.6,
        "last_updated": "2024-01-15T10:30:00Z"
    },
    {
        "id": "cardano",
        "symbol": "ADA",
        "name": "Cardano",
        "current_price": 0.85,
        "market_cap": 30000000000,
        "volume_24h": 800000000,
        "price_change_24h": 0.02,
        "price_change_percentage_24h": 2.4,
        "last_updated": "2024-01-15T10:30:00Z"
    },
    {
        "id": "solana",
        "symbol": "SOL",
        "name": "Solana",
        "current_price": 95.00,
        "market_cap": 41000000000,
        "volume_24h": 2000000000,
        "price_change_24h": -3.00,
        "price_change_percentage_24h": -3.1,
        "last_updated": "2024-01-15T10:30:00Z"
    }
]


def generate_hourly_historical_data(current_price: float, symbol: str) -> List[Dict[str, Any]]:
    """Generate 24 hours of historical price data"""
    historical_data = []
    base_price = current_price * 0.95  # Start slightly lower than current price
    
    for i in range(24):
        # Generate timestamp for each hour (going backwards from current time)
        timestamp = datetime.now() - timedelta(hours=23-i)
        
        # Add some realistic price variation
        variation = random.uniform(-0.02, 0.02)  # ±2% variation
        price = base_price * (1 + variation)
        
        # Add some volume data
        volume = random.uniform(0.8, 1.2) * (current_price * 1000)  # Rough volume estimate
        
        historical_data.append({
            "timestamp": timestamp.isoformat(),
            "price": round(price, 2),
            "volume": round(volume, 2)
        })
        
        base_price = price  # Use current price as base for next iteration
    
    return historical_data


def generate_daily_historical_data(current_price: float, symbol: str) -> List[Dict[str, Any]]:
    """Generate 30 days of historical price data"""
    historical_data = []
    base_price = current_price * 0.9  # Start lower than current price
    
    for i in range(30):
        # Generate timestamp for each day (going backwards from current time)
        timestamp = datetime.now() - timedelta(days=29-i)
        
        # Add some realistic price variation with trend
        trend = (i / 30) * 0.1  # Gradual upward trend
        variation = random.uniform(-0.05, 0.05)  # ±5% daily variation
        price = base_price * (1 + trend + variation)
        
        # Add some volume data
        volume = random.uniform(0.7, 1.3) * (current_price * 10000)  # Daily volume estimate
        
        historical_data.append({
            "timestamp": timestamp.isoformat(),
            "price": round(price, 2),
            "volume": round(volume, 2),
            "high": round(price * random.uniform(1.02, 1.08), 2),  # Daily high
            "low": round(price * random.uniform(0.92, 0.98), 2)   # Daily low
        })
        
        base_price = price  # Use current price as base for next iteration
    
    return historical_data


@router.get("/crypto", response_model=List[Dict[str, Any]])
async def get_crypto_list():
    try:

        crypto_list = []
        for coin in SAMPLE_CRYPTO_DATA:
            crypto_list.append({
                "id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "current_price": coin["current_price"],
                "price_change_percentage_24h": coin["price_change_percentage_24h"],
                "market_cap": coin["market_cap"]
            })
        
        return crypto_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching crypto list: {str(e)}")


@router.get("/crypto/{coin_id}", response_model=Dict[str, Any])
async def get_crypto_detail(coin_id: str):
    try:

        coin = next((c for c in SAMPLE_CRYPTO_DATA if c["id"].lower() == coin_id.lower()), None)
        
        if not coin:
            raise HTTPException(status_code=404, detail=f"Crypto coin '{coin_id}' not found")
        
        # Generate historical data
        hourly_data = generate_hourly_historical_data(coin["current_price"], coin["symbol"])
        daily_data = generate_daily_historical_data(coin["current_price"], coin["symbol"])

        return {
            "id": coin["id"],
            "symbol": coin["symbol"],
            "name": coin["name"],
            "current_price": coin["current_price"],
            "market_cap": coin["market_cap"],
            "volume_24h": coin["volume_24h"],
            "price_change_24h": coin["price_change_24h"],
            "price_change_percentage_24h": coin["price_change_percentage_24h"],
            "last_updated": coin["last_updated"],
            "additional_info": {
                "circulating_supply": "19,000,000" if coin["symbol"] == "BTC" else "120,000,000" if coin["symbol"] == "ETH" else "N/A",
                "max_supply": "21,000,000" if coin["symbol"] == "BTC" else "Unlimited" if coin["symbol"] == "ETH" else "N/A",
                "all_time_high": coin["current_price"] * 1.5,
                "all_time_low": coin["current_price"] * 0.3
            },
            "historical_data": {
                "hourly": hourly_data,
                "daily": daily_data
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching crypto details: {str(e)}") 