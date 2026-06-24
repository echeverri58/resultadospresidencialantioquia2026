import sys
import re

with open('index.js', 'r', encoding='utf-8') as f:
    js = f.read()

# We want to replace the style: function (feature) { ... } for communesLayer and barriosLayer
# Let's find the exact indices and just replace them manually based on the exact string that is currently there.
# Since the broken code is literally in both places, let's just use string replace for the broken code snippet!

broken_code = """                if (growthWinner) {
                    color = getCandidateColor(growthWinner);
                    let totalCrecimiento = cAbe + cCep;
                    if (totalCrecimiento > 0) {
                        let candCrecimiento = growthWinner === 'ABELARDO DE LA ESPRIELLA' ? cAbe : cCep;
                        let pct = (candCrecimiento / totalCrecimiento) * 100;
                        opacity = 0.3 + ((Math.min(Math.max(pct, 50), 100) - 50) / 50) * 0.6;
                    } else {
                        opacity = 0.3;
                    }
                }} else {
                        opacity = 0.5;
                    }
                }
            } else {"""

fixed_code = """                if (growthWinner) {
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
            } else {"""

if broken_code in js:
    js = js.replace(broken_code, fixed_code)
    with open('index.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Fixed broken code.")
else:
    print("Broken code snippet not found exactly. Needs regex.")

    # Let's write a regex that matches from "style: function (feature)" to "return {"
    pattern = r'style: function \(feature\) \{[\s\S]*?return \{'
    
    fixed_style = """style: function (feature) {
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

            return {"""
    
    js = re.sub(pattern, fixed_style, js)
    with open('index.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Fixed using regex.")
