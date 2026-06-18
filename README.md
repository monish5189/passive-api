# 💰 Passive Income API — Complete Setup Guide
### Build once. Earn USDC while you sleep.

---

## What This Is

A FastAPI server with **3 paid endpoints** protected by **x402** —
the new HTTP payment protocol backed by Coinbase, Cloudflare, Google, AWS, Stripe.

Every time an AI agent (or anyone) calls your API, they pay you **USDC**
directly to your crypto wallet. No subscriptions, no billing dashboard,
no middlemen. Payment IS the authentication.

```
You build API → Deploy free on Railway → List on x402scan.com
AI agents call your API → USDC lands in your wallet
```

---

## Your 3 Earning Endpoints

| Endpoint | Price/call | What it does |
|----------|-----------|--------------|
| `GET /api/geometry` | $0.005 | Ball trajectory simulator (your pool code!) |
| `GET /api/image-analyze` | $0.010 | Image brightness + dominant color |
| `GET /api/unit-convert` | $0.003 | Naval/engineering unit conversions |

At 500 calls/day → ~$3–5/day → ~$100–150/month. Fully passive.

---

## STEP 1 — Get a Crypto Wallet (10 min, FREE)

You need a Base network wallet to receive USDC.

**Option A — MetaMask (recommended):**
1. Install MetaMask: https://metamask.io
2. Create new wallet → save your seed phrase safely
3. Copy your wallet address (starts with `0x...`)
4. Add Base network:
   - Network Name: `Base`
   - RPC URL: `https://mainnet.base.org`
   - Chain ID: `8453`
   - Symbol: `ETH`

**Option B — Coinbase Wallet:**
1. https://coinbase.com/wallet → Download app
2. Create wallet → copy address

**Get testnet USDC (for testing, FREE):**
- Go to: https://faucet.circle.com
- Select: Base Sepolia
- Paste your wallet address → Get free test USDC

---

## STEP 2 — Setup Project in Termux

```bash
# Install Python packages
pkg install python git

# Create project folder
mkdir ~/passive-api && cd ~/passive-api

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Copy the project files here (from the zip you downloaded)
# Then install dependencies:
pip install -r requirements.txt
```

---

## STEP 3 — Configure Your Wallet

```bash
# Copy the example env file
cp .env.example .env

# Edit it with your wallet address
nano .env
```

Change this line:
```
PAY_TO_ADDRESS=0xYOUR_WALLET_ADDRESS_HERE
```
To your actual wallet address.

Keep `X402_NETWORK=base-sepolia` for testing first.

---

## STEP 4 — Test Locally in Termux

```bash
# Start the server
cd ~/passive-api
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# In another Termux session, test:
curl http://localhost:8000/
curl "http://localhost:8000/api/unit-convert/list"

# Geometry test (free in dev mode without x402 installed):
curl "http://localhost:8000/api/geometry?x0=100&y0=250&angle_deg=35&speed=15"

# Unit convert test:
curl "http://localhost:8000/api/unit-convert?value=50&conversion=knots_to_kmh"
```

---

## STEP 5 — Deploy to Railway (FREE hosting)

Railway gives you a public HTTPS URL. Free hobby plan included.

### Option A: GitHub (recommended)

```bash
# On your PC or Termux with git:
cd ~/passive-api

git init
git add .
git commit -m "initial passive income api"

# Push to GitHub (create a free repo at github.com)
git remote add origin https://github.com/YOUR_USERNAME/passive-api.git
git push -u origin main
```

Then:
1. Go to https://railway.com → Sign up free
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your `passive-api` repo
4. Railway auto-detects Python → builds → deploys ✅

### Set Environment Variables on Railway:
1. Click your service → **Variables** tab
2. Add:
   - `PAY_TO_ADDRESS` = your wallet address
   - `X402_NETWORK` = `base-sepolia` (testnet) or `base` (mainnet)

### Get your public URL:
- Click **Settings** → **Domains** → **Generate Domain**
- You'll get: `https://yourapp.up.railway.app`

---

## STEP 6 — Switch to Mainnet (Real Earnings)

Once tested on testnet:

1. On Railway → Variables → change `X402_NETWORK` to `base`
2. Railway redeploys automatically

Now AI agents pay **real USDC** to your wallet on every API call.

---

## STEP 7 — List Your API for Discovery

So AI agents can find and pay you:

**x402scan.com** — Main discovery platform:
- Go to: https://x402scan.com
- Submit your API URL: `https://yourapp.up.railway.app`
- It crawls your `/.well-known/x402.json` and lists you

**MCP-Hive** — Agent tool marketplace:
- https://mcphive.com → Submit API

**Circle Agent Marketplace** (highest visibility):
- https://developers.circle.com/agent-marketplace
- Submit via their Google Form

---

## STEP 8 — Monitor Earnings

Check your wallet anytime:
- https://basescan.org → paste your wallet address
- See all incoming USDC transactions

Or install Coinbase Wallet app → automatic notifications.

---

## Scaling Up (Optional)

Once running, add more endpoints:

```python
# Example: Add a new paid endpoint
@app.get("/api/new-thing")
@pay("$0.01")
async def new_thing(param: str = Query(...)):
    # your logic here
    return {"result": "..."}
```

Ideas based on your skills:
- `/api/hull-stability` — Ship stability calculator
- `/api/ocr-image` — Text extraction from image URL
- `/api/color-detect` — Detect specific colors in image (OpenCV logic)
- `/api/rpm-to-speed` — Propeller/shaft RPM to vessel speed

---

## Realistic Income Estimates

| Daily calls | Price | Daily income | Monthly |
|-------------|-------|-------------|---------|
| 100 | $0.005 avg | $0.50 | $15 |
| 500 | $0.005 avg | $2.50 | $75 |
| 2,000 | $0.007 avg | $14.00 | $420 |
| 10,000 | $0.007 avg | $70.00 | $2,100 |

Traffic comes from other AI agents calling your API automatically.
No promotion needed — just listing on x402scan is enough.

---

## Maintenance

Realistically: **30 min/month**
- Check basescan.org to see earnings
- Railway auto-restarts if it crashes
- Update endpoints if you add new features

That's it. Build once, earn forever. 🎯
