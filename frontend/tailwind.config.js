import forms from '@tailwindcss/forms';

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
        blue: {
          50: '#e1fcf2',
          100: '#b4f8e0',
          200: '#83f2cb',
          300: '#52edb5',
          400: '#28e5a0',
          500: '#03da7c',
          600: '#02b967',
          700: '#029452',
          800: '#016b3d',
          900: '#014728',
          950: '#002513',
        },
        indigo: {
          50: '#e1fcf2',
          100: '#b4f8e0',
          200: '#83f2cb',
          300: '#52edb5',
          400: '#28e5a0',
          500: '#03da7c',
          600: '#02b967',
          700: '#029452',
          800: '#016b3d',
          900: '#014728',
          950: '#002513',
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [
    forms,
  ],
}
