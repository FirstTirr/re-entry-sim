import re

with open('src/App.vue', 'r') as f:
    content = f.read()

# 1. Import Globe
import_script = """import { ref, computed, watch, nextTick } from 'vue'
import Globe from 'globe.gl'"""

content = content.replace("import { ref, computed } from 'vue'", import_script)

# 2. Add visual fragmentation to runSimulation
fragmentation_logic = """
      // [FRAGMENTATION ANALYSIS]
      const maxG = maxHeatFluxLimit.value === 1e6 ? 12 : (maxHeatFluxLimit.value === 3e6 ? 22 : 45); // Set threshold based on material
      let fragmented = false;
      const fragMasses = [...res.data.mass]; 
      
      for(let i=0; i<fragMasses.length; i++) {
         if(!fragmented && res.data.g_force[i] > maxG) {
             fragmented = true;
         }
         if(fragmented) {
             fragMasses[i] = fragMasses[i] * 0.15 + (Math.random() * 2); // Split into chunks, only largest chunk mass remains tracked on main chart
         }
      }
      res.data.mass = fragMasses;

      fullResults.value = res.data;
"""

content = content.replace("fullResults.value = res.data", fragmentation_logic)

# 3. Add Globe HTML
globe_html = """
          <div class="kpi-card globe-card" style="grid-column: span 2; min-height: 350px; position: relative;">
            <div class="kpi-title">3D Trajectory & Coriolis Map</div>
            <div id="globeViz" style="width: 100%; height: 280px; margin-top: 10px; border-radius: 8px; overflow: hidden; background: #000;"></div>
          </div>
"""

content = content.replace('<div class="kpi-card" :class="{\'danger-bg\': isStructuralFailure}">', globe_html + '\n          <div class="kpi-card" :class="{\'danger-bg\': isStructuralFailure}">')

# 4. Add Globe Logic
globe_logic = """
const globeEl = ref(null)
let myGlobe = null

watch(fullResults, async (newData) => {
    if(!newData) return;
    await nextTick();
    const globeContainer = document.getElementById('globeViz');
    if(!globeContainer) return;
    
    if(!myGlobe) {
        myGlobe = Globe()(globeContainer)
            .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
            .backgroundColor('rgba(0,0,0,0)');
    }
    
    const N = newData.latitude.length;
    const pathData = [];
    const stepGlobe = Math.max(1, Math.floor(N / 200));
    for(let i=0; i<N; i+=stepGlobe) {
       pathData.push({
          lat: newData.latitude[i],
          lng: newData.longitude[i],
          alt: Math.max(0, newData.altitude[i] / 6371000)
       });
    }
    pathData.push({
          lat: newData.latitude[N-1],
          lng: newData.longitude[N-1],
          alt: Math.max(0, newData.altitude[N-1] / 6371000)
    });

    myGlobe.pathsData([{ coords: pathData }])
      .pathPointLat(d => d.lat)
      .pathPointLng(d => d.lng)
      .pathPointAlt(d => d.alt)
      .pathColor(() => '#ef4444')
      .pathStroke(2)
      .pathTransitionDuration(0);
      
    myGlobe.pointOfView({ lat: newData.latitude[N-1], lng: newData.longitude[N-1], altitude: 1.5 }, 2000);
})
"""

content = content.replace("const runSimulation = async () => {", globe_logic + "\nconst runSimulation = async () => {")

with open('src/App.vue', 'w') as f:
    f.write(content)
