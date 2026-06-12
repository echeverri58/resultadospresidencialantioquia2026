import re

with open('index.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update switchTab
switch_tab_orig = """function switchTab(tab) {
    currentTab = tab;
    
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`content-${tab}`).classList.add('active');
    
    postsLayer.clearLayers();
    
    if (communesLayer) map.removeLayer(communesLayer);
    if (barriosLayer) map.removeLayer(barriosLayer);
    
    document.getElementById('map-legend').style.display = 'block';

    if (tab === 'communes') {
        if (communesLayer) {
            communesLayer.addTo(map);
        }
        map.setView([6.25, -75.56], 12);
        renderMedellinGeneralResults();
    } else if (tab === 'barrios') {
        if (barriosLayer) {
            barriosLayer.addTo(map);
        }
        renderPostMarkers('MEDELLIN'); // Show markers to explain gaps
        map.setView([6.25, -75.56], 12);
        renderMedellinGeneralResults();
    } else {
        document.getElementById('map-legend').style.display = 'none';
        resetSelectors();
    }
}"""

switch_tab_new = """function switchTab(tab) {
    currentTab = tab;
    
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`tab-${tab}`).classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`content-${tab}`).classList.add('active');
    
    postsLayer.clearLayers();
    
    if (communesLayer) map.removeLayer(communesLayer);
    if (barriosLayer) map.removeLayer(barriosLayer);
    
    const strategyOverlay = document.getElementById('strategy-overlay-panel');
    const compCard = document.getElementById('comparative-card');
    const resultsCard = document.getElementById('results-card');
    
    if (tab === 'strategy') {
        strategyOverlay.style.display = 'flex';
        compCard.style.display = 'none';
        resultsCard.style.display = 'none';
        document.getElementById('map-legend').style.display = 'none';
        
        renderStrategyMap();
    } else {
        strategyOverlay.style.display = 'none';
        compCard.style.display = 'block';
        resultsCard.style.display = 'block';
        document.getElementById('map-legend').style.display = 'block';
        
        if (tab === 'communes') {
            if (communesLayer) {
                communesLayer.addTo(map);
            }
            map.setView([6.25, -75.56], 12);
            renderMedellinGeneralResults();
        } else if (tab === 'barrios') {
            if (barriosLayer) {
                barriosLayer.addTo(map);
            }
            renderPostMarkers('MEDELLIN'); // Show markers to explain gaps
            map.setView([6.25, -75.56], 12);
            renderMedellinGeneralResults();
        } else {
            document.getElementById('map-legend').style.display = 'none';
            resetSelectors();
        }
    }
}"""

if switch_tab_orig in content:
    content = content.replace(switch_tab_orig, switch_tab_new)
else:
    print("Could not find switchTab to replace.")

# 2. Add renderStrategyMap and downloadStrategy
strategy_logic = """
// Render Strategy Map (Heatmap of Oportunidad)
function renderStrategyMap() {
    if (barriosLayer) {
        barriosLayer.addTo(map);
    }
    map.setView([6.25, -75.56], 12);
    
    let tops = [];
    let candIdxEspriella = electoralData.candidates.indexOf("ABELARDO DE LA ESPRIELLA");
    let candIdxPaloma = electoralData.candidates.indexOf("PALOMA VALENCIA LASERNA");
    let candIdxCepeda = electoralData.candidates.indexOf("IVÁN CEPEDA CASTRO");
    
    if (geoBarriosData) {
        // Color barrios layer dynamically
        barriosLayer.eachLayer(function(layer) {
            let props = layer.feature.properties;
            if (props.results && props.total_votes > 0) {
                let fVotes = 0, pVotes = 0;
                props.results.forEach(r => {
                    if (r.candidate === "ABELARDO DE LA ESPRIELLA" || r.candidate === "PALOMA VALENCIA LASERNA") fVotes += r.votes;
                    if (r.candidate === "IVÁN CEPEDA CASTRO") pVotes += r.votes;
                });
                
                let otros = props.total_votes - fVotes - pVotes;
                tops.push({ name: props.nombre, otros: otros });
                
                // Color ramp for "otros" (Green scale)
                // Assuming max otros in a barrio is around 3000
                let intensity = Math.min(otros / 3000, 1.0);
                
                // From light green to dark green
                // Light: #dcfce7 (220, 252, 231)
                // Dark: #166534 (22, 101, 52)
                let r = Math.round(220 - intensity * (220 - 22));
                let g = Math.round(252 - intensity * (252 - 101));
                let b = Math.round(231 - intensity * (231 - 52));
                let fillColor = `rgb(${r}, ${g}, ${b})`;
                
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

content = content + '\n' + strategy_logic

with open('index.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('index.js updated.')
