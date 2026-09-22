import React from 'react';
import SpotlightCard from './SpotlightCard';
import CountUp from './CountUp';
import { CheckCircle2, AlertTriangle, Shield, AlertCircle } from 'lucide-react';

export default function SpotlightVerdictCard({ prediction }) {
  if (!prediction) return null;

  const isPotable = prediction.is_potable;
  const spotlightColor = isPotable ? 'rgba(16, 185, 129, 0.22)' : 'rgba(239, 68, 68, 0.25)';
  const borderColor = isPotable ? 'rgba(16, 185, 129, 0.45)' : 'rgba(239, 68, 68, 0.45)';
  const scoreColor = isPotable ? '#34D399' : '#F87171';
  const deltaColor = prediction.delta_pct >= 0 ? '#34D399' : '#F87171';
  const deltaFormatted = prediction.delta_pct >= 0 ? `+${prediction.delta_pct.toFixed(1)}%` : `${prediction.delta_pct.toFixed(1)}%`;

  return (
    <SpotlightCard
      spotlightColor={spotlightColor}
      borderColor={borderColor}
      className={`p-6 mb-6 shadow-xl transition-all ${
        isPotable ? 'shadow-emerald-950/30' : 'shadow-rose-950/30'
      }`}
    >
      {/* Status Badge */}
      <div className="flex items-center justify-between gap-3 mb-3">
        <div
          className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-bold uppercase tracking-wider border ${
            isPotable
              ? 'bg-emerald-950/50 text-emerald-400 border-emerald-500/30'
              : 'bg-rose-950/50 text-rose-400 border-rose-500/30'
          }`}
        >
          <span className="relative flex h-2 w-2">
            <span
              className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                isPotable ? 'bg-emerald-400' : 'bg-rose-400'
              }`}
            />
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                isPotable ? 'bg-emerald-500' : 'bg-rose-500'
              }`}
            />
          </span>
          <span>{isPotable ? 'POTABLE / SAFE' : 'CONTAMINATED / UNFIT'}</span>
        </div>

        <span className="text-xs font-mono text-slate-400 flex items-center gap-1">
          <Shield className="w-3.5 h-3.5 text-teal-400" />
          Policy τ = {prediction.threshold.toFixed(2)}
        </span>
      </div>

      {/* Main Verdict Title */}
      <h2 className="text-xl md:text-2xl font-bold text-white tracking-tight mb-2 flex items-center gap-2.5">
        {isPotable ? (
          <>
            <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />
            <span>Cleared for Human Consumption</span>
          </>
        ) : (
          <>
            <AlertTriangle className="w-6 h-6 text-rose-400 shrink-0" />
            <span>Hazardous Contaminant Warning</span>
          </>
        )}
      </h2>

      {/* Advisory Message */}
      <p
        className="text-sm text-slate-300 leading-relaxed mb-6"
        dangerouslySetInnerHTML={{ __html: prediction.advisory }}
      />

      {/* 4-KPI Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 pt-4 border-t border-white/10">
        <div className="bg-slate-950/60 rounded-xl p-3 border border-white/5">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Potability Score
          </div>
          <div className="text-xl font-mono font-extrabold" style={{ color: scoreColor }}>
            <CountUp to={prediction.confidence_pct} decimals={1} suffix="%" />
          </div>
        </div>

        <div className="bg-slate-950/60 rounded-xl p-3 border border-white/5">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Policy Bar
          </div>
          <div className="text-xl font-mono font-extrabold text-white">
            {(prediction.threshold * 100).toFixed(0)}%
          </div>
        </div>

        <div className="bg-slate-950/60 rounded-xl p-3 border border-white/5">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            Safety Margin
          </div>
          <div className="text-xl font-mono font-extrabold" style={{ color: deltaColor }}>
            {deltaFormatted}
          </div>
        </div>

        <div className="bg-slate-950/60 rounded-xl p-3 border border-white/5">
          <div className="text-[11px] font-mono text-slate-400 uppercase tracking-wider mb-1">
            WHO Breaches
          </div>
          <div
            className={`text-xl font-mono font-extrabold ${
              prediction.violations_count > 0 ? 'text-rose-400' : 'text-emerald-400'
            }`}
          >
            {prediction.violations_count}
          </div>
        </div>
      </div>
    </SpotlightCard>
  );
}
