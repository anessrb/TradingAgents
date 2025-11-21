'use client';

import { useState, useEffect, useCallback } from 'react';
import { api, type AgentStatus, type Decision } from '@/lib/api';
import InitializeAgent from '@/components/InitializeAgent';
import Dashboard from '@/components/Dashboard';

export default function Home() {
  const [isBackendRunning, setIsBackendRunning] = useState<boolean | null>(null);
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check backend health
  useEffect(() => {
    const checkBackend = async () => {
      const isRunning = await api.healthCheck();
      setIsBackendRunning(isRunning);
    };
    checkBackend();
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, []);

  // Fetch agent status
  const refreshStatus = useCallback(async (showLoading = false) => {
    try {
      if (showLoading) {
        setIsLoading(true);
      }
      const status = await api.getAgentStatus();
      setAgentStatus(status);
    } catch (error) {
      setAgentStatus(null);
    } finally {
      if (showLoading) {
        setIsLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    if (isBackendRunning) {
      refreshStatus(true); // Show loading on initial fetch
    }
  }, [isBackendRunning, refreshStatus]);

  if (isBackendRunning === null || isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center">
        <div className="animate-pulse text-blue-400 text-xl">Loading...</div>
      </div>
    );
  }

  if (!isBackendRunning) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center p-4">
        <div className="bg-red-500/10 backdrop-blur-xl border border-red-500/30 rounded-2xl p-8 max-w-md shadow-2xl">
          <div className="text-4xl mb-4">⚠️</div>
          <h2 className="text-2xl font-bold text-red-400 mb-4">Backend Offline</h2>
          <p className="text-gray-300 mb-4">
            Start the trading backend first:
          </p>
          <code className="block bg-slate-950 text-green-400 p-4 rounded-lg font-mono text-sm">
            source .venv/bin/activate<br/>
            python3 backend.py
          </code>
        </div>
      </div>
    );
  }

  if (!agentStatus) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 flex items-center justify-center p-4">
        <InitializeAgent onInitialized={refreshStatus} />
      </div>
    );
  }

  return <Dashboard agentStatus={agentStatus} refreshStatus={refreshStatus} />;
}
