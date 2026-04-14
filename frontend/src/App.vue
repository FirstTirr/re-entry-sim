<template>
  <div class="dashboard">
        <header class="header">
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
    </header>

    <div class="main-layout" v-if="activeTab === 'simulator'">
      <aside class="sidebar">
        <div class="panel">
          <h2><i class="icon-settings"></i> Parameter Awal</h2>
          <div class="input-grid">
            <div class="form-group">
              <label>Material / Alloy</label>
              <select v-model="materialType" @change="updateMaterial">
                <option value="alu">Aluminium 6061</option>
                <option value="ti">Titanium Alloy</option>
                <option value="carbon">Carbon-Carbon Shield</option>
              </select>
            </div>
            <div class="form-group">
              <label>Massa (kg)</label>
              <input type="number" v-model.number="params.mass" />
            </div>
            <div class="form-group">
              <label>Kec. Awal (m/s)</label>
              <input type="number" v-model.number="params.velocity" />
            </div>
            <div class="form-group">
              <label>Ketinggian (m)</label>
              <input type="number" v-model.number="params.altitude" />
            </div>
            <div class="form-group">
              <label>Sudut (rad)</label>
              <input type="number" step="0.01" v-model.number="params.gamma" />
            </div>
            <div class="form-group">
              <label>Luas (m²)</label>
              <input type="number" step="0.1" v-model.number="params.area" />
            </div>
            <div class="form-group">
              <label>Drag Coeff</label>
              <input type="number" step="0.1" v-model.number="params.drag_coeff" />
            </div>
            <div class="form-group">
              <label>Step Waktu (s)</label>
              <input type="number" step="0.1" v-model.number="params.dt" />
            </div>
            <div class="form-group">
              <label>Shape Factor</label>
              <input type="number" step="0.1" v-model.number="params.shape_factor" />
            </div>
            <div class="form-group">
              <label>Latitude Awal</label>
              <input type="number" step="0.1" v-model.number="params.initial_lat" />
            </div>
            <div class="form-group">
              <label>Longitude Awal</label>
              <input type="number" step="0.1" v-model.number="params.initial_lon" />
            </div>
            <div class="form-group">
              <label>Maks Waktu (s)</label>
              <input type="number" step="10" v-model.number="params.t_max" />
            </div>
          </div>
          <div class="toggle-group">
            <label class="toggle-label">
              <input type="checkbox" v-model="liveTelemetryEnabled" />
              Aktifkan Live Telemetry
            </label>
          </div>
          <button @click="runSimulation" :disabled="loading" class="btn-primary">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Menghitung...' : (isPlaying ? 'Ulangi Simulasi' : 'Mulai Simulasi') }}
          </button>
          <div v-if="error" class="error-msg">{{ error }}</div>
          
          <div class="csv-container" v-if="results">
            <h3>Live Telemetry Log (CSV)</h3>
            <textarea readonly :value="csvContent" ref="csvBox"></textarea>
            <button @click="downloadCsv" class="btn-primary" style="margin-top: 1rem">Download CSV</button>
          </div>
        </div>
      </aside>

      <main class="content">
        <div class="kpi-board" v-if="results">
          <div class="kpi-card">
            <div class="kpi-title">{{ isPlaying ? "Sisa Massa (Live)" : "Sisa Massa Akhir" }} <span v-if="isPlaying" class="live-dot"></span></div>
            <div class="kpi-value">{{ lastMass.toFixed(2) }} <span class="unit">kg</span></div>
            <div class="kpi-sub" :class="{ 'warning': lossPercent > 50 }">
              Hilang: {{ lossPercent.toFixed(1) }}%
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">{{ isPlaying ? "Ketinggian (Live)" : "Ketinggian Akhir" }}</div>
            <div class="kpi-value">{{ (lastAlt / 1000).toFixed(2) }} <span class="unit">km</span></div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">{{ isPlaying ? "Kecepatan (Live)" : "Kecepatan Akhir" }}</div>
            <div class="kpi-value">{{ lastVel.toFixed(0) }} <span class="unit">m/s</span></div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">{{ isPlaying ? "Waktu Elapsed" : "Total Waktu" }}</div>
            <div class="kpi-value">{{ lastTime.toFixed(1) }} <span class="unit">s</span></div>
          </div>
          
          <div class="kpi-card">
            <div class="kpi-title">Peak G-Force</div>
            <div class="kpi-value">{{ peakG }} <span class="unit">G</span></div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">Peak Heat Flux</div>
            <div class="kpi-value">{{ peakQ }} <span class="unit">W/m²</span></div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">Lokasi Jatuh</div>
            <div class="kpi-value" style="font-size: 1rem">{{ finalLat }}°, {{ finalLon }}°</div>
          </div>

          
          <div class="kpi-card" :class="{'danger-bg': isStructuralFailure}">
            <div class="kpi-title">Structural Status</div>
            <div class="kpi-value" style="font-size: 1.2rem; color: #ef4444" v-if="isStructuralFailure">⚠️ MELTED / FAILED</div>
            <div class="kpi-value" style="font-size: 1.2rem; color: #10b981" v-else>✅ INTACT</div>
          </div>
          <div class="kpi-card" :class="{'blackout-bg': isBlackout}">
            <div class="kpi-title">Comms Radio (Plasma)</div>
            <div class="kpi-value" style="font-size: 1.2rem; color: #f59e0b" v-if="isBlackout">🔥 BLACKOUT</div>
            <div class="kpi-value" style="font-size: 1.2rem; color: #38bdf8" v-else>📡 NOMINAL</div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">Impact Velocity</div>
            <div class="kpi-value">{{ impactVelocity.toFixed(0) }} <span class="unit">m/s</span></div>
          </div>
          <div class="kpi-card">
            <div class="kpi-title">Impact Energy</div>
            <div class="kpi-value">{{ impactEnergyTNT.toFixed(4) }} <span class="unit">Ton TNT</span></div>
            <div class="kpi-sub">{{ impactEnergyJ.toExponential(2) }} J</div>
          </div>

</div>

        <div class="view-toggles" v-if="results" style="display: flex; gap: 10px; margin-bottom: 20px; justify-content: center;">
          <button class="nav-btn" :class="{active: activeView === 'grafik'}" @click="activeView = 'grafik'">📊 Grafik 2D</button>
          <button class="nav-btn" :class="{active: activeView === 'globe'}" @click="activeView = 'globe'">🌍 Globe 3D</button>
        </div>

        <div class="globe-wrap" v-show="activeView === 'globe' && results" style="width: 100%; height: 600px; border-radius: 12px; overflow: hidden; background: #000; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
          <div id="globeViz" style="width: 100%; height: 100%;"></div>
        </div>

        <div class="charts-board" v-show="activeView === 'grafik' && results">
          <div class="chart-card">
            <h3>Lintasan Trajektori & Profil Kecepatan</h3>
            <div class="chart-wrapper">
              <Line :data="trajectoryChartData" :options="trajectoryOptions" />
            </div>
          </div>
          <div class="chart-card">
            <h3>Laju Pengikisan Massa (Ablation)</h3>
            <div class="chart-wrapper">
              <Line :data="massChartData" :options="massOptions" />
            </div>
          </div>

          <div class="chart-card">
            <h3>Beban Mekanik (G-Force)</h3>
            <div class="chart-wrapper">
              <Line :data="gForceChartData" :options="trajectoryOptions" />
            </div>
          </div>
          <div class="chart-card">
            <h3>Laju Pemanasan (Heating Rate)</h3>
            <div class="chart-wrapper">
              <Line :data="heatChartData" :options="trajectoryOptions" />
            </div>
          </div>
        </div>
        
        <div class="empty-state" v-if="!results">
          <div class="empty-icon">🛰️</div>
          <h2>Siap Memulai Simulasi</h2>
          <p>Sesuaikan parameter di sebelah kiri dan klik "Mulai Simulasi" untuk melihat visualisasi kurva penerbangan dan profil termodinamika pengikisan puing angkasa secara realistis.</p>
        </div>
      </main>
    </div>

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
          <li><b>Gaya Hambat Udara (Drag):</b> $ F_d = rac{1}{2} 
ho v^2 C_d A $ - Dengan $ C_d $ sebagai fungsi berkelanjutan terhadap Mach.</li>
          <li><b>Gaya Gravitasi:</b> $ g = g_0 \left( rac{R_e}{R_e + h} 
ight)^2 $ - Gravitasi menurun pada jangkauan luar angkasa.</li>
          <li><b>Stagnation Heating Rate:</b> $ \dot{q} = 1.83 	imes 10^{-4} \cdot v^3 \cdot \sqrt{rac{
ho}{R_n}} $ - Untuk menentukan seberapa cepat objek ini meleleh.</li>
          <li><b>Laju Pengikisan Massa (Ablation):</b> $ rac{dm}{dt} = -rac{\dot{q} \cdot A}{H_{ablation}} $</li>
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
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import Globe from 'globe.gl'
import * as THREE from 'three'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, Filler
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler)

const params = ref({
  velocity: 7800.0,
  gamma: -0.05,
  altitude: 400000.0,
  mass: 100.0,
  area: 2.0,
  drag_coeff: 2.2,
  heat_of_ablation: 1e7,
  shape_factor: 1.0,
  initial_lat: 0.0,
  initial_lon: 0.0,
  material_type: 'custom',
  dt: 0.5,
  t_max: 4000.0
})

const results = ref(null)
const fullResults = ref(null)
const loading = ref(false)
const error = ref(null)
const isPlaying = ref(false)
const activeTab = ref('simulator')
const activeView = ref('grafik')
const maxHeatFluxLimit = ref(1e6)
const materialType = ref('alu')
const simulationInterval = ref(null)
const currentFrame = ref(0)
const liveTelemetryEnabled = ref(true)

onMounted(() => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition((position) => {
      params.value.initial_lat = parseFloat(position.coords.latitude.toFixed(4));
      params.value.initial_lon = parseFloat(position.coords.longitude.toFixed(4));
    }, (err) => {
      console.warn("Geolocation ditolak atau gagal:", err);
    });
  }
})



const csvContent = computed(() => {
  if (!results.value) return ""
  let str = "Time(s),Altitude(km),Velocity(m/s),Mach,G-Force,HeatFlux(W/m2),Mass(kg),Lat,Lon\n"
  for(let i=0; i<results.value.time.length; i++) {
    // Only sample every 50 frames to avoid lag in textarea
    if (i % 50 === 0 || i === results.value.time.length - 1) {
       str += `${results.value.time[i].toFixed(2)},${(results.value.altitude[i]/1000).toFixed(2)},${results.value.velocity[i].toFixed(1)},${results.value.mach[i].toFixed(2)},${results.value.g_force[i].toFixed(2)},${results.value.heating_rate[i].toExponential(2)},${results.value.mass[i].toFixed(2)},${results.value.latitude[i].toFixed(4)},${results.value.longitude[i].toFixed(4)}\n`
    }
  }
  return str
})
const csvBox = ref(null)
const downloadCsv = () => {
  // Use full raw data for download, not downsampled
  if (!fullResults.value) return
  let str = "Time(s),Altitude(km),Velocity(m/s),Mach,G-Force,HeatFlux(W/m2),Mass(kg),Lat,Lon\n"
  for(let i=0; i<fullResults.value.time.length; i++) {
       str += `${fullResults.value.time[i].toFixed(2)},${(fullResults.value.altitude[i]/1000).toFixed(2)},${fullResults.value.velocity[i].toFixed(1)},${fullResults.value.mach[i].toFixed(2)},${fullResults.value.g_force[i].toFixed(2)},${fullResults.value.heating_rate[i].toExponential(2)},${fullResults.value.mass[i].toFixed(2)},${fullResults.value.latitude[i].toFixed(4)},${fullResults.value.longitude[i].toFixed(4)}\n`
  }
  const blob = new Blob([str], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.setAttribute('href', url)
  a.setAttribute('download', 'telemetry_log.csv')
  document.body.appendChild(a)
  a.click()
  a.remove()
}

// Auto scroll textarea

watch(csvContent, () => {
    if (csvBox.value) {
        csvBox.value.scrollTop = csvBox.value.scrollHeight;
    }
})

const updateMaterial = () => {
  if (materialType.value === 'alu') {
    params.value.heat_of_ablation = 1e7;
    maxHeatFluxLimit.value = 1e6; // 1 MW/m2
  } else if (materialType.value === 'ti') {
    params.value.heat_of_ablation = 2e7;
    maxHeatFluxLimit.value = 3e6; // 3 MW/m2
  } else if (materialType.value === 'carbon') {
    params.value.heat_of_ablation = 3.5e7;
    maxHeatFluxLimit.value = 15e6; // 15 MW/m2
  }
}
updateMaterial() // init


const globeEl = ref(null)
let myGlobe = null

watch(() => [activeView.value, results.value], async ([newView, newResults]) => {
  if (newView === 'globe' && myGlobe && newResults) {
     await nextTick();
     const container = document.getElementById('globeViz');
     if (container) {
         myGlobe.width(container.clientWidth);
         myGlobe.height(container.clientHeight);
     }
  }
}, { immediate: true })

const updateGlobeData = (newData) => {
    if(!newData || activeView.value !== 'globe') return;
    
    const renderGlobe = () => {
        const globeContainer = document.getElementById('globeViz');
        if(!globeContainer) return;
        
        let width = globeContainer.clientWidth || 800;
        let height = globeContainer.clientHeight || 600;
        
        if(!myGlobe) {
            myGlobe = new Globe(globeContainer)
                .width(width)
                .height(height)
                .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-night.jpg')
                .bumpImageUrl('https://unpkg.com/three-globe/example/img/earth-topology.png')
                .backgroundColor('#111111')
                .showAtmosphere(true);
        } else {
            if (width > 0) {
                myGlobe.width(width);
                myGlobe.height(height);
            }
        }
        
        const N = newData.latitude.length;
        if (N === 0) return;
        
        const pathData = [];
        const stepGlobe = Math.max(1, Math.floor(N / 300));
        
        for(let i=0; i < N - stepGlobe; i+=stepGlobe) {
           let vel = newData.velocity[i];
           let pathColor = '#3b82f6'; // Normal (Biru) untuk V < 3000 m/s
           if (vel >= 6000) pathColor = '#ef4444'; // Sangat Kencang (Merah)
           else if (vel >= 3000) pathColor = '#eab308'; // Agak Kencang (Kuning)
           
           pathData.push({
              coords: [
                  {
                      lat: newData.latitude[i],
                      lng: newData.longitude[i],
                      alt: Math.max(0, newData.altitude[i] / 6371000)
                  },
                  {
                      lat: newData.latitude[i + stepGlobe],
                      lng: newData.longitude[i + stepGlobe],
                      alt: Math.max(0, newData.altitude[i + stepGlobe] / 6371000)
                  }
              ],
              color: pathColor
           });
        }
        
        // Final segment connecting the last gap
        let finalVel = newData.velocity[N-1];
        let finalColor = finalVel >= 6000 ? '#ef4444' : (finalVel >= 3000 ? '#eab308' : '#3b82f6');
        
        // To avoid missing the exact impact coordinate due to skipping
        const lastI = Math.floor((N - 1) / stepGlobe) * stepGlobe;
        if (lastI < N - 1) {
            pathData.push({
                coords: [
                    { lat: newData.latitude[lastI], lng: newData.longitude[lastI], alt: Math.max(0, newData.altitude[lastI] / 6371000) },
                    { lat: newData.latitude[N-1], lng: newData.longitude[N-1], alt: Math.max(0, newData.altitude[N-1] / 6371000) }
                ],
                color: finalColor
            });
        }

        myGlobe.pathsData(pathData)
          .pathPoints('coords')
          .pathPointLat(d => d.lat)
          .pathPointLng(d => d.lng)
          .pathPointAlt(d => d.alt)
          .pathColor(segment => segment.color)
          .pathStroke(2.5)
          .pathTransitionDuration(0);
          
        // Tambahkan Titik Awal & Lokasi Roket (Current Point)
        const startPoint = { 
            lat: newData.latitude[0], 
            lng: newData.longitude[0], 
            alt: Math.max(0, newData.altitude[0] / 6371000),
            name: "START MENGorbit"
        };
        const currentPoint = {
            lat: newData.latitude[N-1], 
            lng: newData.longitude[N-1], 
            alt: Math.max(0, newData.altitude[N-1] / 6371000),
            name: isPlaying.value ? "ROKET TRANSECT" : "IMPACT (JATUH)"
        };
        
        myGlobe.labelsData([startPoint, currentPoint])
          .labelLat(d => d.lat)
          .labelLng(d => d.lng)
          .labelAltitude(d => d.alt + 0.05)
          .labelDotRadius(0.8)
          .labelDotOrientation(() => 'bottom')
          .labelColor(d => d.name === "START MENGorbit" ? '#3b82f6' : '#ef4444')
          .labelText(d => d.name)
          .labelSize(2.0)
          .labelResolution(2);
          
        if (!isPlaying.value) {
            myGlobe.pointOfView({ lat: newData.latitude[N-1], lng: newData.longitude[N-1], altitude: 2.2 }, 1000);
        } else if (N < 10) {
            myGlobe.pointOfView({ lat: newData.latitude[0], lng: newData.longitude[0], altitude: 2.2 }, 0);
        }
    };
    
    // Skip timeout frame delay if globe already generated to allow 60fps live sync
    if (!myGlobe) {
        setTimeout(renderGlobe, 150);
    } else {
        renderGlobe();
    }
}

watch(results, (newData) => {
    updateGlobeData(newData);
}, { deep: true })

watch(activeView, (newView) => {
    if (newView === 'globe') {
        updateGlobeData(results.value);
    }
})

const runSimulation = async () => {
  if (isPlaying.value) {
    if (simulationInterval.value) cancelAnimationFrame(simulationInterval.value)
    isPlaying.value = false
  }

  loading.value = true
  error.value = null
  try {
    const res = await fetch('http://localhost:8000/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params.value)
    })
    
    if (!res.ok) {
      const errData = await res.json()
      throw new Error(errData.detail || 'Terjadi kesalahan pada server backend.')
    }
    
    fullResults.value = await res.json()
    const rawData = fullResults.value
    
    // Mulai Telemetry dengan titik 0
    if (liveTelemetryEnabled.value) {
      results.value = {
        time: [rawData.time[0]],
        altitude: [rawData.altitude[0]],
        velocity: [rawData.velocity[0]],
        mass: [rawData.mass[0]],
        g_force: [rawData.g_force[0]],
        heating_rate: [rawData.heating_rate[0]],
        latitude: [rawData.latitude[0]],
        longitude: [rawData.longitude[0]],
        mach: [rawData.mach[0]]
      }
      
      currentFrame.value = 1
      const totalPoints = rawData.time.length
      const stepSize = Math.max(1, Math.ceil(totalPoints / 1200))
      
      // Tunggu sedikit agar UI sinkronisasi status loading
      setTimeout(() => {
          isPlaying.value = true
          const performAnimation = () => {
            if (!isPlaying.value) return; // kalau di-cancel
            let nextFrame = currentFrame.value + stepSize;
            if (nextFrame >= totalPoints) {
                nextFrame = totalPoints;
                results.value = fullResults.value;
                isPlaying.value = false;
            } else {
                results.value = {
                    time: rawData.time.slice(0, nextFrame),
                    altitude: rawData.altitude.slice(0, nextFrame),
                    velocity: rawData.velocity.slice(0, nextFrame),
                    mass: rawData.mass.slice(0, nextFrame),
                    g_force: rawData.g_force.slice(0, nextFrame),
                    heating_rate: rawData.heating_rate.slice(0, nextFrame),
                    latitude: rawData.latitude.slice(0, nextFrame),
                    longitude: rawData.longitude.slice(0, nextFrame),
                    mach: rawData.mach.slice(0, nextFrame)
                };
                currentFrame.value = nextFrame;
                simulationInterval.value = requestAnimationFrame(performAnimation);
            }
          };
          simulationInterval.value = requestAnimationFrame(performAnimation);
      }, 100)
    } else {
      results.value = fullResults.value
      isPlaying.value = false
    }
    
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

// Data Extractors
const lastMass = computed(() => results.value ? results.value.mass[results.value.mass.length - 1] : 0)
const lastAlt = computed(() => results.value ? results.value.altitude[results.value.altitude.length - 1] : 0)
const lastVel = computed(() => results.value ? results.value.velocity[results.value.velocity.length - 1] : 0)
const lastTime = computed(() => results.value ? results.value.time[results.value.time.length - 1] : 0)
const lossPercent = computed(() => results.value ? ((params.value.mass - lastMass.value) / params.value.mass) * 100 : 0)


const peakG = computed(() => results.value && results.value.g_force ? Math.max(...results.value.g_force).toFixed(2) : 0)
const peakQ = computed(() => results.value && results.value.heating_rate ? Math.max(...results.value.heating_rate).toExponential(2) : 0)
const finalLat = computed(() => results.value && results.value.latitude ? results.value.latitude[results.value.latitude.length - 1].toFixed(4) : 0)
const finalLon = computed(() => results.value && results.value.longitude ? results.value.longitude[results.value.longitude.length - 1].toFixed(4) : 0)

const gForceChartData = computed(() => ({
  labels: results.value ? results.value.time : [],
  datasets: [{
    label: 'G-Force Load (G)',
    data: results.value ? results.value.g_force : [],
    borderColor: '#eab308',
    backgroundColor: 'rgba(234, 179, 8, 0.1)',
    tension: 0.35,
    cubicInterpolationMode: 'monotone',
    pointRadius: 0
  }]
}))

const heatChartData = computed(() => ({
  labels: results.value ? results.value.time : [],
  datasets: [{
    label: 'Heating Rate (W/m²)',
    data: results.value ? results.value.heating_rate : [],
    borderColor: '#ef4444',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    tension: 0.35,
    cubicInterpolationMode: 'monotone',
    pointRadius: 0
  }]
}))


const impactVelocity = computed(() => results.value && results.value.velocity.length > 0 ? results.value.velocity[results.value.velocity.length - 1] : 0)
const impactEnergyJ = computed(() => 0.5 * lastMass.value * Math.pow(impactVelocity.value, 2))
const impactEnergyTNT = computed(() => impactEnergyJ.value / 4.184e9) // 1 Ton TNT = 4.184 GJ
const isStructuralFailure = computed(() => results.value && results.value.heating_rate ? Math.max(...results.value.heating_rate) > maxHeatFluxLimit.value : false)
const isBlackout = computed(() => {
  if (!results.value) return false
  const currentQ = results.value.heating_rate[results.value.heating_rate.length - 1] || 0;
  const currentAlt = results.value.altitude[results.value.altitude.length - 1] || 120000;
  return currentAlt < 90000 && currentAlt > 35000 && currentQ > 5e5;
})

// Common Style For Charts
const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  normalized: true,
  interaction: { mode: 'index', intersect: false },
  plugins: { 
    legend: { labels: { color: '#cbd5e1', font: { family: 'Inter' } } },
    tooltip: { backgroundColor: '#1e293b', titleColor: '#f8fafc', bodyColor: '#cbd5e1', borderColor: '#334155', borderWidth: 1 }
  },
  scales: {
    x: { 
      grid: { color: '#334155' }, 
      ticks: { color: '#94a3b8', maxTicksLimit: 15 }, 
      title: { display: true, text: 'Waktu (Detik)', color: '#94a3b8' } 
    }
  }
}

const trajectoryChartData = computed(() => {
  if (!results.value) return { labels: [], datasets: [] }
  return {
    labels: results.value.time,
    datasets: [
      {
        label: 'Ketinggian (km)',
        data: results.value.altitude.map(a => a / 1000),
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        yAxisID: 'y',
        fill: true,
        tension: 0.35,
        cubicInterpolationMode: 'monotone',
        pointRadius: 0,
        borderWidth: 2
      },
      {
        label: 'Kecepatan (m/s)',
        data: results.value.velocity,
        borderColor: '#f43f5e',
        backgroundColor: 'transparent',
        yAxisID: 'y1',
        tension: 0.35,
        cubicInterpolationMode: 'monotone',
        pointRadius: 0,
        borderWidth: 2
      }
    ]
  }
})

const trajectoryOptions = computed(() => ({
  ...commonOptions,
  scales: {
    ...commonOptions.scales,
    y: { 
      type: 'linear', display: true, position: 'left', 
      grid: { color: '#334155' }, ticks: { color: '#38bdf8' },
      title: { display: true, text: 'Ketinggian (km)', color: '#38bdf8' }
    },
    y1: { 
      type: 'linear', display: true, position: 'right', 
      grid: { drawOnChartArea: false }, ticks: { color: '#f43f5e' },
      title: { display: true, text: 'Kecepatan (m/s)', color: '#f43f5e' }
    },
  }
}))

const massChartData = computed(() => {
  if (!results.value) return { labels: [], datasets: [] }
  return {
    labels: results.value.time,
    datasets: [{
      label: 'Sisa Massa Aktual (kg)',
      data: results.value.mass,
      borderColor: '#10b981',
      backgroundColor: 'rgba(16, 185, 129, 0.15)',
      fill: true,
      tension: 0.35,
      cubicInterpolationMode: 'monotone',
      pointRadius: 0,
      borderWidth: 2
    }]
  }
})

const massOptions = computed(() => ({
  ...commonOptions,
  scales: {
    ...commonOptions.scales,
    y: { 
      grid: { color: '#334155' }, ticks: { color: '#10b981' },
      title: { display: true, text: 'Massa Objek (kg)', color: '#10b981' }
    }
  }
}))
</script>

<style>
/* CSS RESET & VARIABLES */
:root {
  --bg-dark: #0f172a;
  --bg-card: #1e293b;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --accent-blue: #3b82f6;
  --accent-blue-hover: #2563eb;
  --border-color: #334155;
  --danger: #ef4444;
  --success: #10b981;
}

body {
  margin: 0;
  background-color: var(--bg-dark);
  color: var(--text-main);
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.dashboard {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* HEADER */
.header {
  display: flex;
  align-items: center;
  padding: 1.25rem 2.5rem;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.logo {
  font-size: 2.5rem;
  margin-right: 1.25rem;
  filter: drop-shadow(0 0 8px rgba(59, 130, 246, 0.5));
}

.title-container h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  background: linear-gradient(to right, #60a5fa, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.title-container p {
  margin: 0.25rem 0 0 0;
  color: var(--text-muted);
  font-size: 0.9rem;
}

/* LAYOUT */
.main-layout {
  display: flex;
  flex: 1;
  padding: 2rem;
  gap: 2rem;
  width: 100%;
  box-sizing: border-box;
}

.sidebar {
  width: 400px;
  flex-shrink: 0;
}

/* INPUT PANEL */
.panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 1.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.panel h2 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.15rem;
  color: #e2e8f0;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 1rem;
}

.toggle-group {
  margin: 1.5rem 0 1rem;
  display: flex;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.95rem;
  cursor: pointer;
  user-select: none;
}

.toggle-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: var(--primary-color);
  cursor: pointer;
}

.input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.form-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.form-group input {
  background: var(--bg-dark);
  border: 1px solid var(--border-color);
  color: var(--text-main);
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s ease;
  width: 100%;
  box-sizing: border-box;
  min-width: 0;
}

.form-group input:focus {
  outline: none;
  border-color: var(--accent-blue);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
}

/* BUTTON */
.btn-primary {
  margin-top: 1.75rem;
  width: 100%;
  background: var(--accent-blue);
  color: white;
  border: none;
  padding: 0.875rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.05rem;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-blue-hover);
  transform: translateY(-1px);
  box-shadow: 0 6px 15px rgba(59, 130, 246, 0.4);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.error-msg {
  margin-top: 1.25rem;
  padding: 1rem;
  background: rgba(239, 68, 68, 0.1);
  border-left: 4px solid var(--danger);
  color: #fca5a5;
  font-size: 0.875rem;
  border-radius: 6px;
}

/* CONTENT & KPI */
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-width: 0;
}

.kpi-board {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1.5rem;
}

.kpi-card {
  background: linear-gradient(145deg, var(--bg-card) 0%, #172033 100%);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; width: 4px; height: 100%;
  background: var(--accent-blue);
}
.kpi-card:nth-child(1)::before { background: #10b981; }
.kpi-card:nth-child(2)::before { background: #38bdf8; }
.kpi-card:nth-child(3)::before { background: #f43f5e; }
.kpi-card:nth-child(4)::before { background: #a855f7; }
.kpi-card:nth-child(5)::before { background: #eab308; }
.kpi-card:nth-child(6)::before { background: #ef4444; }
.kpi-card:nth-child(7)::before { background: #94a3b8; }

.kpi-title {
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.kpi-value {
  font-size: 2.25rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.1;
}

.kpi-value .unit {
  font-size: 1rem;
  color: var(--text-muted);
  font-weight: 500;
  margin-left: 2px;
}

.kpi-sub {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: var(--success);
  font-weight: 600;
  background: rgba(16, 185, 129, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: inline-block;
  align-self: flex-start;
}

.kpi-sub.warning {
  color: var(--danger);
  background: rgba(239, 68, 68, 0.1);
}

/* CHARTS */
.charts-board {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1400px) {
  .charts-board {
    grid-template-columns: 1fr 1fr;
  }
}

.chart-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.chart-card h3 {
  margin: 0 0 1.5rem 0;
  font-size: 1.15rem;
  color: #f8fafc;
  font-weight: 600;
}

.chart-wrapper {
  position: relative;
  height: 380px;
  width: 100%;
}

/* EMPTY STATE */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 2px dashed #475569;
  border-radius: 16px;
  padding: 4rem 2rem;
  text-align: center;
  box-shadow: inset 0 0 50px rgba(0,0,0,0.2);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  opacity: 0.9;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(2deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}

.empty-state h2 {
  margin: 0 0 1rem;
  font-size: 1.75rem;
  font-weight: 700;
}

.empty-state p {
  color: var(--text-muted);
  max-width: 600px;
  line-height: 1.7;
  margin: 0;
  font-size: 1.05rem;
}

@media (max-width: 1024px) {
  .main-layout { flex-direction: column; }
  .sidebar { width: 100%; }
}

.live-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ff4757;
  margin-left: 8px;
  animation: blink 1s infinite;
}

@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
}

.csv-container {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 1.5rem;
  margin-top: 1.5rem;
  border: 1px solid var(--border-color);
}
.csv-container textarea {
  width: 100%;
  height: 200px;
  background: #0f172a;
  color: #a5b4fc;
  border: 1px solid #334155;
  padding: 1rem;
  font-family: 'Consolas', monospace;
  font-size: 0.85rem;
  border-radius: 8px;
  resize: none;
  box-sizing: border-box;
}
.danger-bg { border-left: 4px solid #ef4444; }
.blackout-bg { border-left: 4px solid #f59e0b; }


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

</style>
