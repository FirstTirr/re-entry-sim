const fs = require('fs');
const file = './src/App.vue';
let content = fs.readFileSync(file, 'utf8');

// 1. Add New Inputs to script
content = content.replace(
  "heat_of_ablation: 1e7,",
  "heat_of_ablation: 1e7,\n  shape_factor: 1.0,\n  initial_lat: 0.0,\n  initial_lon: 0.0,\n  material_type: 'custom',"
);

// 2. Add New Chart Variables & Table Logic
const scriptSetupEnd = content.indexOf('// Common Style For Charts');
const beforeCommon = content.substring(scriptSetupEnd - 50, scriptSetupEnd);
const newComputeds = `
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
    tension: 0.2, pointRadius: 0
  }]
}))

const heatChartData = computed(() => ({
  labels: results.value ? results.value.time : [],
  datasets: [{
    label: 'Heating Rate (W/m²)',
    data: results.value ? results.value.heating_rate : [],
    borderColor: '#ef4444',
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    tension: 0.2, pointRadius: 0
  }]
}))
`;
content = content.replace('// Common Style For Charts', newComputeds + '\n// Common Style For Charts');

// 3. Add to UI inputs
const inputGrid = `<div class="form-group">
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
            </div>`;
content = content.replace(/<div class="form-group">\s*<label>Max Waktu \(s\)<\/label>\s*<input type="number" step="10" v-model\.number="params.t_max" \/>\s*<\/div>/, inputGrid);

// 4. Update the Simulation assignment hook to get new arrays
const oldSimRes = `mass: [rawData.mass[0]]`;
const newSimRes = `mass: [rawData.mass[0]],
        g_force: [rawData.g_force[0]],
        heating_rate: [rawData.heating_rate[0]],
        latitude: [rawData.latitude[0]],
        longitude: [rawData.longitude[0]]`;
content = content.replace(oldSimRes, newSimRes);

const oldSimSlice = `mass: rawData.mass.slice(0, nextFrame)`;
const newSimSlice = `mass: rawData.mass.slice(0, nextFrame),
                    g_force: rawData.g_force.slice(0, nextFrame),
                    heating_rate: rawData.heating_rate.slice(0, nextFrame),
                    latitude: rawData.latitude.slice(0, nextFrame),
                    longitude: rawData.longitude.slice(0, nextFrame)`;
content = content.replace(oldSimSlice, newSimSlice);

// 5. Add new KPI cards
const kpiCards = `
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
          </div>`;
content = content.replace('</div>\n        </div>\n\n        <div class="charts-board"', kpiCards + '\n</div>\n        </div>\n\n        <div class="charts-board"');

// 6. Add new Charts
const newCharts = `
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
          </div>`;
content = content.replace('</div>\n        </div>\n        \n        <div class="empty-state"', '</div>\n' + newCharts + '\n        </div>\n        \n        <div class="empty-state"');

fs.writeFileSync(file, content);
