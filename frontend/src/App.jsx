import React, { useState, useEffect, useCallback } from 'react';
import AuroraHero from './components/AuroraHero';
import ScenarioPresets from './components/ScenarioPresets';
import SpotlightVerdictCard from './components/SpotlightVerdictCard';
import PotabilityGauge from './components/PotabilityGauge';
import WHORadarChart from './components/WHORadarChart';
import CulpritDiagnostics from './components/CulpritDiagnostics';
import TelemetryControls from './components/TelemetryControls';
import BatchProcessing from './components/BatchProcessing';
import ArchitectureTab from './components/ArchitectureTab';
import { Microscope, FileSpreadsheet, Network } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('triage');
  const [backendHealthy, setBackendHealthy] = useState(true);
  const [presets, setPresets] = useState(null);
  const [limits, setLimits] = useState(null);
  const [activePreset, setActivePreset] = useState("Pristine Tap (Safe)");
  const [threshold, setThreshold] = useState(0.65);
  const [stationType, setStationType] = useState('Urban_Treatment');
  const [dataSource, setDataSource] = useState('Regional_Network_B');

  const [sample, setSample] = useState({
    ph: 7.35,
    Hardness: 195.0,
    Solids: 16500.0,
    Chloramines: 6.8,
    Sulfate: 315.0,
    Conductivity: 390.0,
    Organic_carbon: 11.0,
    Trihalomethanes: 58.0,
    Turbidity: 3.1
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  // Fetch presets and limits once on mount
  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(() => setBackendHealthy(true))
      .catch(() => setBackendHealthy(false));

    fetch('/api/presets')
      .then(res => res.json())
      .then(data => setPresets(data))
      .catch(console.error);

    fetch('/api/limits')
      .then(res => res.json())
      .then(data => setLimits(data))
      .catch(console.error);
  }, []);

  // Run prediction API
  const runPrediction = useCallback(async (currentSample, curThreshold, curStation, curSource) => {
    setLoading(true);
    try {
      const payload = {
        ...currentSample,
        Station_Type: curStation,
        Data_Source: curSource,
        threshold: curThreshold
      };

      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Prediction API failed');
      const data = await res.json();
      setPrediction(data);
      setBackendHealthy(true);
    } catch (err) {
      console.error(err);
      setBackendHealthy(false);
    } finally {
      setLoading(false);
    }
  }, []);

  // Trigger prediction on sample or threshold changes (with lightweight debounce)
  useEffect(() => {
    const timer = setTimeout(() => {
      runPrediction(sample, threshold, stationType, dataSource);
    }, 80);
    return () => clearTimeout(timer);
  }, [sample, threshold, stationType, dataSource, runPrediction]);

  // Handle preset selection
  const handleSelectPreset = (presetName) => {
    if (!presets || !presets[presetName]) return;
    const cfg = presets[presetName];
    setActivePreset(presetName);
    if (cfg.Station_Type) setStationType(cfg.Station_Type);
    if (cfg.Data_Source) setDataSource(cfg.Data_Source);

    setSample({
      ph: cfg.ph,
      Hardness: cfg.Hardness,
      Solids: cfg.Solids,
      Chloramines: cfg.Chloramines,
      Sulfate: cfg.Sulfate,
      Conductivity: cfg.Conductivity,
      Organic_carbon: cfg.Organic_carbon,
      Trihalomethanes: cfg.Trihalomethanes,
      Turbidity: cfg.Turbidity
    });
  };

  // Handle single param change
  const handleParamChange = (key, value) => {
    setActivePreset(null); // Clear preset selection when manually adjusting
    setSample(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const tabs = [
    { id: 'triage', label: 'Real-Time Telemetry Triage', icon: Microscope },
    { id: 'batch', label: 'Batch Ingestion Engine', icon: FileSpreadsheet },
    { id: 'architecture', label: 'Pipeline Metrics & Architecture', icon: Network },
  ];

  return (
    <div className="min-h-screen bg-[#090D16] text-[#F8FAFC] pb-16">
      {/* Top Background Glow Ambient */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[300px] bg-teal-500/10 blur-[130px] pointer-events-none -z-10" />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8">
        {/* Aurora Hero Banner */}
        <AuroraHero backendHealthy={backendHealthy} />

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center gap-2 p-1.5 rounded-2xl bg-slate-900/80 backdrop-blur-md border border-white/10 mb-8 max-w-2xl">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 ${
                  isActive
                    ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30 shadow-md shadow-teal-500/10'
                    : 'text-slate-400 hover:text-white hover:bg-white/5 border border-transparent'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        {activeTab === 'triage' && (
          <div>
            {/* Quick Scenario Simulator Bar */}
            <ScenarioPresets
              activePreset={activePreset}
              onSelectPreset={handleSelectPreset}
            />

            {/* 2-Column Responsive Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
              {/* Left Column: Interactive Telemetry Controls */}
              <div className="lg:col-span-5 order-2 lg:order-1">
                <TelemetryControls
                  sample={sample}
                  onChange={handleParamChange}
                  threshold={threshold}
                  onThresholdChange={setThreshold}
                  stationType={stationType}
                  onStationTypeChange={setStationType}
                  dataSource={dataSource}
                  onDataSourceChange={setDataSource}
                  limits={limits}
                />
              </div>

              {/* Right Column: Visual Verdict, Speedometer, Radar & Culprits */}
              <div className="lg:col-span-7 order-1 lg:order-2 space-y-6">
                {prediction && (
                  <>
                    <SpotlightVerdictCard prediction={prediction} />

                    {/* Dual High-Contrast Visual Charts */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <PotabilityGauge
                        probability={prediction.potability_probability}
                        threshold={threshold}
                      />
                      <WHORadarChart
                        radarData={prediction.radar_data}
                        isPotable={prediction.is_potable}
                      />
                    </div>

                    {/* Detected Culprit Diagnostic Cards & Audit */}
                    <CulpritDiagnostics
                      violations={prediction.violations}
                      auditTable={prediction.audit_table}
                    />
                  </>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'batch' && (
          <BatchProcessing threshold={threshold} />
        )}

        {activeTab === 'architecture' && (
          <ArchitectureTab />
        )}
      </main>
    </div>
  );
}
