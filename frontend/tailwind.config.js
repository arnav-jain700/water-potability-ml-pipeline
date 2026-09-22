/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: '#090D16',
        darkSurface: '#0F172A',
        darkCard: 'rgba(15, 23, 42, 0.85)',
        aquaBrand: '#00E5BE',
        aquaGlow: 'rgba(0, 229, 190, 0.35)',
        safeGreen: '#10B981',
        safeGlow: 'rgba(16, 185, 129, 0.25)',
        dangerRed: '#EF4444',
        dangerGlow: 'rgba(239, 68, 68, 0.25)',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'text-shine': 'textShine 6s linear infinite',
        'pulse-radar': 'pulseRing 2.2s infinite cubic-bezier(0.66, 0, 0, 1)',
        'aurora': 'auroraMove 15s ease infinite alternate',
      },
      keyframes: {
        textShine: {
          '0%': { backgroundPosition: '0% center' },
          '100%': { backgroundPosition: '200% center' },
        },
        pulseRing: {
          '0%': { boxShadow: '0 0 0 0 rgba(0, 229, 190, 0.7)' },
          '70%': { boxShadow: '0 0 0 9px rgba(0, 229, 190, 0)' },
          '100%': { boxShadow: '0 0 0 0 rgba(0, 229, 190, 0)' },
        },
        auroraMove: {
          '0%': { backgroundPosition: '0% 50%' },
          '50%': { backgroundPosition: '100% 50%' },
          '100%': { backgroundPosition: '0% 50%' },
        }
      }
    },
  },
  plugins: [],
}
