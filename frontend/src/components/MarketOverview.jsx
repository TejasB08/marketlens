import { useEffect, useState } from "react"
import { getMarketOverview } from "../services/api"

function MarketOverview() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMarketOverview()
      .then(result => {
        setData(result)
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch market overview", err)
        setLoading(false)
      })
  }, [])

  if (loading) return <p>Loading market data...</p>
  if (!data) return <p>Could not load market data.</p>

  return (
    <div>
      <h2>Market Overview</h2>
      <div style={{ display: "flex", gap: "20px" }}>
        {Object.entries(data).map(([name, values]) => (
          <div key={name} style={{ border: "1px solid #ccc", padding: "16px", borderRadius: "8px" }}>
            <h3>{name}</h3>
            <p>Price: ₹{values.current_price}</p>
            <p style={{ color: values.change_percent < 0 ? "red" : "green" }}>
              {values.change_percent}%
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default MarketOverview