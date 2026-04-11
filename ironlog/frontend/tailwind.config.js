/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          base: '#F8F7F4',
          surface: '#EFEEEB',
          raised: '#FFFFFF',
          inset: '#E8E6E1',
          hover: '#EAE9E5',
          active: '#E2E0DB',
        },
        border: {
          subtle: '#E4E2DD',
          DEFAULT: '#D6D3CC',
          strong: '#C4C1B9',
        },
        text: {
          primary: '#2C3E3A',
          secondary: '#6B7C77',
          tertiary: '#8A8784',
          placeholder: '#B0ADA7',
          inverse: '#F8F7F4',
        },
        sage: {
          50: '#EFF3F0',
          100: '#D9E3DC',
          200: '#B8C4C0',
          300: '#94A89B',
          400: '#7A9480',
          500: '#5E7D64',
          600: '#4A6650',
          700: '#374D3C',
          800: '#2C3E3A',
        },
        powder: {
          50: '#EFF5F8',
          100: '#D4E5EE',
          200: '#A3BFD4',
          300: '#7C9AAF',
          400: '#5E8199',
          500: '#4A6F85',
          600: '#3A5A6D',
          700: '#2E4A5E',
        },
        clay: {
          50: '#FBF3EE',
          100: '#F0DDD2',
          200: '#DFC0AE',
          300: '#C9A08A',
          400: '#B8876D',
          500: '#A07258',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'sans-serif'],
        serif: ['"Newsreader"', 'Georgia', 'serif'],
        mono: ['"DM Mono"', '"Geist Mono"', 'monospace'],
      },
      borderRadius: {
        xs: '4px',
        sm: '6px',
        md: '10px',
        lg: '14px',
        xl: '20px',
      },
      boxShadow: {
        xs: '0 1px 2px rgba(44, 62, 58, 0.04)',
        sm: '0 2px 8px rgba(44, 62, 58, 0.06)',
        md: '0 4px 16px rgba(44, 62, 58, 0.08)',
        lg: '0 8px 32px rgba(44, 62, 58, 0.10)',
        focus: '0 0 0 3px rgba(94, 125, 100, 0.15)',
      },
      transitionTimingFunction: {
        gentle: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
        'out-soft': 'cubic-bezier(0.16, 1, 0.3, 1)',
      },
    },
  },
  plugins: [],
}
