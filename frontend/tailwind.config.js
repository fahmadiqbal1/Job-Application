/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}'
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#07090f',
          900: '#0d1117',
          800: '#141b2d',
          700: '#1e2a45',
          600: '#243358',
        },
        brand: {
          cyan: 'hsl(187, 74%, 32%)',
          'cyan-light': 'hsl(187, 74%, 52%)',
          purple: 'hsl(270, 70%, 45%)',
          'purple-light': 'hsl(270, 70%, 65%)',
        },
      },
      fontFamily: {
        display: ['Space Grotesk', 'system-ui', 'sans-serif'],
        body: ['DM Sans', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, hsl(187,74%,32%), hsl(270,70%,45%))',
        'gradient-brand-subtle': 'linear-gradient(135deg, hsl(187,74%,32%,0.15), hsl(270,70%,45%,0.15))',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.4s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'count-up': 'countUp 1s ease-out',
      },
      keyframes: {
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
