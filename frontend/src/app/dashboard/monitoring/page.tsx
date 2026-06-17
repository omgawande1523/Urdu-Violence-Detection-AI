"use client";

import React, { useState } from "react";

export default function ModelMonitoring() {
  const [metrics, setMetrics] = useState({
    cpu: 34.2,
    memory: 58.1,
    gpu: 12.0,
    gpuMemory: 22.4,
    latency: 48.2,
    errorCount: 0,
    psiDrift: 0.021
  });

  const [driftHistory, setDriftHistory] = useState([
    { metric: "Level 1 Label Drift (PSI)", score: 0.021, status: "Normal", color: "text-green-400" },
    { metric: "Level 2 Label Drift (PSI)", score: 0.045, status: "Normal", color: "text-green-400" },
    { metric: "Urdu Term Vocabulary Drift", score: 0.112, status: "Warning", color: "text-yellow-400" }
  ]);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-wider uppercase">System Monitoring Console</h1>
        <p className="text-sm text-gray-400 mt-1">Real-time status indicators tracking latency, hardware utilization, and prediction drift</p>
      </div>

      {/* Hardware Utilization Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* CPU Util */}
        <div className="p-6 rounded-2xl glass-card space-y-4">
          <div className="flex justify-between items-center text-xs text-gray-400 font-bold uppercase">
            <span>CPU Load</span>
            <span className="font-mono text-white">{metrics.cpu}%</span>
          </div>
          <div className="w-full bg-[#0d1321] rounded-full h-2 overflow-hidden">
            <div className="h-full bg-indigo-500" style={{ width: `${metrics.cpu}%` }} />
          </div>
        </div>

        {/* Memory Util */}
        <div className="p-6 rounded-2xl glass-card space-y-4">
          <div className="flex justify-between items-center text-xs text-gray-400 font-bold uppercase">
            <span>Memory Load</span>
            <span className="font-mono text-white">{metrics.memory}%</span>
          </div>
          <div className="w-full bg-[#0d1321] rounded-full h-2 overflow-hidden">
            <div className="h-full bg-indigo-500" style={{ width: `${metrics.memory}%` }} />
          </div>
        </div>

        {/* GPU Util */}
        <div className="p-6 rounded-2xl glass-card space-y-4">
          <div className="flex justify-between items-center text-xs text-gray-400 font-bold uppercase">
            <span>GPU Engine</span>
            <span className="font-mono text-white">{metrics.gpu}%</span>
          </div>
          <div className="w-full bg-[#0d1321] rounded-full h-2 overflow-hidden">
            <div className="h-full bg-red-500 animate-pulse" style={{ width: `${metrics.gpu}%` }} />
          </div>
        </div>

        {/* GPU Memory Util */}
        <div className="p-6 rounded-2xl glass-card space-y-4">
          <div className="flex justify-between items-center text-xs text-gray-400 font-bold uppercase">
            <span>GPU Framebuffer</span>
            <span className="font-mono text-white">{metrics.gpuMemory}%</span>
          </div>
          <div className="w-full bg-[#0d1321] rounded-full h-2 overflow-hidden">
            <div className="h-full bg-red-500" style={{ width: `${metrics.gpuMemory}%` }} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Latency History */}
        <div className="p-6 rounded-2xl glass-card space-y-6">
          <div className="flex justify-between items-center">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Historical Request Latency</h3>
            <span className="text-xs text-gray-400 font-mono">Avg: {metrics.latency} ms</span>
          </div>
          {/* Custom SVG chart for Latency */}
          <div className="h-56 w-full bg-[#0d1321]/30 rounded-xl border border-gray-800/50 p-4 relative flex items-end">
            <svg className="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
              <path d="M 0 40 L 0 25 L 10 20 L 20 35 L 30 18 L 40 22 L 50 15 L 60 20 L 70 30 L 80 18 L 90 24 L 100 16 L 100 40 Z" fill="rgba(99, 102, 241, 0.15)" />
              <path d="M 0 25 L 10 20 L 20 35 L 30 18 L 40 22 L 50 15 L 60 20 L 70 30 L 80 18 L 90 24 L 100 16" fill="none" stroke="#6366f1" strokeWidth="1.5" />
            </svg>
            <div className="absolute top-2 left-4 text-[10px] text-gray-500 font-mono">100ms</div>
            <div className="absolute bottom-2 left-4 text-[10px] text-gray-500 font-mono">0ms</div>
          </div>
        </div>

        {/* Data & Model Drift Log */}
        <div className="p-6 rounded-2xl glass-card space-y-6">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Concept & Population Drift Logs</h3>
          <div className="space-y-4">
            {driftHistory.map((log, index) => (
              <div key={index} className="p-4 rounded-xl bg-[#0d1321]/40 border border-gray-800 flex justify-between items-center text-xs">
                <div>
                  <p className="font-semibold text-white">{log.metric}</p>
                  <p className="text-[10px] text-gray-500 mt-0.5">Calculated using Kolmogorov-Smirnov algorithm</p>
                </div>
                <div className="text-right space-y-1">
                  <span className="font-mono text-white font-bold block">{log.score}</span>
                  <span className={`text-[10px] font-bold uppercase ${log.color}`}>{log.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
