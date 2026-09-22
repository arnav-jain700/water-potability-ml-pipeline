import React, { useState } from 'react';
import { AlertCircle, CheckCircle2, ChevronDown, ChevronUp, Table } from 'lucide-react';
import SpotlightCard from './SpotlightCard';

export default function CulpritDiagnostics({ violations, auditTable }) {
  const [showAuditTable, setShowAuditTable] = useState(true);

  return (
    <div className="space-y-6">
      {/* Chemical Culprits Section */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
            <span>🚨 Detected Chemical Culprits</span>
            {violations.length > 0 && (
              <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 text-[10px] px-2 py-0.5 rounded-full font-bold">
                {violations.length} CRITICAL BREACHES
              </span>
            )}
          </h3>
        </div>

        {violations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {violations.map((v) => (
              <SpotlightCard
                key={v.parameter}
                spotlightColor="rgba(239, 68, 68, 0.18)"
                borderColor="rgba(239, 68, 68, 0.35)"
                className="p-3.5 border-l-4 border-l-rose-500"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-semibold text-rose-300 text-sm flex items-center gap-1.5">
                    <span>{v.icon}</span>
                    <span>{v.name}</span>
                  </span>
                  <span className="text-[10px] font-mono font-bold bg-rose-500/20 text-rose-300 px-1.5 py-0.5 rounded border border-rose-500/30">
                    BREACH
                  </span>
                </div>
                <div className="font-mono text-base font-bold text-white mb-0.5">
                  {v.formatted_reading}
                </div>
                <div className="text-xs text-slate-300">
                  {v.boundary}
                </div>
              </SpotlightCard>
            ))}
          </div>
        ) : (
          <div className="p-4 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-emerald-300 text-sm flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            <div>
              <strong className="text-emerald-200">Optimal Physicochemical Profile:</strong> All 9 sensor parameters strictly conform to EPA and WHO drinking water envelopes. Zero contaminants detected.
            </div>
          </div>
        )}
      </div>

      {/* Physicochemical Regulatory Audit Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-white/10 overflow-hidden">
        <button
          onClick={() => setShowAuditTable(!showAuditTable)}
          className="w-full p-4 flex items-center justify-between bg-slate-950/40 hover:bg-slate-900/80 transition-colors text-left"
        >
          <span className="text-sm font-semibold text-white flex items-center gap-2">
            <Table className="w-4 h-4 text-teal-400" />
            Physicochemical Regulatory Audit
          </span>
          <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
            <span>{showAuditTable ? 'Hide Table' : 'Show All 9 Parameters'}</span>
            {showAuditTable ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {showAuditTable && (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 border-b border-white/10 text-slate-400 font-mono uppercase tracking-wider">
                <tr>
                  <th className="py-2.5 px-4">Parameter</th>
                  <th className="py-2.5 px-4">Current Reading</th>
                  <th className="py-2.5 px-4">WHO Guideline Envelope</th>
                  <th className="py-2.5 px-4">Regulatory Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono">
                {auditTable.map((item, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-2.5 px-4 text-slate-200 font-sans font-medium">
                      {item.parameter}
                    </td>
                    <td className="py-2.5 px-4 text-white font-bold">
                      {item.reading}
                    </td>
                    <td className="py-2.5 px-4 text-slate-400">
                      {item.guideline}
                    </td>
                    <td className="py-2.5 px-4">
                      {item.in_bounds ? (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-emerald-950/50 text-emerald-400 border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3" /> Within Guideline
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-rose-950/50 text-rose-400 border border-rose-500/20">
                          <AlertCircle className="w-3 h-3" /> Guideline Breach
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
