import re
with open('index.js', 'r', encoding='utf-8') as f:
    js = f.read()

start = js.find('function switchTab(tab) {')
end = start + 2000
print(js[start:end])
