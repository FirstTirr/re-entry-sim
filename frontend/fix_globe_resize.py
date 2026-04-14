import re

with open('/home/tirr/project/re-entry/frontend/src/App.vue', 'r') as f:
    text = f.read()

# Replace hardcoded heights
text = re.sub(
r"""        if\(!myGlobe\) {
        myGlobe = Globe\(\)\(globeContainer\)
            \.width\(globeContainer\.clientWidth \|\| 400\)
            \.height\(280\)""",
r"""        if(!myGlobe) {
        myGlobe = Globe()(globeContainer)
            .width(globeContainer.clientWidth || 800)
            .height(globeContainer.clientHeight || 600)""", text)

text = re.sub(
r"""    \} else \{
        if \(globeContainer\.clientWidth\) \{
             myGlobe\.width\(globeContainer\.clientWidth\);
        \}
    \}""",
r"""    } else {
        if (globeContainer.clientWidth) {
             myGlobe.width(globeContainer.clientWidth);
             myGlobe.height(globeContainer.clientHeight);
        }
    }""", text)

# Add watch(activeView) to resize the globe when it's opened.
resize_watcher = """watch(activeView, async (newView) => {
  if (newView === 'globe' && myGlobe && results.value) {
     await nextTick();
     const container = document.getElementById('globeViz');
     if (container) {
         myGlobe.width(container.clientWidth);
         myGlobe.height(container.clientHeight);
     }
  }
})"""

text = text.replace("const globeEl = ref(null)", resize_watcher + "\n\nconst globeEl = ref(null)")


with open('/home/tirr/project/re-entry/frontend/src/App.vue', 'w') as f:
    f.write(text)

