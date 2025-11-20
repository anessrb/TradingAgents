"""
Market Data Service with fallback to generated realistic data
Yahoo Finance API has been unreliable, so we generate realistic market data
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List
import yfinance as yf


class MarketDataService:
    """Handles market data fetching with fallback to realistic generated data"""

    # Stock metadata for realistic simulation
    STOCK_DATA = {
        "AAPL": {"name": "Apple Inc.", "base_price": 195.50, "volatility": 0.015, "sector": "Technology"},
        "GOOGL": {"name": "Alphabet Inc.", "base_price": 142.30, "volatility": 0.018, "sector": "Technology"},
        "MSFT": {"name": "Microsoft Corporation", "base_price": 420.50, "volatility": 0.012, "sector": "Technology"},
        "AMZN": {"name": "Amazon.com Inc.", "base_price": 178.25, "volatility": 0.020, "sector": "Consumer Cyclical"},
        "TSLA": {"name": "Tesla Inc.", "base_price": 248.50, "volatility": 0.030, "sector": "Automotive"},
        "NVDA": {"name": "NVIDIA Corporation", "base_price": 875.28, "volatility": 0.025, "sector": "Technology"},
        "META": {"name": "Meta Platforms Inc.", "base_price": 528.50, "volatility": 0.020, "sector": "Technology"},
        "JPM": {"name": "JPMorgan Chase & Co.", "base_price": 215.75, "volatility": 0.010, "sector": "Financial"},
        "V": {"name": "Visa Inc.", "base_price": 285.50, "volatility": 0.012, "sector": "Financial"},
        "WMT": {"name": "Walmart Inc.", "base_price": 85.25, "volatility": 0.008, "sector": "Consumer Defensive"}
    }

    @staticmethod
    def try_yahoo_finance(symbol: str, period: str = "1mo", interval: str = "1d") -> Dict:
        """Try to fetch from Yahoo Finance first"""
        try:
            hist = yf.download(symbol, period=period, interval=interval, progress=False, timeout=5)
            if not hist.empty and len(hist) > 0:
                ticker = yf.Ticker(symbol)
                try:
                    info = ticker.info
                except:
                    info = {}

                current_price = float(hist['Close'].iloc[-1])
                prev_price = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price

                hist_reset = hist.reset_index()
                date_col = 'Date' if 'Date' in hist_reset.columns else hist_reset.index.name or 'index'

                historical_data = {
                    "Date": [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d) for d in (hist_reset[date_col] if date_col in hist_reset.columns else hist_reset.index)],
                    "Open": [float(x) for x in hist['Open'].tolist()],
                    "High": [float(x) for x in hist['High'].tolist()],
                    "Low": [float(x) for x in hist['Low'].tolist()],
                    "Close": [float(x) for x in hist['Close'].tolist()],
                    "Volume": [int(x) if x == x else 0 for x in hist['Volume'].tolist()]
                }

                return {
                    "symbol": symbol,
                    "current_price": current_price,
                    "previous_close": prev_price,
                    "change_percent": float((current_price - prev_price) / prev_price * 100) if prev_price != 0 else 0.0,
                    "volume": int(hist['Volume'].iloc[-1]) if hist['Volume'].iloc[-1] == hist['Volume'].iloc[-1] else 0,
                    "high_52w": float(hist['High'].max()),
                    "low_52w": float(hist['Low'].min()),
                    "company_name": info.get("longName", MarketDataService.STOCK_DATA.get(symbol, {}).get("name", symbol)),
                    "sector": info.get("sector", MarketDataService.STOCK_DATA.get(symbol, {}).get("sector", "N/A")),
                    "historical_data": historical_data,
                    "data_source": "yahoo_finance"
                }
        except Exception as e:
            print(f"Yahoo Finance failed: {e}")
        return None

    @staticmethod
    def generate_realistic_data(symbol: str, period: str = "1mo", interval: str = "1d") -> Dict:
        """Generate realistic market data when API is unavailable"""

        if symbol not in MarketDataService.STOCK_DATA:
            # Unknown symbol - create generic data
            stock_info = {
                "name": symbol,
                "base_price": random.uniform(50, 500),
                "volatility": random.uniform(0.010, 0.025),
                "sector": "Unknown"
            }
        else:
            stock_info = MarketDataService.STOCK_DATA[symbol]

        # Determine number of data points based on period and interval
        if interval == "1m":
            # 1-minute data for scalping
            period_map = {"1d": 390, "5d": 1950, "1mo": 8000}  # Trading minutes
            data_points = period_map.get(period, 390)
            time_delta = timedelta(minutes=1)
        elif interval == "5m":
            period_map = {"1d": 78, "5d": 390, "1mo": 1600}
            data_points = period_map.get(period, 78)
            time_delta = timedelta(minutes=5)
        elif interval == "15m":
            period_map = {"1d": 26, "5d": 130, "1mo": 530}
            data_points = period_map.get(period, 26)
            time_delta = timedelta(minutes=15)
        else:  # 1d default
            period_days = {
                "1d": 1,
                "5d": 5,
                "1mo": 30,
                "3mo": 90,
                "6mo": 180,
                "1y": 365,
                "2y": 730
            }.get(period, 30)
            data_points = period_days
            time_delta = timedelta(days=1)

        # Generate price history with random walk
        dates = []
        opens = []
        highs = []
        lows = []
        closes = []
        volumes = []

        # Start time based on interval
        if interval in ["1m", "5m", "15m"]:
            current_date = datetime.now() - (time_delta * data_points)
        else:
            current_date = datetime.now() - timedelta(days=data_points)

        current_price = stock_info["base_price"]

        # Adjust volatility for shorter timeframes
        volatility_multiplier = {
            "1m": 0.1,   # Much smaller moves per minute
            "5m": 0.2,
            "15m": 0.3,
            "1d": 1.0
        }.get(interval, 1.0)

        for i in range(data_points):
            # Format date based on interval
            if interval in ["1m", "5m", "15m"]:
                dates.append(current_date.strftime('%Y-%m-%d %H:%M'))
            else:
                dates.append(current_date.strftime('%Y-%m-%d'))

            # Random walk with drift
            return_std = stock_info["volatility"] * volatility_multiplier
            period_return = random.gauss(0.0001, return_std)  # Slight upward drift
            open_price = current_price
            close_price = open_price * (1 + period_return)

            # Intraday high/low
            intraday_range = abs(random.gauss(0, return_std * 0.5))
            high_price = max(open_price, close_price) * (1 + intraday_range)
            low_price = min(open_price, close_price) * (1 - intraday_range)

            # Volume (adjust based on interval)
            if interval == "1m":
                volume = int(random.uniform(50_000, 500_000))
            elif interval == "5m":
                volume = int(random.uniform(200_000, 2_000_000))
            elif interval == "15m":
                volume = int(random.uniform(500_000, 5_000_000))
            else:
                volume = int(random.uniform(5_000_000, 50_000_000))

            opens.append(round(open_price, 2))
            highs.append(round(high_price, 2))
            lows.append(round(low_price, 2))
            closes.append(round(close_price, 2))
            volumes.append(volume)

            current_price = close_price
            current_date += time_delta

        current_price = closes[-1]
        prev_price = closes[-2] if len(closes) > 1 else current_price

        return {
            "symbol": symbol,
            "current_price": current_price,
            "previous_close": prev_price,
            "change_percent": round((current_price - prev_price) / prev_price * 100, 2),
            "volume": volumes[-1],
            "high_52w": max(highs),
            "low_52w": min(lows),
            "company_name": stock_info["name"],
            "sector": stock_info["sector"],
            "historical_data": {
                "Date": dates,
                "Open": opens,
                "High": highs,
                "Low": lows,
                "Close": closes,
                "Volume": volumes
            },
            "data_source": "simulated"
        }

    @staticmethod
    def get_market_data(symbol: str, period: str = "1mo", interval: str = "1d") -> Dict:
        """Get market data - try Yahoo Finance first, fall back to generated data"""
        print(f"📊 Fetching market data for {symbol} ({interval} interval)...")

        # Try Yahoo Finance first
        data = MarketDataService.try_yahoo_finance(symbol, period, interval)

        if data:
            print(f"✅ Got real data from Yahoo Finance for {symbol}")
            return data

        # Fall back to generated data
        print(f"⚠️  Yahoo Finance unavailable, generating realistic data for {symbol}")
        data = MarketDataService.generate_realistic_data(symbol, period, interval)
        print(f"✅ Generated realistic market data for {symbol}: ${data['current_price']:.2f} ({interval})")

        return data
