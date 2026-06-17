"use client";

import React, { useState } from "react";

// Pure TS classifier helper for batch analysis
interface PredictResultSimple {
  level1_pred: string;
  level1_conf: number;
  level2_pred: string;
  level2_conf: number;
}

const mockPredict = (text: string): PredictResultSimple => {
  const isViolence = /قتل|مارو|دھماکہ|آگ|نقصان|حملہ|ہلاک|پھانسی|نفرت/g.test(text);
  let level2 = "None";
  let level2Conf = 0.0;
  
  if (isViolence) {
    if (/سیاسی|حکومت|پارٹی/g.test(text)) {
      level2 = "Political";
      level2Conf = 0.842;
    } else if (/فرقے|مذہب|مذہبی|کافر/g.test(text)) {
      level2 = "Religious";
      level2Conf = 0.912;
    } else {
      level2 = "General";
      level2Conf = 0.724;
    }
  }

  return {
    level1_pred: isViolence ? "Violence" : "Non-Violence",
    level1_conf: isViolence ? 0.941 : 0.892,
    level2_pred: level2,
    level2_conf: level2Conf
  };
};

export default function BatchProcess() {
  const [fileContent, setFileContent] = useState<string>("");
  const [fileName, setFileName] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [progress, setProgress] = useState(0);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    
    const reader = new FileReader();
    reader.onload = (event) => {
      setFileContent(event.target?.result as string || "");
    };
    reader.readAsText(file);
  };

  const handleProcess = () => {
    if (!fileContent) return;
    setLoading(true);
    setProgress(0);
    setResults([]);

    const lines = fileContent.split("\n").map(l => l.trim()).filter(l => l !== "");
    const total = lines.length;
    const tempResults: any[] = [];

    // Simulate batch execution over chunks to show progress indicator
    let index = 0;
    const interval = setInterval(() => {
      if (index >= total) {
        clearInterval(interval);
        setResults(tempResults);
        setLoading(false);
        return;
      }
      
      const currentText = lines[index];
      const out = mockPredict(currentText);
      tempResults.push({
        id: index + 1,
        text: currentText,
        level1: out.level1_pred,
        level1_conf: out.level1_conf,
        level2: out.level2_pred,
        level2_conf: out.level2_conf
      });

      index++;
      setProgress(Math.round((index / total) * 100));
    }, 150); // Fast batching simulation
  };

  const handleExport = () => {
    if (results.length === 0) return;
    
    // Create CSV content
    const headers = "ID,Text,Level 1 Prediction,Level 1 Confidence,Level 2 Prediction,Level 2 Confidence\n";
    const rows = results.map(r => 
      `"${r.id}","${r.text.replace(/"/g, '""')}","${r.level1}",${r.level1_conf.toFixed(4)},"${r.level2}",${r.level2_conf.toFixed(4)}`
    ).join("\n");
    
    const blob = new Blob([headers + rows], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `batch_predictions_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-wider uppercase">Batch Processing Terminal</h1>
        <p className="text-sm text-gray-400 mt-1">Upload files containing social posts to execute high-throughput predictions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Control Card */}
        <div className="lg:col-span-1 space-y-6">
          <div className="p-6 rounded-2xl glass-card space-y-5">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">File Ingestion</h3>
            
            {/* Upload Box */}
            <div className="border-2 border-dashed border-gray-800 hover:border-red-500/50 rounded-xl p-6 transition flex flex-col items-center justify-center text-center bg-[#0d1321]/30">
              <svg className="w-10 h-10 text-gray-600 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <label className="cursor-pointer text-xs font-semibold text-red-400 hover:text-red-300 uppercase tracking-widest">
                Browse Files
                <input
                  type="file"
                  accept=".csv,.txt,.json"
                  className="hidden"
                  onChange={handleFileUpload}
                />
              </label>
              <p className="text-[10px] text-gray-500 mt-1">Supports .CSV, .JSON or .TXT newline files</p>
            </div>

            {fileName && (
              <div className="flex justify-between items-center p-3 rounded-xl bg-gray-900/60 border border-gray-800 text-xs">
                <span className="text-white font-mono truncate w-40">{fileName}</span>
                <span className="text-gray-400">{(fileContent.length / 1024).toFixed(1)} KB</span>
              </div>
            )}

            <button
              onClick={handleProcess}
              disabled={loading || !fileContent}
              className="w-full py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-xl transition glow-btn-red text-sm flex items-center justify-center cursor-pointer"
            >
              {loading ? `INGESTING (${progress}%)` : "RUN BATCH CLASSIFICATION"}
            </button>
          </div>

          {/* Reference Template format info */}
          <div className="p-6 rounded-2xl glass-card space-y-3">
            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Required Schema Format</h3>
            <div className="bg-[#070b14] p-3 rounded-lg border border-gray-800 text-[10px] font-mono text-gray-400 space-y-1">
              <p className="text-white font-bold"># CSV Newline Format</p>
              <p>مخالفین پر حملہ کر کے انہیں ہلاک کر دو۔</p>
              <p>امن اور محبت کا پیغام پھیلانا ہی ہمارا مقصد ہے۔</p>
              <p>سیاسی رہنما کی تقریر نے نفرت کو ہوا دی ہے۔</p>
            </div>
          </div>
        </div>

        {/* Right Output Table Card */}
        <div className="lg:col-span-2 space-y-6">
          {results.length > 0 ? (
            <div className="p-6 rounded-2xl glass-card space-y-6">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider">Inference Results Registry</h3>
                  <p className="text-xs text-gray-400 mt-1">Successfully classified {results.length} posts</p>
                </div>
                <button
                  onClick={handleExport}
                  className="px-4 py-2 border border-green-500/30 hover:bg-green-500/10 text-green-400 rounded-xl text-xs font-bold uppercase tracking-wider transition cursor-pointer"
                >
                  Export CSV Report
                </button>
              </div>

              {/* Table list */}
              <div className="overflow-x-auto max-h-[460px] overflow-y-auto pr-2">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="border-b border-gray-800 text-gray-400 font-bold uppercase sticky top-0 bg-[#0c1221] z-10">
                      <th className="pb-3 font-semibold w-12">ID</th>
                      <th className="pb-3 font-semibold">Post Content</th>
                      <th className="pb-3 font-semibold">Threat State</th>
                      <th className="pb-3 font-semibold">Subcategory</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.map((row) => (
                      <tr key={row.id} className="border-b border-gray-800/30 hover:bg-gray-900/10">
                        <td className="py-3.5 font-mono text-gray-500">{row.id}</td>
                        <td className="py-3.5 text-gray-200 max-w-xs truncate dir-rtl text-right pr-6" title={row.text}>
                          {row.text}
                        </td>
                        <td className="py-3.5">
                          <span className={`px-2 py-0.5 rounded font-bold uppercase tracking-widest text-[9px] border ${
                            row.level1 === "Violence"
                              ? "bg-red-950/40 text-red-400 border-red-500/20"
                              : "bg-green-950/40 text-green-400 border-green-500/20"
                          }`}>
                            {row.level1}
                          </span>
                        </td>
                        <td className="py-3.5 text-indigo-400 font-semibold">{row.level2.toUpperCase()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="h-96 rounded-2xl border border-dashed border-gray-800 flex flex-col items-center justify-center text-gray-500 text-sm">
              <svg className="w-12 h-12 text-gray-700 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <span>Ready to scan. Please import a data file on the left console panel.</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
