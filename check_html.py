import re
with open('index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f):
        if 'map-wrapper' in line or 'strategy-overlay-panel' in line or 'id="map"' in line:
            print(f'{i+1}: {line.strip()}')
