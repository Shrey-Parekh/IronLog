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
        sans: ['"Plus Jakarta Sans"', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        serif: ['"Crimson Pro"', '"Newsreader"', 'Georgia', 'serif'],
        display: ['"Fraunces"', '"Crimson Pro"', 'Georgia', 'serif'],
        mono: ['"JetBrains Mono"', '"DM Mono"', 'monospace'],
      },
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem', letterSpacing: '0.01em' }],
        'sm': ['0.875rem', { lineHeight: '1.25rem', letterSpacing: '0.005em' }],
        'base': ['1rem', { lineHeight: '1.5rem', letterSpacing: '0' }],
        'lg': ['1.125rem', { lineHeight: '1.75rem', letterSpacing: '-0.005em' }],
        'xl': ['1.25rem', { lineHeight: '1.875rem', letterSpacing: '-0.01em' }],
        '2xl': ['1.5rem', { lineHeight: '2rem', letterSpacing: '-0.015em' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem', letterSpacing: '-0.02em' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem', letterSpacing: '-0.025em' }],
      },
      borderRadius: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '24px',
        '2xl': '32px',
      },
      boxShadow: {
        xs: '0 1px 2px rgba(44, 62, 58, 0.04)',
        sm: '0 2px 8px rgba(44, 62, 58, 0.06), 0 1px 2px rgba(44, 62, 58, 0.04)',
        md: '0 4px 16px rgba(44, 62, 58, 0.08), 0 2px 4px rgba(44, 62, 58, 0.04)',
        lg: '0 8px 32px rgba(44, 62, 58, 0.10), 0 4px 8px rgba(44, 62, 58, 0.06)',
        xl: '0 16px 48px rgba(44, 62, 58, 0.12), 0 8px 16px rgba(44, 62, 58, 0.08)',
        focus: '0 0 0 3px rgba(94, 125, 100, 0.15)',
        'focus-sage': '0 0 0 4px rgba(94, 125, 100, 0.2)',
        'inner-soft': 'inset 0 2px 4px rgba(44, 62, 58, 0.06)',
      },
      transitionTimingFunction: {
        gentle: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
        'out-soft': 'cubic-bezier(0.16, 1, 0.3, 1)',
        'in-soft': 'cubic-bezier(0.4, 0, 1, 1)',
        'bounce-soft': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
      },
      animation: {
        'fade-in': 'fadeIn 0.4s ease-out-soft',
        'fade-in-up': 'fadeInUp 0.5s ease-out-soft',
        'fade-in-down': 'fadeInDown 0.5s ease-out-soft',
        'scale-in': 'scaleIn 0.3s ease-out-soft',
        'slide-in-right': 'slideInRight 0.4s ease-out-soft',
        'slide-in-left': 'slideInLeft 0.4s ease-out-soft',
        'bounce-soft': 'bounceSoft 0.6s ease-bounce-soft',
        'pulse-soft': 'pulseSoft 2s ease-gentle infinite',
        'shimmer': 'shimmer 2s ease-gentle infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeInUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeInDown: {
          '0%': { opacity: '0', transform: 'translateY(-16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(-24px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        slideInLeft: {
          '0%': { opacity: '0', transform: 'translateX(24px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        bounceSoft: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}

