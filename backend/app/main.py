from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.quote import router as quote_router

app = FastAPI(
    title="MarketLens API",
    description="Stock research platform for Indian retail traders",
    version="1.0.0"
)

# CORS middleware - allows React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(quote_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "MarketLens API is running"}