import { useEffect, useState } from "react"
import { getMarketNews } from "../services/api"

function MarketNews() {
  const [news, setNews] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getMarketNews(10)
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
      <div style={{ border: "1px solid #ccc", borderRadius: "8px", overflow: "hidden" }}>
        {news.map((item, idx) => (
          <a
            key={idx}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              display: "block",
              padding: "10px 14px",
              borderBottom: idx < news.length - 1 ? "1px solid #eee" : "none",
              textDecoration: "none",
              color: "#222"
            }}
          >
            <div style={{ fontSize: "15px" }}>{item.title}</div>
            {(item.publisher || item.published) && (
              <div style={{ fontSize: "12px", color: "#888", marginTop: "2px" }}>
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