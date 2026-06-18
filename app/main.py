"""
Passive Income API Server  —  v2.0
===================================
23 paid endpoints using x402 micropayments (USDC on Base).
Each API call earns USDC directly to your wallet. No middlemen.

ORIGINAL (3):
  /api/geometry        Ball trajectory simulator
  /api/image-analyze   Image brightness + color
  /api/unit-convert    Naval/engineering unit converter

NEW (20):
  ── DATA / FINANCE ──
  /api/crypto/price           Live crypto price (CoinGecko, free)
  /api/crypto/top             Top N coins by market cap
  /api/crypto/trending        Trending coins right now
  /api/forex/rates            Live forex exchange rates (free)
  /api/stock/summary          Stock summary + price (Yahoo Finance via yfinance)

  ── WEATHER / GEO ──
  /api/weather/current        Current weather for any city (Open-Meteo, free)
  /api/weather/forecast       7-day forecast
  /api/geo/ip-lookup          IP → country/city/lat/lon (ip-api.com, free)
  /api/geo/geocode            City name → lat/lon (Nominatim, free)
  /api/geo/timezone           Lat/lon → timezone info

  ── WEB / INTERNET TOOLS ──
  /api/web/screenshot-info    URL metadata: title, description, status code
  /api/web/dns-lookup         DNS records for a domain (A, MX, TXT, CNAME)
  /api/web/ssl-check          SSL certificate expiry + issuer info
  /api/web/url-expand         Unshorten / follow redirect chain of a URL

  ── TEXT / NLP TOOLS ──
  /api/text/word-count        Word, sentence, char count + readability score
  /api/text/hash              SHA256 / MD5 / SHA512 of any string
  /api/text/lorem             Generate Lorem Ipsum paragraphs
  /api/text/password-gen      Cryptographically secure password generator

  ── MATH / SCIENCE ──
  /api/math/compound-interest Compound interest / loan calculator
  /api/math/statistics        Mean, median, mode, std-dev of a number list
  /api/math/bmi               BMI calculator with category
  /api/science/constants       Physical / mathematical constants lookup
"""

import os, math, json, hashlib, secrets, string, socket, ssl, re
import statistics as stats_lib
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional, List

import httpx
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image

# ── x402 payment middleware ──────────────────────────────────────────────────
try:
    from fastapi_x402 import init_x402, pay
    X402_AVAILABLE = True
except ImportError:
    X402_AVAILABLE = False
    def pay(price):
        def decorator(func):
            return func
        return decorator

# ── Config ───────────────────────────────────────────────────────────────────
YOUR_WALLET = os.getenv("PAY_TO_ADDRESS", "0xYOUR_WALLET_ADDRESS_HERE")
NETWORK     = os.getenv("X402_NETWORK",  "base-sepolia")

app = FastAPI(
    title="Passive Income API  — 23 Endpoints",
    description=(
        "Pay-per-call API using x402 USDC micropayments on Base. "
        "23 endpoints across finance, weather, geo, web tools, text & math."
    ),
    version="2.0.0",
)

if X402_AVAILABLE:
    init_x402(app, pay_to=YOUR_WALLET, network=NETWORK)


# ═══════════════════════════════════════════════════════════════════════════════
# FREE — Root / Discovery
# ═══════════════════════════════════════════════════════════════════════════════
@app.get("/", tags=["Free"])
async def root():
    return {
        "name": "Passive Income API",
        "version": "2.0.0",
        "total_endpoints": 23,
        "network": NETWORK,
        "pay_to": YOUR_WALLET,
        "categories": {
            "original": ["/api/geometry", "/api/image-analyze", "/api/unit-convert"],
            "finance":  ["/api/crypto/price", "/api/crypto/top", "/api/crypto/trending",
                         "/api/forex/rates", "/api/stock/summary"],
            "weather":  ["/api/weather/current", "/api/weather/forecast"],
            "geo":      ["/api/geo/ip-lookup", "/api/geo/geocode", "/api/geo/timezone"],
            "web_tools":["/api/web/screenshot-info", "/api/web/dns-lookup",
                         "/api/web/ssl-check", "/api/web/url-expand"],
            "text":     ["/api/text/word-count", "/api/text/hash",
                         "/api/text/lorem", "/api/text/password-gen"],
            "math":     ["/api/math/compound-interest", "/api/math/statistics",
                         "/api/math/bmi", "/api/science/constants"],
        },
        "docs": "/docs",
        "discovery": "/.well-known/x402.json",
    }

@app.get("/health", tags=["Free"])
async def health():
    return {"status": "ok", "time": datetime.now(timezone.utc).isoformat()}

@app.get("/.well-known/x402.json", tags=["Free"])
async def x402_discovery():
    p = Path(__file__).parent / ".well-known" / "x402.json"
    if p.exists():
        return JSONResponse(json.loads(p.read_text()))
    return JSONResponse({"x402Version": 2, "pay_to": YOUR_WALLET, "network": NETWORK})


# ═══════════════════════════════════════════════════════════════════════════════
# ORIGINAL ENDPOINTS (kept exactly as before)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/geometry", tags=["Original"])
@pay("$0.005")
async def ball_trajectory(
    x0: float = Query(...), y0: float = Query(...),
    angle_deg: float = Query(...),
    speed: float = Query(10.0), friction: float = Query(0.02),
    table_w: float = Query(1000.0), table_h: float = Query(500.0),
    steps: int = Query(50, ge=5, le=500),
):
    """Paid $0.005 — Ball trajectory with wall bounces."""
    angle_rad = math.radians(angle_deg)
    vx = speed * math.cos(angle_rad)
    vy = speed * math.sin(angle_rad)
    x, y = float(x0), float(y0)
    path = [{"x": round(x, 2), "y": round(y, 2)}]
    bounces = 0
    for _ in range(steps):
        x += vx; y += vy
        vx *= (1 - friction); vy *= (1 - friction)
        if x <= 0 or x >= table_w: vx = -vx; x = max(0.0, min(x, table_w)); bounces += 1
        if y <= 0 or y >= table_h: vy = -vy; y = max(0.0, min(y, table_h)); bounces += 1
        path.append({"x": round(x, 2), "y": round(y, 2)})
        if abs(vx) < 0.01 and abs(vy) < 0.01: break
    total = sum(math.hypot(path[i+1]["x"]-path[i]["x"], path[i+1]["y"]-path[i]["y"]) for i in range(len(path)-1))
    return {"path": path, "bounces": bounces, "total_distance": round(total, 2), "final_position": path[-1]}


@app.get("/api/image-analyze", tags=["Original"])
@pay("$0.01")
async def image_analyze(image_url: str = Query(..., description="Public image URL")):
    """Paid $0.01 — Brightness, dominant color, resolution analysis."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(image_url); r.raise_for_status()
    except Exception as e:
        raise HTTPException(400, f"Cannot fetch image: {e}")
    try:
        img = Image.open(BytesIO(r.content)).convert("RGB")
    except Exception as e:
        raise HTTPException(400, f"Cannot decode image: {e}")
    w, h = img.size
    px = list(img.getdata()); n = len(px)
    avg_r = sum(p[0] for p in px) // n
    avg_g = sum(p[1] for p in px) // n
    avg_b = sum(p[2] for p in px) // n
    brightness = (avg_r + avg_g + avg_b) // 3
    dom = img.quantize(colors=2).getpalette()[:3]
    return {
        "resolution": {"width": w, "height": h},
        "aspect_ratio": round(w / h, 3),
        "brightness": brightness,
        "brightness_label": "dark" if brightness < 85 else "medium" if brightness < 170 else "bright",
        "average_color_rgb": [avg_r, avg_g, avg_b],
        "dominant_color_rgb": dom,
    }


CONVERSIONS = {
    "bar_to_psi": lambda v: v*14.5038,  "psi_to_bar": lambda v: v/14.5038,
    "bar_to_pa":  lambda v: v*100_000,  "pa_to_bar":  lambda v: v/100_000,
    "atm_to_pa":  lambda v: v*101_325,  "pa_to_atm":  lambda v: v/101_325,
    "c_to_f":     lambda v: v*9/5+32,   "f_to_c":     lambda v: (v-32)*5/9,
    "c_to_k":     lambda v: v+273.15,   "k_to_c":     lambda v: v-273.15,
    "knots_to_kmh": lambda v: v*1.852,  "kmh_to_knots": lambda v: v/1.852,
    "knots_to_ms":  lambda v: v*0.5144, "ms_to_knots":  lambda v: v/0.5144,
    "kw_to_hp":   lambda v: v*1.34102,  "hp_to_kw":   lambda v: v/1.34102,
    "nm_to_lbft": lambda v: v*0.73756,  "lbft_to_nm": lambda v: v/0.73756,
    "lpm_to_gpm": lambda v: v*0.26417,  "gpm_to_lpm": lambda v: v/0.26417,
    "m_to_ft":    lambda v: v*3.28084,  "ft_to_m":    lambda v: v/3.28084,
    "kg_to_lb":   lambda v: v*2.20462,  "lb_to_kg":   lambda v: v/2.20462,
    "tonne_to_kg":lambda v: v*1000,     "nm_dist_to_km": lambda v: v*1.852,
}

@app.get("/api/unit-convert", tags=["Original"])
@pay("$0.003")
async def unit_convert(
    value: float = Query(...),
    conversion: str = Query(..., description="e.g. bar_to_psi, c_to_f, knots_to_kmh"),
):
    """Paid $0.003 — 28 naval & engineering unit conversions."""
    fn = CONVERSIONS.get(conversion)
    if not fn:
        raise HTTPException(400, f"Unknown conversion. Available: {sorted(CONVERSIONS)}")
    return {"input": value, "conversion": conversion, "result": round(fn(value), 6)}

@app.get("/api/unit-convert/list", tags=["Free"])
async def list_conversions():
    return {"available": sorted(CONVERSIONS.keys())}


# ═══════════════════════════════════════════════════════════════════════════════
# NEW — FINANCE / CRYPTO  (upstream: CoinGecko free, exchangerate.host free)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/crypto/price", tags=["Finance"])
@pay("$0.005")
async def crypto_price(
    coin_id: str = Query("bitcoin", description="CoinGecko ID e.g. bitcoin, ethereum, solana"),
    vs: str = Query("usd", description="Currency e.g. usd, eur, inr"),
):
    """Paid $0.005 — Live price, market cap, 24h change for any coin."""
    url = (
        f"https://api.coingecko.com/api/v3/coins/{coin_id}"
        f"?localization=false&tickers=false&community_data=false&developer_data=false"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url); r.raise_for_status()
            d = r.json()
    except Exception as e:
        raise HTTPException(502, f"CoinGecko error: {e}")
    mkt = d.get("market_data", {})
    return {
        "coin": d.get("name"),
        "symbol": d.get("symbol", "").upper(),
        "currency": vs.upper(),
        "price": mkt.get("current_price", {}).get(vs),
        "market_cap": mkt.get("market_cap", {}).get(vs),
        "volume_24h": mkt.get("total_volume", {}).get(vs),
        "change_24h_pct": mkt.get("price_change_percentage_24h"),
        "high_24h": mkt.get("high_24h", {}).get(vs),
        "low_24h":  mkt.get("low_24h",  {}).get(vs),
        "all_time_high": mkt.get("ath", {}).get(vs),
        "rank": d.get("market_cap_rank"),
        "last_updated": mkt.get("last_updated"),
    }


@app.get("/api/crypto/top", tags=["Finance"])
@pay("$0.008")
async def crypto_top(
    n: int = Query(10, ge=1, le=50, description="Number of top coins"),
    vs: str = Query("usd", description="Currency"),
):
    """Paid $0.008 — Top N coins by market cap with price & change."""
    url = (
        f"https://api.coingecko.com/api/v3/coins/markets"
        f"?vs_currency={vs}&order=market_cap_desc&per_page={n}&page=1"
        f"&sparkline=false&price_change_percentage=24h"
    )
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url); r.raise_for_status()
            coins = r.json()
    except Exception as e:
        raise HTTPException(502, f"CoinGecko error: {e}")
    return {
        "currency": vs.upper(),
        "count": len(coins),
        "coins": [
            {
                "rank": c["market_cap_rank"],
                "name": c["name"],
                "symbol": c["symbol"].upper(),
                "price": c["current_price"],
                "market_cap": c["market_cap"],
                "change_24h_pct": c["price_change_percentage_24h"],
                "volume_24h": c["total_volume"],
            }
            for c in coins
        ],
    }


@app.get("/api/crypto/trending", tags=["Finance"])
@pay("$0.005")
async def crypto_trending():
    """Paid $0.005 — Trending coins on CoinGecko right now."""
    url = "https://api.coingecko.com/api/v3/search/trending"
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url); r.raise_for_status()
            d = r.json()
    except Exception as e:
        raise HTTPException(502, f"CoinGecko error: {e}")
    return {
        "trending_coins": [
            {
                "rank": item["item"]["score"] + 1,
                "name": item["item"]["name"],
                "symbol": item["item"]["symbol"],
                "market_cap_rank": item["item"].get("market_cap_rank"),
                "thumb": item["item"].get("thumb"),
            }
            for item in d.get("coins", [])
        ]
    }


@app.get("/api/forex/rates", tags=["Finance"])
@pay("$0.004")
async def forex_rates(
    base: str = Query("USD", description="Base currency e.g. USD, EUR, INR"),
    symbols: str = Query("EUR,GBP,INR,JPY,AUD,CAD,CHF",
                         description="Comma-separated target currencies"),
):
    """Paid $0.004 — Live forex exchange rates (exchangerate-api open endpoint)."""
    url = f"https://open.er-api.com/v6/latest/{base.upper()}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url); r.raise_for_status()
            d = r.json()
    except Exception as e:
        raise HTTPException(502, f"Exchange rate API error: {e}")
    wanted = {s.strip().upper() for s in symbols.split(",")}
    filtered = {k: v for k, v in d.get("rates", {}).items() if k in wanted}
    return {
        "base": base.upper(),
        "rates": filtered,
        "last_updated": d.get("time_last_update_utc"),
        "next_update": d.get("time_next_update_utc"),
    }


@app.get("/api/stock/summary", tags=["Finance"])
@pay("$0.01")
async def stock_summary(
    ticker: str = Query(..., description="Stock ticker e.g. AAPL, TSLA, RELIANCE.NS"),
):
    """Paid $0.01 — Stock price + basic info via Yahoo Finance (yfinance)."""
    try:
        import yfinance as yf
    except ImportError:
        raise HTTPException(503, "yfinance not installed. Add 'yfinance' to requirements.txt")
    try:
        tk = yf.Ticker(ticker.upper())
        info = tk.fast_info
        hist = tk.history(period="2d")
        prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else None
        current    = float(hist["Close"].iloc[-1])  if len(hist) >= 1 else None
        change_pct = ((current - prev_close) / prev_close * 100) if current and prev_close else None
        return {
            "ticker": ticker.upper(),
            "currency": getattr(info, "currency", None),
            "current_price": current,
            "previous_close": prev_close,
            "change_pct_1d": round(change_pct, 3) if change_pct else None,
            "market_cap": getattr(info, "market_cap", None),
            "shares_outstanding": getattr(info, "shares", None),
            "52w_high": getattr(info, "year_high", None),
            "52w_low":  getattr(info, "year_low",  None),
            "exchange": getattr(info, "exchange", None),
        }
    except Exception as e:
        raise HTTPException(502, f"yfinance error: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# NEW — WEATHER  (upstream: Open-Meteo — completely free, no key)
# ═══════════════════════════════════════════════════════════════════════════════

async def _geocode(city: str) -> tuple[float, float, str]:
    """Helper: city name → (lat, lon, display_name) via Nominatim."""
    url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
    async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent": "PassiveAPI/2.0"}) as c:
        r = await c.get(url); r.raise_for_status()
        results = r.json()
    if not results:
        raise HTTPException(404, f"City not found: {city}")
    return float(results[0]["lat"]), float(results[0]["lon"]), results[0]["display_name"]


WMO_CODES = {
    0:"Clear sky",1:"Mainly clear",2:"Partly cloudy",3:"Overcast",
    45:"Fog",48:"Icy fog",51:"Light drizzle",53:"Moderate drizzle",55:"Dense drizzle",
    61:"Slight rain",63:"Moderate rain",65:"Heavy rain",
    71:"Slight snow",73:"Moderate snow",75:"Heavy snow",
    80:"Slight showers",81:"Moderate showers",82:"Violent showers",
    95:"Thunderstorm",96:"Thunderstorm+hail",99:"Thunderstorm+heavy hail",
}

@app.get("/api/weather/current", tags=["Weather"])
@pay("$0.004")
async def weather_current(
    city: str = Query(..., description="City name e.g. Mumbai, London, Tokyo"),
):
    """Paid $0.004 — Current weather: temp, wind, humidity, condition."""
    lat, lon, place = await _geocode(city)
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"weather_code,wind_speed_10m,wind_direction_10m,precipitation&timezone=auto"
    )
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get(url); r.raise_for_status(); d = r.json()
    cur = d["current"]
    code = cur.get("weather_code", 0)
    return {
        "city": place,
        "latitude": lat, "longitude": lon,
        "temperature_c": cur["temperature_2m"],
        "feels_like_c": cur["apparent_temperature"],
        "humidity_pct": cur["relative_humidity_2m"],
        "wind_speed_kmh": cur["wind_speed_10m"],
        "wind_direction_deg": cur["wind_direction_10m"],
        "precipitation_mm": cur["precipitation"],
        "condition": WMO_CODES.get(code, f"Code {code}"),
        "weather_code": code,
        "timezone": d.get("timezone"),
        "time": cur["time"],
    }


@app.get("/api/weather/forecast", tags=["Weather"])
@pay("$0.007")
async def weather_forecast(
    city: str = Query(..., description="City name"),
    days: int = Query(7, ge=1, le=14, description="Forecast days (1-14)"),
):
    """Paid $0.007 — Daily forecast: high/low temp, rain, wind, sunrise/sunset."""
    lat, lon, place = await _geocode(city)
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"wind_speed_10m_max,weather_code,sunrise,sunset"
        f"&timezone=auto&forecast_days={days}"
    )
    async with httpx.AsyncClient(timeout=10.0) as c:
        r = await c.get(url); r.raise_for_status(); d = r.json()
    daily = d["daily"]
    n = len(daily["time"])
    return {
        "city": place,
        "latitude": lat, "longitude": lon,
        "timezone": d.get("timezone"),
        "forecast": [
            {
                "date":        daily["time"][i],
                "high_c":      daily["temperature_2m_max"][i],
                "low_c":       daily["temperature_2m_min"][i],
                "rain_mm":     daily["precipitation_sum"][i],
                "max_wind_kmh":daily["wind_speed_10m_max"][i],
                "condition":   WMO_CODES.get(daily["weather_code"][i], f"Code {daily['weather_code'][i]}"),
                "sunrise":     daily["sunrise"][i],
                "sunset":      daily["sunset"][i],
            }
            for i in range(n)
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NEW — GEO TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/geo/ip-lookup", tags=["Geo"])
@pay("$0.003")
async def ip_lookup(
    ip: str = Query(..., description="IPv4 or IPv6 address e.g. 8.8.8.8"),
):
    """Paid $0.003 — IP → country, city, ISP, lat/lon (ip-api.com free)."""
    url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    try:
        async with httpx.AsyncClient(timeout=8.0) as c:
            r = await c.get(url); r.raise_for_status(); d = r.json()
    except Exception as e:
        raise HTTPException(502, f"ip-api error: {e}")
    if d.get("status") == "fail":
        raise HTTPException(400, d.get("message", "IP lookup failed"))
    return {
        "ip": d.get("query"),
        "country": d.get("country"),
        "country_code": d.get("countryCode"),
        "region": d.get("regionName"),
        "city": d.get("city"),
        "postal": d.get("zip"),
        "latitude": d.get("lat"),
        "longitude": d.get("lon"),
        "timezone": d.get("timezone"),
        "isp": d.get("isp"),
        "org": d.get("org"),
        "asn": d.get("as"),
    }


@app.get("/api/geo/geocode", tags=["Geo"])
@pay("$0.003")
async def geocode(
    location: str = Query(..., description="Address or city name to geocode"),
    limit: int = Query(3, ge=1, le=10),
):
    """Paid $0.003 — Address/city → lat/lon, OSM place type, bounding box."""
    url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit={limit}&addressdetails=1"
    try:
        async with httpx.AsyncClient(timeout=8.0, headers={"User-Agent": "PassiveAPI/2.0"}) as c:
            r = await c.get(url); r.raise_for_status(); results = r.json()
    except Exception as e:
        raise HTTPException(502, f"Nominatim error: {e}")
    if not results:
        raise HTTPException(404, f"Location not found: {location}")
    return {
        "query": location,
        "results": [
            {
                "display_name": res["display_name"],
                "latitude":  float(res["lat"]),
                "longitude": float(res["lon"]),
                "type": res.get("type"),
                "importance": round(float(res.get("importance", 0)), 3),
                "bounding_box": res.get("boundingbox"),
            }
            for res in results
        ],
    }


@app.get("/api/geo/timezone", tags=["Geo"])
@pay("$0.003")
async def geo_timezone(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
):
    """Paid $0.003 — Lat/lon → timezone name, UTC offset, current local time."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m&timezone=auto"
    try:
        async with httpx.AsyncClient(timeout=8.0) as c:
            r = await c.get(url); r.raise_for_status(); d = r.json()
    except Exception as e:
        raise HTTPException(502, f"Timezone lookup error: {e}")
    tz_name = d.get("timezone", "Unknown")
    offset_s = d.get("utc_offset_seconds", 0)
    offset_h = offset_s / 3600
    return {
        "latitude": lat,
        "longitude": lon,
        "timezone": tz_name,
        "abbreviation": d.get("timezone_abbreviation"),
        "utc_offset_hours": offset_h,
        "utc_offset_formatted": f"UTC{'+' if offset_h >= 0 else ''}{offset_h:g}",
        "current_utc_time": datetime.now(timezone.utc).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NEW — WEB / INTERNET TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/web/screenshot-info", tags=["Web Tools"])
@pay("$0.007")
async def url_metadata(
    url: str = Query(..., description="Full URL including https://"),
):
    """Paid $0.007 — Fetch URL metadata: title, description, status, response time."""
    import time
    try:
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True,
                                     headers={"User-Agent": "Mozilla/5.0 PassiveAPI/2.0"}) as c:
            r = await c.get(url)
        elapsed_ms = round((time.monotonic() - start) * 1000, 1)
    except Exception as e:
        raise HTTPException(502, f"Request failed: {e}")

    html = r.text[:30_000]  # first 30k chars is enough for metadata
    def extract(pattern, default=""):
        m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        return m.group(1).strip()[:300] if m else default

    title = extract(r"<title[^>]*>(.*?)</title>")
    desc  = extract(r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']')
    if not desc:
        desc = extract(r'<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']')
    og_title = extract(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']')
    og_image = extract(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']')

    content_type = r.headers.get("content-type", "")
    content_len  = r.headers.get("content-length", "unknown")
    return {
        "url": str(r.url),
        "status_code": r.status_code,
        "response_time_ms": elapsed_ms,
        "title": title or og_title,
        "description": desc,
        "og_image": og_image,
        "content_type": content_type,
        "content_length": content_len,
        "redirect_count": len(r.history),
        "final_url": str(r.url),
        "server": r.headers.get("server", ""),
    }


@app.get("/api/web/dns-lookup", tags=["Web Tools"])
@pay("$0.004")
async def dns_lookup(
    domain: str = Query(..., description="Domain e.g. google.com"),
    record_type: str = Query("A", description="Record type: A, AAAA, MX, TXT, CNAME, NS"),
):
    """Paid $0.004 — DNS records via Google DNS-over-HTTPS (no local DNS needed)."""
    rtype = record_type.upper()
    url = f"https://dns.google/resolve?name={domain}&type={rtype}"
    try:
        async with httpx.AsyncClient(timeout=8.0) as c:
            r = await c.get(url); r.raise_for_status(); d = r.json()
    except Exception as e:
        raise HTTPException(502, f"DNS lookup failed: {e}")

    STATUS_MAP = {0:"NOERROR",1:"FORMERR",2:"SERVFAIL",3:"NXDOMAIN",5:"REFUSED"}
    answers = d.get("Answer", [])
    return {
        "domain": domain,
        "record_type": rtype,
        "status": STATUS_MAP.get(d.get("Status", -1), "UNKNOWN"),
        "authoritative": d.get("AA", False),
        "records": [
            {"name": a["name"], "ttl": a["TTL"], "data": a["data"]}
            for a in answers
        ],
        "record_count": len(answers),
    }


@app.get("/api/web/ssl-check", tags=["Web Tools"])
@pay("$0.006")
async def ssl_check(
    domain: str = Query(..., description="Domain to check e.g. google.com"),
    port: int = Query(443, description="Port (default 443)"),
):
    """Paid $0.006 — SSL certificate expiry, issuer, subject, SANs."""
    import ssl as ssl_lib, socket
    from datetime import datetime
    try:
        ctx = ssl_lib.create_default_context()
        with socket.create_connection((domain, port), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
    except ssl_lib.SSLCertVerificationError as e:
        return {"domain": domain, "valid": False, "error": str(e)}
    except Exception as e:
        raise HTTPException(502, f"SSL check failed: {e}")

    def parse_date(s):
        return datetime.strptime(s, "%b %d %H:%M:%S %Y %Z")

    not_before = parse_date(cert["notBefore"])
    not_after  = parse_date(cert["notAfter"])
    now = datetime.utcnow()
    days_left = (not_after - now).days

    subject = dict(x[0] for x in cert.get("subject", []))
    issuer  = dict(x[0] for x in cert.get("issuer", []))
    sans = [v for t, v in cert.get("subjectAltName", []) if t == "DNS"]

    return {
        "domain": domain,
        "port": port,
        "valid": True,
        "days_until_expiry": days_left,
        "expires_on": not_after.isoformat(),
        "issued_on": not_before.isoformat(),
        "status": "⚠️ EXPIRING SOON" if days_left < 30 else "✅ VALID",
        "subject": subject,
        "issuer": issuer,
        "san_domains": sans[:20],
        "version": cert.get("version"),
        "serial_number": cert.get("serialNumber"),
    }


@app.get("/api/web/url-expand", tags=["Web Tools"])
@pay("$0.003")
async def url_expand(
    url: str = Query(..., description="Short or redirecting URL to expand"),
):
    """Paid $0.003 — Follow redirects and return the full redirect chain."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True,
                                     headers={"User-Agent": "PassiveAPI/2.0"}) as c:
            r = await c.get(url)
    except Exception as e:
        raise HTTPException(502, f"URL expand failed: {e}")

    chain = [{"url": str(h.url), "status": h.status_code} for h in r.history]
    chain.append({"url": str(r.url), "status": r.status_code})
    return {
        "original_url": url,
        "final_url": str(r.url),
        "hops": len(r.history),
        "redirect_chain": chain,
        "is_shortened": len(r.history) > 0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NEW — TEXT / NLP TOOLS  (all pure Python, no external API)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/text/word-count", tags=["Text"])
@pay("$0.002")
async def word_count(
    text: str = Query(..., max_length=10_000, description="Text to analyse"),
):
    """Paid $0.002 — Word, sentence, char count + Flesch readability score."""
    words     = text.split()
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    syllables = sum(max(1, len(re.findall(r'[aeiouAEIOU]', w))) for w in words)
    chars_no_space = len(text.replace(" ", ""))

    nw = len(words) or 1
    ns = len(sentences) or 1

    # Flesch Reading Ease
    flesch = 206.835 - 1.015*(nw/ns) - 84.6*(syllables/nw)
    flesch = max(0, min(100, round(flesch, 1)))
    if   flesch >= 90: level = "Very Easy"
    elif flesch >= 70: level = "Easy"
    elif flesch >= 60: level = "Standard"
    elif flesch >= 50: level = "Fairly Difficult"
    elif flesch >= 30: level = "Difficult"
    else:              level = "Very Confusing"

    unique = len(set(w.lower().strip(".,!?;:") for w in words))
    return {
        "word_count": nw,
        "sentence_count": ns,
        "character_count": len(text),
        "character_count_no_spaces": chars_no_space,
        "syllable_count": syllables,
        "unique_words": unique,
        "avg_word_length": round(chars_no_space / nw, 2),
        "avg_sentence_length_words": round(nw / ns, 1),
        "flesch_reading_ease": flesch,
        "reading_level": level,
        "estimated_reading_time_sec": round(nw / 3.3),  # avg 200 wpm
    }


@app.get("/api/text/hash", tags=["Text"])
@pay("$0.001")
async def text_hash(
    text: str = Query(..., max_length=50_000, description="Text to hash"),
    algorithm: str = Query("all", description="md5 | sha256 | sha512 | sha1 | all"),
):
    """Paid $0.001 — Cryptographic hashes of any text string."""
    algo = algorithm.lower()
    encoded = text.encode()
    results = {}
    if algo in ("md5",    "all"): results["md5"]    = hashlib.md5(encoded).hexdigest()
    if algo in ("sha1",   "all"): results["sha1"]   = hashlib.sha1(encoded).hexdigest()
    if algo in ("sha256", "all"): results["sha256"] = hashlib.sha256(encoded).hexdigest()
    if algo in ("sha512", "all"): results["sha512"] = hashlib.sha512(encoded).hexdigest()
    if not results:
        raise HTTPException(400, "algorithm must be md5, sha1, sha256, sha512, or all")
    return {"input_length": len(text), "encoding": "utf-8", "hashes": results}


LOREM_WORDS = (
    "lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua enim ad minim veniam quis nostrud "
    "exercitation ullamco laboris nisi aliquip ex ea commodo consequat duis aute irure "
    "dolor reprehenderit voluptate velit esse cillum dolore eu fugiat nulla pariatur "
    "excepteur sint occaecat cupidatat non proident sunt culpa qui officia deserunt "
    "mollit anim id est laborum"
).split()

@app.get("/api/text/lorem", tags=["Text"])
@pay("$0.001")
async def lorem_ipsum(
    paragraphs: int = Query(1, ge=1, le=10, description="Number of paragraphs"),
    sentences_per: int = Query(5, ge=2, le=15, description="Sentences per paragraph"),
    words_per_sentence: int = Query(10, ge=5, le=25),
):
    """Paid $0.001 — Generate Lorem Ipsum placeholder text."""
    import random
    rng = random.Random()
    result = []
    word_pool = LOREM_WORDS * 10
    for _ in range(paragraphs):
        para_sentences = []
        for _ in range(sentences_per):
            w = rng.choices(word_pool, k=words_per_sentence)
            w[0] = w[0].capitalize()
            para_sentences.append(" ".join(w) + ".")
        result.append(" ".join(para_sentences))
    full = "\n\n".join(result)
    return {
        "paragraphs": paragraphs,
        "text": full,
        "word_count": len(full.split()),
        "character_count": len(full),
    }


@app.get("/api/text/password-gen", tags=["Text"])
@pay("$0.002")
async def password_gen(
    length: int = Query(20, ge=8, le=128, description="Password length"),
    count: int = Query(5, ge=1, le=20, description="Number of passwords"),
    uppercase: bool = Query(True), lowercase: bool = Query(True),
    digits: bool = Query(True), symbols: bool = Query(True),
):
    """Paid $0.002 — Cryptographically secure passwords + strength score."""
    pool = ""
    if uppercase: pool += string.ascii_uppercase
    if lowercase: pool += string.ascii_lowercase
    if digits:    pool += string.digits
    if symbols:   pool += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    if not pool:
        raise HTTPException(400, "At least one character set must be enabled")

    passwords = ["".join(secrets.choice(pool) for _ in range(length)) for _ in range(count)]
    entropy = round(length * math.log2(len(pool)), 1)
    strength = "Weak" if entropy < 40 else "Fair" if entropy < 60 else "Strong" if entropy < 80 else "Very Strong"
    return {
        "passwords": passwords,
        "length": length,
        "charset_size": len(pool),
        "entropy_bits": entropy,
        "strength": strength,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NEW — MATH / SCIENCE  (all pure Python)
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/math/compound-interest", tags=["Math"])
@pay("$0.003")
async def compound_interest(
    principal: float = Query(..., gt=0, description="Initial amount"),
    rate_pct: float = Query(..., gt=0, description="Annual interest rate (%)"),
    years: float = Query(..., gt=0, description="Time in years"),
    compounds_per_year: int = Query(12, ge=1, le=365,
                                    description="Compounding frequency (12=monthly, 365=daily)"),
    monthly_contribution: float = Query(0.0, ge=0, description="Regular monthly addition"),
):
    """Paid $0.003 — Compound interest / SIP / loan growth calculator."""
    r = rate_pct / 100
    n = compounds_per_year
    t = years

    # Lump sum future value
    fv_lump = principal * (1 + r/n) ** (n*t)

    # Monthly contribution future value (annuity)
    r_period = r / 12
    periods  = int(t * 12)
    if r_period > 0:
        fv_contrib = monthly_contribution * ((1 + r_period)**periods - 1) / r_period
    else:
        fv_contrib = monthly_contribution * periods

    total_fv     = fv_lump + fv_contrib
    total_invest = principal + monthly_contribution * periods
    total_interest = total_fv - total_invest

    yearly = []
    for yr in range(1, int(years) + 1):
        lump  = principal * (1 + r/n) ** (n*yr)
        m_periods = yr * 12
        contrib_fv = (monthly_contribution * ((1+r_period)**m_periods - 1) / r_period
                      if r_period > 0 else monthly_contribution * m_periods)
        yearly.append({
            "year": yr,
            "balance": round(lump + contrib_fv, 2),
            "invested": round(principal + monthly_contribution * m_periods, 2),
        })

    return {
        "principal": principal,
        "annual_rate_pct": rate_pct,
        "years": years,
        "compounds_per_year": n,
        "monthly_contribution": monthly_contribution,
        "final_balance": round(total_fv, 2),
        "total_invested": round(total_invest, 2),
        "total_interest_earned": round(total_interest, 2),
        "roi_pct": round(total_interest / total_invest * 100, 2) if total_invest > 0 else 0,
        "yearly_breakdown": yearly,
    }


@app.get("/api/math/statistics", tags=["Math"])
@pay("$0.002")
async def statistics_calc(
    numbers: str = Query(..., description="Comma-separated numbers e.g. 1,2,3,4,5"),
):
    """Paid $0.002 — Descriptive stats: mean, median, mode, std-dev, quartiles."""
    try:
        data = [float(x.strip()) for x in numbers.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(400, "Invalid numbers. Use comma-separated values e.g. 1,2,3")
    if len(data) < 2:
        raise HTTPException(400, "Need at least 2 numbers")

    data_sorted = sorted(data)
    n = len(data)
    try:
        mode_val = stats_lib.mode(data)
    except stats_lib.StatisticsError:
        mode_val = None

    q1 = stats_lib.quantiles(data, n=4)[0]
    q3 = stats_lib.quantiles(data, n=4)[2]
    iqr = q3 - q1

    return {
        "count": n,
        "sum": round(sum(data), 6),
        "mean": round(stats_lib.mean(data), 6),
        "median": round(stats_lib.median(data), 6),
        "mode": mode_val,
        "std_dev": round(stats_lib.stdev(data), 6),
        "variance": round(stats_lib.variance(data), 6),
        "min": data_sorted[0],
        "max": data_sorted[-1],
        "range": round(data_sorted[-1] - data_sorted[0], 6),
        "q1": round(q1, 6),
        "q3": round(q3, 6),
        "iqr": round(iqr, 6),
        "outliers": [x for x in data if x < q1 - 1.5*iqr or x > q3 + 1.5*iqr],
    }


@app.get("/api/math/bmi", tags=["Math"])
@pay("$0.001")
async def bmi_calculator(
    weight_kg: float = Query(..., gt=0, description="Weight in kg"),
    height_cm: float = Query(..., gt=0, description="Height in cm"),
    age: Optional[int] = Query(None, ge=5, le=120, description="Age (optional, for context)"),
    sex: Optional[str] = Query(None, description="male or female (optional)"),
):
    """Paid $0.001 — BMI + category, healthy weight range, body fat estimate."""
    h_m = height_cm / 100
    bmi = round(weight_kg / (h_m ** 2), 2)

    if   bmi < 16.0: cat = "Severely Underweight"
    elif bmi < 18.5: cat = "Underweight"
    elif bmi < 25.0: cat = "Normal weight"
    elif bmi < 30.0: cat = "Overweight"
    elif bmi < 35.0: cat = "Obese Class I"
    elif bmi < 40.0: cat = "Obese Class II"
    else:            cat = "Obese Class III (Morbidly Obese)"

    healthy_min = round(18.5 * h_m**2, 1)
    healthy_max = round(24.9 * h_m**2, 1)

    # Deurenberg body fat estimate (if age + sex provided)
    body_fat = None
    if age and sex:
        sex_factor = 1 if sex.lower() == "male" else 0
        body_fat = round(1.2*bmi + 0.23*age - 10.8*sex_factor - 5.4, 1)

    return {
        "weight_kg": weight_kg,
        "height_cm": height_cm,
        "bmi": bmi,
        "category": cat,
        "healthy_range_kg": {"min": healthy_min, "max": healthy_max},
        "kg_to_healthy_weight": round(healthy_min - weight_kg, 1)
                                if weight_kg < healthy_min else
                                round(weight_kg - healthy_max, 1)
                                if weight_kg > healthy_max else 0,
        "estimated_body_fat_pct": body_fat,
    }


CONSTANTS = {
    "speed_of_light":       {"value": 299_792_458,    "unit": "m/s",      "symbol": "c"},
    "gravitational":        {"value": 6.674e-11,       "unit": "N·m²/kg²", "symbol": "G"},
    "planck":               {"value": 6.626e-34,       "unit": "J·s",      "symbol": "h"},
    "boltzmann":            {"value": 1.381e-23,       "unit": "J/K",      "symbol": "k"},
    "avogadro":             {"value": 6.022e23,        "unit": "mol⁻¹",    "symbol": "Nₐ"},
    "electron_charge":      {"value": 1.602e-19,       "unit": "C",        "symbol": "e"},
    "electron_mass":        {"value": 9.109e-31,       "unit": "kg",       "symbol": "mₑ"},
    "proton_mass":          {"value": 1.673e-27,       "unit": "kg",       "symbol": "mₚ"},
    "neutron_mass":         {"value": 1.675e-27,       "unit": "kg",       "symbol": "mₙ"},
    "gas_constant":         {"value": 8.314,           "unit": "J/(mol·K)","symbol": "R"},
    "faraday":              {"value": 96_485.3,        "unit": "C/mol",    "symbol": "F"},
    "stefan_boltzmann":     {"value": 5.670e-8,        "unit": "W/(m²·K⁴)","symbol": "σ"},
    "vacuum_permittivity":  {"value": 8.854e-12,       "unit": "F/m",      "symbol": "ε₀"},
    "vacuum_permeability":  {"value": 1.257e-6,        "unit": "H/m",      "symbol": "μ₀"},
    "standard_gravity":     {"value": 9.80665,         "unit": "m/s²",     "symbol": "g"},
    "atmospheric_pressure": {"value": 101_325,         "unit": "Pa",       "symbol": "atm"},
    "pi":                   {"value": math.pi,         "unit": "dimensionless","symbol": "π"},
    "euler":                {"value": math.e,          "unit": "dimensionless","symbol": "e"},
    "golden_ratio":         {"value": (1+5**0.5)/2,    "unit": "dimensionless","symbol": "φ"},
    "fine_structure":       {"value": 7.297e-3,        "unit": "dimensionless","symbol": "α"},
}

@app.get("/api/science/constants", tags=["Math"])
@pay("$0.002")
async def science_constants(
    name: str = Query("all", description=(
        "Constant name e.g. speed_of_light, gravitational, planck, pi, "
        "or 'all' for full list"
    )),
):
    """Paid $0.002 — Physical & mathematical constants (NIST 2022 values)."""
    if name.lower() == "all":
        return {"constants": CONSTANTS, "count": len(CONSTANTS)}
    key = name.lower().replace(" ", "_").replace("-", "_")
    if key not in CONSTANTS:
        raise HTTPException(
            400,
            f"Unknown constant '{name}'. Available: {sorted(CONSTANTS.keys())}"
        )
    return {"name": key, **CONSTANTS[key]}

@app.get("/api/loan-emi", tags=["Finance"])
async def loan_emi(
    principal: float,
    annual_rate: float,
    years: int
):
    monthly_rate = annual_rate / 12 / 100
    months = years * 12

    emi = (
        principal
        * monthly_rate
        * (1 + monthly_rate) ** months
    ) / (
        (1 + monthly_rate) ** months - 1
    )

    return {
        "principal": principal,
        "annual_rate": annual_rate,
        "years": years,
        "emi": round(emi, 2)
    }

@app.get("/api/gst-calculator", tags=["Finance"])
async def gst_calculator(
    amount: float,
    gst_rate: float = 18
):
    gst = amount * gst_rate / 100

    return {
        "base_amount": amount,
        "gst_rate": gst_rate,
        "gst_amount": round(gst, 2),
        "total_amount": round(amount + gst, 2)
    }
import re

@app.get("/api/email-validator", tags=["Utilities"])
async def email_validator(email: str):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return {
        "email": email,
        "valid": bool(re.match(pattern, email))
    }

@app.get("/api/profit-margin", tags=["Business"])
async def profit_margin(cost: float, selling_price: float):
    profit = selling_price - cost
    margin = (profit / selling_price) * 100 if selling_price else 0

    return {
        "cost": cost,
        "selling_price": selling_price,
        "profit": round(profit, 2),
        "margin_percent": round(margin, 2)
    }

@app.get("/api/roi-calculator", tags=["Business"])
async def roi_calculator(
    investment: float,
    return_amount: float
):
    roi = ((return_amount - investment) / investment) * 100

    return {
        "investment": investment,
        "return_amount": return_amount,
        "roi_percent": round(roi, 2)
    }


import qrcode
from fastapi.responses import StreamingResponse
from io import BytesIO

@app.get("/api/qr-generator", tags=["Utilities"])
async def qr_generator(text: str):
    img = qrcode.make(text)

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="image/png"
    )
from datetime import date

@app.get("/api/age-calculator", tags=["Utilities"])
async def age_calculator(
    birth_year: int,
    birth_month: int,
    birth_day: int
):
    today = date.today()
    born = date(birth_year, birth_month, birth_day)

    age = today.year - born.year - (
        (today.month, today.day) < (born.month, born.day)
    )

    return {
        "birth_date": str(born),
        "age": age
    }

@app.get("/api/password-strength", tags=["Utilities"])
async def password_strength(password: str):
    score = 0

    if len(password) >= 8:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(not c.isalnum() for c in password):
        score += 1

    levels = {
        0: "Very Weak",
        1: "Weak",
        2: "Fair",
        3: "Good",
        4: "Strong",
        5: "Very Strong"
    }

    return {
        "score": score,
        "strength": levels[score]
    }

import uuid

@app.get("/api/uuid-generator", tags=["Utilities"])
async def uuid_generator():
    return {
        "uuid": str(uuid.uuid4())
    }

