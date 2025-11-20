#!/usr/bin/env python3
"""
Test script to verify chart data retrieval works correctly
"""

from trading_agent import TradingAgent
import json

def test_market_data():
    print("🧪 Testing Market Data Retrieval\n")
    print("=" * 80)

    # Create a temporary agent (no API key needed for this test)
    agent = TradingAgent("TestAgent", 10000.0)

    symbols = ["AAPL", "GOOGL", "TSLA"]

    for symbol in symbols:
        print(f"\n📊 Testing {symbol}...")
        try:
            data = agent.get_market_data(symbol, period="5d")

            if data:
                print(f"✅ Success!")
                print(f"   Company: {data['company_name']}")
                print(f"   Current Price: ${data['current_price']:.2f}")
                print(f"   Change: {data['change_percent']:.2f}%")
                print(f"   Historical data points: {len(data['historical_data']['Date'])}")

                # Verify data is JSON serializable
                try:
                    json.dumps(data)
                    print(f"   ✅ Data is JSON serializable")
                except Exception as e:
                    print(f"   ❌ JSON serialization failed: {e}")

            else:
                print(f"❌ Failed to fetch data for {symbol}")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("-" * 80)

    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_market_data()
