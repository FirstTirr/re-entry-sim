import re

with open('src/App.vue', 'r') as f:
    content = f.read()

# 1. Add activeTab ref
content = content.replace("const isPlaying = ref(false)", "const isPlaying = ref(false)\nconst activeTab = ref('simulator')")

# 2. Update Header
new_header = """    <header class="header">
      <div class="header-left">
        <div class="logo">🚀</div>
        <div class="title-container">
          <h1>Space Debris Re-entry Simulator</h1>
          <p>Ablation & Trajectory Analysis Dashboard</p>
        </div>
      </div>
      <nav class="nav-links">
        <button :class="{ active: activeTab === 'simulator' }" @click="activeTab = 'simulator'">Simulator</button>
        <button :class="{ active: activeTab === 'penjelasan' }" @click="activeTab = 'penjelasan'">Penjelasan</button>
      </nav>
    </header>"""

content = re.sub(r'<header class="header">.*?</header>', new_header, content, flags=re.DOTALL)

# 3. Add v-if to main-layout
content = content.replace('<div class="main-layout">', '<div class="main-layout" v-if="activeTab === \'simulator\'">')

# 4. Add Explanation Page and Footer
explanation_and_footer = """
    <div class="explanation-page" v-if="activeTab === 'penjelasan'">
      <div class="explanation-content">
        <h2>Tentang Project Ini</h2>
        <p>Space Debris Re-entry Simulator adalah aplikasi berbasis web yang mensimulasikan proses masuknya kembali (re-entry) sampah antariksa atau objek ke atmosfer Bumi. Aplikasi ini menggabungkan komputasi numerik berkinerja tinggi menggunakan Fortran di backend dengan visualisasi dinamis menggunakan Vue.js di frontend.</p>

        <h3>Kenapa Harus Menggunakan Rumus Dinamis?</h3>
        <p>Keccepatan dan variabel selama masuk atmosfer (re-entry) tidaklah konstan. Tekanan udara, densitas, suhu (Heat Flux), maupun koefisien drag (Cd) sangat bergantung pada kecepatan (Mach) dan ketinggian (Altitude). Jika kita hanya menggunakan rumus kinematika biasa (seperti gerak parabola dengan koefisien gesek udara yang tetap), hasilnya akan sangat tidak akurat karena:</p>
        <ul>
          <li><b>Densitas Udara Tidak Konstan:</b> Atmosfer Bumi semakin tebal saat objek mendekati tanah. Kami menggunakan model <i>U.S. Standard Atmosphere 1976</i>.</li>
          <li><b>Drag Transonic dan Hypersonic:</b> Pada kecepatan di atas kecepatan suara (Mach > 1), karakteristik hambatan objek berubah drastis akibat pembentukan gelombang kejut (shockwave). Koefisien drag yang konstan (misal Cd = 0.5) akan menghasilkan perhitungan energi Impact yang fatal.</li>
          <li><b>Panas Ekstrim (Ablation):</b> Saat kecepatan sangat tinggi (Hipersonik), bukan hanya gesekan udara yang terjadi, melainkan kompresi gas di depan objek. Hal ini memanaskan udara hingga berubah menjadi plasma. Rumus biasa tidak dapat menghitung titik leleh (Melting Point) material secara realistis. Oleh sebab itu, fungsi perhitungan Heat Flux dan G-Force harus sejalan dan berubah sepanjang waktu (dinamis).</li>
        </ul>

        <h3>Rumus-rumus Utama yang Dipakai</h3>
        <ul>
          <li><b>Kecepatan Suara & Mach:</b> $ a = \sqrt{\gamma \cdot R \cdot T} $ di mana $ T $ bergantung pada lapisan atmosfer.</li>
          <li><b>Gaya Hambat Udara (Drag):</b> $ F_d = \frac{1}{2} \rho v^2 C_d A $ - Dengan $ C_d $ sebagai fungsi berkelanjutan terhadap Mach.</li>
          <li><b>Gaya Gravitasi:</b> $ g = g_0 \left( \frac{R_e}{R_e + h} \right)^2 $ - Gravitasi menurun pada jangkauan luar angkasa.</li>
          <li><b>Stagnation Heating Rate:</b> $ \dot{q} = 1.83 \times 10^{-4} \cdot v^3 \cdot \sqrt{\frac{\rho}{R_n}} $ - Untuk menentukan seberapa cepat objek ini meleleh.</li>
          <li><b>Laju Pengikisan Massa (Ablation):</b> $ \frac{dm}{dt} = -\frac{\dot{q} \cdot A}{H_{ablation}} $</li>
        </ul>

        <h3>Tech Stack</h3>
        <div class="tech-stack">
          <span class="badge vue">Vue.js 3</span>
          <span class="badge chartjs">Chart.js</span>
          <span class="badge python">Python (Flask)</span>
          <span class="badge fortran">Fortran 90</span>
          <span class="badge meson">Meson / Ninja Build</span>
        </div>
      </div>
    </div>
    
    <footer class="footer">
      <p>&copy; 2026 Space Debris Simulator | Developed by <a href="https://tirr.my.id" target="_blank" rel="noopener noreferrer">tirr.my.id</a></p>
    </footer>
  </div>
</template>"""

content = content.replace("  </div>\n</template>", explanation_and_footer)

# 5. Add CSS
css = """
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  align-items: center;
}
.nav-links {
  display: flex;
  gap: 10px;
}
.nav-links button {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-muted);
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}
.nav-links button:hover {
  background: var(--bg-card);
  color: var(--text);
}
.nav-links button.active {
  background: var(--primary);
  color: white;
  border-color: var(--primary);
}

/* Explanation Page */
.explanation-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem;
  animation: fadeIn 0.4s ease-out;
}
.explanation-content {
  background: var(--bg-card);
  padding: 2.5rem;
  border-radius: 16px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}
.explanation-content h2 {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  color: var(--primary);
}
.explanation-content h3 {
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-size: 1.4rem;
  color: #a5b4fc;
}
.explanation-content p {
  line-height: 1.7;
  margin-bottom: 1rem;
  color: var(--text-muted);
}
.explanation-content ul {
  padding-left: 2rem;
  margin-bottom: 1.5rem;
  color: var(--text-muted);
}
.explanation-content li {
  margin-bottom: 0.8rem;
  line-height: 1.6;
}

.tech-stack {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 1rem;
}
.badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 600;
}
.badge.vue { background: rgba(16, 185, 129, 0.2); color: #10b981; }
.badge.chartjs { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.badge.python { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
.badge.fortran { background: rgba(139, 92, 246, 0.2); color: #8b5cf6; }
.badge.meson { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

/* Footer */
.footer {
  text-align: center;
  padding: 2rem;
  margin-top: 2rem;
  border-top: 1px solid var(--border-color);
  color: var(--text-muted);
  font-size: 0.95rem;
}
.footer a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}
.footer a:hover {
  text-decoration: underline;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
"""

content = content.replace("</style>", css + "\n</style>")

with open('src/App.vue', 'w') as f:
    f.write(content)
