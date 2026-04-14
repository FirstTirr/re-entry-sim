import re

with open('/home/tirr/project/re-entry/frontend/src/App.vue', 'r') as f:
    text = f.read()

# Fix the unbalanced brace and syntax of Globe().pathsData
text = re.sub(
r"""    } else {
        if \(globeContainer\.clientWidth\) {
             myGlobe.width\(globeContainer\.clientWidth\);
        }
    }
    }
    
    const N = newData\.latitude\.length;""",
r"""    } else {
        if (globeContainer.clientWidth) {
             myGlobe.width(globeContainer.clientWidth);
        }
    }
    
    const N = newData.latitude.length;""", text)

with open('/home/tirr/project/re-entry/frontend/src/App.vue', 'w') as f:
    f.write(text)

print("Applied fix")
