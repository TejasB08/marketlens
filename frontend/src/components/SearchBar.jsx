import { useState } from "react"

function SearchBar({ onSearch }) {
  const [input, setInput] = useState("")

  const handleSubmit = () => {
    if (input.trim() === "") return
    onSearch(input.trim().toUpperCase())
  }

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleSubmit()
  }

  return (
    <div style={{ display: "flex", gap: "8px", marginBottom: "24px" }}>
      <input
        type="text"
        placeholder="Search stock... e.g. RELIANCE.NS"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        style={{ padding: "10px", fontSize: "16px", width: "300px", borderRadius: "6px", border: "1px solid #ccc" }}
      />
      <button
        onClick={handleSubmit}
        style={{ padding: "10px 20px", fontSize: "16px", borderRadius: "6px", background: "#0066cc", color: "white", border: "none", cursor: "pointer" }}
      >
        Search
      </button>
    </div>
  )
}

export default SearchBar