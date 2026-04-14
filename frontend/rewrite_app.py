import re

with open('/home/tirr/project/re-entry/frontend/src/App.vue', 'r') as f:
    text = f.read()

# 1. Add activeView ref
text = re.sub(r'const activeTab = ref\(.*?penjelasan.*?\)', r"const activeTab = ref('simulator')\nconst activeView = ref('grafik')", text)

# 2. Modify Template
template_old = r"""
          <div class="kpi-card globe-card" style="grid-column: span 2; min-height: 350px; position: relative;">
            <div class="kpi-title">3D Trajectory & Coriolis Map</div>
            <div id="globeViz" style="width: 100%; height: 280px; margin-top: 10px; border-radius: 8px; overflow: hidden; background: #000;"></div>
          </div>
"""
text = text.replace(template_old, "")

template_charts_old = r"""<div class="charts-board" v-if="results">"""

template_charts_new = r"""<div class="view-toggles" v-if="results" style="display: flex; gap: 10px; margin-bottom: 20px; justify-content: center;">
          <button class="nav-btn" :class="{active: activeView === 'grafik'}" @click="activeView = 'grafik'">📊 Grafik 2D</button>
          <button class="nav-btn" :class="{active: activeView === 'globe'}" @click="activeView = 'globe'">🌍 Globe 3D</button>
        </div>

        <div class="globe-wrap" v-show="activeView === 'globe'" style="width: 100%; height: 600px; border-radius: 12px; overflow: hidden; background: #000; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);">
          <div id="globeViz" style="width: 100%; height: 100%;"></div>
        </div>

        <div class="charts-board" v-show="activeView === 'grafik' && results">"""

text = text.replace(template_charts_old, template_charts_new)

with open('/home/tirr/project/re-entry/frontend/src/App.vue', 'w') as f:
    f.write(text)

