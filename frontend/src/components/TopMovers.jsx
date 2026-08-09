import { useEffect, useState } from "react"
import { getTopMovers } from "../services/api"

function TopMovers() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getTopMovers()
      .then(result => {
        setData(result)
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch top movers", err)
        setLoading(false)
      })
  }, [])

  if (loading) return <p>Loading top movers...</p>
  if (!data) return <p>Could not load top movers.</p>

  return (
    <div>
      <h3>Top Movers</h3>
      <div style={{ display: "flex", gap: "20px" }}>
        <div style={{ flex: 1 }}>
          <h4>Gainers</h4>
          {data.gainers.map(stock => (
            <div
              key={stock.ticker}
              style={{ border: "1px solid #ccc", padding: "8px 12px", borderRadius: "6px", marginBottom: "6px" }}
            >
              <span>{stock.ticker}</span>{" "}
              <span style={{ color: "green" }}>{stock.change_percent}%</span>
            </div>
          ))}
        </div>
        <div style={{ flex: 1 }}>
          <h4>Losers</h4>
          {data.losers.map(stock => (
            <div
              key={stock.ticker}
              style={{ border: "1px solid #ccc", padding: "8px 12px", borderRadius: "6px", marginBottom: "6px" }}
            >
              <span>{stock.ticker}</span>{" "}
              <span style={{ color: "red" }}>{stock.change_percent}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default TopMovers