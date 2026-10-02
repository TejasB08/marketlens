import { useState } from "react"
import MarketOverview from "./components/MarketOverview"
import SearchBar from "./components/SearchBar"
import StockDetail from "./components/StockDetail"
import Screener from "./components/Screener"
import Watchlist from "./components/Watchlist"

function App() {
  const [selectedTicker, setSelectedTicker] = useState(null)

  return (
    <div style={{ padding: "24px", maxWidth: "1000px", margin: "0 auto" }}>
      <h1>MarketLens</h1>
      <MarketOverview />
      <hr style={{ margin: "32px 0" }} />
      <SearchBar onSearch={setSelectedTicker} />
      {selectedTicker && <StockDetail ticker={selectedTicker} />}
      <hr style={{ margin: "32px 0" }} />
      <Screener onSelectTicker={setSelectedTicker} />
      <hr style={{ margin: "32px 0" }} />
      <Watchlist onSelectTicker={setSelectedTicker} />
    </div>
  )
}

export default App