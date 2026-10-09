import { useEffect, useState } from "react"
import { getWatchlist, removeFromWatchlist } from "../services/api"

function Watchlist({ onSelectTicker, refreshTrigger }) {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const loadWatchlist = () => {
    setLoading(true)
    getWatchlist()
      .then(result => {
        setStocks(result.tickers)
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch watchlist", err)
        setError("Could not load watchlist.")
        setLoading(false)
      })
  }

  useEffect(() => {
    loadWatchlist()
  }, [refreshTrigger]) // Refresh when the refreshTrigger prop changes

  const handleRemove = async (ticker) => {
    try {
      await removeFromWatchlist(ticker)
      setStocks(stocks.filter(s => s.ticker !== ticker))
    } catch (err) {
      console.error("Failed to remove from watchlist", err)
    }
  }

  return (
    <div>
      {/* Header bar with the "+" placeholder (no action yet) */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "12px 20px",
          borderBottom: "1px solid #ccc"
        }}
      >
        <h2 style={{ margin: 0, fontSize: "18px" }}>Watchlist</h2>
        <button
          aria-label="Add to watchlist"
          style={{ background: "none", border: "none", fontSize: "22px", lineHeight: 1, cursor: "pointer" }}
        >
          +
        </button>
      </div>

      {loading && <p style={{ padding: "0 20px" }}>Loading watchlist...</p>}
      {error && <p style={{ padding: "0 20px", color: "red" }}>{error}</p>}

      {!loading && !error && stocks.length === 0 && (
        <p style={{ padding: "0 20px", color: "#666", fontSize: "14px" }}>
          No stocks yet. Add some from a stock's page.
        </p>
      )}

      {!loading && !error && stocks.map(stock => (
        <div
          key={stock.ticker}
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: "8px",
            padding: "10px 20px",
            borderBottom: "1px solid #eee"
          }}
        >
          <button
            onClick={() => onSelectTicker(stock.ticker)}
            style={{ background: "none", border: "none", color: "#0066cc", cursor: "pointer", padding: 0, font: "inherit", textAlign: "left" }}
          >
            {stock.ticker}
          </button>

          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <div style={{ textAlign: "right" }}>
              <div>{stock.current_price}</div>
              <div style={{ fontSize: "12px", color: stock.change_percent >= 0 ? "green" : "red" }}>
                {stock.change_percent}%
              </div>
            </div>
            <button
              onClick={() => handleRemove(stock.ticker)}
              aria-label={`Remove ${stock.ticker}`}
              style={{ color: "red", border: "none", background: "none", cursor: "pointer", fontSize: "16px" }}
            >
              ×
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

export default Watchlist