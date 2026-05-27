/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#0066cc',
        secondary: '#00cc99',
        dark: '#1a1a2e',
        light: '#f5f5f5',
      },
    },
  },
  plugins: [],
  darkMode: 'class',
}
