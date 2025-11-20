'use client';

import { useState, useEffect } from 'react';
import { api, type AgentStatus, type Decision, type MarketData } from '@/lib/api';
import { formatCurrency, formatPercent, formatNumber } from '@/lib/utils';
import { TrendingUp, TrendingDown, Activity, DollarSign, Target, Zap, BarChart3, Clock } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface Props {
  agentStatus: AgentStatus;
  refreshStatus: () => Promise<void>;
}

export default function Dashboard({ agentStatus, refreshStatus }: Props) {
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [interval, setInterval] = useState<'1m' | '5m' | '15m' | '1d'>('1m');
  const [period, setPeriod] = useState('1d');
  const [isTrading, setIsTrading] = useState(false);
  const [lastDecision, setLastDecision] = useState<(Decision & { symbol: string }) | null>(null);
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [autoScalp, setAutoScalp] = useState(false);

  const popularStocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META'];

  // Fetch market data
  const loadMarketData = async () => {
    try {
      const data = await api.getMarketData(selectedSymbol, period, interval);
      setMarketData(data);
    } catch (error) {
      console.error('Failed to load market data:', error);
    }
  };

  useEffect(() => {
    loadMarketData();
  }, [selectedSymbol, interval, period]);

  // Make trading decision
  const handleTrade = async () => {
    setIsTrading(true);
    try {
      const decision = await api.makeDecision(selectedSymbol);
      setLastDecision({ ...decision, symbol: selectedSymbol });
      await refreshStatus();
    } catch (error) {
      console.error('Trading failed:', error);
    } finally {
      setIsTrading(false);
    }
  };

  // Auto-scalp every minute
  useEffect(() => {
    if (!autoScalp) return;

    const intervalId = setInterval(async () => {
      await handleTrade();
    }, interval === '1m' ? 60000 : interval === '5m' ? 300000 : 900000);

    return () => clearInterval(intervalId);
  }, [autoScalp, interval]);

  // Prepare chart data
  const chartData = marketData?.historical_data.Date.map((date, i) => ({
    time: interval === '1d' ? date : date.split(' ')[1] || date,
    price: marketData.historical_data.Close[i],
    volume: marketData.historical_data.Volume[i],
  })).slice(-100) || []; // Last 100 points

  const isProfit = agentStatus.total_return >= 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950">
      {/* Header */}
      <header className="bg-slate-900/50 backdrop-blur-xl border-b border-slate-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="text-4xl">🤖</div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                  AI Scalping Dashboard
                </h1>
                <p className="text-gray-400 text-sm">Agent: {agentStatus.name}</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 bg-green-500/10 px-4 py-2 rounded-full border border-green-500/30">
                <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-green-400 text-sm font-medium">Live</span>
              </div>
              <div className="text-right">
                <div className="text-xs text-gray-500">Interval</div>
                <div className="text-sm font-bold text-blue-400">{interval}</div>
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
          />
          <StatCard
            icon={<TrendingUp className="w-6 h-6" />}
            label="Total Return"
            value={formatCurrency(agentStatus.total_return)}
            change={`${agentStatus.total_trades} trades`}
            isPositive={isProfit}
          />
          <StatCard
            icon={<Activity className="w-6 h-6" />}
            label="Cash Balance"
            value={formatCurrency(agentStatus.current_balance)}
            change={`${agentStatus.holdings.length} positions`}
            isPositive={true}
          />
          <StatCard
            icon={<Target className="w-6 h-6" />}
            label="Holdings Value"
            value={formatCurrency(agentStatus.holdings_value)}
            change="Active trades"
            isPositive={agentStatus.holdings_value > 0}
          />
        </div>

        {/* AI Decision Panel */}
        {lastDecision && (
          <div className="bg-gradient-to-r from-purple-900/20 via-blue-900/20 to-purple-900/20 backdrop-blur-xl border border-purple-500/30 rounded-2xl p-6 shadow-2xl">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  🧠 Latest AI Decision
                  <span className="text-sm font-normal text-gray-400">({lastDecision.symbol})</span>
                </h3>
              </div>
              <div className={`px-4 py-2 rounded-full font-bold ${
                lastDecision.action === 'BUY' ? 'bg-green-500/20 text-green-400 border border-green-500/50' :
                lastDecision.action === 'SELL' ? 'bg-red-500/20 text-red-400 border border-red-500/50' :
                'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50'
              }`}>
                {lastDecision.action === 'BUY' ? '🟢' : lastDecision.action === 'SELL' ? '🔴' : '🟡'} {lastDecision.action}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <div className="text-gray-400 text-sm">Confidence</div>
                <div className="text-2xl font-bold text-white">{(lastDecision.confidence * 100).toFixed(0)}%</div>
              </div>
              {lastDecision.suggested_quantity && (
                <div>
                  <div className="text-gray-400 text-sm">Suggested Quantity</div>
                  <div className="text-2xl font-bold text-white">{lastDecision.suggested_quantity}</div>
                </div>
              )}
            </div>
            <div className="bg-slate-900/50 rounded-xl p-4">
              <div className="text-gray-400 text-sm mb-2">💭 AI Reasoning:</div>
              <div className="text-white">{lastDecision.reasoning}</div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Trading Panel */}
          <div className="lg:col-span-1 space-y-4">
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Scalping Control
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-2">Stock Symbol</label>
                  <select
                    value={selectedSymbol}
                    onChange={(e) => setSelectedSymbol(e.target.value)}
                    className="w-full bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2 text-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  >
                    {popularStocks.map(stock => (
                      <option key={stock} value={stock}>{stock}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm text-gray-400 mb-2">Interval</label>
                  <div className="grid grid-cols-4 gap-2">
                    {(['1m', '5m', '15m', '1d'] as const).map(int => (
                      <button
                        key={int}
                        onClick={() => setInterval(int)}
                        className={`py-2 rounded-lg font-medium transition ${
                          interval === int
                            ? 'bg-blue-500 text-white'
                            : 'bg-slate-800/50 text-gray-400 hover:bg-slate-700/50'
                        }`}
                      >
                        {int}
                      </button>
                    ))}
                  </div>
                </div>

                {marketData && (
                  <div className="bg-slate-800/30 rounded-lg p-4 space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-400 text-sm">Current Price</span>
                      <span className="text-white font-bold">${marketData.current_price.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400 text-sm">Change</span>
                      <span className={marketData.change_percent >= 0 ? 'text-green-400' : 'text-red-400'}>
                        {formatPercent(marketData.change_percent)}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400 text-sm">Volume</span>
                      <span className="text-white text-sm">{formatNumber(marketData.volume)}</span>
                    </div>
                  </div>
                )}

                <button
                  onClick={handleTrade}
                  disabled={isTrading}
                  className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-3 rounded-lg transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
                >
                  {isTrading ? (
                    <span className="flex items-center justify-center gap-2">
                      <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                      Analyzing...
                    </span>
                  ) : (
                    '🎲 Let AI Decide'
                  )}
                </button>

                <button
                  onClick={() => setAutoScalp(!autoScalp)}
                  className={`w-full font-bold py-3 rounded-lg transition-all ${
                    autoScalp
                      ? 'bg-red-500 hover:bg-red-600 text-white'
                      : 'bg-slate-800/50 hover:bg-slate-700/50 text-gray-300'
                  }`}
                >
                  {autoScalp ? '⏹️ Stop Auto-Scalping' : '▶️ Start Auto-Scalping'}
                </button>

                {autoScalp && (
                  <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 text-yellow-400 text-sm flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    Auto-trading every {interval === '1m' ? '1 min' : interval === '5m' ? '5 min' : '15 min'}
                  </div>
                )}
              </div>
            </div>

            {/* Holdings */}
            {agentStatus.holdings.length > 0 && (
              <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">Portfolio</h3>
                <div className="space-y-3">
                  {agentStatus.holdings.map((holding) => (
                    <div key={holding.symbol} className="bg-slate-800/30 rounded-lg p-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-bold text-white">{holding.symbol}</span>
                        <span className="text-sm text-gray-400">{holding.quantity} shares</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">P/L</span>
                        <span className={holding.pnl >= 0 ? 'text-green-400' : 'text-red-400'}>
                          {formatCurrency(holding.pnl)} ({formatPercent(holding.pnl_pct)})
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chart */}
          <div className="lg:col-span-2">
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-400" />
                  {selectedSymbol} Chart ({interval})
                </h3>
                {marketData && (
                  <div className="text-sm text-gray-400">
                    {marketData.data_source === 'simulated' ? '⚠️ Simulated' : '✅ Real'} Data
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
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <XAxis
                          dataKey="time"
                          stroke="#64748b"
                          tick={{ fill: '#94a3b8', fontSize: 12 }}
                          tickLine={false}
                        />
                        <YAxis
                          domain={['auto', 'auto']}
                          stroke="#64748b"
                          tick={{ fill: '#94a3b8', fontSize: 12 }}
                          tickLine={false}
                          tickFormatter={(value) => `$${value.toFixed(2)}`}
                        />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                          labelStyle={{ color: '#94a3b8' }}
                        />
                        <Area
                          type="monotone"
                          dataKey="price"
                          stroke="#3b82f6"
                          strokeWidth={2}
                          fillOpacity={1}
                          fill="url(#colorPrice)"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="h-32">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={chartData}>
                        <XAxis dataKey="time" hide />
                        <YAxis hide />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '8px',
                            color: '#fff'
                          }}
                        />
                        <Area
                          type="monotone"
                          dataKey="volume"
                          stroke="#8b5cf6"
                          strokeWidth={0}
                          fillOpacity={0.6}
                          fill="#8b5cf6"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              ) : (
                <div className="h-96 flex items-center justify-center text-gray-500">
                  Loading chart data...
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, change, isPositive }: {
  icon: React.ReactNode;
  label: string;
  value: string;
  change: string;
  isPositive: boolean;
}) {
  return (
    <div className="bg-gradient-to-br from-slate-900/90 to-slate-800/90 backdrop-blur-xl border border-slate-700 rounded-2xl p-6 hover:border-blue-500/50 transition-all">
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 bg-blue-500/10 rounded-xl text-blue-400">
          {icon}
        </div>
        <div className={`text-sm font-medium px-3 py-1 rounded-full ${
          isPositive ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
        }`}>
          {change}
        </div>
      </div>
      <div className="text-gray-400 text-sm mb-1">{label}</div>
      <div className="text-2xl font-bold text-white">{value}</div>
    </div>
  );
}
