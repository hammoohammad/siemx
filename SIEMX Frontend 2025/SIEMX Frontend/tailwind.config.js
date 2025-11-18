/******** Tailwind config for SIEMX ********/
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1f7ae0',
          50: '#e6f0fc',
          100: '#cfe2fa',
          200: '#9ec5f5',
          300: '#6ea9ef',
          400: '#3d8dea',
          500: '#1f7ae0',
          600: '#1860b3',
          700: '#124786',
          800: '#0b2e59',
          900: '#05152c'
        },
        neon: {
          green: '#22d3ee',
          lime: '#00ff88'
        }
      },
      boxShadow: {
        soft: '0 6px 24px rgba(0,0,0,0.25)'
      }
    }
  },
  plugins: []
};
