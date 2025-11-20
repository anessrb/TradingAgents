#!/usr/bin/env python3
"""
Simple test script to see the AI agent in action
Run this to see what the AI is thinking!
"""

from trading_agent import TradingAgent
import os

def main():
    print("=" * 80)
    print("🤖 AI TRADING AGENT TEST")
    print("=" * 80)
    print()

    # Initialize agent
    api_key = os.getenv("MISTRAL_API_KEY", "")
    agent = TradingAgent(
        name="TestAgent",
        initial_balance=10000.0,
        api_key=api_key
    )

    print(f"✅ Agent initialized with ${agent.balance:,.2f}")
    print(f"🔑 API Key configured: {bool(api_key)}")
    print()

    # Test symbols
    symbols = ["AAPL", "GOOGL", "TSLA"]

    for symbol in symbols:
        print("\n" + "=" * 80)
        print(f"Testing {symbol}...")
        print("=" * 80)

        decision = agent.make_decision(symbol)

        if decision:
            print(f"\n✅ Decision complete!")
            print(f"Current Balance: ${agent.balance:,.2f}")
            print(f"Portfolio Value: ${agent.calculate_portfolio_value():,.2f}")

        print("\n" + "-" * 80)
        input("Press Enter to continue to next symbol...")

    # Show final stats
    print("\n" + "=" * 80)
    print("📊 FINAL STATISTICS")
    print("=" * 80)

    stats = agent.get_performance_stats()
    print(f"\nInitial Balance: ${stats['initial_balance']:,.2f}")
    print(f"Final Portfolio Value: ${stats['total_portfolio_value']:,.2f}")
    print(f"Total Return: ${stats['total_return']:,.2f} ({stats['return_percentage']:.2f}%)")
    print(f"Total Trades: {stats['total_trades']}")

    print("\n📈 Holdings:")
    for holding in stats['holdings']:
        print(f"  {holding['symbol']}: {holding['quantity']} shares @ ${holding['current_price']:.2f}")
        print(f"    P/L: ${holding['pnl']:,.2f} ({holding['pnl_pct']:.2f}%)")

    print("\n💾 Saving agent state...")
    agent.save_state("test_agent_state.json")

    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
