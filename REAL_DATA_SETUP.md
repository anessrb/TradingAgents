# 🔥 Get REAL Market Data!

## The Problem

Yahoo Finance API is currently having issues (not returning data). This is a known problem with yfinance.

## The Solution: Alpha Vantage (FREE!)

Alpha Vantage provides **real market data** with a free tier:
- ✅ **Real-time data** (15-minute delay on free tier)
- ✅ **Intraday data** (1min, 5min, 15min, 30min, 60min)
- ✅ **Daily/Weekly/Monthly** data
- ✅ **500 API calls per day** (free tier)
- ✅ **5 requests per minute**

## 🚀 Quick Setup (2 minutes!)

### Step 1: Get FREE API Key

Go to: **https://www.alphavantage.co/support/#api-key**

1. Enter your email
2. Click "GET FREE API KEY"
3. Copy the API key (looks like: `YOUR_API_KEY_HERE`)

### Step 2: Add to .env

```bash
# Add this line to your .env file
ALPHA_VANTAGE_KEY=YOUR_API_KEY_HERE
```

Or run this command (replace with your actual key):
```bash
echo "ALPHA_VANTAGE_KEY=YOUR_API_KEY_HERE" >> .env
```

### Step 3: Restart Backend

```bash
# Stop the current backend (Ctrl+C in the terminal)
# Then restart:
source .venv/bin/activate
python3 backend.py
```

## ✅ That's It!

The system will now:
- ✅ Try Alpha Vantage first (REAL data)
- ✅ Fall back to yfinance if needed
- ✅ Only use simulated data as last resort

## 🎯 Benefits

With real data you'll get:
- 📊 **Actual market prices**
- 📈 **Real volume data**
- ⚡ **Live 1-minute candles**
- 🎯 **Accurate trading decisions**

## 📝 Free Tier Limits

- **500 calls/day** (plenty for testing!)
- **5 calls/minute**
- **15-minute delay** (still great for scalping practice)

For unlimited real-time data, upgrade to premium ($50/month).

## 🔧 Code Changes Made

I've already:
- ✅ Installed `requests` library (for API calls)
- ✅ Updated `market_data_service.py` with Alpha Vantage integration
- ✅ Configured automatic fallback (Alpha Vantage → Yahoo Finance → Simulated)
- ✅ Full support for 1m/5m/15m/1d intervals

Just add your API key and restart! 🚀

---

## 🧪 Test It Works

After adding your API key, test it:

```bash
source .venv/bin/activate
python3 -c "
import os
os.environ['ALPHA_VANTAGE_KEY'] = 'YOUR_KEY_HERE'
from market_data_service import MarketDataService
data = MarketDataService.get_market_data('AAPL', period='1d', interval='1m')
print(f'✅ Got {len(data[\"historical_data\"][\"Date\"])} data points')
print(f'📊 Source: {data[\"data_source\"]}')
print(f'💰 Current price: ${data[\"current_price\"]:.2f}')
"
```

You should see:
```
✅ Got REAL data from Alpha Vantage for AAPL
✅ Got 390 data points
📊 Source: alpha_vantage
💰 Current price: $195.50
```

---

**Get your free key now:** https://www.alphavantage.co/support/#api-key
