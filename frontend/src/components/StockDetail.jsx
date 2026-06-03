import { useEffect, useState } from "react"
import { getQuote } from "../services/api"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts"
import { getHistory } from "../services/api"

function StockDetail({ ticker }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState(null)

  useEffect(() => {
    if (!ticker) return

    setLoading(true)
    setError(null)
    setData(null)
    setHistory(null)

    getQuote(ticker)
      .then(result => {
        setData(result)
        setLoading(false)
        return getHistory(ticker)
      })
      .then(histResult => {
        setHistory(histResult)
      })
      .catch(err => {
        setError("Could not find stock. Please check the ticker symbol.")
        setLoading(false)
      })
  }, [ticker])

  if (loading) return <p>Loading {ticker}...</p>
  if (error) return <p style={{ color: "red" }}>{error}</p>
  if (!data) return null

  return (
    <div>
      {/* Price Section */}
      <div style={{ marginBottom: "24px" }}>
        <h2>{data.ticker}</h2>
        <h3 style={{ fontSize: "32px", margin: "8px 0" }}>₹{data.current_price}</h3>
        <p style={{ color: data.change_percent < 0 ? "red" : "green", fontSize: "18px" }}>
          {data.change_percent}% today
        </p>
        <p style={{ color: "#666" }}>Volume: {data.volume?.toLocaleString()}</p>
      </div>

      {/* Indicators Section */}
      <div>
        <h3>Technical Indicators</h3>
        <div style={{ display: "flex", gap: "16px", flexWrap: "wrap" }}>

          <div style={{ border: "1px solid #ccc", padding: "16px", borderRadius: "8px", minWidth: "120px" }}>
            <p style={{ color: "#666", margin: "0" }}>RSI</p>
            <p style={{ fontSize: "24px", margin: "4px 0", color: data.indicators.rsi < 30 ? "green" : data.indicators.rsi > 70 ? "red" : "black" }}>
              {data.indicators.rsi}
            </p>
            <p style={{ fontSize: "12px", color: "#666" }}>
              {data.indicators.rsi < 30 ? "Oversold" : data.indicators.rsi > 70 ? "Overbought" : "Neutral"}
            </p>
          </div>

          <div style={{ border: "1px solid #ccc", padding: "16px", borderRadius: "8px", minWidth: "120px" }}>
            <p style={{ color: "#666", margin: "0" }}>EMA 20</p>
            <p style={{ fontSize: "24px", margin: "4px 0" }}>{data.indicators.ema20}</p>
          </div>

          <div style={{ border: "1px solid #ccc", padding: "16px", borderRadius: "8px", minWidth: "120px" }}>
            <p style={{ color: "#666", margin: "0" }}>EMA 50</p>
            <p style={{ fontSize: "24px", margin: "4px 0" }}>{data.indicators.ema50}</p>
          </div>

          <div style={{ border: "1px solid #ccc", padding: "16px", borderRadius: "8px", minWidth: "120px" }}>
            <p style={{ color: "#666", margin: "0" }}>MACD</p>
            <p style={{ fontSize: "24px", margin: "4px 0", color: data.indicators.macd > data.indicators.macd_signal ? "green" : "red" }}>
              {data.indicators.macd}
            </p>
            <p style={{ fontSize: "12px", color: "#666" }}>
              {data.indicators.macd > data.indicators.macd_signal ? "Bullish" : "Bearish"}
            </p>
          </div>
          {/* Chart Section */}
{history && (
  <div style={{ marginTop: "32px" }}>
    <h3>6 Month Price Chart</h3>
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={history}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 11 }}
          tickFormatter={(val) => val.slice(5)}
        />
        <YAxis
          domain={["auto", "auto"]}
          tick={{ fontSize: 11 }}
          tickFormatter={(val) => `₹${val}`}
        />
        <Tooltip
          formatter={(value) => [`₹${value}`, "Close"]}
          labelFormatter={(label) => `Date: ${label}`}
        />
        <Line
          type="monotone"
          dataKey="close"
          stroke="#0066cc"
          dot={false}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
)}

        </div>
      </div>
    </div>
  )
}

export default StockDetail