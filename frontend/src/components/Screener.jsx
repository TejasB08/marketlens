import { useEffect, useState } from "react"
import { runPreset } from "../services/api"
import ScreenerTable from "./ScreenerTable"
import SectorBreakdown from "./SectorBreakdown"

const PRESET_OPTIONS = [
  { id: "oversold", label: "Oversold" },
  { id: "breakout_watch", label: "Breakout Watch" }
]

function Screener({ preset, onPresetChange, onSelectTicker }) {
  const [stocks, setStocks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Runs on open and every time the toggle changes. The `cancelled` flag
  // stops a slow earlier request from overwriting a newer one if you
  // switch the toggle quickly.
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    runPreset(preset)
      .then(data => {
        if (!cancelled) setStocks(data.results)
      })
      .catch(() => {
        if (!cancelled) {
          setError("Could not load screener results. Is the backend running?")
          setStocks([])
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [preset])

  return (
    <div>
      <h2>Screener</h2>

      <SectorBreakdown />

      <div style={{ marginTop: "32px" }}>
        <div style={{ display: "flex", gap: "12px", marginBottom: "12px" }}>
          {PRESET_OPTIONS.map(option => {
            const active = preset === option.id
            return (
              <button
                key={option.id}
                onClick={() => onPresetChange(option.id)}
                style={{
                  padding: "8px 16px",
                  borderRadius: "6px",
                  border: "1px solid #0066cc",
                  background: active ? "#0066cc" : "white",
                  color: active ? "white" : "#0066cc",
                  cursor: "pointer"
                }}
              >
                {option.label}
              </button>
            )
          })}
        </div>

        {loading && <p>Scanning NIFTY 50... (first scan can take ~1 min)</p>}
        {error && <p style={{ color: "red" }}>{error}</p>}

        {!loading && !error && (
          <>
            <p>{stocks.length} stocks match</p>
            <ScreenerTable stocks={stocks} onSelectTicker={onSelectTicker} />
          </>
        )}
      </div>
    </div>
  )
}

export default Screener