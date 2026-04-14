/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sap: {
          blue: '#0070f2',
          darkBlue: '#0854a0',
          green: '#107e3e',
          bg: '#f3f4f5',
          text: '#32363a',
        }
      }
    },
  },
  plugins: [],
}
