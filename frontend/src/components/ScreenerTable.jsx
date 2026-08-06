function ScreenerTable({ stocks, onSelectTicker }) {
  if (stocks.length === 0) {
    return <p>No stocks match this screen right now.</p>
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "12px" }}>
      <thead>
        <tr style={{ borderBottom: "2px solid #ddd", textAlign: "left" }}>
          <th style={{ padding: "8px" }}>Ticker</th>
          <th style={{ padding: "8px" }}>Price</th>
          <th style={{ padding: "8px" }}>Change %</th>
          <th style={{ padding: "8px" }}>RSI</th>
          <th style={{ padding: "8px" }}>EMA20</th>
          <th style={{ padding: "8px" }}>EMA50</th>
          <th style={{ padding: "8px" }}>MACD</th>
        </tr>
      </thead>
      <tbody>
        {stocks.map((stock) => (
          <tr key={stock.ticker} style={{ borderBottom: "1px solid #eee" }}>
            <td style={{ padding: "8px" }}>
              {/* Reuses the same selectedTicker mechanism SearchBar already uses,
                  so clicking a row shows StockDetail below — no routing needed */}
              <button
                onClick={() => onSelectTicker(stock.ticker)}
                style={{
                  background: "none",
                  border: "none",
                  color: "#0066cc",
                  cursor: "pointer",
                  padding: 0,
                  font: "inherit",
                  textDecoration: "underline"
                }}
              >
                {stock.ticker}
              </button>
            </td>
            <td style={{ padding: "8px" }}>{stock.current_price}</td>
            <td style={{ padding: "8px", color: stock.change_percent >= 0 ? "green" : "red" }}>
              {stock.change_percent}%
            </td>
            <td style={{ padding: "8px" }}>{stock.rsi}</td>
            <td style={{ padding: "8px" }}>{stock.ema20}</td>
            <td style={{ padding: "8px" }}>{stock.ema50}</td>
            <td style={{ padding: "8px" }}>{stock.macd}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default ScreenerTable