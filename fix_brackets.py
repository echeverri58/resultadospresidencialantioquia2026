import sys

with open('index.js', 'r', encoding='utf-8') as f:
    js = f.read()

start = js.find('style: function (feature) {')
end = js.find('onEachFeature: function (feature, layer) {', start)

if start == -1 or end == -1:
    print('Not found')
    sys.exit(1)

new_style = """style: function (feature) {
            let color = defaultColor;
            let opacity = 0.2;

            if (currentTab === 'growth') {
                let cAbe = feature.properties.crecimiento_abelardo || 0;
                let cCep = feature.properties.crecimiento_cepeda || 0;

                let growthWinner = null;
                if (cAbe > cCep && cAbe > 0) growthWinner = 'ABELARDO DE LA ESPRIELLA';
                else if (cCep > cAbe && cCep > 0) growthWinner = 'ALEXANDER CEPEDA';

                if (growthWinner) {
                    color = getCandidateColor(growthWinner);
                    let totalCrecimiento = cAbe + cCep;
                    if (totalCrecimiento > 0) {
                        let candCrecimiento = growthWinner === 'ABELARDO DE LA ESPRIELLA' ? cAbe : cCep;
                        let pct = (candCrecimiento / totalCrecimiento) * 100;
                        opacity = 0.3 + ((Math.min(Math.max(pct, 50), 100) - 50) / 50) * 0.6;
                    } else {
                        opacity = 0.3;
                    }
                } else {
                    opacity = 0.5;
                }
            } else {
                const winner = feature.properties.winner;
                if (winner && winner !== 'Sin Datos' && feature.properties.results && feature.properties.results.length > 0) {
                    color = getCandidateColor(winner);
                    const pct = feature.properties.results[0].pct;
                    opacity = 0.3 + ((Math.min(Math.max(pct, 30), 80) - 30) / 50) * 0.6;
                }
            }

            return {
                fillColor: color,
                weight: 1.5,
                opacity: 0.5,
                color: '#cbd5e1', // border for light theme
                fillOpacity: opacity
            };
        },
        """

js_new = js[:start] + new_style + js[end:]

with open('index.js', 'w', encoding='utf-8') as f:
    f.write(js_new)

print('Success')
