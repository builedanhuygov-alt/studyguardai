// StudyGuard AI — Tailwind theme (generated from tokens.json).
// Usage: const sg = require('./design/tokens/tailwind.theme.js'); module.exports = { theme: { extend: sg } }
module.exports = {
  colors: {
    brand: { 50:'#EEF0FF',100:'#E0E3FF',200:'#C7CCFF',300:'#A5ADFF',400:'#818CFF',500:'#6366F1',600:'#4F46E5',700:'#4338CA',800:'#3730A3',900:'#312E81' },
    coach: { 500:'#8B5CF6', 600:'#7C3AED' },
    growth: { 500:'#10B981', 600:'#059669' },
    streak: { 500:'#F59E0B', 600:'#D97706' },
    success:'#16A34A', warning:'#D97706', danger:'#DC2626', info:'#2563EB',
    ink: { DEFAULT:'#141922', muted:'#4B535E' },
    surface: { DEFAULT:'#FFFFFF', alt:'#EEF1F5', dark:'#141922', darkAlt:'#1E242E' }
  },
  fontFamily: {
    sans:['Inter','-apple-system','Segoe UI','Roboto','sans-serif'],
    display:['Newsreader','Georgia','serif'],
    mono:['JetBrains Mono','Consolas','monospace']
  },
  fontSize: { xs:'12px', sm:'14px', base:'16px', lg:'18px', xl:'20px', '2xl':'24px', '3xl':'30px', '4xl':'36px', '5xl':'48px' },
  spacing: { 1:'4px',2:'8px',3:'12px',4:'16px',5:'20px',6:'24px',8:'32px',10:'40px',12:'48px',16:'64px',20:'80px',24:'96px' },
  borderRadius: { sm:'10px', md:'14px', lg:'20px', xl:'28px', pill:'999px' },
  boxShadow: {
    xs:'0 1px 2px rgba(13,18,28,.06)', sm:'0 2px 6px rgba(13,18,28,.08)',
    md:'0 6px 16px rgba(13,18,28,.10)', lg:'0 14px 34px rgba(13,18,28,.14)'
  },
  transitionTimingFunction: { standard:'cubic-bezier(.2,0,0,1)', spring:'cubic-bezier(.34,1.56,.64,1)' },
  screens: { sm:'640px', md:'768px', lg:'1024px', xl:'1280px', '2xl':'1536px' }
};
