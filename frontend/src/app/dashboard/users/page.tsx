"use client";

import React, { useState } from "react";

export default function UserManagement() {
  const [users, setUsers] = useState([
    { id: 1, name: "admin_oper", email: "admin@threatdetect.net", role: "Admin", status: "Active" },
    { id: 2, name: "moderator_beta", email: "moderator_beta@threatdetect.net", role: "Moderator", status: "Active" },
    { id: 3, name: "analyst_demo", email: "analyst_demo@threatdetect.net", role: "Analyst", status: "Active" }
  ]);

  const [audits, setAudits] = useState([
    { id: 501, user: "admin_oper", action: "User Created", resource: "user/moderator_beta", ip: "192.168.1.104", time: "2026-06-17 10:14:02" },
    { id: 502, user: "moderator_beta", action: "Prediction Override", resource: "prediction/48102", ip: "192.168.1.109", time: "2026-06-17 11:42:19" },
    { id: 503, user: "analyst_demo", action: "Batch Prediction Ingestion", resource: "batch/2209", ip: "10.0.0.12", time: "2026-06-17 12:05:51" },
    { id: 504, user: "admin_oper", action: "Model Version Retrained", resource: "model/v2.12", ip: "192.168.1.104", time: "2026-06-17 13:00:00" }
  ]);

  const [newUsername, setNewUsername] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newRole, setNewRole] = useState("Analyst");

  const handleAddUser = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername || !newEmail) return;

    const newUser = {
      id: users.length + 1,
      name: newUsername,
      email: newEmail,
      role: newRole,
      status: "Active"
    };

    setUsers([...users, newUser]);
    
    // Add audit entry
    const newAudit = {
      id: audits.length + 501,
      user: "admin_oper",
      action: "User Created",
      resource: `user/${newUsername}`,
      ip: "127.0.0.1",
      time: new Date().toISOString().slice(0, 19).replace('T', ' ')
    };
    setAudits([newAudit, ...audits]);
    
    // Reset inputs
    setNewUsername("");
    setNewEmail("");
    setNewRole("Analyst");
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-wider uppercase">Access Command & Auditing</h1>
        <p className="text-sm text-gray-400 mt-1">Audit security logs and edit user credentials under RBAC policies</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Add User Control Card */}
        <div className="lg:col-span-1 space-y-6">
          <div className="p-6 rounded-2xl glass-card space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">Create User Credentials</h3>
            
            <form onSubmit={handleAddUser} className="space-y-4">
              <div>
                <label className="block text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1.5">Username</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 bg-[#0d1321]/60 border border-gray-800 rounded-lg focus:border-red-500 focus:outline-none text-white text-xs transition"
                  placeholder="e.g. analyst_john"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1.5">Email Address</label>
                <input
                  type="email"
                  className="w-full px-3 py-2 bg-[#0d1321]/60 border border-gray-800 rounded-lg focus:border-red-500 focus:outline-none text-white text-xs transition"
                  placeholder="e.g. john@threatdetect.net"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-gray-400 uppercase tracking-widest mb-1.5">Role Permission</label>
                <select
                  className="w-full px-3 py-2 bg-[#0d1321]/60 border border-gray-800 rounded-lg focus:border-red-500 focus:outline-none text-white text-xs transition"
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                >
                  <option value="Admin">Admin</option>
                  <option value="Moderator">Moderator</option>
                  <option value="Analyst">Analyst</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full py-2.5 bg-red-600 hover:bg-red-500 text-white font-bold rounded-lg text-xs tracking-wider transition glow-btn-red cursor-pointer"
              >
                PROVISION CREDENTIALS
              </button>
            </form>
          </div>
        </div>

        {/* User Database & Audit log Table list */}
        <div className="lg:col-span-2 space-y-6">
          {/* User database table */}
          <div className="p-6 rounded-2xl glass-card space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">Operator Registry</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-gray-800 text-gray-400 font-bold uppercase">
                    <th className="pb-3">Username</th>
                    <th className="pb-3">Email Address</th>
                    <th className="pb-3">System Role</th>
                    <th className="pb-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} className="border-b border-gray-800/30 hover:bg-gray-900/10">
                      <td className="py-3.5 font-bold text-white">{u.name}</td>
                      <td className="py-3.5 text-gray-300">{u.email}</td>
                      <td className="py-3.5">
                        <span className="bg-red-950/40 text-red-400 border border-red-500/10 px-2 py-0.5 rounded font-bold uppercase text-[9px]">
                          {u.role}
                        </span>
                      </td>
                      <td className="py-3.5 text-right text-green-400 font-bold">{u.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Audit Trail */}
          <div className="p-6 rounded-2xl glass-card space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider font-mono">Secops Audit Log</h3>
            <div className="overflow-x-auto max-h-56 overflow-y-auto pr-2">
              <table className="w-full text-left border-collapse text-xs">
                <thead>
                  <tr className="border-b border-gray-800 text-gray-400 font-bold uppercase sticky top-0 bg-[#0c1221] z-10">
                    <th className="pb-3">Operator</th>
                    <th className="pb-3">Operation</th>
                    <th className="pb-3">Resource Target</th>
                    <th className="pb-3">Origin IP</th>
                    <th className="pb-3 text-right">Date/Time</th>
                  </tr>
                </thead>
                <tbody>
                  {audits.map((a) => (
                    <tr key={a.id} className="border-b border-gray-800/30 hover:bg-gray-900/10">
                      <td className="py-3 font-semibold text-white">{a.user}</td>
                      <td className="py-3 text-gray-300">{a.action}</td>
                      <td className="py-3 text-gray-500 font-mono">{a.resource}</td>
                      <td className="py-3 text-gray-500 font-mono">{a.ip}</td>
                      <td className="py-3 text-gray-500 text-right font-mono">{a.time}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
