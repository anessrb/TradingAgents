#!/usr/bin/env python3
"""
🚀 AI Scalping Bot - Automated high-frequency trading
Trades every 1-2 minutes based on AI decisions
"""

import time
import os
from datetime import datetime
from trading_agent import TradingAgent
from market_data_service import MarketDataService


class ScalpingBot:
    """Automated scalping bot that trades at high frequency"""

    def __init__(self, initial_balance: float, symbols: list, interval: str = "1m"):
        self.symbols = symbols
        self.interval = interval
        self.running = False

        # Initialize agent
        api_key = os.getenv("MISTRAL_API_KEY", "")
        self.agent = TradingAgent(
            name="ScalpingBot",
            initial_balance=initial_balance,
            api_key=api_key
        )

        # Determine check frequency based on interval
        self.check_seconds = {
            "1m": 60,
            "5m": 300,
            "15m": 900
        }.get(interval, 60)

        print(f"\n{'='*80}")
        print(f"🤖 SCALPING BOT INITIALIZED")
        print(f"{'='*80}")
        print(f"💰 Initial Balance: ${initial_balance:,.2f}")
        print(f"📊 Symbols: {', '.join(symbols)}")
        print(f"⏱️  Interval: {interval} (checking every {self.check_seconds}s)")
        print(f"🔑 Mistral AI: {'✅ Enabled' if api_key else '⚠️  Using fallback strategy'}")
        print(f"{'='*80}\n")

    def run(self):
        """Start the scalping bot"""
        self.running = True
        cycle = 0

        print("▶️  Starting automated trading...")
        print("Press Ctrl+C to stop\n")

        try:
            while self.running:
                cycle += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                print(f"\n{'─'*80}")
                print(f"🔄 Cycle #{cycle} - {timestamp}")
                print(f"{'─'*80}")

                # Rotate through symbols
                for symbol in self.symbols:
                    self._trade_symbol(symbol)

                # Show performance
                self._show_performance()

                # Wait for next cycle
                print(f"\n⏳ Waiting {self.check_seconds} seconds until next cycle...")
                time.sleep(self.check_seconds)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping bot...")
            self._show_final_stats()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self._show_final_stats()

    def _trade_symbol(self, symbol: str):
        """Analyze and potentially trade a symbol"""
        print(f"\n📊 Analyzing {symbol}...")

        try:
            # Get market data
            data = MarketDataService.get_market_data(symbol, period="1d", interval=self.interval)

            if not data:
                print(f"  ❌ Could not fetch data for {symbol}")
                return

            # Make decision
            decision = self.agent.make_decision(symbol)

            if not decision:
                print(f"  ❌ Could not make decision for {symbol}")
                return

            print(f"  💭 Decision: {decision['action']} (Confidence: {decision['confidence']:.0%})")

        except Exception as e:
            print(f"  ❌ Error trading {symbol}: {e}")

    def _show_performance(self):
        """Display current performance"""
        stats = self.agent.get_performance_stats()

        portfolio_value = stats['total_portfolio_value']
        total_return = stats['total_return']
        return_pct = stats['return_percentage']

        print(f"\n{'─'*80}")
        print(f"📈 PERFORMANCE")
        print(f"{'─'*80}")
        print(f"  💼 Portfolio Value: ${portfolio_value:,.2f}")
        print(f"  💰 Cash Balance: ${stats['current_balance']:,.2f}")
        print(f"  📊 Holdings Value: ${stats['holdings_value']:,.2f}")
        print(f"  {'🟢' if total_return >= 0 else '🔴'} Total Return: ${total_return:,.2f} ({return_pct:+.2f}%)")
        print(f"  📝 Total Trades: {stats['total_trades']}")

        if stats['holdings']:
            print(f"\n  📦 Current Positions:")
            for holding in stats['holdings']:
                pnl_emoji = '🟢' if holding['pnl'] >= 0 else '🔴'
                print(f"     {pnl_emoji} {holding['symbol']}: {holding['quantity']} shares @ ${holding['current_price']:.2f} | P/L: ${holding['pnl']:.2f} ({holding['pnl_pct']:+.2f}%)")

    def _show_final_stats(self):
        """Display final statistics"""
        stats = self.agent.get_performance_stats()

        print(f"\n{'='*80}")
        print(f"📊 FINAL STATISTICS")
        print(f"{'='*80}")
        print(f"💰 Initial Balance: ${stats['initial_balance']:,.2f}")
        print(f"💼 Final Portfolio Value: ${stats['total_portfolio_value']:,.2f}")
        print(f"{'🟢' if stats['total_return'] >= 0 else '🔴'} Total Return: ${stats['total_return']:,.2f} ({stats['return_percentage']:+.2f}%)")
        print(f"📝 Total Trades: {stats['total_trades']}")

        if stats['holdings']:
            print(f"\n📦 Final Positions:")
            for holding in stats['holdings']:
                print(f"   {holding['symbol']}: {holding['quantity']} shares")
                print(f"      Cost Basis: ${holding['cost_basis']:,.2f}")
                print(f"      Current Value: ${holding['current_value']:,.2f}")
                print(f"      P/L: ${holding['pnl']:,.2f} ({holding['pnl_pct']:+.2f}%)")

        # Save state
        print(f"\n💾 Saving agent state...")
        self.agent.save_state("scalping_bot_state.json")

        print(f"\n{'='*80}")
        print(f"✅ Bot stopped successfully")
        print(f"{'='*80}\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='AI Scalping Bot')
    parser.add_argument('--balance', type=float, default=10000, help='Initial balance (default: 10000)')
    parser.add_argument('--symbols', nargs='+', default=['AAPL', 'GOOGL', 'TSLA'], help='Symbols to trade')
    parser.add_argument('--interval', choices=['1m', '5m', '15m'], default='1m', help='Trading interval')

    args = parser.parse_args()

    # Create and run bot
    bot = ScalpingBot(
        initial_balance=args.balance,
        symbols=args.symbols,
        interval=args.interval
    )

    bot.run()


if __name__ == "__main__":
    main()
