import re

with open('/home/tirr/project/re-entry/frontend/src/App.vue', 'r') as f:
    text = f.read()

# 1. Provide width and height to Globe
new_init = """    if(!myGlobe) {
        myGlobe = Globe()(globeContainer)
            .width(globeContainer.clientWidth || 400)
            .height(280)
            .globeImageUrl('https://unpkg.com/three-globe/example/img/earth-blue-marble.jpg')
            .backgroundColor('rgba(0,0,0,0)');
    } else {
        if (globeContainer.clientWidth) {
             myGlobe.width(globeContainer.clientWidth);
        }
    }"""
text = re.sub(r'if\(!myGlobe\) \{\s*myGlobe = Globe\(\)\(globeContainer\)[^;]*;', new_init, text, flags=re.MULTILINE)

# 2. Fix the pathData reference
text = text.replace("myGlobe.pathsData([{ coords: pathData }])", "myGlobe.pathsData([{ pnts: pathData }])")

with open('/home/tirr/project/re-entry/frontend/src/App.vue', 'w') as f:
    f.write(text)

