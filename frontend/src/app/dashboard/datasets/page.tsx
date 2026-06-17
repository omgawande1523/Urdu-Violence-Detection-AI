"use client";

import React, { useState } from "react";

export default function DatasetManagement() {
  const [datasets, setDatasets] = useState([
    { id: 1, name: "Urdu_Social_Violence_Base", tag: "v1.0.0", count: 12000, hash: "dvc-sha-94a8bc", created: "2026-05-12" },
    { id: 2, name: "Urdu_Election_Threat_Feed", tag: "v1.1.0-elections", count: 2209, hash: "dvc-sha-481cfc", created: "2026-06-01" },
    { id: 3, name: "Moderator_Annotated_Overrides", tag: "v2.0.0-retrain", count: 450, hash: "dvc-sha-a3b4c9", created: "2026-06-15" }
  ]);

  // Annotation Review Queue State
  const [reviewQueue, setReviewQueue] = useState([
    { id: 101, text: "ان تمام کرپٹ سیاستدانوں کو سرعام پھانسی دے دینی چاہئے۔", predictedL1: "Violence", predictedL2: "Political", finalL1: "", finalL2: "" },
    { id: 102, text: "حکومت کو غریب عوام کے لیے آٹے کی قیمتوں میں فوری کمی کرنی چاہئے۔", predictedL1: "Non-Violence", predictedL2: "None", finalL1: "", finalL2: "" },
    { id: 103, text: "اس خاص فرقے کے لوگوں کے کاروبار کا بائیکاٹ کریں اور انہیں نقصان پہنچائیں۔", predictedL1: "Violence", predictedL2: "Religious", finalL1: "", finalL2: "" }
  ]);

  const [activeReviewIdx, setActiveReviewIdx] = useState(0);

  const handleOverride = (l1: string, l2: string) => {
    const updated = [...reviewQueue];
    updated[activeReviewIdx].finalL1 = l1;
    updated[activeReviewIdx].finalL2 = l2;
    setReviewQueue(updated);
    
    // Go to next review item
    if (activeReviewIdx < reviewQueue.length - 1) {
      setActiveReviewIdx(activeReviewIdx + 1);
    }
  };

  const handleRetrain = async () => {
    alert("Retraining pipeline has been successfully queued using MLflow. Check active model status in the Model Monitoring tab.");
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center p-6 bg-gradient-to-r from-red-950/20 via-slate-900 to-indigo-950/10 rounded-2xl border border-gray-800">
        <div>
          <h1 className="text-xl font-bold text-white tracking-wider uppercase">Dataset Management & Registry</h1>
          <p className="text-sm text-gray-400 mt-1">Manage versioned gold datasets and run moderator annotation audits</p>
        </div>
        <button
          onClick={handleRetrain}
          className="mt-4 md:mt-0 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-xl text-xs tracking-wider transition glow-btn-indigo cursor-pointer"
        >
          TRIGGER MLFLOW RETRAINING
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Side: Dataset Registry */}
        <div className="lg:col-span-1 space-y-6">
          <div className="p-6 rounded-2xl glass-card space-y-5">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">Dataset Registry</h3>
            <div className="space-y-4">
              {datasets.map((dataset) => (
                <div key={dataset.id} className="p-4 rounded-xl bg-[#0d1321]/40 border border-gray-800 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-semibold text-white truncate w-32">{dataset.name}</span>
                    <span className="text-[10px] bg-red-950/40 text-red-400 border border-red-500/10 px-2 py-0.5 rounded font-bold">{dataset.tag}</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[10px] text-gray-400 font-mono">
                    <div>Records: <span className="text-gray-200">{dataset.count}</span></div>
                    <div>Created: <span className="text-gray-200">{dataset.created}</span></div>
                  </div>
                  <div className="text-[10px] text-gray-500 font-mono truncate">DVC Hash: {dataset.hash}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Side: Annotation Review queue */}
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl glass-card space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Moderator Annotation Audit</h3>
                <p className="text-xs text-gray-400 mt-1">Audit predictions, check drift labels, and override weights.</p>
              </div>
              <span className="text-xs text-gray-500 font-mono">Item {activeReviewIdx + 1} of {reviewQueue.length}</span>
            </div>

            {/* Current Item Panel */}
            {activeReviewIdx < reviewQueue.length ? (
              <div className="space-y-6">
                {/* Urdu Post Display */}
                <div className="p-6 bg-[#0c111f] rounded-xl border border-gray-800 dir-rtl text-right text-lg text-white font-semibold">
                  {reviewQueue[activeReviewIdx].text}
                </div>

                {/* Predictions display */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-gray-900/40 border border-gray-800 text-xs">
                    <span className="text-gray-400 uppercase font-semibold">Model Pred Level 1</span>
                    <p className="text-md font-bold text-red-400 mt-1">{reviewQueue[activeReviewIdx].predictedL1}</p>
                  </div>
                  <div className="p-4 rounded-xl bg-gray-900/40 border border-gray-800 text-xs">
                    <span className="text-gray-400 uppercase font-semibold">Model Pred Level 2</span>
                    <p className="text-md font-bold text-indigo-400 mt-1">{reviewQueue[activeReviewIdx].predictedL2.toUpperCase()}</p>
                  </div>
                </div>

                {/* Audit controls */}
                <div className="space-y-4">
                  <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest">Select Override Outcome</h4>
                  <div className="flex flex-wrap gap-3">
                    <button
                      onClick={() => handleOverride("Non-Violence", "None")}
                      className="px-4 py-2.5 bg-green-500/10 hover:bg-green-500/20 text-green-400 rounded-xl text-xs font-bold uppercase border border-green-500/20 transition cursor-pointer"
                    >
                      Audit Safe (Non-Violence)
                    </button>
                    
                    {["Gender", "Economic", "Ethnic", "Political", "Religious", "General"].map((cat) => (
                      <button
                        key={cat}
                        onClick={() => handleOverride("Violence", cat)}
                        className="px-4 py-2.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-xl text-xs font-bold uppercase border border-red-500/20 transition cursor-pointer"
                      >
                        Override to {cat}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-gray-500 text-sm">
                <svg className="w-12 h-12 text-green-500 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                </svg>
                <span>Audit Queue Completed. Newly saved tags have been pushed to DVC registry.</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
