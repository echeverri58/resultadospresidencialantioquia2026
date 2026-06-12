import re

with open('index.js', 'r', encoding='utf-8') as f:
    content = f.read()

switch_tab_orig = """function switchTab(tab) {
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

switch_tab_new = """function switchTab(tab) {
    currentTab = tab;
    
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    let activeTabBtn = document.getElementById(`tab-${tab}`);
    if (activeTabBtn) activeTabBtn.classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    let activeContent = document.getElementById(`content-${tab}`);
    if (activeContent) activeContent.classList.add('active');
    
    if (postsLayer) postsLayer.clearLayers();
    
    if (communesLayer) map.removeLayer(communesLayer);
    if (barriosLayer) map.removeLayer(barriosLayer);
    
    const strategyOverlay = document.getElementById('strategy-overlay-panel');
    const compCard = document.getElementById('comparative-card');
    const resultsContainer = document.querySelector('.results-container');
    const mapLegend = document.getElementById('map-legend');
    
    if (tab === 'strategy') {
        if (strategyOverlay) strategyOverlay.style.display = 'flex';
        if (compCard) compCard.style.display = 'none';
        if (resultsContainer) resultsContainer.style.display = 'none';
        if (mapLegend) mapLegend.style.display = 'none';
        
        if (typeof renderStrategyMap === 'function') renderStrategyMap();
    } else {
        if (strategyOverlay) strategyOverlay.style.display = 'none';
        if (compCard) compCard.style.display = 'block';
        if (resultsContainer) resultsContainer.style.display = 'block';
        if (mapLegend) mapLegend.style.display = 'block';
        
        if (tab === 'communes') {
            if (communesLayer) {
                communesLayer.addTo(map);
            }
            map.setView([6.25, -75.56], 12);
            if (typeof renderMedellinGeneralResults === 'function') renderMedellinGeneralResults();
        } else if (tab === 'barrios') {
            if (barriosLayer) {
                barriosLayer.addTo(map);
            }
            if (typeof renderPostMarkers === 'function') renderPostMarkers('MEDELLIN'); // Show markers to explain gaps
            map.setView([6.25, -75.56], 12);
            if (typeof renderMedellinGeneralResults === 'function') renderMedellinGeneralResults();
        } else {
            if (mapLegend) mapLegend.style.display = 'none';
            if (typeof resetSelectors === 'function') resetSelectors();
        }
    }
}"""

content = content.replace(switch_tab_orig, switch_tab_new)

with open('index.js', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated switchTab correctly.")
