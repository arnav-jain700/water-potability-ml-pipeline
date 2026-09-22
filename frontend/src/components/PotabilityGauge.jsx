import React from 'react';
import { Compass } from 'lucide-react';

export default function PotabilityGauge({ probability, threshold }) {
  const probPct = Math.min(Math.max(probability * 100, 0), 100);
  const threshPct = Math.min(Math.max(threshold * 100, 0), 100);
  const isSafe = probPct >= threshPct;

  // Arc geometry: 180 degrees from -180 to 0 (left to right)
  // When unrotated (0 deg), the pointer needle points straight UP (12 o'clock = 50%).
  // Left (0%) is at -90 deg rotation, Right (100%) is at +90 deg rotation.
  // Formula: needleAngle = -90 + (probPct / 100) * 180
  const needleAngle = -90 + (probPct / 100) * 180;

  // Function to calculate SVG arc path
  const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
    const angleInRadians = (angleInDegrees * Math.PI) / 180.0;
    return {
      x: centerX + radius * Math.cos(angleInRadians),
      y: centerY + radius * Math.sin(angleInRadians)
    };
  };

  const describeArc = (x, y, radius, startAngle, endAngle) => {
    const start = polarToCartesian(x, y, radius, endAngle);
    const end = polarToCartesian(x, y, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
    return [
      'M', start.x, start.y,
      'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y
    ].join(' ');
  };

  // Dimensions
  const cx = 150;
  const cy = 135;
  const r = 100;
  const strokeW = 16;

  // Polar angle for threshold line: -180 is left (0%), -90 is top (50%), 0 is right (100%)
  const safeThreshPct = Math.max(50, Math.min(threshPct, 95));
  const threshAngle = -180 + (threshPct / 100) * 180;
  const yellowEndAngle = -180 + (safeThreshPct / 100) * 180;

  // Segment arcs
  const redArc = describeArc(cx, cy, r, -180, -90); // 0% to 50%
  const yellowArc = describeArc(cx, cy, r, -90, yellowEndAngle); // 50% to Threshold%
  const greenArc = describeArc(cx, cy, r, yellowEndAngle, 0); // Threshold% to 100%

  // Threshold needle line coordinates
  const threshInner = polarToCartesian(cx, cy, r - strokeW - 4, threshAngle);
  const threshOuter = polarToCartesian(cx, cy, r + strokeW / 2 + 6, threshAngle);

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-2">
        <div className="flex items-center gap-2 text-sm font-semibold text-white">
          <Compass className="w-4 h-4 text-teal-400" />
          <span>Potability Confidence Gauge</span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20 font-bold uppercase">
          Inference Engine
        </span>
      </div>

      <div className="relative flex flex-col items-center justify-center pt-2">
        <svg viewBox="0 0 300 170" className="w-full max-w-[280px] overflow-visible">
          {/* Background Track */}
          <path
            d={describeArc(cx, cy, r, -180, 0)}
            fill="none"
            stroke="rgba(255,255,255,0.06)"
            strokeWidth={strokeW}
            strokeLinecap="round"
          />

          {/* Red Zone (0 - 50%) */}
          <path
            d={redArc}
            fill="none"
            stroke="rgba(239, 68, 68, 0.45)"
            strokeWidth={strokeW}
          />

          {/* Amber Zone (50% - Threshold%) */}
          {threshPct > 50 && (
            <path
              d={yellowArc}
              fill="none"
              stroke="rgba(245, 158, 11, 0.45)"
              strokeWidth={strokeW}
            />
          )}

          {/* Green Zone (Threshold% - 100%) */}
          <path
            d={greenArc}
            fill="none"
            stroke="rgba(16, 185, 129, 0.45)"
            strokeWidth={strokeW}
          />

          {/* Scale Marks & Ticks */}
          <text x="35" y="152" fill="#94A3B8" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle">0%</text>
          <text x="150" y="24" fill="#94A3B8" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle">50%</text>
          <text x="265" y="152" fill="#94A3B8" fontSize="10" fontFamily="JetBrains Mono" textAnchor="middle">100%</text>

          {/* Static Threshold Red Marker Line on Arc */}
          <line
            x1={threshInner.x}
            y1={threshInner.y}
            x2={threshOuter.x}
            y2={threshOuter.y}
            stroke="#EF4444"
            strokeWidth="3.5"
            strokeLinecap="round"
          />

          {/* Center Moving Pointer Needle (Rotates from -90deg at 0% to +90deg at 100%) */}
          <g
            transform={`rotate(${needleAngle} ${cx} ${cy})`}
            style={{
              transform: `rotate(${needleAngle}deg)`,
              transformOrigin: `${cx}px ${cy}px`,
              transition: 'transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)'
            }}
          >
            <polygon
              points={`${cx - 3.5},${cy} ${cx + 3.5},${cy} ${cx},${cy - r + 8}`}
              fill={isSafe ? '#00E5BE' : '#EF4444'}
            />
            <circle cx={cx} cy={cy} r="6.5" fill="#FFFFFF" />
            <circle cx={cx} cy={cy} r="3.5" fill="#090D16" />
          </g>
        </svg>

        {/* Digital Readout */}
        <div className="text-center -mt-3">
          <div className="font-mono text-3xl font-extrabold text-white flex items-center justify-center">
            <span style={{ color: isSafe ? '#00E5BE' : '#EF4444' }}>
              {probPct.toFixed(1)}%
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 font-mono">
            Safety Bar: <span className="text-rose-400 font-bold">{threshPct.toFixed(0)}%</span> (Red line on arc)
          </p>
        </div>
      </div>
    </div>
  );
}
