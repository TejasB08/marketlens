import axios from 'axios'

const BASE_URL = 'http://localhost:8000/api/v1'

export const getQuote = async (ticker) => {
  const response = await axios.get(`${BASE_URL}/quote/${ticker}`)
  return response.data
}

export const getMarketOverview = async () => {
  const response = await axios.get(`${BASE_URL}/market/overview`)
  return response.data
}