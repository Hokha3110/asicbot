/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        jade: {
          950: '#04130d',
          900: '#081c15',
          850: '#0c241c',
          800: '#112f24',
          700: '#184737',
          600: '#23654f',
          500: '#10b981', // Ngọc bích chính
          400: '#34d399', // Ngọc bích sáng
          300: '#6ee7b7',
          200: '#a7f3d0',
          100: '#d1fae5',
        },
        surface: {
          950: '#070b09',
          900: '#0b120f',
          850: '#0f1814',
          800: '#14201b',
          700: '#1e2e28',
          600: '#2a3d36',
        }
      },
      boxShadow: {
        'glow-jade': '0 0 25px -5px rgba(16, 185, 129, 0.25)',
        'glow-subtle': '0 4px 20px -2px rgba(0, 0, 0, 0.4)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
