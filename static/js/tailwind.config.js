module.exports = {
  content: ["./**/*.html", "./**/*.js"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#22c55e",
          dark: "#16a34a",
        },
        secondary: {
          DEFAULT: "#1a1a1a",
          light: "#374151",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      container: {
        center: true,
        padding: "1rem",
      },
    },
  },
  plugins: [],
};
