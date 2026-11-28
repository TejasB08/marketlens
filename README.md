# MarketLens — Indian Stock Market Research Platform

MarketLens is a full-stack stock market research platform built to help retail traders explore Indian equities through market data, technical analysis, stock screening, and financial news.

The project combines a **React frontend**, a **FastAPI backend**, and Python-based data analysis to provide a modular foundation for stock market research and future machine learning integrations.

## Features

- **Market Overview:** Explore key Indian market indices and market movements.
- **Stock Analysis:** Retrieve stock quotes and analyze historical price movements.
- **Technical Indicators:** Calculate RSI, EMA 20, EMA 50, and MACD.
- **Interactive Charts:** Visualize historical stock price data.
- **Stock Screener:** Filter stocks using technical indicators and configurable screening conditions.
- **Market News:** Retrieve and display financial news headlines.
- **Watchlist:** Track selected stocks through the application.
- **ML Experiments:** Explore machine learning approaches to next-day stock price direction prediction.

## Tech Stack

| Category           | Technologies                             |
| ------------------ | ---------------------------------------- |
| Frontend           | React, Vite, JavaScript, Axios, Recharts |
| Backend            | Python, FastAPI, Pydantic                |
| Data Analysis      | Pandas, NumPy                            |
| Technical Analysis | `ta`                                     |
| Machine Learning   | scikit-learn                             |
| Market Data        | `yfinance`                               |
| Development Tools  | Git, GitHub, VS Code                     |

## Architecture

MarketLens separates its frontend, API layer, business logic, data retrieval, and analytics to keep the application maintainable and extensible.

```text
React Frontend
      |
      | HTTP / REST API
      v
FastAPI Backend
      |
      v
API Routes
      |
      v
Service Layer
      |
      +-------------------+
      |                   |
      v                   v
Data Access          Analytics
      |                   |
      v                   v
Market Data          Technical Indicators
Provider             and Screening Logic
      |
      v
Normalized Data
      |
      v
API Response
      |
      v
React Frontend
```

Market data retrieval is isolated within dedicated modules, keeping provider-specific logic separate from the core application and simplifying potential future integrations.

## Project Structure

```text
marketlens/
├── backend/
│   └── app/
│       ├── analytics/       # Technical indicators
│       ├── api/
│       │   └── routes/      # Quote, screener, news, watchlist APIs
│       ├── data/            # Data retrieval and storage modules
│       ├── schemas/         # API request and response schemas
│       ├── services/        # Application and business logic
│       ├── utils/           # Caching and logging
│       └── main.py          # FastAPI entry point
│
├── frontend/
│   └── src/
│       ├── assets/
│       ├── components/      # Dashboard and feature components
│       ├── pages/           # Page-level components
│       ├── services/
│       │   └── api.js       # Backend API integration
│       ├── App.jsx
│       ├── App.css
│       ├── index.css
│       └── main.jsx
│
└── README.md
```

## API Overview

The FastAPI backend exposes REST endpoints for the application's main features.

| Module        | Responsibility                                      |
| ------------- | --------------------------------------------------- |
| Quote API     | Stock quotes and related market data                |
| Screener API  | Stock screening and predefined screening conditions |
| News API      | Market news retrieval                               |
| Watchlist API | Watchlist operations                                |

Interactive API documentation is available at `/docs` when the backend is running locally.

## Getting Started

### Prerequisites

- Python 3.13 (recommended for the backend dependencies)
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/TejasB08/marketlens.git
cd marketlens
```

### 2. Start the backend

From the project root, create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the project dependencies from the root `requirements.txt`:

```bash
pip install -r requirements.txt
```

Navigate to the backend directory:

```bash
cd backend
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The backend will typically be available at:

- API server: `http://localhost:8000`
- Interactive API documentation: `http://localhost:8000/docs`

#### Optional PostgreSQL connection check

From `backend`, copy `.env.example` to `.env` if `.env` does not already exist.
Edit `.env` locally with your PostgreSQL settings. For the MarketLens local instance,
use `localhost`, `5432`, `marketlens`, and `marketlens_user` for `DB_HOST`, `DB_PORT`,
`DB_NAME`, and `DB_USER`. Set `DB_PASSWORD` to the database user's password.

Use UTF-8 and one `KEY=value` per line. Put comments on separate lines. Single
or double quotes can preserve leading or trailing spaces. Values are literal,
including `#` and `$`, with no interpolation or escape processing. Git ignores
`.env`. Set the same five variables in the backend process environment for
deployment. Each environment variable takes precedence over its file value.

With the backend virtual environment active, run from `backend`:

```powershell
python -m app.data.db
```

`PostgreSQL connection verified.` and exit code `0` mean the check authenticated
and ran `SELECT 1`. Missing settings and failed connections return exit code `1`
with a message that omits credentials. The check does not create tables. To test a
failed connection, temporarily override `DB_PORT` in the shell with an unused
local port.

#### Apply database migrations

After installing the backend requirements and verifying the PostgreSQL connection,
run from `backend` with the virtual environment active.

```powershell
python -m alembic upgrade head
python -m alembic current
```

Alembic uses the same database settings as the connection check. To review the
initial SQL without connecting to a database, run `python -m alembic upgrade head --sql`.

For database integration tests, create a separate PostgreSQL database with an empty
public schema and a name beginning with `marketlens_test_`. Grant its test role
permission to create tables in that schema. Set `MARKETLENS_TEST_DB_HOST`,
`MARKETLENS_TEST_DB_PORT`, `MARKETLENS_TEST_DB_NAME`, `MARKETLENS_TEST_DB_USER`, and
`MARKETLENS_TEST_DB_PASSWORD` in the test shell. Enter the password through a masked
prompt or inject it from a secret store. The suite requires explicit test settings,
checks the connected database name, and rolls back its migration and test data.

```powershell
python -m unittest discover -s tests -v
```

### 3. Start the frontend

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL provided by Vite, typically `http://localhost:5173`.

Ensure that the frontend API configuration points to the running backend and that any required CORS settings are configured.

### Test Google sign-in locally

In Google Cloud Console, configure Google Auth Platform branding, audience, and
the sign-in scopes `openid`, `email`, and `profile`. If the app is external and in
Testing, add the Google accounts you plan to use as test users. Create an OAuth
client with application type **Web application** and register this exact authorized
redirect URI for the Vite development server.

```text
http://localhost:5173/api/v1/auth/google/callback
```

Set these values in the backend process environment or edit `backend/.env` locally.

```dotenv
AUTH_PUBLIC_ORIGIN=http://localhost:5173
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
```

Apply the database migration and start FastAPI and Vite. Use `localhost` throughout
the browser flow so the callback receives the same host-only cookie.

1. Visit `http://localhost:5173/api/v1/auth/session` to confirm the guest response
   is `{"user":null}`.
2. Visit `http://localhost:5173/api/v1/auth/google/login` and finish Google's sign-in.
   A successful callback redirects to `/`. A failed callback redirects to `/?auth=failed`.
   React sign-in controls are a later milestone.
3. Visit `/api/v1/auth/session` on the same origin and verify that the response
   contains only the user ID and profile fields. In DevTools, confirm the session
   cookie is HttpOnly and SameSite=Lax.
4. In the same origin's browser console, first run
   `await fetch('/api/v1/auth/logout', {method: 'POST'}).then(r => r.status)`.
   For a signed-in user this returns `403` without the CSRF header. Then run:

   ```js
   const csrf = document.cookie.match(/(?:^|;\s*)marketlens_csrf=([^;]+)/)?.[1]
   await fetch('/api/v1/auth/logout', {
     method: 'POST',
     headers: {'X-CSRF-Token': csrf},
   }).then(r => r.status)
   ```

   Expect `204`, then confirm `/api/v1/auth/session` returns the guest response.

In production, use a separate Google OAuth web client, set `AUTH_PUBLIC_ORIGIN`
to the HTTPS site origin, register that origin's `/api/v1/auth/google/callback`,
and forward `/api` to FastAPI on the same browser origin. HTTPS enables Secure
cookies with the `__Host-` prefix. For authenticated writes, send the readable
`__Host-marketlens_csrf` cookie value in `X-CSRF-Token`; the browser sends the
HttpOnly session cookie separately. Configure the reverse proxy and any request
tracing to omit auth query strings, cookie headers, and OAuth request bodies.
Leave Vite proxy debug tracing disabled during OAuth testing.

## Market Data Integration

MarketLens currently uses `yfinance` for market data retrieval. Data fetching is isolated within dedicated modules to keep provider-specific logic separate from the core application and simplify potential future integrations.

## Machine Learning Experiments

MarketLens also serves as a foundation for experimenting with machine learning on financial time-series data.

The experimental workflow includes:

1. Preparing historical stock data.
2. Engineering features from returns, moving averages, momentum, and volatility.
3. Creating labels for next-day price direction.
4. Training and evaluating classification models, including Random Forest.
5. Using chronological train/test splits to evaluate models on later observations.

**Important:** These experiments are educational and exploratory. Historical model performance does not establish a reliable trading edge, and predictions should not be treated as investment advice.

## Engineering Considerations

- **Modular design:** Separate API routes, services, data access, and analytics.
- **Caching:** Reduce unnecessary repeated requests for market data.
- **Data validation:** Use structured schemas for API responses.
- **Extensibility:** Keep external data retrieval isolated from application logic.
- **Time-series evaluation:** Account for chronological ordering when evaluating predictive models.

## Roadmap

- [x] Implement the FastAPI backend and React frontend.
- [x] Integrate stock quotes and technical indicators.
- [x] Build market overview and historical chart components.
- [x] Implement technical stock screening.
- [x] Implement the market news feed.
- [x] Implement watchlist functionality.
- [ ] Integrate a database for persistent application data.
- [ ] Implement user authentication and account management.
- [ ] Add automated tests and improve error handling.
- [ ] Configure and deploy the frontend and backend.
- [ ] Add application screenshots and a live demo.

## Limitations

- Market data availability and quality depend on the external provider.
- Some features may require additional configuration before deployment.
- ML experiments are not validated financial forecasting systems.
- Database-backed persistence and user authentication are planned enhancements.

## Author

**Tejas Barde**

- GitHub: [@TejasB08](https://github.com/TejasB08)
- Project: [MarketLens](https://github.com/TejasB08/marketlens)

---

