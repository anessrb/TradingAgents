from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
from trading_agent import TradingAgent
import os

app = FastAPI(title="Trading Agent API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent: Optional[TradingAgent] = None

# Request models
class InitializeAgentRequest(BaseModel):
    name: str
    initial_balance: float
    api_key: Optional[str] = None

class TradeRequest(BaseModel):
    symbol: str

class ManualTradeRequest(BaseModel):
    symbol: str
    action: str
    quantity: int

@app.get("/")
def read_root():
    return {
        "message": "Trading Agent API is running!",
        "agent_initialized": agent is not None
    }

@app.post("/agent/initialize")
def initialize_agent(request: InitializeAgentRequest):
    """Initialize a new trading agent"""
    global agent
    api_key = request.api_key or os.getenv("MISTRAL_API_KEY")
    agent = TradingAgent(
        name=request.name,
        initial_balance=request.initial_balance,
        api_key=api_key
    )
    return {
        "message": f"Agent '{request.name}' initialized",
        "initial_balance": request.initial_balance,
        "has_api_key": bool(api_key)
    }

@app.get("/agent/status")
def get_agent_status():
    """Get current agent status"""
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")

    stats = agent.get_performance_stats()
    return {
        "name": agent.name,
        "initialized": True,
        **stats
    }

@app.post("/agent/decide")
def make_decision(request: TradeRequest):
    """Let agent analyze and make trading decision"""
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")

    decision = agent.make_decision(request.symbol)
    if not decision:
        raise HTTPException(status_code=400, detail="Could not make decision")

    return decision

@app.post("/agent/trade")
def execute_manual_trade(request: ManualTradeRequest):
    """Execute a manual trade"""
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")

    market_data = agent.get_market_data(request.symbol)
    if not market_data:
        raise HTTPException(status_code=400, detail="Could not fetch market data")

    success = agent.execute_trade(
        request.symbol,
        request.action,
        request.quantity,
        market_data["current_price"],
        "Manual trade"
    )

    if not success:
        raise HTTPException(status_code=400, detail="Trade execution failed")

    return {"message": "Trade executed successfully"}

@app.get("/agent/portfolio")
def get_portfolio():
    """Get current portfolio"""
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")

    return {
        "balance": agent.balance,
        "holdings": agent.portfolio,
        "portfolio_value": agent.calculate_portfolio_value()
    }

@app.get("/agent/history")
def get_trade_history():
    """Get trade history"""
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")

    return {
        "trades": agent.trade_history,
        "total_trades": len(agent.trade_history)
    }

@app.get("/market/{symbol}")
def get_market_data(symbol: str, period: str = "1mo", interval: str = "1d"):
    """Get market data for a symbol with custom interval for scalping"""
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")

    from market_data_service import MarketDataService
    data = MarketDataService.get_market_data(symbol, period, interval)
    if not data:
        raise HTTPException(status_code=404, detail="Market data not found")

    return data

@app.post("/agent/save")
def save_agent_state(filename: str = "agent_state.json"):
    """Save agent state to file"""
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized")

    agent.save_state(filename)
    return {"message": f"State saved to {filename}"}

@app.post("/agent/load")
def load_agent_state(filename: str = "agent_state.json"):
    """Load agent state from file"""
    global agent
    if not agent:
        # Create a temporary agent to load state
        agent = TradingAgent("temp", 0)

    try:
        agent.load_state(filename)
        return {"message": f"State loaded from {filename}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
