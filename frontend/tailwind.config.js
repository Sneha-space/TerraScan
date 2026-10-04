/** @type {import('tailwindcss').Config} */

// Colours come from land-record paperwork: register ink, the paper it is
// written on, the red ink officers correct with, and the green of a seal.
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#F5F6F3",
        sheet: "#FFFFFF",
        ink: {
          DEFAULT: "#1D2742",
          hover: "#2A3658",
          soft: "#475069",
          faint: "#6A7284",
        },
        rule: {
          DEFAULT: "#DCDFE3",
          soft: "#E9EBEE",
        },
        // needs review, and every correction a human makes
        correction: {
          DEFAULT: "#B42318",
          wash: "#FBEDEB",
        },
        // verified
        seal: {
          DEFAULT: "#2F6B4F",
          wash: "#E7F0EA",
        },
        // a score below the threshold; DEFAULT is for fills, text for words
        turmeric: {
          DEFAULT: "#C48A26",
          text: "#8A5A12",
          wash: "#FBF2E2",
        },
        // approved by the machine
        machine: {
          DEFAULT: "#46618F",
          wash: "#ECF0F7",
        },
      },
      fontFamily: {
        // Anek covers Latin and the Indian scripts in one design, so a
        // Bengali value and its English sit together. The browser takes each
        // character from the first family that has it.
        sans: [
          '"Anek Latin Variable"',
          '"Anek Bangla Variable"',
          '"Anek Devanagari Variable"',
          "system-ui",
          "sans-serif",
        ],
      },
      fontSize: {
        xs: ["0.78rem", { lineHeight: "1.1rem" }],
        sm: ["0.875rem", { lineHeight: "1.3rem" }],
        base: ["0.97rem", { lineHeight: "1.5rem" }],
        lg: ["1.15rem", { lineHeight: "1.65rem" }],
        xl: ["1.4rem", { lineHeight: "1.9rem" }],
        "2xl": ["1.8rem", { lineHeight: "2.2rem" }],
        "3xl": ["2.4rem", { lineHeight: "2.8rem" }],
      },
      borderRadius: {
        panel: "8px",
        control: "6px",
        stamp: "3px",
      },
    },
  },
  plugins: [],
};
