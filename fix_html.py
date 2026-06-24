with open('index.html', 'r', encoding='latin-1', errors='ignore') as f:
    html = f.read()

html = html.replace('id="tab-crecimiento" onclick="switchTab(\'crecimiento\')"', 'id="tab-growth" onclick="switchTab(\'growth\')"')
html = html.replace('id="content-crecimiento"', 'id="content-growth"')

with open('index.html', 'w', encoding='latin-1') as f:
    f.write(html)
