from fastapi import FastAPI
from routes.crypto_coins import router as coins_router
from routes.crypto_analytics import router as analytics_router

app = FastAPI(
    title="Crypto Analytics API",
    version="0.1.0",
    description="API for crypto price analytics with Kafka and ksqlDB"
)

app.include_router(coins_router)
app.include_router(analytics_router)


@app.get("/health")
def health():
    return {"status": "ok"}