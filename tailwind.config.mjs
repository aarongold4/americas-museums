import typography from '@tailwindcss/typography';

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Travel Utility palette — refined Booking-adjacent
        brand: {
          DEFAULT: '#003B95',  // primary navy (header, links)
          50:  '#EFF4FB',
          100: '#DBE5F0',
          600: '#003B95',
          700: '#002F75',
        },
        action: {
          DEFAULT: '#006CE4',  // CTA bright blue
          hover:   '#0057BB',
        },
        ink: {
          DEFAULT: '#1F2937',
          muted:   '#6B7280',
          faint:   '#9CA3AF',
        },
        surface: {
          page: '#F4F6F8',
          card: '#FFFFFF',
          line: '#E5E7EB',
          line2: '#F3F4F6',
        },
        // Semantic badge palette
        ok:    { bg: '#ECFDF5', fg: '#065F46' },
        warn:  { bg: '#FEF3C7', fg: '#92400E' },
        info:  { bg: '#EFF6FF', fg: '#1E40AF' },
        neutral: { bg: '#F3F4F6', fg: '#4B5563' },
      },
      fontFamily: {
        sans: ['"DM Sans Variable"', 'DM Sans', 'system-ui', 'sans-serif'],
        display: ['"DM Sans Variable"', 'DM Sans', 'system-ui', 'sans-serif'],
      },
      fontSize: {
        // tightened scale for utility/dense layouts
        '2xs': ['11px', { lineHeight: '14px' }],
        xs:   ['12px', { lineHeight: '16px' }],
        sm:   ['13px', { lineHeight: '18px' }],
        base: ['15px', { lineHeight: '22px' }],
        lg:   ['17px', { lineHeight: '26px' }],
        xl:   ['20px', { lineHeight: '28px' }],
        '2xl': ['24px', { lineHeight: '32px' }],
        '3xl': ['30px', { lineHeight: '38px' }],
        '4xl': ['36px', { lineHeight: '42px' }],
      },
      borderRadius: {
        sm: '4px',
        DEFAULT: '6px',
        md: '8px',
        lg: '12px',
      },
      letterSpacing: {
        tightish: '-0.01em',
        widish: '0.06em',
        wider2: '0.1em',
      },
      maxWidth: {
        content: '1100px',
        prose: '680px',
      },
    },
  },
  plugins: [typography],
};
