import React from 'react';
import { Activity, ShieldCheck, Cpu, Waves } from 'lucide-react';

export default function AuroraHero({ backendHealthy = true }) {
  return (
    <div className="relative overflow-hidden rounded-2xl aurora-mesh border border-white/10 p-6 md:p-8 mb-8 shadow-2xl shadow-black/40">
      {/* Top Telemetry & Spec Row */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
        <div className="inline-flex items-center gap-2 bg-emerald-950/60 border border-emerald-500/30 rounded-full px-3.5 py-1.5 text-xs font-mono font-semibold tracking-wider text-emerald-400 uppercase">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span>{backendHealthy ? 'LIVE SENSOR STREAM ACTIVE • MODEL v2.4' : 'OFFLINE / CONNECTING...'}</span>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-slate-300">
          <span className="inline-flex items-center gap-1.5 bg-white/5 border border-white/10 rounded-full px-3 py-1">
            <Cpu className="w-3.5 h-3.5 text-teal-400" />
            Tuned Random Forest (400 Trees)
          </span>
          <span className="inline-flex items-center gap-1.5 bg-white/5 border border-white/10 rounded-full px-3 py-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            Cost-Sensitive τ* = 0.65
          </span>
          <span className="inline-flex items-center gap-1.5 bg-white/5 border border-white/10 rounded-full px-3 py-1">
            <Waves className="w-3.5 h-3.5 text-sky-400" />
            9 Sensor Telemetry
          </span>
          <span className="inline-flex items-center gap-1.5 bg-white/5 border border-white/10 rounded-full px-3 py-1 text-amber-300">
            ★ 0.779 ROC-AUC
          </span>
        </div>
      </div>

      {/* Hero Title & Subtitle */}
      <div className="flex items-center gap-4">
        <div className="hidden sm:flex items-center justify-center w-14 h-14 rounded-2xl bg-teal-500/10 border border-teal-500/30 text-teal-400 shadow-inner">
          <Waves className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl md:text-5xl font-extrabold tracking-tight shiny-text">
            AquaGuard ML
          </h1>
          <p className="text-slate-300 text-sm md:text-base mt-1 font-normal max-w-3xl">
            Production Environmental Telemetry Engine & Early-Warning Water Potability Classifier • Asymmetric Risk Optimization
          </p>
        </div>
      </div>
    </div>
  );
}
