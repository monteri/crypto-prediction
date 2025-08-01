from fastapi import FastAPI
from routes import router
from routes.crypto_analytics import router as analytics_router

app = FastAPI(
    title="Crypto Analytics API",
    version="0.1.0",
    description="API for crypto price analytics with Kafka and ksqlDB"
)

app.include_router(router)
app.include_router(analytics_router)


@app.get("/health")
def health():
    return {"status": "ok"}