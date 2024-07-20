const defaultTheme = require('tailwindcss/defaultTheme');
const plugin = require("tailwindcss/plugin");

module.exports = {
  content: [
    '../templates/**/*.html',
    '../../templates/**/*.html',
    '../../**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        transparent: 'transparent',
        "main-gray": "#3c3c3c",
        "lighter-gray": "#4a4a4a",
        "separator-gray": "#5c5c5c",
        "ring-gray": "#808080",
        "dark-gray": "#343434",
        "darker-gray": "#262626",
        "darker-active": "#1a1a1a",
      },
      fontSize: {
        "13px": "13px",
        "15px": "15px",
        "17px": "17px",
        "4-5xl": ["2.625rem", "1.1"],
        "5-6xl": ["3.375rem", "1.1"]
      },
      maxWidth: {
        "400-px": "400px",
        "450-px": "450px",
        "500-px": "500px",
        "550-px": "550px",
        "600-px": "600px",
      },
      borderWidth: {
        "3": "3px",
      },
      fontFamily: {
        sans: ['Inter var', ...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/line-clamp'),
    require('@tailwindcss/aspect-ratio'),
  ],
}
