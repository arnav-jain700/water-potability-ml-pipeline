import React from 'react';
import { Sparkles, AlertOctagon, Scale } from 'lucide-react';

export default function ScenarioPresets({ activePreset, onSelectPreset }) {
  const presets = [
    {
      id: "Pristine Tap (Safe)",
      title: "Pristine Municipal Tap",
      subtitle: "Baseline meeting EPA / WHO standards",
      icon: Sparkles,
      color: "emerald",
      badgeClass: "text-emerald-400 bg-emerald-950/40 border-emerald-500/30 hover:border-emerald-400"
    },
    {
      id: "Industrial Spill (Hazardous)",
      title: "Toxic Industrial Spill",
      subtitle: "Severe TDS, high chloramines & sulfate",
      icon: AlertOctagon,
      color: "rose",
      badgeClass: "text-rose-400 bg-rose-950/40 border-rose-500/30 hover:border-rose-400"
    },
    {
      id: "Borderline Infiltration (Edge Case)",
      title: "Borderline Agricultural Runoff",
      subtitle: "Tests τ* = 0.65 asymmetric threshold",
      icon: Scale,
      color: "amber",
      badgeClass: "text-amber-400 bg-amber-950/40 border-amber-500/30 hover:border-amber-400"
    }
  ];

  return (
    <div className="mb-6">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <span>⚡ Instant Scenario Simulation</span>
        </h3>
        <span className="text-[11px] text-slate-500 font-mono">1-Click Telemetry Profiling</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {presets.map((preset) => {
          const Icon = preset.icon;
          const isActive = activePreset === preset.id;
          return (
            <button
              key={preset.id}
              onClick={() => onSelectPreset(preset.id)}
              className={`text-left p-3.5 rounded-xl border transition-all duration-200 relative group ${
                isActive
                  ? 'bg-slate-800/90 border-teal-400 shadow-lg shadow-teal-500/10'
                  : 'bg-slate-900/60 border-white/10 hover:bg-slate-800/60 hover:border-white/20'
              }`}
            >
              <div className="flex items-center gap-2.5 mb-1.5">
                <span className={`p-1.5 rounded-lg border ${preset.badgeClass}`}>
                  <Icon className="w-4 h-4" />
                </span>
                <span className="text-sm font-semibold text-white tracking-tight group-hover:text-teal-300 transition-colors">
                  {preset.title}
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-snug pl-0.5">
                {preset.subtitle}
              </p>
              {isActive && (
                <div className="absolute top-2 right-2 flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-teal-500"></span>
                </div>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
