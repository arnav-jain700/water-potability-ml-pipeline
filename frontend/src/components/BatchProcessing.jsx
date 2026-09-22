import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Download, CheckCircle2, AlertTriangle, Search, Filter } from 'lucide-react';
import SpotlightCard from './SpotlightCard';

export default function BatchProcessing({ threshold }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterVerdict, setFilterVerdict] = useState('ALL');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const executeBatchTriage = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('threshold', threshold.toString());

    try {
      const response = await fetch('/api/batch-predict', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to process batch CSV');
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadDemoBatch = () => {
    // Generate realistic demo batch distribution
    const demoPoints = [];
    const demoRows = [];
    for (let i = 0; i < 40; i++) {
      const isSafe = i % 3 !== 0;
      const ph = isSafe ? (6.8 + (i % 7) * 0.2) : (4.0 + (i % 5) * 0.4);
      const sulfate = isSafe ? (280 + (i % 6) * 15) : (420 + (i % 8) * 10);
      const prob = isSafe ? 0.72 + (i % 5) * 0.04 : 0.28 + (i % 4) * 0.05;
      demoPoints.push({
        ph: Math.round(ph * 100) / 100,
        Sulfate: Math.round(sulfate),
        Solids: isSafe ? 18000 + i * 200 : 42000 + i * 500,
        Chloramines: isSafe ? 6.5 + (i % 4) * 0.3 : 11.2 + (i % 3) * 0.4,
        probability: Math.round(prob * 1000) / 1000,
        verdict: isSafe ? 'Potable / Safe' : 'Toxic / Unsafe',
        is_potable: isSafe
      });
      demoRows.push({
        Is_Potable: isSafe,
        Triage_Verdict: isSafe ? 'Potable / Safe' : 'Toxic / Unsafe',
        Confidence_Pct: (prob * 100).toFixed(1),
        ph: ph.toFixed(2),
        Hardness: (180 + i * 2).toFixed(0),
        Solids: (isSafe ? 18000 + i * 200 : 42000 + i * 500).toFixed(0),
        Chloramines: (isSafe ? 6.5 : 11.2).toFixed(1),
        Sulfate: sulfate.toFixed(0),
        Conductivity: (400 + i * 5).toFixed(0),
        Organic_carbon: (isSafe ? 11.0 : 24.0).toFixed(1),
        Trihalomethanes: (isSafe ? 55 : 115).toFixed(0),
        Turbidity: (isSafe ? 3.2 : 6.4).toFixed(1)
      });
    }

    const safeCount = demoPoints.filter(p => p.is_potable).length;
    const toxicCount = demoPoints.length - safeCount;
    setResults({
      summary: {
        total_samples: demoPoints.length,
        safe_count: safeCount,
        toxic_count: toxicCount,
        safe_percentage: Math.round((safeCount / demoPoints.length) * 100),
        toxic_percentage: Math.round((toxicCount / demoPoints.length) * 100),
        threshold_applied: threshold
      },
      scatter_points: demoPoints,
      preview_rows: demoRows,
      csv_data: "ph,Sulfate,Solids,Triage_Verdict\n" + demoPoints.map(p => `${p.ph},${p.Sulfate},${p.Solids},${p.verdict}`).join("\n")
    });
  };

  const downloadCSV = () => {
    if (!results || !results.csv_data) return;
    const blob = new Blob([results.csv_data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'aquaguard_triaged_batch_results.csv';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const filteredRows = results?.preview_rows?.filter((r) => {
    const matchesSearch = searchTerm === '' ||
      Object.values(r).some(val => String(val).toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesVerdict = filterVerdict === 'ALL' ||
      (filterVerdict === 'SAFE' && r.Is_Potable) ||
      (filterVerdict === 'TOXIC' && !r.Is_Potable);
    return matchesSearch && matchesVerdict;
  }) || [];

  return (
    <div className="space-y-6">
      {/* Upload Zone */}
      <SpotlightCard className="p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-lg font-bold text-white mb-1">
              High-Throughput Batch Telemetry Ingestion
            </h3>
            <p className="text-xs text-slate-400">
              Upload municipal sensor telemetry CSV files to score hundreds of water sources simultaneously.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadDemoBatch}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-teal-500/20 border border-teal-500/40 hover:bg-teal-500/30 text-xs font-mono text-teal-300 transition-colors shrink-0 font-bold"
            >
              ⚡ Load Demo Batch (Charts)
            </button>
            <a
              href="/api/batch-template"
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-950 border border-white/10 hover:border-teal-400 text-xs font-mono text-teal-300 transition-colors shrink-0"
            >
              <FileText className="w-4 h-4" />
              Download Template
            </a>
          </div>
        </div>

        <div
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-white/15 rounded-2xl p-8 text-center cursor-pointer hover:border-teal-400/50 hover:bg-teal-500/[0.02] transition-all"
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".csv"
            className="hidden"
          />
          <UploadCloud className="w-10 h-10 text-teal-400 mx-auto mb-3" />
          <p className="text-sm font-semibold text-white mb-1">
            {file ? file.name : "Click or drag & drop municipal telemetry CSV"}
          </p>
          <p className="text-xs text-slate-400">
            Supports standardized 9-parameter water quality logs (up to 10,000 samples)
          </p>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        {file && (
          <div className="mt-4 flex justify-end">
            <button
              onClick={executeBatchTriage}
              disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition-all disabled:opacity-50"
            >
              {loading ? "Processing Batch Ingestion..." : "🚀 Execute Batch Triage Inference"}
            </button>
          </div>
        )}
      </SpotlightCard>

      {/* Results View */}
      {results && (
        <div className="space-y-6">
          {/* Top Metrics Row */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-4">
              <div className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-1">
                Total Ingested Volume
              </div>
              <div className="text-2xl font-mono font-extrabold text-white">
                {results.summary.total_samples} samples
              </div>
            </div>

            <div className="rounded-2xl bg-slate-900/80 border border-emerald-500/30 p-4">
              <div className="text-xs font-mono text-emerald-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Potable Sources Cleared
              </div>
              <div className="text-2xl font-mono font-extrabold text-emerald-400">
                {results.summary.safe_count} ({results.summary.safe_percentage}%)
              </div>
            </div>

            <div className="rounded-2xl bg-slate-900/80 border border-rose-500/30 p-4">
              <div className="text-xs font-mono text-rose-400 uppercase tracking-wider mb-1 flex items-center gap-1.5">
                <AlertTriangle className="w-3.5 h-3.5" />
                Contaminated Flagged
              </div>
              <div className="text-2xl font-mono font-extrabold text-rose-400">
                {results.summary.toxic_count} ({results.summary.toxic_percentage}%)
              </div>
            </div>
          </div>

          {/* Visual Charts: Donut + Scatter Plot */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* SVG Donut */}
            <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-5 flex flex-col items-center justify-center">
              <div className="text-xs font-mono text-slate-400 uppercase tracking-wider mb-3 w-full text-left">
                Safety Ratio
              </div>
              <div className="relative w-40 h-40">
                <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                  <circle
                    cx="18"
                    cy="18"
                    r="15.91549430918954"
                    fill="transparent"
                    stroke="#EF4444"
                    strokeWidth="3.8"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="15.91549430918954"
                    fill="transparent"
                    stroke="#10B981"
                    strokeWidth="3.8"
                    strokeDasharray={`${results.summary.safe_percentage} ${100 - results.summary.safe_percentage}`}
                    strokeDashoffset="0"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center font-mono">
                  <span className="text-xl font-bold text-white">{results.summary.safe_percentage}%</span>
                  <span className="text-[10px] text-emerald-400">POTABLE</span>
                </div>
              </div>
              <div className="flex gap-4 text-xs font-mono mt-4">
                <span className="text-emerald-400">● Safe: {results.summary.safe_count}</span>
                <span className="text-rose-400">● Unsafe: {results.summary.toxic_count}</span>
              </div>
            </div>

            {/* SVG Scatter Plot: pH vs Sulfate */}
            <div className="lg:col-span-2 rounded-2xl bg-slate-900/80 border border-white/10 p-5">
              <div className="flex items-center justify-between mb-3">
                <div className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                  Cluster Distribution: pH vs. Sulfate Minerals
                </div>
                <div className="text-[11px] font-mono text-slate-500">
                  Showing {results.scatter_points.length} sample points
                </div>
              </div>

              <div className="h-56 relative w-full bg-slate-950/60 rounded-xl p-3 border border-white/5">
                <svg viewBox="0 0 500 220" className="w-full h-full overflow-visible">
                  {/* Grid lines */}
                  <line x1="40" y1="20" x2="40" y2="180" stroke="rgba(255,255,255,0.1)" />
                  <line x1="40" y1="180" x2="480" y2="180" stroke="rgba(255,255,255,0.1)" />

                  {/* pH Axis ticks (0 to 14) */}
                  <text x="40" y="200" fill="#64748B" fontSize="9" fontFamily="JetBrains Mono" textAnchor="middle">0</text>
                  <text x="260" y="200" fill="#64748B" fontSize="9" fontFamily="JetBrains Mono" textAnchor="middle">7 (pH)</text>
                  <text x="480" y="200" fill="#64748B" fontSize="9" fontFamily="JetBrains Mono" textAnchor="middle">14</text>

                  {/* Sulfate Axis ticks (100 to 500) */}
                  <text x="32" y="180" fill="#64748B" fontSize="9" fontFamily="JetBrains Mono" textAnchor="end">100</text>
                  <text x="32" y="25" fill="#64748B" fontSize="9" fontFamily="JetBrains Mono" textAnchor="end">500mg</text>

                  {/* Safe pH Envelope Shading (6.5 to 8.5) */}
                  <rect
                    x={40 + (6.5 / 14) * 440}
                    y="20"
                    width={(2.0 / 14) * 440}
                    height="160"
                    fill="rgba(16, 185, 129, 0.06)"
                    stroke="rgba(16, 185, 129, 0.2)"
                    strokeDasharray="3 3"
                  />

                  {/* Scatter Dots */}
                  {results.scatter_points.map((pt, pIdx) => {
                    const cx = 40 + (Math.min(Math.max(pt.ph, 0), 14) / 14) * 440;
                    const cy = 180 - (Math.min(Math.max(pt.Sulfate - 100, 0), 400) / 400) * 160;
                    const color = pt.is_potable ? '#10B981' : '#EF4444';

                    return (
                      <circle
                        key={pIdx}
                        cx={cx}
                        cy={cy}
                        r="3.5"
                        fill={color}
                        opacity="0.8"
                        stroke="#000"
                        strokeWidth="0.5"
                      >
                        <title>{`pH: ${pt.ph}, Sulfate: ${pt.Sulfate}mg/L, Status: ${pt.verdict}`}</title>
                      </circle>
                    );
                  })}
                </svg>
              </div>
            </div>
          </div>

          {/* Scored Results Table */}
          <div className="rounded-2xl bg-slate-900/80 border border-white/10 overflow-hidden">
            <div className="p-4 bg-slate-950/60 border-b border-white/10 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Search parameters or stations..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="bg-slate-900 border border-white/10 rounded-xl pl-8 pr-3 py-1.5 text-xs font-mono text-white focus:outline-none focus:border-teal-400"
                  />
                </div>

                <div className="flex items-center gap-1 text-xs font-mono">
                  {['ALL', 'SAFE', 'TOXIC'].map((mode) => (
                    <button
                      key={mode}
                      onClick={() => setFilterVerdict(mode)}
                      className={`px-2.5 py-1 rounded-lg border transition-colors ${
                        filterVerdict === mode
                          ? 'bg-teal-500/20 border-teal-500/40 text-teal-300 font-bold'
                          : 'bg-slate-900 border-white/10 text-slate-400'
                      }`}
                    >
                      {mode}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={downloadCSV}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-teal-500 hover:bg-teal-400 text-slate-950 font-bold text-xs font-mono uppercase tracking-wider transition-colors"
              >
                <Download className="w-3.5 h-3.5" />
                Export Scored CSV
              </button>
            </div>

            <div className="overflow-x-auto max-h-80 overflow-y-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="sticky top-0 bg-slate-950 border-b border-white/10 text-slate-400 uppercase tracking-wider">
                  <tr>
                    <th className="py-2.5 px-3">Verdict</th>
                    <th className="py-2.5 px-3">Confidence</th>
                    <th className="py-2.5 px-3">pH</th>
                    <th className="py-2.5 px-3">Hardness</th>
                    <th className="py-2.5 px-3">Solids</th>
                    <th className="py-2.5 px-3">Chloramines</th>
                    <th className="py-2.5 px-3">Sulfate</th>
                    <th className="py-2.5 px-3">Conductivity</th>
                    <th className="py-2.5 px-3">TOC</th>
                    <th className="py-2.5 px-3">THMs</th>
                    <th className="py-2.5 px-3">Turbidity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {filteredRows.map((r, i) => (
                    <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          r.Is_Potable
                            ? 'bg-emerald-950/50 text-emerald-400 border border-emerald-500/20'
                            : 'bg-rose-950/50 text-rose-400 border border-rose-500/20'
                        }`}>
                          {r.Triage_Verdict}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-white font-bold">{r.Confidence_Pct}%</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.ph).toFixed(2)}</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.Hardness).toFixed(0)}</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.Solids).toFixed(0)}</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.Chloramines).toFixed(1)}</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.Sulfate).toFixed(0)}</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.Conductivity).toFixed(0)}</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.Organic_carbon).toFixed(1)}</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.Trihalomethanes).toFixed(0)}</td>
                      <td className="py-2 px-3 text-slate-300">{Number(r.Turbidity).toFixed(1)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
