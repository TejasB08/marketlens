from fastapi import APIRouter, HTTPException
from app.services.screener_service import scan_universe
from app.services.filters import run_preset, PRESETS
from app.schemas.screener_schema import ScreenerResponseSchema

router = APIRouter()


@router.get("/screener/scan", response_model=ScreenerResponseSchema)
def full_scan():
    """
    GET /screener/scan
    Returns indicators for every stock in the NIFTY 50 universe,
    unfiltered. Mainly useful for debugging / inspecting raw scan output.
    """
    scanned = scan_universe()

    if not scanned:
        raise HTTPException(status_code=503, detail="Could not fetch screener data")

    return {
        "preset": None,
        "count": len(scanned),
        "results": list(scanned.values())
    }


@router.get("/screener/preset/{preset_name}", response_model=ScreenerResponseSchema)
def screen_preset(preset_name: str):
    """
    GET /screener/preset/oversold
    GET /screener/preset/breakout_watch
    Runs a named preset screen and returns only stocks that pass it.
    """
    scanned = scan_universe()

    if not scanned:
        raise HTTPException(status_code=503, detail="Could not fetch screener data")

    try:
        filtered = run_preset(scanned, preset_name)
    except ValueError:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown preset '{preset_name}'. Available: {list(PRESETS.keys())}"
        )

    return {
        "preset": preset_name,
        "count": len(filtered),
        "results": list(filtered.values())
    }