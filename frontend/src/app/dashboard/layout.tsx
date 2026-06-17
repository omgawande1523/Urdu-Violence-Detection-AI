"use client";

import React, { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";

interface NavItem {
  name: string;
  path: string;
  icon: React.ReactNode;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [userName, setUserName] = useState("analyst_demo");
  const [userRole, setUserRole] = useState("Analyst");
  const [systemHealthy, setSystemHealthy] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      router.push("/login");
      return;
    }
    setUserName(localStorage.getItem("userName") || "analyst_demo");
    setUserRole(localStorage.getItem("userRole") || "Analyst");
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userRole");
    localStorage.removeItem("userName");
    router.push("/login");
  };

  const navItems: NavItem[] = [
    {
      name: "Dashboard Home",
      path: "/dashboard",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
        </svg>
      ),
    },
    {
      name: "Live Analysis",
      path: "/dashboard/predictions",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
    },
    {
      name: "Batch Process",
      path: "/dashboard/batch",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
    },
    {
      name: "Datasets registry",
      path: "/dashboard/datasets",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
        </svg>
      ),
    },
    {
      name: "Monitoring & drift",
      path: "/dashboard/monitoring",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
    },
    {
      name: "User Management",
      path: "/dashboard/users",
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="flex min-h-screen bg-[#070b14]">
      {/* Sidebar */}
      <aside className="w-64 bg-[#0a0f1d] border-r border-gray-800 flex flex-col justify-between">
        <div>
          {/* Logo */}
          <div className="p-6 border-b border-gray-800 flex items-center space-x-3">
            <span className="w-3 h-3 rounded-full bg-red-500 animate-pulse" />
            <h2 className="text-md font-bold tracking-widest text-white uppercase">AVIP URDU</h2>
          </div>
          
          {/* Nav Links */}
          <nav className="p-4 space-y-2">
            {navItems.map((item) => {
              const active = pathname === item.path;
              return (
                <Link
                  key={item.name}
                  href={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition cursor-pointer ${
                    active
                      ? "bg-red-950/40 text-red-400 border border-red-500/20"
                      : "text-gray-400 hover:text-white hover:bg-gray-800/30"
                  }`}
                >
                  {item.icon}
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>

        {/* User Card */}
        <div className="p-4 border-t border-gray-800 space-y-4">
          <div className="flex items-center space-x-3 p-2 rounded-xl bg-gray-900/50">
            <div className="w-10 h-10 rounded-full bg-red-900/30 flex items-center justify-center border border-red-500/20 text-white font-bold uppercase">
              {userName.slice(0, 2)}
            </div>
            <div>
              <p className="text-sm font-semibold text-white truncate w-32">{userName}</p>
              <span className="text-[10px] bg-red-950/40 text-red-400 px-2 py-0.5 rounded border border-red-500/10 font-bold uppercase">
                {userRole}
              </span>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="w-full py-2.5 border border-gray-800 hover:border-red-500/30 text-gray-400 hover:text-red-400 rounded-xl text-xs font-semibold tracking-wider transition cursor-pointer"
          >
            LOGOUT GATEWAY
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <header className="h-16 border-b border-gray-800 bg-[#070b14]/50 backdrop-blur px-8 flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <h1 className="text-sm font-bold tracking-widest text-gray-400 uppercase">
              Security Operations Center
            </h1>
            <div className="flex items-center space-x-2 text-xs">
              <span className={`w-2.5 h-2.5 rounded-full ${systemHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-gray-400">System State:</span>
              <span className={`font-semibold ${systemHealthy ? 'text-green-400' : 'text-red-400'}`}>
                {systemHealthy ? 'ACTIVE / SECURE' : 'DRIFTING / ALERT'}
              </span>
            </div>
          </div>
          
          <div className="text-xs text-gray-500 font-mono">
            {new Date().toISOString().slice(0, 10)} SECURE GATEWAY
          </div>
        </header>

        {/* Dynamic Route Content */}
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </div>
    </div>
  );
}
