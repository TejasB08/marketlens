import { useState } from "react"
import { runPreset } from "../services/api"
import ScreenerTable from "./ScreenerTable"

function Screener({ onSelectTicker }) {
  const [stocks, setStocks] = useState([])
  const [activePreset, setActivePreset] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePresetClick = async (presetName) => {
    setLoading(true)
    setError(null)
    setActivePreset(presetName)

    try {
      const data = await runPreset(presetName)
      setStocks(data.results)
    } catch (err) {
      setError("Could not load screener results. Is the backend running?")
      setStocks([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Stock Screener</h2>

      <div style={{ display: "flex", gap: "12px", marginBottom: "12px" }}>
        <button onClick={() => handlePresetClick("oversold")}>
          Oversold
        </button>
        <button onClick={() => handlePresetClick("breakout_watch")}>
          Breakout Watch
        </button>
      </div>

      {loading && <p>Scanning NIFTY 50... (first scan can take ~1 min)</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {!loading && !error && activePreset && (
        <>
          <p>{stocks.length} stocks match</p>
          <ScreenerTable stocks={stocks} onSelectTicker={onSelectTicker} />
        </>
      )}
    </div>
  )
}

export default Screener