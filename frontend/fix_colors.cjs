const fs = require('fs');
const file = './src/App.vue';
let content = fs.readFileSync(file, 'utf8');

const targetCSS = \`.kpi-card:nth-child(1)::before { background: var(--success); }
.kpi-card:nth-child(2)::before { background: #06b6d4; }
.kpi-card:nth-child(3)::before { background: #f43f5e; }
.kpi-card:nth-child(4)::before { background: #a855f7; }\`;

const newCSS = \`.kpi-card:nth-child(1)::before { background: #10b981; } /* Sisa Massa (Green) */
.kpi-card:nth-child(2)::before { background: #38bdf8; } /* Ketinggian (Blue) */
.kpi-card:nth-child(3)::before { background: #f43f5e; } /* Kecepatan (Red) */
.kpi-card:nth-child(4)::before { background: #a855f7; } /* Total Waktu (Purple) */
.kpi-card:nth-child(5)::before { background: #eab308; } /* G-Force (Yellow) */
.kpi-card:nth-child(6)::before { background: #ef4444; } /* Heat Flux (Red) */
.kpi-card:nth-child(7)::before { background: #94a3b8; } /* Lokasi (Grey) */\`;

content = content.replace(targetCSS, newCSS);
fs.writeFileSync(file, content);
