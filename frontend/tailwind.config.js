/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
        },
        accent: {
          cyan: '#06b6d4',
          emerald: '#10b981',
          violet: '#8b5cf6',
        },
        surface: {
          light: '#F8FAFC',
          dark: '#0F172A',
          darkCard: '#111827',
        },
      },
      boxShadow: {
        soft: '0 2px 8px -2px rgba(16, 24, 40, 0.06), 0 4px 16px -4px rgba(16, 24, 40, 0.08)',
        glow: '0 0 0 1px rgba(99, 102, 241, 0.1), 0 8px 24px -8px rgba(99, 102, 241, 0.35)',
        card: '0 1px 3px rgba(16,24,40,0.06), 0 1px 2px rgba(16,24,40,0.04)',
      },
      borderRadius: {
        xl2: '18px',
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%)',
        'brand-gradient-soft': 'linear-gradient(135deg, #eef2ff 0%, #f5f3ff 100%)',
      },
    },
  },
  plugins: [],
}
