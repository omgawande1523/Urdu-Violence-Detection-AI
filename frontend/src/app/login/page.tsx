"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("Analyst"); // Default selectable for demo
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username || !password) {
      setError("Please fill in all fields.");
      return;
    }

    setLoading(true);
    setError("");

    // Simulate login & set localStorage token details
    setTimeout(() => {
      localStorage.setItem("authToken", "simulated-jwt-token-string");
      localStorage.setItem("userRole", role);
      localStorage.setItem("userName", username);
      router.push("/dashboard");
    }, 800);
  };

  return (
    <div className="relative min-h-screen flex items-center justify-center bg-[#070b14] overflow-hidden">
      {/* Background neon blobs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-900/20 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-indigo-900/20 rounded-full blur-3xl" />
      
      <div className="w-full max-w-md p-8 rounded-2xl glass-panel relative z-10">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center p-3 bg-red-950/40 rounded-xl border border-red-500/20 mb-4">
            <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white uppercase">Violence Detection</h1>
          <p className="text-sm text-gray-400 mt-2">Explainable Incitation Monitoring Platform</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-950/50 border border-red-500/30 text-red-400 rounded-lg text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Username</label>
            <input
              type="text"
              className="w-full px-4 py-3 bg-[#0d1321]/60 border border-gray-800 rounded-xl focus:border-red-500 focus:outline-none text-white text-sm transition"
              placeholder="e.g. admin_analyst"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Password</label>
            <input
              type="password"
              className="w-full px-4 py-3 bg-[#0d1321]/60 border border-gray-800 rounded-xl focus:border-red-500 focus:outline-none text-white text-sm transition"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Simulated Role (RBAC Demo)</label>
            <select
              className="w-full px-4 py-3 bg-[#0d1321]/60 border border-gray-800 rounded-xl focus:border-red-500 focus:outline-none text-white text-sm transition"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            >
              <option value="Admin">Admin (Full Control)</option>
              <option value="Moderator">Moderator (Auditing & Review)</option>
              <option value="Analyst">Analyst (Inference & Data Analysis)</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-red-600 text-white font-bold rounded-xl hover:bg-red-500 transition glow-btn-red text-sm flex items-center justify-center cursor-pointer"
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
            ) : "AUTHENTICATE"}
          </button>
        </form>
        
        <div className="mt-6 text-center text-xs text-gray-500">
          Secure biometric & JWT encrypted session gateway.
        </div>
      </div>
    </div>
  );
}
