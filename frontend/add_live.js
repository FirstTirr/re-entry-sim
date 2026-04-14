const fs = require('fs');
const file = './src/App.vue';
let content = fs.readFileSync(file, 'utf8');

// 1. Add isPlaying state inside script setup
content = content.replace(
  "const results = ref(null)",
  "const results = ref(null)\nconst fullResults = ref(null)\nconst isPlaying = ref(false)\nconst simulationInterval = ref(null)\nconst currentFrame = ref(0)"
);

// 2. Modify runSimulation to do the interval animation
const oldSim = `const runSimulation = async () => {
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
    
    results.value = await res.json()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}`;

const newSim = `const runSimulation = async () => {
  if(isPlaying.value) {
    if(simulationInterval.value) clearInterval(simulationInterval.value)
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
    const rawData = fullResults.value;
    
    // Start Live Telemetry
    results.value = {
      time: [rawData.time[0]],
      altitude: [rawData.altitude[0]],
      velocity: [rawData.velocity[0]],
      mass: [rawData.mass[0]]
    }
    
    currentFrame.value = 1
    
    const totalPoints = rawData.time.length;
    // Aim for approx 5 seconds telemetry
    // Assuming 60 fps (16ms interval), we have ~300 frames.
    const stepSize = Math.max(1, Math.ceil(totalPoints / 300));
    
    // Wait until loading finishes before starting animation safely
    setTimeout(() => {
        isPlaying.value = true
        simulationInterval.value = setInterval(() => {
            let nextFrame = currentFrame.value + stepSize;
            if (nextFrame >= totalPoints) {
                // Done
                nextFrame = totalPoints;
                results.value = fullResults.value;
                isPlaying.value = false;
                clearInterval(simulationInterval.value);
            } else {
                results.value = {
                    time: rawData.time.slice(0, nextFrame),
                    altitude: rawData.altitude.slice(0, nextFrame),
                    velocity: rawData.velocity.slice(0, nextFrame),
                    mass: rawData.mass.slice(0, nextFrame)
                };
            }
            currentFrame.value = nextFrame;
        }, 16);
    }, 100);

  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}`;

content = content.replace(oldSim, newSim);

// 3. Modify titles
content = content.replace(
  '<div class="kpi-title">Sisa Massa Akhir</div>',
  '<div class="kpi-title">{{ isPlaying ? "Sisa Massa (Live)" : "Sisa Massa Akhir" }} <span v-if="isPlaying" class="live-dot"></span></div>'
);
content = content.replace(
  '<div class="kpi-title">Ketinggian Akhir</div>',
  '<div class="kpi-title">{{ isPlaying ? "Ketinggian (Live)" : "Ketinggian Akhir" }}</div>'
);
content = content.replace(
  '<div class="kpi-title">Kecepatan Akhir</div>',
  '<div class="kpi-title">{{ isPlaying ? "Kecepatan (Live)" : "Kecepatan Akhir" }}</div>'
);
content = content.replace(
  '<div class="kpi-title">Total Waktu</div>',
  '<div class="kpi-title">{{ isPlaying ? "Waktu Elapsed (Live)" : "Total Waktu" }}</div>'
);

// Add css for live dot
if (!content.includes('.live-dot')) {
    content = content.replace('</style>', `
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
</style>`);
}

fs.writeFileSync(file, content);
console.log("Telemetry injection complete!");
