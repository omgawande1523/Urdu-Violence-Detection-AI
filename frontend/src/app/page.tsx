"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (token) {
      router.push("/dashboard");
    } else {
      router.push("/login");
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-[#070b14] flex items-center justify-center">
      <div className="animate-pulse flex flex-col items-center space-y-4">
        <div className="w-12 h-12 rounded-full border-4 border-t-red-500 border-gray-800 animate-spin" />
        <p className="text-gray-400 text-xs tracking-widest font-mono">ESTABLISHING SECURE CONNECTION...</p>
      </div>
    </div>
  );
}
