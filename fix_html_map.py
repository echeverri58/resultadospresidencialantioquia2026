import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# The first map div is inside map-wrapper right before the strategy-overlay-panel
bad_map = """        <main class="map-wrapper" style="position: relative;">
            <div id="map"></div>"""
            
good_map = """        <main class="map-wrapper" style="position: relative;">"""

content = content.replace(bad_map, good_map)

# Also update v=10 to v=11
content = content.replace('index.js?v=10', 'index.js?v=11')
content = content.replace('index.css?v=10', 'index.css?v=11')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Removed double map div and updated cache buster to 11")
