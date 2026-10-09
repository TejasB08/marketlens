import { useEffect, useState } from "react"
import { getMarketNews } from "../services/api"

function MarketNews() {
  const [news, setNews] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 12 = four full rows of three. The page scrolls to show them all.
    getMarketNews(12)
      .then(result => {
        setNews(result.results)
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch market news", err)
        setLoading(false)
      })
  }, [])

  if (loading) return <p>Loading news...</p>
  if (!news || news.length === 0) return <p>No market news available right now.</p>

  return (
    <div>
      <h3>Market News</h3>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(3, 1fr)",
          gap: "16px"
        }}
      >
        {news.map((item, idx) => (
          <a
            key={idx}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "block",
              padding: "12px 14px",
              border: "1px solid #ccc",
              borderRadius: "8px",
              textDecoration: "none",
              color: "#222"
            }}
          >
            <div style={{ fontSize: "15px" }}>{item.title}</div>
            {(item.publisher || item.published) && (
              <div style={{ fontSize: "12px", color: "#888", marginTop: "6px" }}>
                {item.publisher}
                {item.publisher && item.published ? " · " : ""}
                {item.published}
              </div>
            )}
          </a>
        ))}
      </div>
    </div>
  )
}

export default MarketNews