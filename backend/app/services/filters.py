"""
Individual filter predicates + preset screen definitions.
Each filter function takes one stock's scanned data (from scan_universe())
and returns True if the stock passes that filter.
"""


def rsi_below(stock: dict, threshold: float) -> bool:
    """True if RSI is below threshold (classic oversold signal)."""
    rsi = stock.get("rsi")
    return rsi is not None and rsi < threshold


def rsi_above(stock: dict, threshold: float) -> bool:
    """True if RSI is above threshold (classic overbought signal)."""
    rsi = stock.get("rsi")
    return rsi is not None and rsi > threshold


def ema_bullish_crossover(stock: dict) -> bool:
    """
    True if the short-term trend (EMA20) is above the medium-term
    trend (EMA50) — a common 'breakout'/bullish momentum signal.
    """
    ema20 = stock.get("ema20")
    ema50 = stock.get("ema50")
    return ema20 is not None and ema50 is not None and ema20 > ema50


def macd_bullish(stock: dict) -> bool:
    """True if MACD line is above its signal line (bullish momentum)."""
    macd = stock.get("macd")
    signal = stock.get("macd_signal")
    return macd is not None and signal is not None and macd > signal


def volume_above(stock: dict, threshold: int) -> bool:
    """True if volume exceeds a fixed threshold (crude volume-spike check)."""
    volume = stock.get("volume")
    return volume is not None and volume > threshold


def apply_filters(scanned_data: dict, filters: list) -> dict:
    """
    Runs a list of filter functions against every stock in scanned_data.
    A stock passes only if it passes ALL filters (AND logic).

    filters: list of no-arg callables, e.g. via lambda, so filters with
    parameters (like rsi_below) can be pre-bound before passing in:
        apply_filters(data, [lambda s: rsi_below(s, 30)])
    """
    results = {}
    for ticker, stock in scanned_data.items():
        if all(f(stock) for f in filters):
            results[ticker] = stock
    return results


# --- Preset screens ---
# Each preset is a list of filter lambdas pre-bound with their thresholds.
PRESETS = {
    "oversold": [
        lambda s: rsi_below(s, 30),
    ],
    "breakout_watch": [
        lambda s: ema_bullish_crossover(s),
        lambda s: macd_bullish(s),
    ],
}


def run_preset(scanned_data: dict, preset_name: str) -> dict:
    """
    Runs a named preset screen against scanned_data.
    Raises ValueError if the preset name doesn't exist —
    lets the API layer turn that into a clean 400 response.
    """
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}")
    return apply_filters(scanned_data, PRESETS[preset_name])