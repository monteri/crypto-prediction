from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.crypto_analytics import router as analytics_router
from routes.crypto_alerts import router as alerts_router

app = FastAPI(
    title="Crypto Analytics API",
    version="0.1.0",
    description="API for crypto price analytics with Kafka and ksqlDB, including real-time alerting"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(analytics_router)
app.include_router(alerts_router)


@app.get("/health")
def health():
    return {"status": "ok"}