const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface MarketData {
  symbol: string;
  current_price: number;
  previous_close: number;
  change_percent: number;
  volume: number;
  high_52w: number;
  low_52w: number;
  company_name: string;
  sector: string;
  historical_data: {
    Date: string[];
    Open: number[];
    High: number[];
    Low: number[];
    Close: number[];
    Volume: number[];
  };
  data_source?: string;
}

export interface AgentStatus {
  name: string;
  initialized: boolean;
  initial_balance: number;
  current_balance: number;
  holdings_value: number;
  total_portfolio_value: number;
  total_return: number;
  return_percentage: number;
  total_trades: number;
  holdings: Holding[];
}

export interface Holding {
  symbol: string;
  quantity: number;
  avg_price: number;
  current_price: number;
  current_value: number;
  cost_basis: number;
  pnl: number;
  pnl_pct: number;
}

export interface Trade {
  timestamp: string;
  action: 'BUY' | 'SELL';
  symbol: string;
  quantity: number;
  price: number;
  total: number;
  balance_after: number;
  reasoning: string;
}

export interface Decision {
  action: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  reasoning: string;
  suggested_quantity?: number;
  ai_full_response?: string;
}

export const api = {
  // Agent management
  initializeAgent: async (name: string, balance: number, apiKey?: string) => {
    const res = await fetch(`${API_BASE_URL}/agent/initialize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, initial_balance: balance, api_key: apiKey || '' }),
    });
    return res.json();
  },

  getAgentStatus: async (): Promise<AgentStatus> => {
    const res = await fetch(`${API_BASE_URL}/agent/status`);
    if (!res.ok) throw new Error('Failed to fetch agent status');
    return res.json();
  },

  // Trading decisions
  makeDecision: async (symbol: string): Promise<Decision> => {
    const res = await fetch(`${API_BASE_URL}/agent/decide`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ symbol }),
    });
    return res.json();
  },

  // Market data
  getMarketData: async (symbol: string, period: string = '1mo', interval: string = '1d'): Promise<MarketData> => {
    const res = await fetch(`${API_BASE_URL}/market/${symbol}?period=${period}&interval=${interval}`);
    if (!res.ok) throw new Error('Failed to fetch market data');
    return res.json();
  },

  // Trade history
  getTradeHistory: async (): Promise<{ trades: Trade[]; total_trades: number }> => {
    const res = await fetch(`${API_BASE_URL}/agent/history`);
    return res.json();
  },

  // Portfolio
  getPortfolio: async () => {
    const res = await fetch(`${API_BASE_URL}/agent/portfolio`);
    return res.json();
  },

  // Check if backend is running
  healthCheck: async (): Promise<boolean> => {
    try {
      const res = await fetch(`${API_BASE_URL}/`);
      return res.ok;
    } catch {
      return false;
    }
  },
};
