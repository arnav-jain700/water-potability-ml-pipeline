import React from 'react';
import SpotlightCard from './SpotlightCard';
import { Network, Trophy, ShieldAlert, Cpu, GitCommit } from 'lucide-react';

export default function ArchitectureTab() {
  const models = [
    {
      name: "Logistic Regression (Linear Baseline)",
      cvRoc: "0.618",
      testRoc: "0.615",
      macroF1: "0.562",
      notes: "Linear hyperplane fails on bounded safety intervals (e.g. 6.5 <= pH <= 8.5)",
      champion: false
    },
    {
      name: "XGBoost Classifier",
      cvRoc: "0.745",
      testRoc: "0.741",
      macroF1: "0.675",
      notes: "Strong gradient boosting, slight variance sensitivity on noisy chemical telemetry",
      champion: false
    },
    {
      name: "Baseline Random Forest",
      cvRoc: "0.772",
      testRoc: "0.768",
      macroF1: "0.696",
      notes: "Unconstrained tree depth allowed mild variance overfitting",
      champion: false
    },
    {
      name: "Tuned Champion Random Forest 🏆",
      cvRoc: "0.779",
      testRoc: "0.779",
      macroF1: "0.702",
      notes: "Production Champion: 400 trees with leaf regularization and balanced weights",
      champion: true
    }
  ];

  const pipelineSteps = [
    {
      step: "01",
      title: "Data Ingestion & Integrity",
      desc: "Dual-source master dataset containing 7,776 continuous telemetry readings with zero data drift."
    },
    {
      step: "02",
      title: "Tukey's IQR Winsorization",
      desc: "Robust outlier fencing ([Q1 - 1.5 IQR, Q3 + 1.5 IQR]) with strict physical zero-floor clipping."
    },
    {
      step: "03",
      title: "5-NN Multivariate Imputation",
      desc: "K-Nearest Neighbors imputer preserves inter-chemical covariance structures without mean distortion."
    },
    {
      step: "04",
      title: "Atomic ColumnTransformer",
      desc: "StandardScaler on 9 numerical features coupled with OneHotEncoder on provenance attributes."
    },
    {
      step: "05",
      title: "Calibrated Random Forest",
      desc: "400 estimators, min_samples_leaf=4, class_weight='balanced_subsample' for robust generalization."
    },
    {
      step: "06",
      title: "Asymmetric Cost-Sensitive Gate",
      desc: "Optimal decision threshold τ* = 0.65 minimizing catastrophic false potable classifications."
    }
  ];

  return (
    <div className="space-y-6">
      {/* Pipeline Workflow Diagram */}
      <SpotlightCard className="p-6">
        <div className="flex items-center gap-2 mb-4 text-white font-bold text-base">
          <Network className="w-5 h-5 text-teal-400" />
          <span>Production ML Pipeline Architecture</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {pipelineSteps.map((s) => (
            <div
              key={s.step}
              className="p-4 rounded-xl bg-slate-950/60 border border-white/10 hover:border-teal-500/40 transition-colors relative"
            >
              <div className="text-[11px] font-mono font-bold text-teal-400 bg-teal-500/10 w-7 h-7 rounded-lg flex items-center justify-center mb-2 border border-teal-500/20">
                {s.step}
              </div>
              <h4 className="text-sm font-bold text-white mb-1">{s.title}</h4>
              <p className="text-xs text-slate-400 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </SpotlightCard>

      {/* Asymmetric Risk Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <SpotlightCard
          spotlightColor="rgba(56, 189, 248, 0.15)"
          borderColor="rgba(56, 189, 248, 0.3)"
          className="p-6"
        >
          <div className="flex items-center gap-2 mb-2 text-sky-400 font-bold text-sm">
            <ShieldAlert className="w-4 h-4" />
            <span>Asymmetric Risk Economics</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-3">
            In municipal drinking water safety, errors are fundamentally asymmetric. Falsely clearing poisonous water for human consumption carries catastrophic health costs compared to benign temporary false alarms.
          </p>
          <div className="bg-slate-950/70 p-3 rounded-xl border border-sky-500/20 font-mono text-xs text-sky-300">
            Cost(False Negative) = 10 × Cost(False Positive) → τ* = 0.65
          </div>
        </SpotlightCard>

        <SpotlightCard
          spotlightColor="rgba(16, 185, 129, 0.15)"
          borderColor="rgba(16, 185, 129, 0.3)"
          className="p-6"
        >
          <div className="flex items-center gap-2 mb-2 text-emerald-400 font-bold text-sm">
            <Cpu className="w-4 h-4" />
            <span>Empirical Public Safety Gains</span>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed mb-3">
            Calibrating the decision bar to <code className="text-teal-300">τ* = 0.65</code> eliminates over <strong>60% of false potable poisonings</strong> while preserving 0.779 ROC-AUC generalization across untouched holdout validation sets.
          </p>
          <div className="bg-slate-950/70 p-3 rounded-xl border border-emerald-500/20 font-mono text-xs text-emerald-300">
            Production Clearance Standard: Minimum 65.0% Confidence
          </div>
        </SpotlightCard>
      </div>

      {/* Validation Benchmark Matrix */}
      <SpotlightCard className="p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2 text-white font-bold text-base">
            <Trophy className="w-5 h-5 text-amber-400" />
            <span>Algorithm Validation Leaderboard (5-Fold Stratified CV)</span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-slate-950 border-b border-white/10 text-slate-400 uppercase tracking-wider">
              <tr>
                <th className="py-3 px-4">Algorithm</th>
                <th className="py-3 px-4">5-Fold CV ROC-AUC</th>
                <th className="py-3 px-4">Test ROC-AUC</th>
                <th className="py-3 px-4">Macro F1</th>
                <th className="py-3 px-4">Architecture Rationale</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {models.map((m, idx) => (
                <tr
                  key={idx}
                  className={`transition-colors ${
                    m.champion ? 'bg-teal-500/10 hover:bg-teal-500/15' : 'hover:bg-white/[0.02]'
                  }`}
                >
                  <td className="py-3 px-4 font-bold text-white flex items-center gap-2">
                    {m.name}
                    {m.champion && (
                      <span className="text-[10px] bg-teal-500 text-slate-950 px-2 py-0.5 rounded font-extrabold uppercase tracking-wider">
                        Production Champion
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-emerald-400 font-bold">{m.cvRoc}</td>
                  <td className="py-3 px-4 text-teal-300 font-bold">{m.testRoc}</td>
                  <td className="py-3 px-4 text-slate-300">{m.macroF1}</td>
                  <td className="py-3 px-4 text-slate-400 font-sans text-xs">{m.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </SpotlightCard>
    </div>
  );
}
