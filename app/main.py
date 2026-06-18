"""
Passive Income API Server
=========================
3 paid endpoints using x402 micropayments (USDC on Base).
Each API call earns you USDC directly to your wallet — no middlemen.

Endpoints:
  GET /                  → free info page
  GET /api/geometry      → ball trajectory calculator (your OpenCV skill!)
  GET /api/image-analyze → basic image color/brightness analysis
  GET /api/unit-convert  → naval/engineering unit converter
"""

import os
import math
import json
import httpx
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image

# ── x402 payment middleware ─────────────────────────────────────────────────
# Install: pip install "fastapi-x402"
# Docs:    https://github.com/jordo1138/fastapi-x402
try:
    from fastapi_x402 import init_x402, pay
    X402_AVAILABLE = True
except ImportError:
    # If not installed, run without payments (dev mode)
    X402_AVAILABLE = False
    def pay(price):
        """No-op decorator when x402 not installed (dev mode)."""
        def decorator(func):
            return func
        return decorator

# ── Config ───────────────────────────────────────────────────────────────────
YOUR_WALLET = os.getenv("PAY_TO_ADDRESS", "0xYOUR_WALLET_ADDRESS_HERE")
NETWORK     = os.getenv("X402_NETWORK", "base-sepolia")   # testnet by default
                                                           # change to "base" for mainnet

app = FastAPI(
    title="Passive Income API",
    description="Pay-per-call API using x402 USDC micropayments on Base",
    version="1.0.0",
)

# Wire up x402 middleware (only when library is installed)
if X402_AVAILABLE:
    init_x402(app, pay_to=YOUR_WALLET, network=NETWORK)


# ═══════════════════════════════════════════════════════════════════════════════
# FREE ENDPOINT — Discovery / info
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/")
async def root():
    """Free info page — no payment needed."""
    return {
        "name": "Passive Income API",
        "description": "Pay-per-call API. AI agents pay you USDC per request.",
        "network": NETWORK,
        "pay_to": YOUR_WALLET,
        "endpoints": {
            "/api/geometry":     "$0.005 — Ball/projectile trajectory calculator",
            "/api/image-analyze":"$0.01  — Image brightness, dominant color analysis",
            "/api/unit-convert": "$0.003 — Engineering unit converter (naval, mechanical)",
        },
        "payment_protocol": "x402 (HTTP 402 + USDC on Base)",
        "docs": "/docs",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PAID ENDPOINT 1 — Geometry / Ball Trajectory
# Price: $0.005 per call
# Based on your existing pool-ball geometry Python code!
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/geometry")
@pay("$0.005")
async def ball_trajectory(
    x0: float = Query(..., description="Start X position"),
    y0: float = Query(..., description="Start Y position"),
    angle_deg: float = Query(..., description="Launch angle in degrees"),
    speed: float = Query(10.0, description="Initial speed (units/sec)"),
    friction: float = Query(0.02, description="Friction coefficient (0-1)"),
    table_w: float = Query(1000.0, description="Table/field width"),
    table_h: float = Query(500.0, description="Table/field height"),
    steps: int = Query(50, ge=5, le=500, description="Simulation steps"),
):
    """
    Paid ($0.005): Simulate ball/projectile trajectory with wall bounces.

    Returns full path coordinates — useful for:
    - Pool/billiards AI agents
    - Sports analytics bots
    - Physics simulations
    """
    angle_rad = math.radians(angle_deg)
    vx = speed * math.cos(angle_rad)
    vy = speed * math.sin(angle_rad)
    x, y = float(x0), float(y0)

    path = [{"x": round(x, 2), "y": round(y, 2)}]
    bounces = 0

    for _ in range(steps):
        x += vx
        y += vy

        # Apply friction
        vx *= (1 - friction)
        vy *= (1 - friction)

        # Wall bounces
        if x <= 0 or x >= table_w:
            vx = -vx
            x = max(0.0, min(x, table_w))
            bounces += 1
        if y <= 0 or y >= table_h:
            vy = -vy
            y = max(0.0, min(y, table_h))
            bounces += 1

        path.append({"x": round(x, 2), "y": round(y, 2)})

        # Stop if nearly stationary
        if abs(vx) < 0.01 and abs(vy) < 0.01:
            break

    total_dist = sum(
        math.hypot(path[i+1]["x"] - path[i]["x"],
                   path[i+1]["y"] - path[i]["y"])
        for i in range(len(path) - 1)
    )

    return {
        "path": path,
        "total_steps": len(path),
        "bounces": bounces,
        "total_distance": round(total_dist, 2),
        "final_position": path[-1],
        "input": {
            "start": {"x": x0, "y": y0},
            "angle_deg": angle_deg,
            "speed": speed,
            "friction": friction,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PAID ENDPOINT 2 — Image Analysis (OpenCV-style, pure Python)
# Price: $0.01 per call
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/api/image-analyze")
@pay("$0.01")
async def image_analyze(
    image_url: str = Query(..., description="Public URL of image to analyze"),
):
    """
    Paid ($0.01): Download and analyze an image.

    Returns:
    - Average brightness (0-255)
    - Dominant color (RGB)
    - Resolution
    - Aspect ratio

    Useful for AI agents doing visual content moderation or metadata extraction.
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(image_url)
            resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot fetch image: {e}")

    try:
        img = Image.open(BytesIO(resp.content)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot decode image: {e}")

    width, height = img.size
    pixels = list(img.getdata())
    n = len(pixels)

    avg_r = sum(p[0] for p in pixels) // n
    avg_g = sum(p[1] for p in pixels) // n
    avg_b = sum(p[2] for p in pixels) // n
    brightness = (avg_r + avg_g + avg_b) // 3

    # Dominant color: quantize to 2 colors, pick most common
    quantized = img.quantize(colors=2)
    palette = quantized.getpalette()[:6]  # first 2 colors = 2×RGB
    dom_color = palette[:3]

    return {
        "resolution": {"width": width, "height": height},
        "aspect_ratio": round(width / height, 3),
        "brightness": brightness,
        "brightness_label": (
            "dark" if brightness < 85 else
            "medium" if brightness < 170 else
            "bright"
        ),
        "average_color_rgb": [avg_r, avg_g, avg_b],
        "dominant_color_rgb": dom_color,
        "image_url": image_url,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PAID ENDPOINT 3 — Engineering Unit Converter
# Price: $0.003 per call
# (Leverages your naval engineering background!)
# ═══════════════════════════════════════════════════════════════════════════════
CONVERSIONS = {
    # Pressure
    "bar_to_psi":      lambda v: v * 14.5038,
    "psi_to_bar":      lambda v: v / 14.5038,
    "bar_to_pa":       lambda v: v * 100_000,
    "pa_to_bar":       lambda v: v / 100_000,
    "atm_to_pa":       lambda v: v * 101_325,
    "pa_to_atm":       lambda v: v / 101_325,

    # Temperature
    "c_to_f":          lambda v: v * 9/5 + 32,
    "f_to_c":          lambda v: (v - 32) * 5/9,
    "c_to_k":          lambda v: v + 273.15,
    "k_to_c":          lambda v: v - 273.15,

    # Speed (naval)
    "knots_to_kmh":    lambda v: v * 1.852,
    "kmh_to_knots":    lambda v: v / 1.852,
    "knots_to_ms":     lambda v: v * 0.514444,
    "ms_to_knots":     lambda v: v / 0.514444,

    # Power
    "kw_to_hp":        lambda v: v * 1.34102,
    "hp_to_kw":        lambda v: v / 1.34102,

    # Torque
    "nm_to_lbft":      lambda v: v * 0.737562,
    "lbft_to_nm":      lambda v: v / 0.737562,

    # Flow
    "lpm_to_gpm":      lambda v: v * 0.264172,
    "gpm_to_lpm":      lambda v: v / 0.264172,
    "m3h_to_lpm":      lambda v: v * 16.6667,

    # Length
    "m_to_ft":         lambda v: v * 3.28084,
    "ft_to_m":         lambda v: v / 3.28084,
    "nm_distance_to_km": lambda v: v * 1.852,
    "km_to_nm_distance": lambda v: v / 1.852,

    # Mass / Weight
    "kg_to_lb":        lambda v: v * 2.20462,
    "lb_to_kg":        lambda v: v / 2.20462,
    "tonne_to_kg":     lambda v: v * 1000,
}

@app.get("/api/unit-convert")
@pay("$0.003")
async def unit_convert(
    value: float = Query(..., description="Numeric value to convert"),
    conversion: str = Query(..., description=(
        "Conversion key. Examples: bar_to_psi, c_to_f, knots_to_kmh, "
        "kw_to_hp, nm_to_lbft, lpm_to_gpm, kg_to_lb. "
        "Call GET /api/unit-convert/list for all options (free)."
    )),
):
    """
    Paid ($0.003): Engineering & naval unit conversions.

    Covers: pressure, temperature, speed (knots), power, torque,
    flow rate, length, mass.
    """
    fn = CONVERSIONS.get(conversion)
    if fn is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown conversion '{conversion}'. "
                   f"Available: {sorted(CONVERSIONS.keys())}",
        )
    result = fn(value)
    return {
        "input_value": value,
        "conversion": conversion,
        "result": round(result, 6),
    }


@app.get("/api/unit-convert/list")
async def list_conversions():
    """Free: list all available conversion keys."""
    return {"available_conversions": sorted(CONVERSIONS.keys())}


# ── Health check (for Railway deploy) ────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


# ── x402 discovery (agents use this to find your API) ────────────────────────
@app.get("/.well-known/x402.json")
async def x402_discovery():
    """x402 agent discovery manifest — lists all paid endpoints."""
    manifest_path = Path(__file__).parent / ".well-known" / "x402.json"
    if manifest_path.exists():
        return JSONResponse(json.loads(manifest_path.read_text()))
    # Fallback: build dynamically
    return JSONResponse({
        "x402Version": 2,
        "name": "Passive Income API",
        "pay_to": YOUR_WALLET,
        "network": NETWORK,
        "endpoints": [
            {"path": "/api/geometry",     "method": "GET", "price": "$0.005"},
            {"path": "/api/image-analyze","method": "GET", "price": "$0.010"},
            {"path": "/api/unit-convert", "method": "GET", "price": "$0.003"},
        ],
    })
