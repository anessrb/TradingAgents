import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# Configuration
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="AI Trading Agent Dashboard",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .profit {
        color: #00ff00;
    }
    .loss {
        color: #ff0000;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'agent_initialized' not in st.session_state:
    st.session_state.agent_initialized = False
if 'auto_trade' not in st.session_state:
    st.session_state.auto_trade = False

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_URL}/")
        return response.status_code == 200
    except:
        return False

def initialize_agent(name: str, balance: float, api_key: str = ""):
    """Initialize trading agent"""
    try:
        response = requests.post(
            f"{API_URL}/agent/initialize",
            json={"name": name, "initial_balance": balance, "api_key": api_key}
        )
        return response.status_code == 200
    except:
        return False

def get_agent_status():
    """Get agent status"""
    try:
        response = requests.get(f"{API_URL}/agent/status")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def make_decision(symbol: str):
    """Let agent make trading decision"""
    try:
        response = requests.post(
            f"{API_URL}/agent/decide",
            json={"symbol": symbol}
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_trade_history():
    """Get trade history"""
    try:
        response = requests.get(f"{API_URL}/agent/history")
        if response.status_code == 200:
            return response.json()["trades"]
        return []
    except:
        return []

def get_market_data(symbol: str, period: str = "3mo"):
    """Get market data"""
    try:
        response = requests.get(f"{API_URL}/market/{symbol}?period={period}")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Title
st.title("🤖 AI Trading Agent Dashboard")
st.markdown("---")

# Check backend
if not check_backend():
    st.error("⚠️ Backend is not running! Start it with: `python backend.py`")
    st.stop()

# Sidebar - Agent Setup
with st.sidebar:
    st.header("🎯 Agent Setup")

    if not st.session_state.agent_initialized:
        with st.form("init_form"):
            agent_name = st.text_input("Agent Name", value="MistralTrader")
            initial_balance = st.number_input(
                "Initial Balance ($)",
                min_value=1000.0,
                max_value=1000000.0,
                value=10000.0,
                step=1000.0
            )
            api_key = st.text_input(
                "Mistral API Key (optional)",
                type="password",
                help="Leave empty to use fallback strategy"
            )
            init_button = st.form_submit_button("Initialize Agent")

            if init_button:
                if initialize_agent(agent_name, initial_balance, api_key):
                    st.session_state.agent_initialized = True
                    st.success("✅ Agent initialized!")
                    st.rerun()
                else:
                    st.error("Failed to initialize agent")
    else:
        st.success("✅ Agent Active")

        # Trading controls
        st.markdown("---")
        st.subheader("📊 Trade")

        # Popular stocks
        popular_stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "WMT"]
        selected_stock = st.selectbox("Select Stock", popular_stocks)

        custom_stock = st.text_input("Or enter custom symbol", placeholder="e.g., NFLX")
        trade_symbol = custom_stock.upper() if custom_stock else selected_stock

        if st.button("🎲 Let AI Decide", use_container_width=True):
            with st.spinner(f"Analyzing {trade_symbol}..."):
                decision = make_decision(trade_symbol)
                if decision:
                    st.success("Decision made! Check main panel for details.")
                    time.sleep(1)
                    st.rerun()

        st.markdown("---")
        st.subheader("⚙️ Auto-Trading")
        auto_trade_symbols = st.multiselect(
            "Symbols to monitor",
            popular_stocks,
            default=["AAPL"]
        )
        auto_interval = st.slider("Check interval (seconds)", 10, 300, 60)

        if st.button("🔄 Start Auto-Trading", use_container_width=True):
            st.session_state.auto_trade = True

        if st.button("⏹️ Stop Auto-Trading", use_container_width=True):
            st.session_state.auto_trade = False

# Main content
if not st.session_state.agent_initialized:
    st.info("👈 Initialize your trading agent in the sidebar to get started!")
    st.stop()

# Get agent status
status = get_agent_status()

if status:
    # Performance metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Portfolio Value", f"${status['total_portfolio_value']:,.2f}")

    with col2:
        return_color = "normal" if status['total_return'] >= 0 else "inverse"
        st.metric(
            "Total Return",
            f"${status['total_return']:,.2f}",
            f"{status['return_percentage']:.2f}%",
            delta_color=return_color
        )

    with col3:
        st.metric("Cash Balance", f"${status['current_balance']:,.2f}")

    with col4:
        st.metric("Holdings Value", f"${status['holdings_value']:,.2f}")

    st.markdown("---")

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Portfolio", "📈 Charts", "📜 Trade History", "🔍 Market Analysis"])

    with tab1:
        st.subheader("Current Holdings")

        if status['holdings']:
            holdings_df = pd.DataFrame(status['holdings'])
            holdings_df = holdings_df[[
                'symbol', 'quantity', 'avg_price', 'current_price',
                'current_value', 'pnl', 'pnl_pct'
            ]]
            holdings_df.columns = [
                'Symbol', 'Shares', 'Avg Price', 'Current Price',
                'Value', 'P/L ($)', 'P/L (%)'
            ]

            # Format columns
            holdings_df['Avg Price'] = holdings_df['Avg Price'].apply(lambda x: f"${x:.2f}")
            holdings_df['Current Price'] = holdings_df['Current Price'].apply(lambda x: f"${x:.2f}")
            holdings_df['Value'] = holdings_df['Value'].apply(lambda x: f"${x:,.2f}")
            holdings_df['P/L ($)'] = holdings_df['P/L ($)'].apply(lambda x: f"${x:,.2f}")
            holdings_df['P/L (%)'] = holdings_df['P/L (%)'].apply(lambda x: f"{x:.2f}%")

            st.dataframe(holdings_df, use_container_width=True, hide_index=True)

            # Portfolio allocation pie chart
            st.subheader("Portfolio Allocation")
            pie_data = pd.DataFrame(status['holdings'])
            fig = px.pie(
                pie_data,
                values='current_value',
                names='symbol',
                title='Portfolio Distribution by Value'
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No holdings yet. Start trading to build your portfolio!")

        # Performance summary
        st.subheader("Performance Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Initial Investment", f"${status['initial_balance']:,.2f}")
        with col2:
            st.metric("Total Trades", status['total_trades'])
        with col3:
            roi = status['return_percentage']
            st.metric("ROI", f"{roi:.2f}%")

    with tab2:
        st.subheader("Market Charts")

        chart_symbol = st.selectbox(
            "Select symbol to view",
            [h['symbol'] for h in status['holdings']] if status['holdings'] else ["AAPL"],
            key="chart_symbol"
        )

        period = st.select_slider(
            "Time Period",
            options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y"],
            value="3mo"
        )

        market_data = get_market_data(chart_symbol, period)

        if market_data and market_data.get('historical_data'):
            hist_data = market_data['historical_data']

            # Convert to DataFrame
            df = pd.DataFrame({
                'Date': pd.to_datetime(list(hist_data['Close'].keys())),
                'Close': list(hist_data['Close'].values()),
                'Open': list(hist_data['Open'].values()),
                'High': list(hist_data['High'].values()),
                'Low': list(hist_data['Low'].values()),
                'Volume': list(hist_data['Volume'].values())
            })

            # Candlestick chart
            fig = go.Figure(data=[go.Candlestick(
                x=df['Date'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name=chart_symbol
            )])

            fig.update_layout(
                title=f"{chart_symbol} Price Chart",
                xaxis_title="Date",
                yaxis_title="Price ($)",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Volume chart
            fig_volume = go.Figure(data=[go.Bar(
                x=df['Date'],
                y=df['Volume'],
                name='Volume'
            )])

            fig_volume.update_layout(
                title=f"{chart_symbol} Volume",
                xaxis_title="Date",
                yaxis_title="Volume",
                height=300
            )

            st.plotly_chart(fig_volume, use_container_width=True)

    with tab3:
        st.subheader("Trade History")

        trades = get_trade_history()

        if trades:
            trades_df = pd.DataFrame(trades)
            trades_df = trades_df[[
                'timestamp', 'action', 'symbol', 'quantity',
                'price', 'total', 'balance_after', 'reasoning'
            ]]
            trades_df.columns = [
                'Time', 'Action', 'Symbol', 'Quantity',
                'Price', 'Total', 'Balance After', 'AI Reasoning'
            ]

            # Format columns
            trades_df['Time'] = pd.to_datetime(trades_df['Time']).dt.strftime('%Y-%m-%d %H:%M:%S')
            trades_df['Price'] = trades_df['Price'].apply(lambda x: f"${x:.2f}")
            trades_df['Total'] = trades_df['Total'].apply(lambda x: f"${x:,.2f}")
            trades_df['Balance After'] = trades_df['Balance After'].apply(lambda x: f"${x:,.2f}")

            st.dataframe(trades_df, use_container_width=True, hide_index=True)

            # Trade statistics
            st.subheader("Trade Statistics")
            col1, col2, col3 = st.columns(3)

            buy_trades = [t for t in trades if t['action'] == 'BUY']
            sell_trades = [t for t in trades if t['action'] == 'SELL']

            with col1:
                st.metric("Total Trades", len(trades))
            with col2:
                st.metric("Buy Trades", len(buy_trades))
            with col3:
                st.metric("Sell Trades", len(sell_trades))

        else:
            st.info("No trades yet. Make your first decision!")

    with tab4:
        st.subheader("Market Analysis")

        analysis_symbol = st.text_input("Enter symbol to analyze", value="AAPL")

        if st.button("Analyze"):
            with st.spinner(f"Fetching data for {analysis_symbol}..."):
                market_data = get_market_data(analysis_symbol, "1mo")

                if market_data:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.metric("Company", market_data['company_name'])
                        st.metric("Current Price", f"${market_data['current_price']:.2f}")
                        st.metric("Previous Close", f"${market_data['previous_close']:.2f}")
                        st.metric("Change", f"{market_data['change_percent']:.2f}%")

                    with col2:
                        st.metric("Sector", market_data['sector'])
                        st.metric("Volume", f"{market_data['volume']:,}")
                        st.metric("52W High", f"${market_data['high_52w']:.2f}")
                        st.metric("52W Low", f"${market_data['low_52w']:.2f}")

                    # Let AI analyze
                    if st.button("🤖 Get AI Analysis"):
                        decision = make_decision(analysis_symbol)
                        if decision:
                            st.success(f"**AI Recommendation: {decision['action']}**")
                            st.info(f"Confidence: {decision['confidence']:.0%}")
                            st.write(f"**Reasoning:** {decision['reasoning']}")

# Auto-trading loop
if st.session_state.auto_trade:
    st.info(f"🔄 Auto-trading active for: {', '.join(auto_trade_symbols)}")
    placeholder = st.empty()

    for symbol in auto_trade_symbols:
        with placeholder.container():
            st.write(f"Analyzing {symbol}...")
            decision = make_decision(symbol)
            if decision:
                st.write(f"✅ {symbol}: {decision['action']}")

    time.sleep(auto_interval)
    st.rerun()

# Footer
st.markdown("---")
st.caption("🤖 AI Trading Agent powered by Mistral AI | Data from Yahoo Finance | This is for educational purposes only")
