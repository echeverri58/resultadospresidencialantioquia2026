import sys
import re

with open('index.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update setMode
set_mode_replacement = """window.setMode = function(mode) {
    currentMode = mode;
    
    const resultsCard = document.getElementById('results-card');
    const compCard = document.getElementById('comparative-card');
    const rightPanel = document.getElementById('right-panel');
    
    // Update button states
    const resultsModeBtn = document.getElementById('btn-results-mode');
    const stratModeBtn = document.getElementById('btn-strategy-mode');
    
    if (mode === 'results') {
        if (resultsModeBtn) resultsModeBtn.classList.add('active');
        if (stratModeBtn) stratModeBtn.classList.remove('active');
        if (rightPanel) rightPanel.style.display = 'none';
        // Wait, the comparative card handles both modes now.
        // It updates its content based on currentMode.
    } else {
        if (resultsModeBtn) resultsModeBtn.classList.remove('active');
        if (stratModeBtn) stratModeBtn.classList.add('active');
        if (rightPanel) rightPanel.style.display = 'flex';
    }
    
    // Refresh layers if they exist
    if (currentTab === 'communes' && communesLayer) {
        renderCommunes();
    } else if (currentTab === 'barrios' && barriosLayer) {
        renderBarrios();
    }
    
    // Refresh Comparative/Strategy UI
    if (currentTab === 'communes' || currentTab === 'barrios') {
        renderComparativeCard();
    } else {
        const muniSelect = document.getElementById('select-muni');
        if (muniSelect && muniSelect.value) {
            const zoneSelect = document.getElementById('select-zone');
            const postSelect = document.getElementById('select-post');
            if (postSelect && postSelect.value) {
                renderComparativeCard(muniSelect.value, zoneSelect.value, postSelect.value);
            } else if (zoneSelect && zoneSelect.value) {
                renderComparativeCard(muniSelect.value, zoneSelect.value);
            } else {
                renderComparativeCard(muniSelect.value);
            }
        }
    }
};"""

content = re.sub(r'window\.setMode = function\(mode\) \{.*?^\};', set_mode_replacement, content, flags=re.MULTILINE|re.DOTALL)

# 2. Add Top 50 logic to renderComparativeCard
search_str = """    let explanation = `Esto se debe a un doble efecto: la derecha <strong>${derAction} ${Math.abs(diffDer).toFixed(1)} puntos</strong> (${derVotosText}), mientras que la izquierda <strong>${izqAction} ${Math.abs(diffIzq).toFixed(1)} puntos</strong> (${izqVotosText}).`;
    
    document.getElementById('comp-shift-explanation').innerHTML = explanation;
}"""

replace_str = """    let explanation = `Esto se debe a un doble efecto: la derecha <strong>${derAction} ${Math.abs(diffDer).toFixed(1)} puntos</strong> (${derVotosText}), mientras que la izquierda <strong>${izqAction} ${Math.abs(diffIzq).toFixed(1)} puntos</strong> (${izqVotosText}).`;
    
    document.getElementById('comp-shift-explanation').innerHTML = explanation;
    
    // Top 50 Strategy Logic
    if (currentMode === 'strategy') {
        const listContainer = document.getElementById('strat-top-list-container');
        const listEl = document.getElementById('strat-top-list');
        
        if (listContainer && listEl) {
            let tops = [];
            let candIdxEspriella = electoralData.candidates.indexOf("ABELARDO DE LA ESPRIELLA");
            let candIdxPaloma = electoralData.candidates.indexOf("PALOMA VALENCIA LASERNA");
            let candIdxCepeda = electoralData.candidates.indexOf("IVÁN CEPEDA CASTRO");
            
            if (muniName && muniName !== "MEDELLIN") {
                // Show top posts in the municipality
                let muniData = electoralData.hierarchy[muniName];
                Object.values(muniData).forEach(zonePosts => {
                    Object.values(zonePosts).forEach(postInfo => {
                        let fVotes = 0, pVotes = 0, tVotes = 0;
                        Object.values(postInfo.tables).forEach(t => {
                            fVotes += (t[candIdxEspriella] || 0) + (t[candIdxPaloma] || 0);
                            pVotes += t[candIdxCepeda] || 0;
                            tVotes += t.reduce((a, b) => a + b, 0);
                        });
                        tops.push({ name: postInfo.name, otros: tVotes - fVotes - pVotes });
                    });
                });
            } else {
                // Medellin
                if (currentTab === 'communes') {
                    Object.entries(electoralData.communes).forEach(([cod, commData]) => {
                        let fVotes = 0, pVotes = 0;
                        commData.results.forEach(r => {
                            if (r.candidate === "ABELARDO DE LA ESPRIELLA" || r.candidate === "PALOMA VALENCIA LASERNA") fVotes += r.votes;
                            if (r.candidate === "IVÁN CEPEDA CASTRO") pVotes += r.votes;
                        });
                        tops.push({ name: "Comuna " + cod, otros: commData.total_votes - fVotes - pVotes });
                    });
                } else if (currentTab === 'barrios' && geoBarriosData) {
                    geoBarriosData.features.forEach(f => {
                        if (f.properties.winner && f.properties.winner !== 'Sin Datos' && f.properties.results) {
                            let fVotes = 0, pVotes = 0;
                            f.properties.results.forEach(r => {
                                if (r.candidate === "ABELARDO DE LA ESPRIELLA" || r.candidate === "PALOMA VALENCIA LASERNA") fVotes += r.votes;
                                if (r.candidate === "IVÁN CEPEDA CASTRO") pVotes += r.votes;
                            });
                            tops.push({ name: f.properties.nombre, otros: f.properties.total_votes - fVotes - pVotes });
                        }
                    });
                }
            }
            
            if (tops.length > 0) {
                tops.sort((a, b) => b.otros - a.otros);
                
                // Get top 50
                let top50 = tops.slice(0, 50);
                
                // Calculate total potential in the top 50
                let sumTop50 = top50.reduce((acc, curr) => acc + curr.otros, 0);
                
                // Update total element
                const totalEl = document.getElementById('strat-top-list-total');
                if (totalEl) {
                    totalEl.innerHTML = `Potencial en el Top 50: <span style="color: #166534; font-size: 16px;">${formatNumber(sumTop50)} votos</span>`;
                }

                let topHtml = '';
                top50.forEach((t, i) => {
                    topHtml += `<div style="padding: 10px 16px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; transition: background 0.2s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
                        <span style="font-size: 13px; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 8px; width: 75%; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                            <span style="background: #e2e8f0; color: #64748b; width: 24px; height: 24px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; flex-shrink: 0;">${i+1}</span>
                            ${t.name}
                        </span>
                        <span style="font-size: 14px; font-weight: 800; color: #166534;">${formatNumber(t.otros)}</span>
                    </div>`;
                });
                listEl.innerHTML = topHtml;
            } else {
                listEl.innerHTML = '<div style="padding: 16px; text-align: center; color: #64748b; font-size: 13px;">No hay datos suficientes para mostrar el top 50 en esta vista.</div>';
            }
        }
    }
}"""

if search_str in content:
    content = content.replace(search_str, replace_str)
else:
    print('WARNING: Could not inject top 50 logic!')

with open('index.js', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
