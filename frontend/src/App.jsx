import { useState } from "react"
import MarketOverview from "./components/MarketOverview"
import TopMovers from "./components/TopMovers"
import MarketNews from "./components/MarketNews"
import SearchBar from "./components/SearchBar"
import StockDetail from "./components/StockDetail"
import Screener from "./components/Screener"
import Watchlist from "./components/Watchlist"

function App() {
  // Which page is showing when no stock is selected: "home" | "screener"
  const [view, setView] = useState("home")
  const [selectedTicker, setSelectedTicker] = useState(null)
  // Kept here (not inside Screener) so coming back from a stock page
  // returns you to the same Oversold / Breakout toggle you left
  const [screenerPreset, setScreenerPreset] = useState("oversold")
  const [watchlistVersion, setWatchlistVersion] = useState(0)

  const handleWatchlistUpdate = () => {
    setWatchlistVersion((prev) => prev + 1)
  }

  const goHome = () => {
    setView("home")
    setSelectedTicker(null)
  }

  const goScreener = () => {
    setView("screener")
    setSelectedTicker(null)
  }

  const screenerActive = view === "screener" && !selectedTicker

  let content
  if (selectedTicker) {
    // Stock page: its own view. Back returns to whichever page you came from.
    content = (
      <div>
        <button
          onClick={() => setSelectedTicker(null)}
          style={{ marginBottom: "16px", padding: "6px 12px", borderRadius: "6px", border: "1px solid #ccc", background: "white", cursor: "pointer" }}
        >
          ← Back
        </button>
        <StockDetail ticker={selectedTicker} onStockAdded={handleWatchlistUpdate} />
      </div>
    )
  } else if (view === "screener") {
    content = (
      <Screener
        preset={screenerPreset}
        onPresetChange={setScreenerPreset}
        onSelectTicker={setSelectedTicker}
      />
    )
  } else {
    content = (
      <div>
        <MarketOverview />
        <div style={{ marginTop: "24px" }}>
          <TopMovers />
        </div>
        <div style={{ marginTop: "24px" }}>
          <MarketNews />
        </div>
      </div>
    )
  }

  return (
    // Fixed to the viewport so the sidebar and main area scroll independently
    <div style={{ position: "fixed", inset: 0, display: "flex" }}>

      {/* Sidebar: title + watchlist */}
      <aside
        style={{
          width: "300px",
          flexShrink: 0,
          borderRight: "1px solid #ccc",
          display: "flex",
          flexDirection: "column"
        }}
      >
        {/* Same height + border as the top bar, so the two lines meet across the page */}
        <div
          style={{
            height: "73px",
            boxSizing: "border-box",
            padding: "0 20px",
            display: "flex",
            alignItems: "center",
            borderBottom: "1px solid #ccc"
          }}
        >
          <h1 style={{ margin: 0 }}>
            <button
              onClick={goHome}
              style={{ background: "none", border: "none", padding: 0, font: "inherit", cursor: "pointer" }}
            >
              MarketLens
            </button>
          </h1>
        </div>
        <div style={{ flex: 1, overflowY: "auto" }}>
          <Watchlist
            onSelectTicker={setSelectedTicker}
            refreshTrigger={watchlistVersion}
          />
        </div>
      </aside>

      {/* Main column: top bar stays put, content below scrolls */}
      <main style={{ flex: 1, minWidth: 0, display: "flex", flexDirection: "column" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "12px",
            height: "73px",
            boxSizing: "border-box",
            flexShrink: 0,
            padding: "0 24px",
            borderBottom: "1px solid #ccc"
          }}
        >
          <SearchBar onSearch={setSelectedTicker} />
          <button
            onClick={goScreener}
            style={{
              padding: "10px 20px",
              fontSize: "16px",
              borderRadius: "6px",
              border: "1px solid #0066cc",
              background: screenerActive ? "#0066cc" : "white",
              color: screenerActive ? "white" : "#0066cc",
              cursor: "pointer"
            }}
          >
            Screener
          </button>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "24px" }}>
          <div style={{ maxWidth: "1100px", margin: "0 auto" }}>
            {content}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App