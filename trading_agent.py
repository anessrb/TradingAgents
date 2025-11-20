import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from mistralai import Mistral
from market_data_service import MarketDataService


class TradingAgent:
    """AI-powered trading agent using Mistral AI"""

    def __init__(self, name: str, initial_balance: float, api_key: Optional[str] = None):
        self.name = name
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.portfolio = {}  # {symbol: {"quantity": int, "avg_price": float}}
        self.trade_history = []
        self.performance_history = []

        # Initialize Mistral client
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY", "")
        if self.api_key:
            self.client = Mistral(api_key=self.api_key)
        else:
            self.client = None
            print("⚠️ Warning: No Mistral API key provided. Agent will use fallback logic.")

    def get_market_data(self, symbol: str, period: str = "1mo") -> Dict:
        """Fetch market data using MarketDataService"""
        return MarketDataService.get_market_data(symbol, period)

    def analyze_with_ai(self, market_data: Dict) -> Dict:
        """Use Mistral AI to analyze market data and make trading decision"""
        if not self.client:
            # Fallback: More aggressive momentum strategy
            change = market_data["change_percent"]
            if change > 0.5:
                return {"action": "BUY", "confidence": 0.7, "reasoning": "Positive momentum (fallback strategy)", "suggested_quantity": 5}
            elif change < -0.5:
                return {"action": "SELL", "confidence": 0.6, "reasoning": "Negative momentum (fallback strategy)", "suggested_quantity": None}
            else:
                return {"action": "HOLD", "confidence": 0.5, "reasoning": "Neutral market (fallback strategy)", "suggested_quantity": None}

        # Prepare prompt for Mistral
        prompt = f"""You are an expert trading analyst. Analyze the following market data and provide a trading recommendation.

Market Data:
- Symbol: {market_data['symbol']}
- Company: {market_data['company_name']}
- Current Price: ${market_data['current_price']:.2f}
- Previous Close: ${market_data['previous_close']:.2f}
- Change: {market_data['change_percent']:.2f}%
- Volume: {market_data['volume']:,}
- 52-Week High: ${market_data['high_52w']:.2f}
- 52-Week Low: ${market_data['low_52w']:.2f}
- Sector: {market_data['sector']}

Current Portfolio Status:
- Available Balance: ${self.balance:.2f}
- Holdings: {self.portfolio.get(market_data['symbol'], {}).get('quantity', 0)} shares

Based on this data, should I BUY, SELL, or HOLD?
Provide your response in the following JSON format:
{{
    "action": "BUY/SELL/HOLD",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "suggested_quantity": number of shares (if BUY/SELL)
}}"""

        try:
            response = self.client.chat.complete(
                model="mistral-small-latest",
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse AI response
            ai_response = response.choices[0].message.content

            # Store the raw AI response for logging
            print(f"\n🤖 AI RAW RESPONSE:\n{ai_response}\n")

            # Try to extract JSON from response
            if "{" in ai_response and "}" in ai_response:
                json_start = ai_response.index("{")
                json_end = ai_response.rindex("}") + 1
                decision = json.loads(ai_response[json_start:json_end])
            else:
                # Parse text response
                decision = self._parse_text_response(ai_response)

            # Store full AI response in decision
            decision["ai_full_response"] = ai_response

            return decision

        except Exception as e:
            print(f"Error with AI analysis: {e}")
            # Fallback to simple strategy
            return self.analyze_with_ai(market_data) if self.client else {
                "action": "HOLD",
                "confidence": 0.5,
                "reasoning": f"Error in AI analysis: {str(e)}"
            }

    def _parse_text_response(self, text: str) -> Dict:
        """Parse text response if JSON parsing fails"""
        text_upper = text.upper()
        if "BUY" in text_upper:
            action = "BUY"
        elif "SELL" in text_upper:
            action = "SELL"
        else:
            action = "HOLD"

        return {
            "action": action,
            "confidence": 0.6,
            "reasoning": text[:200],
            "suggested_quantity": 1
        }

    def execute_trade(self, symbol: str, action: str, quantity: int, price: float, reasoning: str = "") -> bool:
        """Execute a trade (BUY/SELL)"""
        timestamp = datetime.now().isoformat()

        if action == "BUY":
            total_cost = quantity * price
            if total_cost > self.balance:
                print(f"❌ Insufficient funds. Need ${total_cost:.2f}, have ${self.balance:.2f}")
                return False

            self.balance -= total_cost

            if symbol not in self.portfolio:
                self.portfolio[symbol] = {"quantity": 0, "avg_price": 0}

            # Update average price
            current_qty = self.portfolio[symbol]["quantity"]
            current_avg = self.portfolio[symbol]["avg_price"]
            new_qty = current_qty + quantity
            new_avg = ((current_qty * current_avg) + (quantity * price)) / new_qty

            self.portfolio[symbol]["quantity"] = new_qty
            self.portfolio[symbol]["avg_price"] = new_avg

            trade = {
                "timestamp": timestamp,
                "action": "BUY",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total": total_cost,
                "balance_after": self.balance,
                "reasoning": reasoning
            }
            self.trade_history.append(trade)
            print(f"✅ Bought {quantity} shares of {symbol} at ${price:.2f}")
            return True

        elif action == "SELL":
            if symbol not in self.portfolio or self.portfolio[symbol]["quantity"] < quantity:
                print(f"❌ Insufficient shares. Have {self.portfolio.get(symbol, {}).get('quantity', 0)} shares")
                return False

            total_revenue = quantity * price
            self.balance += total_revenue

            self.portfolio[symbol]["quantity"] -= quantity

            # Remove from portfolio if quantity is 0
            if self.portfolio[symbol]["quantity"] == 0:
                del self.portfolio[symbol]

            trade = {
                "timestamp": timestamp,
                "action": "SELL",
                "symbol": symbol,
                "quantity": quantity,
                "price": price,
                "total": total_revenue,
                "balance_after": self.balance,
                "reasoning": reasoning
            }
            self.trade_history.append(trade)
            print(f"✅ Sold {quantity} shares of {symbol} at ${price:.2f}")
            return True

        return False

    def make_decision(self, symbol: str) -> Optional[Dict]:
        """Analyze market and make trading decision"""
        print(f"\n🔍 Analyzing {symbol}...")

        # Get market data
        market_data = self.get_market_data(symbol)
        if not market_data:
            print(f"❌ Could not fetch market data for {symbol}")
            return None

        # Get AI recommendation
        decision = self.analyze_with_ai(market_data)

        print(f"🤖 AI Decision: {decision['action']} (Confidence: {decision['confidence']:.0%})")
        print(f"💭 Reasoning: {decision['reasoning']}")

        # Execute trade if confidence is high enough (lowered threshold to be more active)
        if decision['confidence'] >= 0.5:
            if decision['action'] == "BUY":
                # Calculate quantity based on available balance
                max_affordable = int(self.balance / market_data['current_price'])
                suggested_qty = decision.get('suggested_quantity', 1)
                quantity = min(max_affordable, suggested_qty) if suggested_qty else max(1, max_affordable // 10)

                if quantity > 0:
                    self.execute_trade(
                        symbol,
                        "BUY",
                        quantity,
                        market_data['current_price'],
                        decision['reasoning']
                    )

            elif decision['action'] == "SELL":
                if symbol in self.portfolio:
                    quantity = self.portfolio[symbol]["quantity"]
                    self.execute_trade(
                        symbol,
                        "SELL",
                        quantity,
                        market_data['current_price'],
                        decision['reasoning']
                    )

        return decision

    def calculate_portfolio_value(self) -> float:
        """Calculate total portfolio value (cash + holdings)"""
        total_value = self.balance

        for symbol, holding in self.portfolio.items():
            market_data = self.get_market_data(symbol, period="1d")
            if market_data:
                total_value += holding["quantity"] * market_data["current_price"]

        return total_value

    def get_performance_stats(self) -> Dict:
        """Get performance statistics"""
        portfolio_value = self.calculate_portfolio_value()
        total_return = portfolio_value - self.initial_balance
        return_pct = (total_return / self.initial_balance) * 100

        # Calculate holdings value
        holdings_value = 0
        holdings_detail = []
        for symbol, holding in self.portfolio.items():
            market_data = self.get_market_data(symbol, period="1d")
            if market_data:
                current_value = holding["quantity"] * market_data["current_price"]
                holdings_value += current_value
                cost_basis = holding["quantity"] * holding["avg_price"]
                pnl = current_value - cost_basis
                pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0

                holdings_detail.append({
                    "symbol": symbol,
                    "quantity": holding["quantity"],
                    "avg_price": holding["avg_price"],
                    "current_price": market_data["current_price"],
                    "current_value": current_value,
                    "cost_basis": cost_basis,
                    "pnl": pnl,
                    "pnl_pct": pnl_pct
                })

        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.balance,
            "holdings_value": holdings_value,
            "total_portfolio_value": portfolio_value,
            "total_return": total_return,
            "return_percentage": return_pct,
            "total_trades": len(self.trade_history),
            "holdings": holdings_detail
        }

    def save_state(self, filename: str = "agent_state.json"):
        """Save agent state to file"""
        state = {
            "name": self.name,
            "initial_balance": self.initial_balance,
            "balance": self.balance,
            "portfolio": self.portfolio,
            "trade_history": self.trade_history,
            "performance_history": self.performance_history
        }
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        print(f"💾 State saved to {filename}")

    def load_state(self, filename: str = "agent_state.json"):
        """Load agent state from file"""
        try:
            with open(filename, 'r') as f:
                state = json.load(f)
            self.name = state["name"]
            self.initial_balance = state["initial_balance"]
            self.balance = state["balance"]
            self.portfolio = state["portfolio"]
            self.trade_history = state["trade_history"]
            self.performance_history = state.get("performance_history", [])
            print(f"📂 State loaded from {filename}")
        except FileNotFoundError:
            print(f"⚠️ No saved state found at {filename}")
