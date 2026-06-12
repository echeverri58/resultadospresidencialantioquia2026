import re

with open('index.js', 'r', encoding='utf-8') as f:
    content = f.read()

# We will replace everything from 'function renderStrategyMap() {' to the end of the file.
match = re.search(r'// Render Strategy Map \(Heatmap of Oportunidad\).*', content, re.DOTALL)

new_strategy_logic = """// Render Strategy Map (Heatmap of Oportunidad)
function renderStrategyMap() {
    if (barriosLayer) {
        barriosLayer.addTo(map);
    }
    map.setView([6.25, -75.56], 12);
    
    let tops = [];
    
    if (geoBarriosData) {
        // Color barrios layer dynamically
        barriosLayer.eachLayer(function(layer) {
            let props = layer.feature.properties;
            if (props.results && props.total_votes > 0) {
                let fVotes = 0, pVotes = 0;
                props.results.forEach(r => {
                    let candName = r.candidate.toUpperCase();
                    if (candName.includes("ESPRIELLA") || candName.includes("PALOMA")) {
                        fVotes += r.votes;
                    }
                    if (candName.includes("CEPEDA")) {
                        pVotes += r.votes;
                    }
                });
                
                let otros = props.total_votes - fVotes - pVotes;
                tops.push({ name: props.nombre, otros: otros });
                
                // Color ramp for "otros" (Green scale)
                // Assuming max otros in a barrio is around 3000
                let intensity = Math.min(otros / 3000, 1.0);
                
                // From light green to dark green
                // Light: #dcfce7 (220, 252, 231)
                // Dark: #166534 (22, 101, 52)
                let r_val = Math.round(220 - intensity * (220 - 22));
                let g_val = Math.round(252 - intensity * (252 - 101));
                let b_val = Math.round(231 - intensity * (231 - 52));
                let fillColor = `rgb(${r_val}, ${g_val}, ${b_val})`;
                
                layer.setStyle({
                    fillColor: fillColor,
                    fillOpacity: 0.8,
                    weight: 1,
                    color: '#166534'
                });
                
                // Bind tooltip
                layer.bindTooltip(`<strong>${props.nombre}</strong><br>Votos oportunidad: ${formatNumber(otros)}`, {sticky: true});
            } else {
                layer.setStyle({
                    fillColor: '#f1f5f9',
                    fillOpacity: 0.4,
                    weight: 1,
                    color: '#cbd5e1'
                });
            }
        });
    }
    
    // Populate Top 50
    if (tops.length > 0) {
        tops.sort((a, b) => b.otros - a.otros);
        let top50 = tops.slice(0, 50);
        let sumTop50 = top50.reduce((acc, curr) => acc + curr.otros, 0);
        
        const totalEl = document.getElementById('strat-top-list-total');
        if (totalEl) {
            totalEl.innerHTML = `Potencial en el Top 50: <span style="color: #166534; font-size: 16px;">${formatNumber(sumTop50)} votos</span>`;
        }

        const listEl = document.getElementById('strat-top-list');
        if (listEl) {
            let topHtml = '';
            top50.forEach((t, i) => {
                topHtml += `<div style="padding: 10px 16px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 13px; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 8px; width: 75%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                        <span style="background: #e2e8f0; color: #64748b; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0;">${i+1}</span>
                        ${t.name}
                    </span>
                    <span style="font-size: 14px; font-weight: 800; color: #166534;">${formatNumber(t.otros)}</span>
                </div>`;
            });
            listEl.innerHTML = topHtml;
        }
    }
}

// Download Strategy Map
window.downloadStrategy = function() {
    const mapContainer = document.querySelector('.map-wrapper');
    const btn = document.getElementById('btn-download-strategy');
    
    // Hide button during capture
    if (btn) btn.style.display = 'none';
    
    setTimeout(() => {
        html2canvas(mapContainer, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            backgroundColor: null
        }).then(canvas => {
            if (btn) btn.style.display = 'flex';
            const link = document.createElement('a');
            link.download = 'estrategia_captacion_john_charcos.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }).catch(err => {
            console.error("Error generating image:", err);
            if (btn) btn.style.display = 'flex';
            alert("Hubo un error al capturar el mapa.");
        });
    }, 500); // 500ms delay to ensure map tiles are rendered
};
"""

if match:
    content = content.replace(match.group(0), new_strategy_logic)
else:
    content += '\n' + new_strategy_logic

with open('index.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Strategy logic replaced successfully.")
