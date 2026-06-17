"use client";

import React, { useState, useEffect } from "react";

export default function DashboardHome() {
  const [stats, setStats] = useState({
    totalProcessed: 14209,
    violenceDetected: 3824,
    avgLatency: "48.2 ms",
    driftScore: "0.021"
  });

  const [recentAudits, setRecentAudits] = useState([
    { id: 1, user: "admin_oper", action: "Triggered retraining", target: "v2.12", time: "10 mins ago" },
    { id: 2, user: "moderator_beta", action: "Overrode Prediction #48102", target: "Non-Violence -> Political", time: "1 hour ago" },
    { id: 3, user: "system", action: "Ingested Social API batch", target: "500 records", time: "3 hours ago" }
  ]);

  return (
    <div className="space-y-8">
      {/* Welcome Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center p-6 bg-gradient-to-r from-red-950/20 via-slate-900 to-indigo-950/10 rounded-2xl border border-gray-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wider uppercase">Operational Command</h1>
          <p className="text-sm text-gray-400 mt-1">Real-time supervision of violence incitation in Urdu social feeds</p>
        </div>
        <span className="mt-4 md:mt-0 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-xl text-green-400 text-xs font-bold font-mono tracking-wider">
          ACTIVE DEPLOYMENT: XLM-R.V1
        </span>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="p-6 rounded-2xl glass-card border-l-4 border-l-red-500">
          <p className="text-xs text-gray-400 font-bold uppercase tracking-wider">Violence Incidents Detected</p>
          <p className="text-3xl font-extrabold text-white mt-2 text-glow-red">{stats.violenceDetected}</p>
          <span className="text-[10px] text-red-400 font-semibold mt-1 block">{(stats.violenceDetected / stats.totalProcessed * 100).toFixed(1)}% of total posts</span>
        </div>

        <div className="p-6 rounded-2xl glass-card border-l-4 border-l-indigo-500">
          <p className="text-xs text-gray-400 font-bold uppercase tracking-wider">Total Posts Scanned</p>
          <p className="text-3xl font-extrabold text-white mt-2">{stats.totalProcessed}</p>
          <span className="text-[10px] text-green-400 font-semibold mt-1 block">+12.4% weekly increase</span>
        </div>

        <div className="p-6 rounded-2xl glass-card border-l-4 border-l-green-500">
          <p className="text-xs text-gray-400 font-bold uppercase tracking-wider">Avg Infer Latency</p>
          <p className="text-3xl font-extrabold text-white mt-2 text-glow-green">{stats.avgLatency}</p>
          <span className="text-[10px] text-gray-400 font-semibold mt-1 block">XLM-RoBERTa + BiLSTM + Attn</span>
        </div>

        <div className="p-6 rounded-2xl glass-card border-l-4 border-l-yellow-500">
          <p className="text-xs text-gray-400 font-bold uppercase tracking-wider">Psi Data Drift Metric</p>
          <p className="text-3xl font-extrabold text-white mt-2">{stats.driftScore}</p>
          <span className="text-[10px] text-yellow-400 font-semibold mt-1 block">No Action Required</span>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Graph Card */}
        <div className="p-6 rounded-2xl glass-card lg:col-span-2 space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Incitation Volatility Sparkline</h3>
            <span className="text-xs text-gray-500 font-mono">Last 7 Days</span>
          </div>
          {/* Custom SVG Line Chart */}
          <div className="h-64 w-full bg-[#0d1321]/30 rounded-xl border border-gray-800/50 p-4 relative flex items-end">
            <svg className="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
              <defs>
                <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              {/* Path area */}
              <path d="M 0 40 L 0 32 L 15 28 L 30 35 L 45 20 L 60 15 L 75 22 L 90 8 L 100 12 L 100 40 Z" fill="url(#chartGrad)" />
              {/* Line path */}
              <path d="M 0 32 L 15 28 L 30 35 L 45 20 L 60 15 L 75 22 L 90 8 L 100 12" fill="none" stroke="#ef4444" strokeWidth="1.5" strokeLinecap="round" />
            </svg>
            {/* Legend indicators */}
            <div className="absolute bottom-2 left-4 text-[10px] text-gray-500 font-mono">Mon</div>
            <div className="absolute bottom-2 right-4 text-[10px] text-gray-500 font-mono">Sun</div>
          </div>
        </div>

        {/* Labels Distribution */}
        <div className="p-6 rounded-2xl glass-card space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Level 2 Category Share</h3>
          <div className="space-y-4">
            {[
              { category: "Political Violence", count: 1204, percent: 31.4, color: "bg-red-500" },
              { category: "Religious Violence", count: 984, percent: 25.7, color: "bg-yellow-500" },
              { category: "Ethnic Violence", count: 681, percent: 17.8, color: "bg-indigo-500" },
              { category: "Gender Violence", count: 480, percent: 12.5, color: "bg-pink-500" },
              { category: "Economic Violence", count: 282, percent: 7.3, color: "bg-blue-500" },
              { category: "General Violence", count: 193, percent: 5.3, color: "bg-green-500" }
            ].map((item) => (
              <div key={item.category} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-gray-300">{item.category}</span>
                  <span className="text-white font-mono">{item.percent}%</span>
                </div>
                <div className="w-full bg-[#0d1321] rounded-full h-1.5 overflow-hidden">
                  <div className={`h-full ${item.color}`} style={{ width: `${item.percent}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="p-6 rounded-2xl glass-card space-y-6">
        <div className="flex justify-between items-center">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">SecOps Event Log</h3>
          <button className="text-xs text-red-400 hover:text-red-300 font-bold uppercase tracking-wider cursor-pointer">
            View All Audit Logs →
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400 font-bold uppercase">
                <th className="pb-3 font-semibold">Operator</th>
                <th className="pb-3 font-semibold">Operation</th>
                <th className="pb-3 font-semibold">Scope / Resource</th>
                <th className="pb-3 font-semibold text-right">Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {recentAudits.map((audit) => (
                <tr key={audit.id} className="border-b border-gray-800/30 hover:bg-gray-900/10">
                  <td className="py-3.5 font-medium text-white flex items-center space-x-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                    <span>{audit.user}</span>
                  </td>
                  <td className="py-3.5 text-gray-300">{audit.action}</td>
                  <td className="py-3.5 text-gray-500 font-mono">{audit.target}</td>
                  <td className="py-3.5 text-gray-500 text-right font-mono">{audit.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
