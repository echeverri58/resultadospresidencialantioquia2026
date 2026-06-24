import sys

with open('index.js', 'r', encoding='utf-8') as f:
    js = f.read()

start = js.find('communesLayer = L.geoJSON(geojsonData, {')
end = js.find('onEachFeature: function (feature, layer) {', start)

if start == -1 or end == -1:
    print('Not found')
    sys.exit(1)

new_style = """communesLayer = L.geoJSON(geojsonData, {
        style: function (feature) {
            let color = defaultColor;
            let opacity = 0.2;

            const winner = feature.properties.winner;
            if (winner && winner !== 'Sin Datos' && feature.properties.results && feature.properties.results.length > 0) {
                color = getCandidateColor(winner);
                const pct = feature.properties.results[0].pct;
                opacity = 0.3 + ((Math.min(Math.max(pct, 30), 80) - 30) / 50) * 0.6;
            }

            return {
                fillColor: color,
                weight: 2,
                opacity: 0.8,
                color: '#475569', // Stronger border for communes so they are visible under barrios
                fillOpacity: opacity
            };
        },
        """

js_new = js[:start] + new_style + js[end:]

with open('index.js', 'w', encoding='utf-8') as f:
    f.write(js_new)

print('Success')
