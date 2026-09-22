import React, { useState } from 'react';
import { ShieldAlert, Info } from 'lucide-react';

export default function WHORadarChart({ radarData, isPotable }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  if (!radarData || radarData.length === 0) return null;

  const size = 320;
  const center = size / 2;
  const radius = 100;
  const total = radarData.length;

  // Converts index and value (0-200% scale) to (x, y)
  const getCoordinates = (index, value) => {
    // Map value where 100 = safe limit
    const normalized = Math.min(Math.max(value / 160, 0), 1.25);
    const angle = (Math.PI * 2 / total) * index - Math.PI / 2;
    return {
      x: center + radius * normalized * Math.cos(angle),
      y: center + radius * normalized * Math.sin(angle)
    };
  };

  // Get label coordinates slightly outside the chart
  const getLabelCoordinates = (index) => {
    const angle = (Math.PI * 2 / total) * index - Math.PI / 2;
    return {
      x: center + (radius + 26) * Math.cos(angle),
      y: center + (radius + 24) * Math.sin(angle)
    };
  };

  // Construct polygons
  const whoPoints = radarData
    .map((_, i) => {
      const { x, y } = getCoordinates(i, 100);
      return `${x},${y}`;
    })
    .join(' ');

  const samplePoints = radarData
    .map((d, i) => {
      const { x, y } = getCoordinates(i, d.current);
      return `${x},${y}`;
    })
    .join(' ');

  const sampleColor = isPotable ? '#00E5BE' : '#EF4444';
  const sampleFill = isPotable ? 'rgba(0, 229, 190, 0.25)' : 'rgba(239, 68, 68, 0.28)';

  return (
    <div className="rounded-2xl bg-slate-900/80 border border-white/10 p-5 shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-2">
        <div className="flex items-center gap-2 text-sm font-semibold text-white">
          <ShieldAlert className="w-4 h-4 text-emerald-400" />
          <span>Physicochemical Fingerprint</span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold uppercase">
          WHO Envelope
        </span>
      </div>

      <div className="relative flex flex-col items-center justify-center">
        <svg viewBox={`0 0 ${size} ${size}`} className="w-full max-w-[300px] overflow-visible">
          {/* Background Concentric Rings (50%, 100%, 150%) */}
          {[0.5, 1.0, 1.25].map((scale, sIdx) => {
            const points = radarData
              .map((_, i) => {
                const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
                const x = center + radius * scale * Math.cos(angle);
                const y = center + radius * scale * Math.sin(angle);
                return `${x},${y}`;
              })
              .join(' ');
            return (
              <polygon
                key={sIdx}
                points={points}
                fill="none"
                stroke={scale === 1.0 ? 'rgba(16, 185, 129, 0.35)' : 'rgba(255, 255, 255, 0.06)'}
                strokeWidth={scale === 1.0 ? '1.5' : '1'}
                strokeDasharray={scale === 1.0 ? '4 3' : undefined}
              />
            );
          })}

          {/* Radial Spokes */}
          {radarData.map((_, i) => {
            const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
            const x = center + radius * 1.25 * Math.cos(angle);
            const y = center + radius * 1.25 * Math.sin(angle);
            return (
              <line
                key={i}
                x1={center}
                y1={center}
                x2={x}
                y2={y}
                stroke="rgba(255, 255, 255, 0.08)"
                strokeWidth="1"
              />
            );
          })}

          {/* WHO Safe Limit Benchmark Polygon (Green) */}
          <polygon
            points={whoPoints}
            fill="rgba(16, 185, 129, 0.12)"
            stroke="#10B981"
            strokeWidth="2"
            strokeDasharray="4 2"
          />

          {/* Current Water Sample Polygon */}
          <polygon
            points={samplePoints}
            fill={sampleFill}
            stroke={sampleColor}
            strokeWidth="2.5"
            className="transition-all duration-300"
          />

          {/* Vertex Dots with Hover Tooltips */}
          {radarData.map((d, i) => {
            const { x, y } = getCoordinates(i, d.current);
            const isBreach = d.current > 100;
            const isHovered = hoveredIndex === i;

            return (
              <g key={i} className="cursor-pointer">
                <circle
                  cx={x}
                  cy={y}
                  r={isHovered ? 6 : 4}
                  fill={isBreach ? '#EF4444' : '#00E5BE'}
                  stroke="#FFFFFF"
                  strokeWidth="1.5"
                  onMouseEnter={() => setHoveredIndex(i)}
                  onMouseLeave={() => setHoveredIndex(null)}
                />
              </g>
            );
          })}

          {/* Axis Labels */}
          {radarData.map((d, i) => {
            const { x, y } = getLabelCoordinates(i);
            const isBreach = d.current > 100;
            return (
              <text
                key={i}
                x={x}
                y={y}
                textAnchor="middle"
                dominantBaseline="central"
                fill={isBreach ? '#FCA5A5' : '#94A3B8'}
                fontSize="9.5"
                fontFamily="JetBrains Mono"
                fontWeight={isBreach ? '700' : '500'}
              >
                {d.subject}
              </text>
            );
          })}
        </svg>

        {/* Hovered or Active Data Pill */}
        <div className="h-6 mt-1 flex items-center justify-center">
          {hoveredIndex !== null ? (
            <div className="text-xs font-mono bg-slate-950 px-2.5 py-0.5 rounded border border-white/10 text-white flex items-center gap-2">
              <span className="text-teal-400 font-bold">{radarData[hoveredIndex].subject}:</span>
              <span>{radarData[hoveredIndex].current.toFixed(0)}% of safe envelope</span>
              {radarData[hoveredIndex].current > 100 && (
                <span className="text-rose-400 font-bold">[BREACH]</span>
              )}
            </div>
          ) : (
            <div className="text-[11px] text-slate-400 flex items-center gap-1.5 font-mono">
              <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-500/40 border border-emerald-400" />
              <span>Green: WHO Safe Floor/Ceiling</span>
              <span className="inline-block w-2.5 h-2.5 rounded-full ml-2" style={{ backgroundColor: sampleColor }} />
              <span>Sample Fingerprint</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
