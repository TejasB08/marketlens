import { useState } from "react"
import MarketOverview from "./components/MarketOverview"
import SearchBar from "./components/SearchBar"
import StockDetail from "./components/StockDetail"

function App() {
  const [selectedTicker, setSelectedTicker] = useState(null)

  return (
    <div style={{ padding: "24px", maxWidth: "1000px", margin: "0 auto" }}>
      <h1>MarketLens</h1>
      <MarketOverview />
      <hr style={{ margin: "32px 0" }} />
      <SearchBar onSearch={setSelectedTicker} />
      {selectedTicker && <StockDetail ticker={selectedTicker} />}
    </div>
  )
}

export default App