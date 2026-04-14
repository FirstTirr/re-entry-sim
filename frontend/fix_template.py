import re
with open('src/App.vue', 'r') as f:
    text = f.read()

# Replace the entire <template> block to ensure it's perfectly balanced
match = re.search(r'<template>.*?</template>', text, re.DOTALL)
if match:
    old_tmpl = match.group(0)
else:
    print("No template found!")
    exit(1)

