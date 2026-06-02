import pandas as pd
import ta


def calculate_indicators(history: pd.DataFrame) -> dict:
    """
    Takes historical OHLCV DataFrame from yfinance
    and returns calculated technical indicators.
    """
    try:
        close = history["Close"]

        # RSI - Relative Strength Index (14 period is industry standard)
        rsi = ta.momentum.RSIIndicator(close=close, window=14)
        rsi_value = round(float(rsi.rsi().iloc[-1]), 2)

        # EMA 20 - Short term trend
        ema20 = ta.trend.EMAIndicator(close=close, window=20)
        ema20_value = round(float(ema20.ema_indicator().iloc[-1]), 2)

        # EMA 50 - Medium term trend
        ema50 = ta.trend.EMAIndicator(close=close, window=50)
        ema50_value = round(float(ema50.ema_indicator().iloc[-1]), 2)

        # MACD - Moving Average Convergence Divergence
        macd = ta.trend.MACD(close=close)
        macd_value = round(float(macd.macd().iloc[-1]), 2)
        macd_signal = round(float(macd.macd_signal().iloc[-1]), 2)

        return {
            "rsi": rsi_value,
            "ema20": ema20_value,
            "ema50": ema50_value,
            "macd": macd_value,
            "macd_signal": macd_signal
        }

    except Exception as e:
        print(f"Error calculating indicators: {e}")
        return {}