/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        paper: '#EFF1EA',
        ink: '#10202E',
        inkmuted: '#3C4C5A',
        rule: '#C7CDBF',
        sage: { DEFAULT: '#4F7A69', light: '#DCE6DE', dark: '#375A4C' },
        gold: { DEFAULT: '#C99A3B', light: '#F3E6C5' },
        rust: { DEFAULT: '#B5533C', light: '#F1DAD3' },
      },
      fontFamily: {
        display: ['"Source Serif 4"', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      backgroundImage: {
        'axis-ticks':
          'repeating-linear-gradient(90deg, var(--tick-color, #C7CDBF) 0, var(--tick-color, #C7CDBF) 1px, transparent 1px, transparent 24px)',
      },
    },
  },
  plugins: [],
};
