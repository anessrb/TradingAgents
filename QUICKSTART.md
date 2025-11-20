# 🚀 Quick Start Guide

## ⚠️ IMPORTANT: Chart Fix Applied!

The chart data retrieval issue has been **FIXED**. The problem was with timestamp serialization.

## 📦 Step 1: Install Dependencies

```bash
pip3 install -r requirements.txt
```

Or install individually:
```bash
pip3 install fastapi uvicorn pydantic streamlit requests yfinance mistralai plotly pandas
```

## 🧪 Step 2: Test Chart Data (Optional)

Verify the fix works:
```bash
python3 test_charts.py
```

You should see:
- ✅ Success for AAPL, GOOGL, TSLA
- ✅ Data is JSON serializable

## 🚀 Step 3: Start the System

### Option A - Easy (One Script)
```bash
./start.sh
```

### Option B - Manual (Two Terminals)

**Terminal 1 - Backend:**
```bash
python3 backend.py
```

**Terminal 2 - Dashboard:**
```bash
streamlit run dashboard.py
```

## 🎮 Step 4: Use the Dashboard

1. Open browser at `http://localhost:8501`
2. Initialize agent:
   - Name: "MistralTrader"
   - Budget: $10,000
   - API Key: Leave empty (already in .env)
3. Click "🎲 Let AI Decide" on AAPL
4. See the **🧠 AI Decision Panel** appear!
5. Go to **Charts tab** → Click "📊 Load Chart"
6. **Charts should now work!** 🎉

## 🐛 Troubleshooting

### Charts Still Not Working?

1. **Check backend terminal** for errors
2. **Restart both servers**:
   ```bash
   # Kill any running processes
   pkill -f "python3 backend.py"
   pkill -f "streamlit"

   # Restart
   python3 backend.py &
   streamlit run dashboard.py
   ```

3. **Test data retrieval**:
   ```bash
   python3 test_charts.py
   ```

### Backend Not Starting?

```bash
# Check if port 8000 is in use
lsof -ti:8000 | xargs kill -9

# Start backend
python3 backend.py
```

### No Trades Happening?

The agent will trade when:
- Confidence ≥ 50% (AI decision)
- OR price changes ≥ 0.5% (fallback)

Markets might be closed or flat. Try different stocks!

## 📊 What Was Fixed

### Before:
```python
"historical_data": hist.to_dict()  # ❌ Timestamp objects not JSON serializable
```

### After:
```python
historical_data = {
    "Date": [d.isoformat() for d in hist_reset['Date']],  # ✅ ISO format strings
    "Open": hist_reset['Open'].tolist(),
    "High": hist_reset['High'].tolist(),
    # ... etc
}
```

## 🎯 Expected Behavior

1. **Charts Tab**: Click "Load Chart" → See candlestick chart + volume
2. **AI Decisions**: Instant display with full reasoning
3. **Trading**: Happens automatically when confidence ≥ 50%
4. **Backend Terminal**: Shows all AI thinking in real-time

## 💡 Tips

- Watch the **backend terminal** to see AI responses
- **Charts tab** needs you to click "Load Chart" button
- Try **auto-trading** with multiple stocks
- Check **Decision Log** to see all recent decisions

---

**Everything should work now!** 🎉

If you still have issues, the problem might be:
1. Dependencies not installed
2. Backend not running
3. Yahoo Finance API temporarily down (try again in a minute)
