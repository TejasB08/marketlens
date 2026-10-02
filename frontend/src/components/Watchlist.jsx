import { useEffect, useState } from "react"
import { getWatchlist, removeFromWatchlist } from "../services/api"

function Watchlist({ onSelectTicker }) {
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
  }, [])

  const handleRemove = async (ticker) => {
    try {
      await removeFromWatchlist(ticker)
      setStocks(stocks.filter(s => s.ticker !== ticker))
    } catch (err) {
      console.error("Failed to remove from watchlist", err)
    }
  }

  if (loading) return <p>Loading watchlist...</p>
  if (error) return <p style={{ color: "red" }}>{error}</p>

  return (
    <div>
      <h2>Watchlist</h2>
      {stocks.length === 0 ? (
        <p>No stocks in your watchlist yet. Add some from a stock's detail page.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "12px" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid #ddd", textAlign: "left" }}>
              <th style={{ padding: "8px" }}>Ticker</th>
              <th style={{ padding: "8px" }}>Price</th>
              <th style={{ padding: "8px" }}>Change %</th>
              <th style={{ padding: "8px" }}>RSI</th>
              <th style={{ padding: "8px" }}></th>
            </tr>
          </thead>
          <tbody>
            {stocks.map(stock => (
              <tr key={stock.ticker} style={{ borderBottom: "1px solid #eee" }}>
                <td style={{ padding: "8px" }}>
                  <button
                    onClick={() => onSelectTicker(stock.ticker)}
                    style={{ background: "none", border: "none", color: "#0066cc", cursor: "pointer", padding: 0, font: "inherit", textDecoration: "underline" }}
                  >
                    {stock.ticker}
                  </button>
                </td>
                <td style={{ padding: "8px" }}>{stock.current_price}</td>
                <td style={{ padding: "8px", color: stock.change_percent >= 0 ? "green" : "red" }}>
                  {stock.change_percent}%
                </td>
                <td style={{ padding: "8px" }}>{stock.rsi}</td>
                <td style={{ padding: "8px" }}>
                  <button
                    onClick={() => handleRemove(stock.ticker)}
                    style={{ color: "red", border: "none", background: "none", cursor: "pointer" }}
                  >
                    Remove
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

export default Watchlist