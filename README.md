# 🤖 AI Trading Agents

An AI-powered trading simulation platform that uses **Mistral AI** to make autonomous trading decisions with real market data from **Yahoo Finance**. Watch your AI agent trade stocks with a virtual budget and track its performance through beautiful charts and statistics.

## ✨ Features

- 🤖 **AI-Powered Trading**: Uses Mistral AI to analyze markets and make trading decisions
- 📊 **Real Market Data**: Fetches live stock data from Yahoo Finance
- 💰 **Virtual Trading**: Simulate trading with no real money at risk
- 📈 **Interactive Dashboard**: Beautiful Streamlit UI with charts and statistics
- 🔄 **Auto-Trading Mode**: Let the agent continuously monitor and trade selected stocks
- 📉 **Performance Tracking**: Track portfolio value, returns, and individual trade performance
- 💾 **State Persistence**: Save and load agent state to continue sessions

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Mistral API (Optional)

The agent can work in two modes:
- **With Mistral AI**: Intelligent AI-driven trading decisions
- **Without API Key**: Uses a simple momentum-based fallback strategy

To use Mistral AI:
1. Get a free API key from [Mistral Console](https://console.mistral.ai/)
2. Copy `.env.example` to `.env`
3. Add your API key to `.env`:
   ```
   MISTRAL_API_KEY=your_api_key_here
   ```

### 3. Start the Backend

Open a terminal and run:

```bash
python backend.py
```

The API will start on `http://localhost:8000`

### 4. Start the Dashboard

Open a **second terminal** and run:

```bash
streamlit run dashboard.py
```

The dashboard will open in your browser automatically!

## 🎮 How to Use

### Quick Test (See AI Thinking in Terminal)

Want to see what the AI is thinking? Run this test script:

```bash
python test_agent.py
```

This will show you the AI's raw decision-making process in the terminal!

### Initialize Your Agent

1. In the sidebar, enter:
   - **Agent Name**: Give your agent a name (e.g., "MistralTrader")
   - **Initial Balance**: Set your virtual budget (e.g., $10,000)
   - **API Key**: Leave empty (your key is already saved in .env)
2. Click "Initialize Agent"

### Make Trading Decisions

**Manual Trading:**
1. Select a stock from the dropdown or enter a custom symbol
2. Click "🎲 Let AI Decide"
3. The agent will analyze the stock and execute a trade if confident

**Auto-Trading:**
1. Select stocks to monitor
2. Set check interval (how often to analyze)
3. Click "🔄 Start Auto-Trading"
4. Watch your agent trade automatically!

### Monitor Performance

The dashboard now shows:
- **🧠 AI Decision Panel**: See the latest AI decision with full reasoning (expanded by default)
- **📝 Decision Log**: Track recent AI decisions with timestamps
- **Portfolio Tab**: View current holdings, allocation, and performance summary
- **Charts Tab**: Interactive candlestick charts and volume data (click "Load Chart" button)
- **Trade History Tab**: Complete log of all trades with AI reasoning
- **Market Analysis Tab**: Analyze any stock and get AI recommendations

### Key Improvements

✅ **See AI Thinking**: The dashboard now shows the full AI reasoning for every decision
✅ **More Active Trading**: Lowered confidence threshold from 60% to 50%
✅ **Better Charts**: Fixed chart display with proper error handling
✅ **Decision Logging**: Track all recent decisions with timestamps
✅ **Terminal Output**: Backend shows AI's raw responses in real-time

## 📁 Project Structure

```
TradingAgents/
├── trading_agent.py      # Core AI trading agent logic
├── backend.py            # FastAPI REST API
├── dashboard.py          # Streamlit web interface
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## 🔌 API Endpoints

The backend provides a RESTful API:

- `POST /agent/initialize` - Initialize a new trading agent
- `GET /agent/status` - Get current agent status and performance
- `POST /agent/decide` - Let agent analyze and trade a symbol
- `GET /agent/portfolio` - Get current portfolio
- `GET /agent/history` - Get trade history
- `GET /market/{symbol}` - Get market data for a symbol
- `POST /agent/save` - Save agent state
- `POST /agent/load` - Load agent state

View interactive API docs at `http://localhost:8000/docs` when the backend is running.

## 🧠 How the AI Agent Works

1. **Market Analysis**: Fetches real-time data from Yahoo Finance
2. **AI Decision Making**: Mistral AI analyzes:
   - Current price and trends
   - Price changes and momentum
   - Volume patterns
   - 52-week highs/lows
   - Company sector and fundamentals
3. **Trade Execution**: If confidence ≥ 60%, executes BUY/SELL/HOLD
4. **Portfolio Management**: Tracks holdings, calculates returns, maintains balance

### Fallback Strategy (No API Key)

Without a Mistral API key, the agent uses a simple momentum strategy:
- **BUY**: When stock is up >2%
- **SELL**: When stock is down >2%
- **HOLD**: Otherwise

## 📊 Example Workflow

```bash
# Terminal 1 - Start Backend
python backend.py

# Terminal 2 - Start Dashboard
streamlit run dashboard.py

# In the dashboard:
# 1. Initialize agent with $10,000
# 2. Select stocks like AAPL, GOOGL, TSLA
# 3. Let AI analyze and trade
# 4. Watch your portfolio grow (or shrink!)
# 5. Review performance charts and stats
```

## 💡 Popular Stocks to Trade

The dashboard includes these popular stocks:
- **AAPL** - Apple
- **GOOGL** - Google/Alphabet
- **MSFT** - Microsoft
- **AMZN** - Amazon
- **TSLA** - Tesla
- **NVDA** - NVIDIA
- **META** - Meta/Facebook
- **JPM** - JPMorgan Chase
- **V** - Visa
- **WMT** - Walmart

You can also enter any valid stock ticker symbol!

## ⚠️ Disclaimer

**This is for educational and entertainment purposes only!**

- This uses **simulated/virtual money** only
- Not real trading or investment advice
- Past performance doesn't guarantee future results
- Always do your own research before real investing
- The AI's decisions are experimental and may lose money

## 🛠️ Tech Stack

- **AI**: Mistral AI (mistral-small-latest model)
- **Market Data**: Yahoo Finance (yfinance)
- **Backend**: FastAPI, Pydantic, Uvicorn
- **Frontend**: Streamlit, Plotly, Pandas
- **Data Viz**: Interactive candlestick charts, pie charts, metrics

## 🎯 Future Enhancements

Some ideas for future development:
- Multiple agents competing against each other
- Different trading strategies (day trading, swing trading, etc.)
- Risk management and stop-loss orders
- Backtesting on historical data
- Portfolio diversification recommendations
- Email/SMS notifications for trades
- Machine learning for pattern recognition

## 🤝 Contributing

Feel free to fork, modify, and experiment with the code! This is a learning project designed to demonstrate AI capabilities in financial analysis.

## 📝 License

MIT License - feel free to use for learning and experimentation!

---

**Built with Claude Code** - An AI assistant that creates, modifies, and manages code directly in your project! 🚀
