'use client';

import { useState, useEffect } from 'react';
import { api, type AgentStatus, type Decision, type MarketData } from '@/lib/api';
import { formatCurrency, formatPercent, formatNumber } from '@/lib/utils';
import { TrendingUp, TrendingDown, Activity, DollarSign, Target, Zap, BarChart3, Clock, Plus, Trash2 } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface Props {
  agentStatus: AgentStatus;
  refreshStatus: () => Promise<void>;
}

export default function Dashboard({ agentStatus, refreshStatus }: Props) {
  const [watchlist, setWatchlist] = useState<string[]>(['AAPL', 'GOOGL', 'TSLA']);
  const [newSymbol, setNewSymbol] = useState('');
  const [interval, setInterval] = useState<'1m' | '5m' | '15m' | '1d'>('1m');
  const [period, setPeriod] = useState('1d');
  const [isTrading, setIsTrading] = useState(false);
  const [lastDecisions, setLastDecisions] = useState<Map<string, Decision & { symbol: string }>>(new Map());
  const [marketDataMap, setMarketDataMap] = useState<Map<string, MarketData>>(new Map());
  const [autoTrade, setAutoTrade] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');

  const popularStocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'WMT'];

  // Refresh balance every second
  useEffect(() => {
    const interval = setInterval(() => {
      refreshStatus();
    }, 1000);
    return () => clearInterval(interval);
  }, [refreshStatus]);

  // Fetch market data for all watchlist symbols
  const loadAllMarketData = async () => {
    for (const symbol of watchlist) {
      try {
        const data = await api.getMarketData(symbol, period, interval);
        setMarketDataMap(prev => new Map(prev).set(symbol, data));
      } catch (error) {
        console.error(`Failed to load ${symbol}:`, error);
      }
    }
  };

  useEffect(() => {
    loadAllMarketData();
    const intervalId = setInterval(loadAllMarketData, 30000); // Refresh every 30s
    return () => clearInterval(intervalId);
  }, [watchlist, interval, period]);

  // Auto-trade all symbols in watchlist
  useEffect(() => {
    if (!autoTrade) return;

    const tradeAll = async () => {
      for (const symbol of watchlist) {
        try {
          const decision = await api.makeDecision(symbol);
          setLastDecisions(prev => new Map(prev).set(symbol, { ...decision, symbol }));
          await refreshStatus();
        } catch (error) {
          console.error(`Failed to trade ${symbol}:`, error);
        }
      }
    };

    tradeAll(); // Initial trade
    const intervalId = setInterval(tradeAll, interval === '1m' ? 60000 : interval === '5m' ? 300000 : 900000);
    return () => clearInterval(intervalId);
  }, [autoTrade, watchlist, interval]);

  const handleAddSymbol = () => {
    if (newSymbol && !watchlist.includes(newSymbol.toUpperCase())) {
      setWatchlist([...watchlist, newSymbol.toUpperCase()]);
      setNewSymbol('');
    }
  };

  const handleRemoveSymbol = (symbol: string) => {
    setWatchlist(watchlist.filter(s => s !== symbol));
  };

  const handleTradeOne = async (symbol: string) => {
    setIsTrading(true);
    try {
      const decision = await api.makeDecision(symbol);
      setLastDecisions(prev => new Map(prev).set(symbol, { ...decision, symbol }));
      await refreshStatus();
    } catch (error) {
      console.error('Trading failed:', error);
    } finally {
      setIsTrading(false);
    }
  };

  const chartData = marketDataMap.get(selectedSymbol)?.historical_data.Date.map((date, i) => ({
    time: interval === '1d' ? date : date.split(' ')[1] || date,
    price: marketDataMap.get(selectedSymbol)!.historical_data.Close[i],
    volume: marketDataMap.get(selectedSymbol)!.historical_data.Volume[i],
  })).slice(-100) || [];

  const isProfit = agentStatus.total_return >= 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-4xl">🤖</div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                  AI Trading Dashboard
                </h1>
                <p className="text-gray-600 text-sm">Agent: {agentStatus.name}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-green-100 px-4 py-2 rounded-full border border-green-300">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-700 text-sm font-medium">Live</span>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Interval</div>
                <div className="text-sm font-bold text-blue-600">{interval}</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            icon={<DollarSign className="w-6 h-6" />}
            label="Portfolio Value"
            value={formatCurrency(agentStatus.total_portfolio_value)}
            change={formatPercent(agentStatus.return_percentage)}
            isPositive={isProfit}
            color="blue"
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6" />}
            label="Total Return"
            value={formatCurrency(agentStatus.total_return)}
            change={`${agentStatus.total_trades} trades`}
            isPositive={isProfit}
            color="purple"
          />
          <StatCard
            icon={<Activity className="w-6 h-6" />}
            label="Cash Balance"
            value={formatCurrency(agentStatus.current_balance)}
            change={`${agentStatus.holdings.length} positions`}
            isPositive={true}
            color="green"
          />
          <StatCard
            icon={<Target className="w-6 h-6" />}
            label="Holdings Value"
            value={formatCurrency(agentStatus.holdings_value)}
            change="Active trades"
            isPositive={agentStatus.holdings_value > 0}
            color="pink"
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Watchlist & Control */}
          <div className="lg:col-span-1 space-y-4">
            {/* Watchlist Management */}
            <div className="bg-white/80 backdrop-blur-xl border border-gray-200 rounded-2xl p-6 shadow-lg">
              <h3 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-600" />
                Watchlist
              </h3>

              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={newSymbol}
                  onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                  onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
                  placeholder="Add symbol..."
                  className="flex-1 px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={handleAddSymbol}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <Plus className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-2">
                {watchlist.map(symbol => {
                  const data = marketDataMap.get(symbol);
                  const decision = lastDecisions.get(symbol);
                  return (
                    <div key={symbol} className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 border border-gray-200">
                      <div className="flex items-center justify-between mb-2">
                        <button
                          onClick={() => setSelectedSymbol(symbol)}
                          className={`font-bold text-lg ${selectedSymbol === symbol ? 'text-blue-600' : 'text-gray-800'}`}
                        >
                          {symbol}
                        </button>
                        <button
                          onClick={() => handleRemoveSymbol(symbol)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      {data && (
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">${data.current_price.toFixed(2)}</span>
                          <span className={data.change_percent >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                            {formatPercent(data.change_percent)}
                          </span>
                        </div>
                      )}
                      {decision && (
                        <div className="mt-2 text-xs">
                          <span className={`px-2 py-1 rounded-full font-medium ${
                            decision.action === 'BUY' ? 'bg-green-100 text-green-700' :
                            decision.action === 'SELL' ? 'bg-red-100 text-red-700' :
                            'bg-yellow-100 text-yellow-700'
                          }`}>
                            {decision.action} ({(decision.confidence * 100).toFixed(0)}%)
                          </span>
                        </div>
                      )}
                      <button
                        onClick={() => handleTradeOne(symbol)}
                        disabled={isTrading}
                        className="w-full mt-2 bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-medium py-2 rounded-lg transition text-sm"
                      >
                        Trade
                      </button>
                    </div>
                  );
                })}
              </div>

              <div className="mt-4 space-y-2">
                <div>
                  <label className="block text-sm text-gray-600 mb-2">Interval</label>
                  <div className="grid grid-cols-4 gap-2">
                    {(['1m', '5m', '15m', '1d'] as const).map(int => (
                      <button
                        key={int}
                        onClick={() => setInterval(int)}
                        className={`py-2 rounded-lg font-medium transition ${
                          interval === int
                            ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {int}
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  onClick={() => setAutoTrade(!autoTrade)}
                  className={`w-full font-bold py-3 rounded-lg transition-all shadow-lg ${
                    autoTrade
                      ? 'bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white'
                      : 'bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white'
                  }`}
                >
                  {autoTrade ? '⏹️ Stop Auto-Trading' : '▶️ Start Auto-Trading'}
                </button>

                {autoTrade && (
                  <div className="bg-yellow-50 border border-yellow-300 rounded-lg p-3 text-yellow-700 text-sm flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Trading {watchlist.length} stocks every {interval === '1m' ? '1 min' : interval === '5m' ? '5 min' : '15 min'}
                  </div>
                )}
              </div>
            </div>

            {/* Portfolio Holdings */}
            {agentStatus.holdings.length > 0 && (
              <div className="bg-white/80 backdrop-blur-xl border border-gray-200 rounded-2xl p-6 shadow-lg">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Portfolio</h3>
                <div className="space-y-3">
                  {agentStatus.holdings.map((holding) => (
                    <div key={holding.symbol} className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-3 border border-gray-200">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-bold text-gray-800">{holding.symbol}</span>
                        <span className="text-sm text-gray-600">{holding.quantity} shares</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">P/L</span>
                        <span className={holding.pnl >= 0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                          {formatCurrency(holding.pnl)} ({formatPercent(holding.pnl_pct)})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chart & Decisions */}
          <div className="lg:col-span-2 space-y-4">
            {/* Chart */}
            <div className="bg-white/80 backdrop-blur-xl border border-gray-200 rounded-2xl p-6 shadow-lg">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-purple-600" />
                  {selectedSymbol} Chart ({interval})
                </h3>
                {marketDataMap.get(selectedSymbol) && (
                  <div className="text-sm text-gray-600">
                    {marketDataMap.get(selectedSymbol)!.data_source === 'simulated' ? '⚠️ Simulated' : '✅ Real'} Data
                  </div>
                )}
              </div>

              {chartData.length > 0 ? (
                <div className="space-y-4">
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={chartData}>
                        <defs>
                          <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <XAxis dataKey="time" stroke="#9ca3af" tick={{ fill: '#6b7280', fontSize: 12 }} tickLine={false} />
                        <YAxis domain={['auto', 'auto']} stroke="#9ca3af" tick={{ fill: '#6b7280', fontSize: 12 }} tickLine={false} tickFormatter={(value) => `$${value.toFixed(2)}`} />
                        <Tooltip
                          contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e5e7eb', borderRadius: '8px', color: '#000' }}
                          labelStyle={{ color: '#6b7280' }}
                        />
                        <Area type="monotone" dataKey="price" stroke="#8b5cf6" strokeWidth={3} fillOpacity={1} fill="url(#colorPrice)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ) : (
                <div className="h-96 flex items-center justify-center text-gray-400">
                  Loading chart data...
                </div>
              )}
            </div>

            {/* AI Decisions */}
            {Array.from(lastDecisions.values()).slice(0, 3).map(decision => (
              <div key={decision.symbol} className="bg-gradient-to-r from-purple-100 via-blue-100 to-pink-100 backdrop-blur-xl border border-purple-300 rounded-2xl p-6 shadow-lg">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
                      🧠 {decision.symbol} Decision
                    </h3>
                  </div>
                  <div className={`px-4 py-2 rounded-full font-bold ${
                    decision.action === 'BUY' ? 'bg-green-200 text-green-800 border-2 border-green-400' :
                    decision.action === 'SELL' ? 'bg-red-200 text-red-800 border-2 border-red-400' :
                    'bg-yellow-200 text-yellow-800 border-2 border-yellow-400'
                  }`}>
                    {decision.action}
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <div className="text-gray-600 text-sm">Confidence</div>
                    <div className="text-2xl font-bold text-gray-800">{(decision.confidence * 100).toFixed(0)}%</div>
                  </div>
                  {decision.suggested_quantity && (
                    <div>
                      <div className="text-gray-600 text-sm">Quantity</div>
                      <div className="text-2xl font-bold text-gray-800">{decision.suggested_quantity}</div>
                    </div>
                  )}
                </div>
                <div className="bg-white/60 rounded-xl p-4">
                  <div className="text-gray-600 text-sm mb-2">💭 Reasoning:</div>
                  <div className="text-gray-800">{decision.reasoning}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, change, isPositive, color }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  change: string;
  isPositive: boolean;
  color: 'blue' | 'purple' | 'green' | 'pink';
}) {
  const colorClasses = {
    blue: 'from-blue-100 to-blue-50 border-blue-200 text-blue-600',
    purple: 'from-purple-100 to-purple-50 border-purple-200 text-purple-600',
    green: 'from-green-100 to-green-50 border-green-200 text-green-600',
    pink: 'from-pink-100 to-pink-50 border-pink-200 text-pink-600',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} backdrop-blur-xl border rounded-2xl p-6 hover:shadow-lg transition-all`}>
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 bg-white/60 rounded-xl ${colorClasses[color].split(' ')[3]}`}>
          {icon}
        </div>
        <div className={`text-sm font-medium px-3 py-1 rounded-full ${
          isPositive ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`}>
          {change}
        </div>
      </div>
      <div className="text-gray-600 text-sm mb-1">{label}</div>
      <div className="text-2xl font-bold text-gray-800">{value}</div>
    </div>
  );
}
