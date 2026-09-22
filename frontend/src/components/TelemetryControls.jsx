import React from 'react';
import { Sliders, Shield, MapPin, Database } from 'lucide-react';

export default function TelemetryControls({
  sample,
  onChange,
  threshold,
  onThresholdChange,
  stationType,
  onStationTypeChange,
  dataSource,
  onDataSourceChange,
  limits
}) {
  const groups = [
    {
      title: "🧪 Physicochemical Baseline",
      params: [
        { key: 'ph', label: 'pH Level', min: 0.0, max: 14.0, step: 0.05, unit: '' },
        { key: 'Hardness', label: 'Hardness', min: 50.0, max: 400.0, step: 1.0, unit: 'mg/L' },
        { key: 'Conductivity', label: 'Conductivity', min: 100.0, max: 800.0, step: 5.0, unit: 'μS/cm' },
        { key: 'Turbidity', label: 'Turbidity', min: 0.0, max: 8.0, step: 0.1, unit: 'NTU' }
      ]
    },
    {
      title: "🧂 Minerals & Dissolved Solids",
      params: [
        { key: 'Solids', label: 'Total Dissolved Solids (TDS)', min: 100.0, max: 50000.0, step: 250.0, unit: 'ppm' },
        { key: 'Sulfate', label: 'Sulfate Minerals', min: 100.0, max: 500.0, step: 1.0, unit: 'mg/L' }
      ]
    },
    {
      title: "☣️ Disinfectants & Organics",
      params: [
        { key: 'Chloramines', label: 'Chloramines', min: 0.0, max: 15.0, step: 0.1, unit: 'ppm' },
        { key: 'Organic_carbon', label: 'Total Organic Carbon (TOC)', min: 0.0, max: 30.0, step: 0.1, unit: 'ppm' },
        { key: 'Trihalomethanes', label: 'Trihalomethanes (THMs)', min: 0.0, max: 140.0, step: 1.0, unit: 'μg/L' }
      ]
    }
  ];

  const stationTypes = [
    "Urban_Treatment",
    "Agricultural_Runoff",
    "Industrial_Catchment",
    "Reservoir_Lake",
    "River_Basin"
  ];

  return (
    <div className="space-y-6">
      {/* Operating Decision Policy Card */}
      <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-4 shadow-xl">
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/10">
          <div className="flex items-center gap-2 text-sm font-semibold text-white">
            <Shield className="w-4 h-4 text-teal-400" />
            <span>Operating Decision Policy</span>
          </div>
          <span className="text-[11px] font-mono text-teal-300 bg-teal-500/10 px-2 py-0.5 rounded border border-teal-500/20 font-bold">
            τ = {threshold.toFixed(2)}
          </span>
        </div>

        <div className="grid grid-cols-2 gap-2 mb-3">
          <button
            type="button"
            onClick={() => onThresholdChange(0.65)}
            className={`p-2.5 rounded-xl border text-xs font-semibold text-left transition-all ${
              threshold === 0.65
                ? 'bg-emerald-950/50 border-emerald-400 text-emerald-300 shadow-md shadow-emerald-500/10'
                : 'bg-slate-950/40 border-white/10 text-slate-400 hover:border-white/20'
            }`}
          >
            <div className="font-bold flex items-center gap-1.5 mb-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400" />
              Public Health (τ* = 0.65)
            </div>
            <div className="text-[10px] text-slate-400 font-normal">
              Minimizes fatal false potables
            </div>
          </button>

          <button
            type="button"
            onClick={() => onThresholdChange(0.50)}
            className={`p-2.5 rounded-xl border text-xs font-semibold text-left transition-all ${
              threshold === 0.50
                ? 'bg-amber-950/50 border-amber-400 text-amber-300 shadow-md shadow-amber-500/10'
                : 'bg-slate-950/40 border-white/10 text-slate-400 hover:border-white/20'
            }`}
          >
            <div className="font-bold flex items-center gap-1.5 mb-0.5">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              Standard (τ = 0.50)
            </div>
            <div className="text-[10px] text-slate-400 font-normal">
              Balanced commercial bar
            </div>
          </button>
        </div>

        {/* Custom Fine-Tune Slider */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs font-mono text-slate-400">
            <span>Threshold Calibration:</span>
            <span className="text-white font-bold">{(threshold * 100).toFixed(0)}%</span>
          </div>
          <input
            type="range"
            min="0.10"
            max="0.90"
            step="0.01"
            value={threshold}
            onChange={(e) => onThresholdChange(parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
      </div>

      {/* Catchment Metadata */}
      <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-4 shadow-xl">
        <div className="flex items-center gap-2 text-sm font-semibold text-white mb-3 pb-2 border-b border-white/10">
          <MapPin className="w-4 h-4 text-sky-400" />
          <span>Catchment Environment</span>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-xs font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              Station Location
            </label>
            <select
              value={stationType}
              onChange={(e) => onStationTypeChange(e.target.value)}
              className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-teal-400"
            >
              {stationTypes.map((t) => (
                <option key={t} value={t}>{t.replace('_', ' ')}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 uppercase tracking-wider mb-1.5">
              Data Stream Provenance
            </label>
            <select
              value={dataSource}
              onChange={(e) => onDataSourceChange(e.target.value)}
              className="w-full bg-slate-950 border border-white/10 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-teal-400"
            >
              <option value="Regional_Network_B">Regional Network B</option>
              <option value="Global_Survey_A">Global Survey A</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sensor Sliders */}
      {groups.map((group, gIdx) => (
        <div key={gIdx} className="rounded-2xl bg-slate-900/80 border border-white/10 p-4 shadow-xl">
          <h4 className="text-xs font-mono uppercase tracking-wider text-teal-400 font-semibold mb-3 pb-2 border-b border-white/10">
            {group.title}
          </h4>

          <div className="space-y-4">
            {group.params.map((p) => {
              const val = sample[p.key] ?? p.min;
              const limit = limits ? limits[p.key] : null;

              return (
                <div key={p.key} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-medium text-slate-200">{p.label}</span>
                    <span className="font-mono font-bold text-teal-300 bg-slate-950 px-2 py-0.5 rounded border border-white/10">
                      {val.toFixed(p.step < 1 ? 2 : 0)} {p.unit}
                    </span>
                  </div>

                  <input
                    type="range"
                    min={p.min}
                    max={p.max}
                    step={p.step}
                    value={val}
                    onChange={(e) => onChange(p.key, parseFloat(e.target.value))}
                    className="w-full"
                  />

                  {limit && (
                    <div className="flex justify-between text-[10px] font-mono text-slate-500">
                      <span>Min: {p.min}</span>
                      <span className="text-emerald-400/80">WHO: {limit.min} - {limit.max} {limit.unit}</span>
                      <span>Max: {p.max}</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
