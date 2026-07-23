/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'primary': 'var(--color-primary)',
        'primary-light': 'var(--color-primary-light)',
        'primary-dark': 'var(--color-primary-dark)',
        'secondary': 'var(--color-secondary)',
        'secondary-light': 'var(--color-secondary-light)',
        'secondary-dark': 'var(--color-secondary-dark)',
        'background': 'var(--color-background)',
        'surface': 'var(--color-surface)',
        'surface-alt': 'var(--color-surface-alt)',
        'surface-dark': 'var(--color-surface-dark)',
        'text': 'var(--color-text)',
        'text-dark': 'var(--color-text-dark)',
        'text-muted': 'var(--color-text-muted)',
        'text-light': 'var(--color-text-light)',
        'border': 'var(--color-border)',
        'border-dark': 'var(--color-border-dark)',
        'success': 'var(--color-success)',
        'warning': 'var(--color-warning)',
        'error': 'var(--color-error)',
        'info': 'var(--color-info)',
      },
      fontFamily: {
        'nohemi': ['Nohemi', 'sans-serif'],
        'nohemi-variable': ['Nohemi-Variable', 'sans-serif'],
        'geist': ['Geist', 'sans-serif'],
        'switzer': ['Switzer', 'sans-serif'],
        'panchang': ['Panchang-Variable', 'sans-serif'],
        'lufga': ['Lufga', 'sans-serif'],
      },
      backgroundImage: {
        'radial-gradient': 'radial-gradient(circle, var(--tw-gradient-stops))',
      },
      boxShadow: {
        'sm': 'var(--shadow-sm)',
        'md': 'var(--shadow-md)',
        'lg': 'var(--shadow-lg)',
      },
      borderRadius: {
        'sm': 'var(--border-radius-sm)',
        'md': 'var(--border-radius-md)',
        'lg': 'var(--border-radius-lg)',
        'full': 'var(--border-radius-full)',
      },
      spacing: {
        'xs': 'var(--spacing-xs)',
        'sm': 'var(--spacing-sm)',
        'md': 'var(--spacing-md)',
        'lg': 'var(--spacing-lg)',
      },
      fontWeight: {
        'light': 'var(--font-weight-light)',
        'regular': 'var(--font-weight-regular)',
        'medium': 'var(--font-weight-medium)',
        'bold': 'var(--font-weight-bold)',
      },
    },
  },
  plugins: [],
}