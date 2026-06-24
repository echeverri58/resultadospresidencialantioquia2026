with open('index.html', 'r', encoding='latin-1') as f:
    html = f.read()

html = html.replace('index.js?v=23', 'index.js?v=24')
html = html.replace('onclick="downloadGrowthAnalysis()"', 'onclick="downloadGrowthAnalysis(event)"')

with open('index.html', 'w', encoding='latin-1') as f:
    f.write(html)
