NIFTY_50 = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "BEL.NS", "BHARTIARTL.NS",
    "CIPLA.NS", "COALINDIA.NS", "DRREDDY.NS", "EICHERMOT.NS", "ETERNAL.NS",
    "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS", "HINDALCO.NS",
    "HINDUNILVR.NS", "ICICIBANK.NS", "INDIGO.NS", "INFY.NS", "ITC.NS",
    "JIOFIN.NS", "JSWSTEEL.NS", "KOTAKBANK.NS", "LT.NS", "M&M.NS",
    "MARUTI.NS", "MAXHEALTH.NS", "NESTLEIND.NS", "NTPC.NS", "ONGC.NS",
    "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SHRIRAMFIN.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TCS.NS", "TATACONSUM.NS", "TMPV.NS", "TATASTEEL.NS",
    "TECHM.NS", "TITAN.NS", "TRENT.NS", "ULTRACEMCO.NS", "WIPRO.NS",
]
# Note: TMPV (Tata Motors Passenger Vehicles) is a recently demerged entity.
# If get_stock_data returns None for it, the ticker may not have settled
# on yfinance yet — check on Yahoo Finance directly and swap if needed.


SECTOR_MAP = {
    "ADANIENT.NS": "Metals & Mining", "ADANIPORTS.NS": "Services",
    "APOLLOHOSP.NS": "Healthcare", "ASIANPAINT.NS": "Consumer Durables",
    "AXISBANK.NS": "Financial Services", "BAJAJ-AUTO.NS": "Automobile",
    "BAJFINANCE.NS": "Financial Services", "BAJAJFINSV.NS": "Financial Services",
    "BEL.NS": "Capital Goods", "BHARTIARTL.NS": "Telecommunication",
    "CIPLA.NS": "Healthcare", "COALINDIA.NS": "Oil, Gas & Fuels",
    "DRREDDY.NS": "Healthcare", "EICHERMOT.NS": "Automobile",
    "ETERNAL.NS": "Consumer Services", "GRASIM.NS": "Construction Materials",
    "HCLTECH.NS": "Information Technology", "HDFCBANK.NS": "Financial Services",
    "HDFCLIFE.NS": "Financial Services", "HINDALCO.NS": "Metals & Mining",
    "HINDUNILVR.NS": "FMCG", "ICICIBANK.NS": "Financial Services",
    "INDIGO.NS": "Services", "INFY.NS": "Information Technology",
    "ITC.NS": "FMCG", "JIOFIN.NS": "Financial Services",
    "JSWSTEEL.NS": "Metals & Mining", "KOTAKBANK.NS": "Financial Services",
    "LT.NS": "Construction", "M&M.NS": "Automobile",
    "MARUTI.NS": "Automobile", "MAXHEALTH.NS": "Healthcare",
    "NESTLEIND.NS": "FMCG", "NTPC.NS": "Power",
    "ONGC.NS": "Oil, Gas & Fuels", "POWERGRID.NS": "Power",
    "RELIANCE.NS": "Oil, Gas & Fuels", "SBILIFE.NS": "Financial Services",
    "SHRIRAMFIN.NS": "Financial Services", "SBIN.NS": "Financial Services",
    "SUNPHARMA.NS": "Healthcare", "TCS.NS": "Information Technology",
    "TATACONSUM.NS": "FMCG", "TMPV.NS": "Automobile",
    "TATASTEEL.NS": "Metals & Mining", "TECHM.NS": "Information Technology",
    "TITAN.NS": "Consumer Durables", "TRENT.NS": "Consumer Services",
    "ULTRACEMCO.NS": "Construction Materials", "WIPRO.NS": "Information Technology",
}