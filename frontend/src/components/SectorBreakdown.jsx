import { useEffect, useState } from "react"
import { getSectorBreakdown } from "../services/api"

function SectorBreakdown() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSectorBreakdown()
      .then(result => {
        setData(result)
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch sector breakdown", err)
        setLoading(false)
      })
  }, [])

  if (loading) return <p>Loading sector breakdown...</p>
  if (!data) return <p>Could not load sector breakdown.</p>

  return (
    <div>
      <h3>Sector Breakdown</h3>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "12px" }}>
        {data.map(sector => (
          <div
            key={sector.sector}
            style={{ border: "1px solid #ccc", padding: "12px 16px", borderRadius: "8px", minWidth: "160px" }}
          >
            <strong>{sector.sector}</strong>
            <p style={{ color: sector.avg_change_percent < 0 ? "red" : "green" }}>
              {sector.avg_change_percent}%
            </p>
            <p style={{ fontSize: "12px", color: "#888" }}>{sector.stock_count} stocks</p>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SectorBreakdown