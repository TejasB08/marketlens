# MarketLens
A full-stack stock research platform for Indian retail traders built with FastAPI, React, and Machine Learning.

> Not a trading app. Not a broker. A place where traders research stocks before making decisions.

## Live Demo
Coming soon after deployment.

## Features
- Live stock quotes with price and volume data
- Technical indicators — RSI, EMA20, EMA50, MACD
- 6 month interactive price chart
- Market overview — NIFTY 50, BANK NIFTY, SENSEX
- Stock screener — filter stocks by indicator conditions *(coming soon)*
- ML-based trading signals — Bullish / Bearish with confidence *(coming soon)*

## Tech Stack
- Backend - FastAPI, Python
- Data yfinance
- Analytics - ta (Technical Analysis library) 
- Frontend - React, Recharts
- ML -  scikit-learn, Random Forest *(coming soon)*

## Project Structure
marketlens/
├── backend/
│   ├── app/
│   │   ├── analytics/
│   │   │   └── indicators.py       → RSI, EMA, MACD calculations
│   │   ├── api/
│   │   │   └── routes/
│   │   │       └── quote.py        → API endpoints
│   │   ├── data/
│   │   │   └── fetch.py            → yfinance data layer
│   │   ├── schemas/
│   │   │   └── quote_schema.py     → Pydantic response models
│   │   ├── services/
│   │   │   └── market_service.py   → Business logic
│   │   ├── utils/
│   │   │   └── logger.py
│   │   └── main.py                 → FastAPI app entry point
│   └── requirements.txt
└── frontend/
    └── src/
        ├── components/
        │   ├── MarketOverview.jsx  → NIFTY, BANKNIFTY, SENSEX cards
        │   ├── SearchBar.jsx       → Stock search input
        │   └── StockDetail.jsx     → Price, indicators, chart
        ├── pages/
        ├── services/
        │   └── api.js              → API call functions
        └── App.jsx                 → Root component

## API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/quote/{ticker}` | Live price + technical indicators |
| GET | `/api/v1/quote/{ticker}/history` | 6 month price history for chart |
| GET | `/api/v1/market/overview` | NIFTY, BANKNIFTY, SENSEX overview |

## Getting Started
### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API runs at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App runs at `http://localhost:5173`

## Architecture
React Frontend
↓
FastAPI Backend
↓
Service Layer (business logic)
↓
Data Layer + Analytics Layer
↓
yfinance (market data)

## Roadmap
- [x] Phase 1 — Live quotes, indicators, price chart
- [ ] Phase 2 — Stock screener
- [ ] Phase 3 — ML trading signals
- [ ] Phase 4 — News sentiment analysis
- [ ] Phase 5 — Deployment and polish

## Author
Built by Tejas Barde as a portfolio project.