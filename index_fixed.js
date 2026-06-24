let map;
let communesLayer = null;
let barriosLayer = null;
let postsLayer = null; // Layer group to hold post circle markers
let resultsChart = null; // Chart.js instance

// Global Data variables
let electoralData = null;
let geojsonData = null;
let geoBarriosData = null;

// Active state
let currentTab = 'communes'; // 'communes', 'barrios', or 'hierarchy'
let selectedCommuneCode = null;

// Candidate colors mapping - standard theme
const candidateColors = {
    "ABELARDO DE LA ESPRIELLA": "#9333ea", // Purple
    "IVÁN CEPEDA CASTRO": "#ea580c",    // Orange
    "SERGIO FAJARDO VALDERRAMA": "#059669",   // Emerald
    "PALOMA VALENCIA LASERNA": "#0284c7",  // Cyan
    "VOTOS EN BLANCO": "#94a3b8",     // Slate 400
    "VOTOS NULOS": "#64748b",
    "VOTOS NO MARCADOS": "#475569"
};

// Default fallback color
const defaultColor = "#94a3b8";

function getCandidateColor(name) {
    return candidateColors[name] || defaultColor;
}

// Format numbers as 1.234.567
function formatNumber(num) {
    return num.toLocaleString('es-CO');
}

// Initialize Leaflet Map (Using Clean Light Voyager tiles)
function initMap() {
    map = L.map('map', {
        zoomControl: true,
        attributionControl: false
    }).setView([6.25, -75.56], 12);

    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
        crossOrigin: true
    }).addTo(map);

    postsLayer = L.layerGroup().addTo(map);
}

// Load App Data
async function loadData() {
    try {
        const [electoralRes, geojsonRes, barriosRes] = await Promise.all([
            fetch('electoral_data.json?v=' + Date.now()),
            fetch('medellin.geojson?v=' + Date.now()),
            fetch('barrios_resultados.geojson?v=' + Date.now())
        ]);
        
        electoralData = await electoralRes.json();
        geojsonData = await geojsonRes.json();
        geoBarriosData = await barriosRes.json();
        
        // Render general results
        renderMedellinGeneralResults();
        renderComparativeCard();
        renderComparativeCard2v();
        renderLegend();
        renderCommunes();
        renderBarrios();
        populateMunicipalities();
        
        if (currentTab === 'hierarchy') {
            resetSelectors();
        } else if (currentTab === 'barrios') {
            switchTab('barrios');
        } else {
            switchTab('communes');
        }
        
    } catch (error) {
        console.error("Error loading application data:", error);
    }
}

// Render Legend dynamically
function renderLegend() {
    const container = document.getElementById('legend-items');
    container.innerHTML = '';
    
    const topCandidates = [
        "ABELARDO DE LA ESPRIELLA",
        "IVÁN CEPEDA CASTRO",
        "SERGIO FAJARDO VALDERRAMA",
        "PALOMA VALENCIA LASERNA",
        "VOTOS EN BLANCO"
    ];
    
    topCandidates.forEach(cand => {
        const item = document.createElement('div');
        item.className = 'legend-item';
        
        const colorBox = document.createElement('span');
        colorBox.className = 'legend-color';
        colorBox.style.backgroundColor = getCandidateColor(cand);
        
        const label = document.createElement('span');
        label.innerText = cand.split(' ')[0] + ' ' + (cand.split(' ')[1] || '');
        
        item.appendChild(colorBox);
        item.appendChild(label);
        container.appendChild(item);
    });
}

// Render general Medellín results
function renderMedellinGeneralResults() {
    document.getElementById('results-title').innerText = "Resultados Generales (Medellín)";
    document.getElementById('results-subtitle').innerText = "Acumulado de todas las comunas y corregimientos";
    selectedCommuneCode = null;
    
    let totals = {};
    let totalVotes = 0;
    
    Object.values(electoralData.communes).forEach(commData => {
        commData.results.forEach(res => {
            totals[res.candidate] = (totals[res.candidate] || 0) + res.votes;
            totalVotes += res.votes;
        });
    });
    
    const sorted = Object.entries(totals)
        .map(([candidate, votes]) => ({
            candidate,
            votes,
            pct: totalVotes > 0 ? (votes / totalVotes * 100) : 0
        }))
        .sort((a, b) => b.votes - a.votes);
        
    renderResultsList(sorted, totalVotes);
    renderComparativeCard();
        renderComparativeCard2v();
}

// Helper to truncate candidate names for chart labels
function getShortCandidateName(name) {
    if (name === "VOTOS EN BLANCO") return "Blanco";
    if (name === "VOTOS NULOS") return "Nulo";
    if (name === "VOTOS NO MARCADOS") return "No Marcado";
    const parts = name.split(' ');
    if (parts.length > 2) {
        return parts[0] + ' ' + parts[1][0] + '.';
    }
    return name;
}

// Create or Update Chart.js horizontal bar chart or line chart (Light Mode styled)
function updateChart(results, titleText, subtitleText, type = 'bar', postInfo = null) {
    const canvas = document.getElementById('results-chart');
    if (!canvas) return;
    
    if (resultsChart) {
        resultsChart.destroy();
        resultsChart = null;
    }
    
    // Custom plugin to draw solid LIGHT background for image export
    const backgroundPlugin = {
        id: 'customCanvasBackgroundColor',
        beforeDraw: (chart) => {
            const {ctx} = chart;
            ctx.save();
            ctx.globalCompositeOperation = 'destination-over';
            ctx.fillStyle = '#ffffff'; // Light Mode solid background
            ctx.fillRect(0, 0, chart.width, chart.height);
            ctx.restore();
        }
    };
    
    const attributionText = "Creada por John Charcos";
    
    if (type === 'line' && postInfo) {
        // Line chart comparing all tables of the post
        const tables = Object.keys(postInfo.tables).sort((a, b) => parseInt(a) - parseInt(b));
        const labels = tables.map(t => `Mesa ${t}`);
        
        const candidatesWithVotes = [];
        electoralData.candidates.forEach((cand, candIdx) => {
            let total = 0;
            tables.forEach(tableId => {
                total += postInfo.tables[tableId][candIdx];
            });
            if (total > 0) {
                candidatesWithVotes.push({ cand, candIdx });
            }
        });
        
        const datasets = candidatesWithVotes.map(({ cand, candIdx }) => {
            const data = tables.map(tableId => postInfo.tables[tableId][candIdx]);
            return {
                label: getShortCandidateName(cand),
                data: data,
                borderColor: getCandidateColor(cand),
                backgroundColor: getCandidateColor(cand),
                tension: 0.15,
                fill: false,
                borderWidth: 2,
                pointRadius: tables.length > 15 ? 1 : 2.5,
                pointHoverRadius: 5
            };
        });
        
        resultsChart = new Chart(canvas, {
            type: 'line',
            plugins: [backgroundPlugin],
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: 'rgba(0, 0, 0, 0.05)' },
                        ticks: { color: '#475569', font: { size: 9 }, maxRotation: 45, minRotation: 45 }
                    },
                    y: {
                        grid: { color: 'rgba(0, 0, 0, 0.05)' },
                        ticks: { color: '#475569', font: { size: 9 } }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            color: '#475569',
                            font: { size: 8 },
                            boxWidth: 8,
                            padding: 6
                        }
                    },
                    title: {
                        display: true,
                        text: [titleText.toUpperCase(), subtitleText, attributionText],
                        color: '#0f172a',
                        font: {
                            family: 'Plus Jakarta Sans',
                            size: 11,
                            weight: 'bold'
                        },
                        padding: { bottom: 6 }
                    }
                }
            }
        });
    } else {
        // Bar chart for general results / aggregates / single table
        const topData = results.slice(0, 6);
        const labels = topData.map(item => getShortCandidateName(item.candidate));
        const dataVals = topData.map(item => item.votes);
        const barColors = topData.map(item => getCandidateColor(item.candidate));
        
        resultsChart = new Chart(canvas, {
            type: 'bar',
            plugins: [backgroundPlugin],
            data: {
                labels: labels,
                datasets: [{
                    label: 'Votos',
                    data: dataVals,
                    backgroundColor: barColors,
                    borderWidth: 0,
                    borderRadius: 4,
                    barThickness: 14
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: 'rgba(0, 0, 0, 0.05)' },
                        ticks: { color: '#475569', font: { size: 9 } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { color: '#0f172a', font: { size: 10, weight: 'bold' } }
                    }
                },
                plugins: {
                    legend: { display: false },
                    title: {
                        display: true,
                        text: [titleText.toUpperCase(), subtitleText, attributionText],
                        color: '#0f172a',
                        font: {
                            family: 'Plus Jakarta Sans',
                            size: 11,
                            weight: 'bold'
                        },
                        padding: { bottom: 10 }
                    }
                }
            }
        });
    }
}

// Download Chart as PNG
function downloadChart() {
    if (!resultsChart) return;
    resultsChart.draw();
    
    const canvas = document.getElementById('results-chart');
    const image = canvas.toDataURL('image/png');
    
    const titleText = document.getElementById('results-title').innerText || 'grafica';
    const cleanTitle = titleText.toLowerCase()
        .replace(/[^a-z0-9]/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
        
    const link = document.createElement('a');
    link.download = `grafica-elecciones-${cleanTitle}.png`;
    link.href = image;
    link.click();
}

// Render Results list inside the Sidebar
function renderResultsList(results, totalVotes, chartType = 'bar', postInfo = null) {
    document.getElementById('total-votes-count').innerText = formatNumber(totalVotes);
    
    let blankItem = results.find(r => r.candidate === "VOTOS EN BLANCO");
    if (blankItem) {
        document.getElementById('blank-votes-count').innerText = formatNumber(blankItem.votes);
        document.getElementById('blank-votes-pct').innerText = `(${blankItem.pct.toFixed(2)}%)`;
    } else {
        document.getElementById('blank-votes-count').innerText = "0";
        document.getElementById('blank-votes-pct').innerText = "(0%)";
    }

    const abstencionBadge = document.getElementById('abstencion-badge');
    if (postInfo && postInfo.potential && postInfo.potential > 0) {
        const potential = postInfo.potential;
        const abstencionPct = Math.max(0, ((potential - totalVotes) / potential) * 100);
        document.getElementById('abstencion-pct').innerText = `${abstencionPct.toFixed(2)}%`;
        abstencionBadge.style.display = 'flex';
    } else {
        abstencionBadge.style.display = 'none';
    }
    
    const container = document.getElementById('candidates-list');
    container.innerHTML = '';
    
    if (results.length === 0) {
        container.innerHTML = `<p style="color: var(--text-secondary); text-align: center; margin-top: 20px;">No hay resultados disponibles.</p>`;
        return;
    }
    
    results.forEach((item, idx) => {
        const card = document.createElement('div');
        card.className = 'candidate-card';
        
        if (idx === 0) {
            const stripe = document.createElement('div');
            stripe.className = 'winner-border';
            stripe.style.backgroundColor = getCandidateColor(item.candidate);
            card.appendChild(stripe);
        }
        
        const header = document.createElement('div');
        header.className = 'cand-header';
        
        const name = document.createElement('span');
        name.className = 'cand-name';
        name.innerText = item.candidate;
        
        const info = document.createElement('div');
        info.className = 'cand-votes-info';
        
        const pct = document.createElement('span');
        pct.className = 'cand-pct';
        pct.style.color = idx === 0 ? getCandidateColor(item.candidate) : 'inherit';
        pct.innerText = `${item.pct.toFixed(2)}%`;
        
        const votes = document.createElement('div');
        votes.className = 'cand-votes';
        votes.innerText = `${formatNumber(item.votes)} votos`;
        
        info.appendChild(pct);
        info.appendChild(votes);
        header.appendChild(name);
        header.appendChild(info);
        
        const barContainer = document.createElement('div');
        barContainer.className = 'progress-bar-container';
        
        const bar = document.createElement('div');
        bar.className = 'progress-bar';
        bar.style.backgroundColor = getCandidateColor(item.candidate);
        bar.style.width = '0%';
        barContainer.appendChild(bar);
        
        card.appendChild(header);
        card.appendChild(barContainer);
        container.appendChild(card);
        
        setTimeout(() => {
            bar.style.width = `${item.pct}%`;
        }, 50);
    });
    
    // Update chart
    const titleText = document.getElementById('results-title').innerText;
    const subtitleText = document.getElementById('results-subtitle').innerText;
    updateChart(results, titleText, subtitleText, chartType, postInfo);
}

// Render Communes GeoJSON Layer
function renderCommunes() {
    if (communesLayer) {
        map.removeLayer(communesLayer);
    }
    
    communesLayer = L.geoJSON(geojsonData, {
        style: function (feature) {
            const codigo = feature.properties.CODIGO;
            const commData = electoralData.communes[codigo];
            
            let color = defaultColor;
            let opacity = 0.2;
            
            if (commData) {
                const winner = commData.winner;
                color = getCandidateColor(winner);
                const pct = commData.winner_pct;
                opacity = 0.3 + ((Math.min(Math.max(pct, 30), 80) - 30) / 50) * 0.6;
            }
            
            return {
                fillColor: color,
                weight: 1.5,
                opacity: 0.5,
                color: '#cbd5e1', // border for light theme
                fillOpacity: opacity
            };
        },
        onEachFeature: function (feature, layer) {
            const codigo = feature.properties.CODIGO;
            const nombre = feature.properties.NOMBRE || feature.properties.IDENTIFICACION || "Comuna Sin Nombre";
            const commData = electoralData.communes[codigo];
            
            let popupContent = `<h3>${nombre}</h3>`;
            if (commData) {
                popupContent += `<p>Ganador: <strong>${commData.winner}</strong> (${commData.winner_pct.toFixed(2)}%)</p>`;
                popupContent += `<p>Votos Totales: ${formatNumber(commData.total_votes)}</p>`;
            } else {
                popupContent += `<p>Sin datos electorales</p>`;
            }
            
            layer.bindPopup(popupContent);
            
            layer.on({
                mouseover: function (e) {
                    const l = e.target;
                    l.setStyle({
                        weight: 3,
                        color: '#a855f7',
                        fillOpacity: Math.min(l.options.fillOpacity + 0.15, 0.95)
                    });
                    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                        l.bringToFront();
                    }
                },
                mouseout: function (e) {
                    communesLayer.resetStyle(e.target);
                },
                click: function (e) {
                    if (commData) {
                        selectedCommuneCode = codigo;
                        document.getElementById('results-title').innerText = nombre;
                        document.getElementById('results-subtitle').innerText = `Resultados en Comuna / Corregimiento`;
                        renderResultsList(commData.results, commData.total_votes);
                    }
                }
            });
        }
    }).addTo(map);
}

// Render Barrios GeoJSON Layer
function renderBarrios() {
    if (barriosLayer) {
        map.removeLayer(barriosLayer);
    }
    
    barriosLayer = L.geoJSON(geoBarriosData, {
        style: function (feature) {
            let color = defaultColor;
            let opacity = 0.2;
            
            if (currentTab === 'growth') {
                const growthWinner = feature.properties.winner_crecimiento;
                if (growthWinner && growthWinner !== 'Sin Datos') {
                    color = getCandidateColor(growthWinner);
                    opacity = 0.7; // higher opacity for clear visibility
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
        onEachFeature: function (feature, layer) {
            const nombre = feature.properties.nombre || "Sin Nombre";
            const winner = feature.properties.winner;
            
            let popupContent = `<h3>${nombre}</h3>`;
            
            if (currentTab === 'growth') {
                if (feature.properties.crecimiento_abelardo !== undefined && feature.properties.crecimiento_abelardo !== null) {
                    const crecAbelardo = feature.properties.crecimiento_abelardo;
                    const crecCepeda = feature.properties.crecimiento_cepeda;
                    popupContent += `<p style="margin-top: 4px; margin-bottom: 8px;"><strong>Crecimiento 1v ➔ 2v:</strong></p>`;
                    popupContent += `<p style="margin: 0;">Abelardo: <strong><span style="color: ${crecAbelardo > 0 ? '#16a34a' : '#dc2626'}">${crecAbelardo > 0 ? '+' : ''}${crecAbelardo.toFixed(1)}%</span></strong> (${formatNumber(feature.properties.votos_1v_abelardo)} ➔ ${formatNumber(feature.properties.votos_2v_abelardo)})</p>`;
                    popupContent += `<p style="margin: 0;">Cepeda: <strong><span style="color: ${crecCepeda > 0 ? '#16a34a' : '#dc2626'}">${crecCepeda > 0 ? '+' : ''}${crecCepeda.toFixed(1)}%</span></strong> (${formatNumber(feature.properties.votos_1v_cepeda)} ➔ ${formatNumber(feature.properties.votos_2v_cepeda)})</p>`;
                                if (feature.properties.posts_details && feature.properties.posts_details.length > 0) {
                        const maxPostsToShow = 10;
                        const sortedPosts = [...feature.properties.posts_details].sort((a, b) => b.a_c - a.a_c); // Sort by Abelardo growth
                        let postsHtml = '<div style="margin-top: 12px; max-height: 150px; overflow-y: auto; padding-right: 5px;">';
                        postsHtml += '<strong style="color: var(--text-secondary); font-size: 11px; text-transform: uppercase;">Detalle por Puesto:</strong>';
                        
                        sortedPosts.slice(0, maxPostsToShow).forEach(p => {
                            postsHtml += `
                            <div style="background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 4px; padding: 6px; margin-top: 6px; font-size: 11px;">
                                <strong style="color: #cbd5e1; display: block; margin-bottom: 4px; font-size: 10px;">${p.name}</strong>
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <span style="color: #9333ea;">Abel: ${p.a_1v} ➔ ${p.a_2v} (<strong style="color: ${p.a_c > 0 ? '#16a34a' : '#dc2626'}">${p.a_c > 0 ? '+' : ''}${p.a_c}</strong>)</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 2px;">
                                    <span style="color: #ea580c;">Cepe: ${p.c_1v} ➔ ${p.c_2v} (<strong style="color: ${p.c_c > 0 ? '#16a34a' : '#dc2626'}">${p.c_c > 0 ? '+' : ''}${p.c_c}</strong>)</span>
                                </div>
                            </div>`;
                        });
                        
                        if (sortedPosts.length > maxPostsToShow) {
                            postsHtml += `<div style="font-size: 10px; color: #94a3b8; margin-top: 6px; text-align: center;">Y ${sortedPosts.length - maxPostsToShow} puestos más...</div>`;
                        }
                        postsHtml += '</div>';
                        popupContent += postsHtml;
                    } else if (feature.properties.posts && feature.properties.posts.length > 0) {
                        const maxPostsToShow = 5;
                        const postsList = feature.properties.posts.slice(0, maxPostsToShow).join(', ');
                        const moreText = feature.properties.posts.length > maxPostsToShow ? ` y ${feature.properties.posts.length - maxPostsToShow} más...` : '';
                        popupContent += `<p style="font-size: 11px; margin-top: 8px; color: var(--text-secondary);"><strong>Puestos (${feature.properties.posts.length}):</strong> ${postsList}${moreText}</p>`;
                    }
                } else {
                    popupContent += `<p>Sin datos de crecimiento 2da Vuelta.</p>`;
                }
            } else {
                if (winner && winner !== 'Sin Datos') {
                    const results = feature.properties.results;
                    popupContent += `<p>Ganador: <strong>${winner}</strong> (${results[0].pct.toFixed(2)}%)</p>`;
                    popupContent += `<p>Votos Totales: ${formatNumber(feature.properties.total_votes)}</p>`;
                    if (feature.properties.posts && feature.properties.posts.length > 0) {
                        const maxPostsToShow = 5;
                        const postsList = feature.properties.posts.slice(0, maxPostsToShow).join(', ');
                        const moreText = feature.properties.posts.length > maxPostsToShow ? ` y ${feature.properties.posts.length - maxPostsToShow} más...` : '';
                        popupContent += `<p style="font-size: 11px; margin-top: 8px; color: var(--text-secondary);"><strong>Puestos (${feature.properties.posts.length}):</strong> ${postsList}${moreText}</p>`;
                    }
                } else {
                    popupContent += `<p>Sin datos electorales</p><p style="font-size: 11px; margin-top: 8px; color: var(--text-secondary);">No se registraron puestos de votación geolocalizados dentro de este barrio o vereda.</p>`;
                }
            }
            
            layer.bindPopup(popupContent);
            
            layer.on({
                mouseover: function (e) {
                    const l = e.target;
                    l.setStyle({
                        weight: 3,
                        color: '#a855f7',
                        fillOpacity: Math.min(l.options.fillOpacity + 0.15, 0.95)
                    });
                    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                        l.bringToFront();
                    }
                },
                mouseout: function (e) {
                    barriosLayer.resetStyle(e.target);
                },
                click: function (e) {
                    if (winner && winner !== 'Sin Datos') {
                        selectedCommuneCode = null;
                        document.getElementById('results-title').innerText = nombre;
                        document.getElementById('results-subtitle').innerText = `Resultados en Barrio / Vereda`;
                        renderResultsList(feature.properties.results, feature.properties.total_votes);
                    }
                }
            });
        }
    }).addTo(map);
}

// Switch Tabs
function switchTab(tab) {
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
        
        // Reset barrios styles and remove strategy tooltips when leaving strategy tab
        if (barriosLayer) {
            barriosLayer.eachLayer(function(layer) {
                barriosLayer.resetStyle(layer);
                layer.unbindTooltip();
            });
        }
        
        if (tab === 'communes') {
            if (communesLayer) {
                communesLayer.addTo(map);
            }
            map.setView([6.25, -75.56], 12);
            if (typeof renderMedellinGeneralResults === 'function') renderMedellinGeneralResults();
        } else if (tab === 'barrios' || tab === 'growth') {
            if (barriosLayer) {
                barriosLayer.addTo(map);
                // Refresh styles to pick up tab-specific coloring
                barriosLayer.eachLayer(function(layer) {
                    barriosLayer.resetStyle(layer);
                });
            }
            if (tab === 'barrios' && typeof renderPostMarkers === 'function') renderPostMarkers('MEDELLIN');
            if (tab === 'growth' && typeof populateTopGrowth === 'function') populateTopGrowth();
            
            map.setView([6.25, -75.56], 12);
            if (typeof renderMedellinGeneralResults === 'function') renderMedellinGeneralResults();
        } else {
            if (mapLegend) mapLegend.style.display = 'none';
            if (typeof resetSelectors === 'function') resetSelectors();
        }
    }
}

// Populate Municipalities dropdown
function populateMunicipalities() {
    const select = document.getElementById('select-muni');
    select.innerHTML = '<option value="">-- Selecciona Municipio --</option>';
    
    const allOpt = document.createElement('option');
    allOpt.value = "TODOS";
    allOpt.innerText = "TODOS (Todos los municipios)";
    select.appendChild(allOpt);
    
    const munis = Object.keys(electoralData.hierarchy).sort();
    munis.forEach(m => {
        const opt = document.createElement('option');
        opt.value = m;
        opt.innerText = m;
        select.appendChild(opt);
    });
}

function resetSelectors() {
    const muniSelect = document.getElementById('select-muni');
    const hasTodos = Array.from(muniSelect.options).some(opt => opt.value === 'TODOS');
    
    if (hasTodos) {
        muniSelect.value = 'TODOS';
        onMuniChange();
    } else {
        muniSelect.value = '';
        
        const zoneSelect = document.getElementById('select-zone');
        zoneSelect.innerHTML = '<option value="">Selecciona un municipio</option>';
        zoneSelect.disabled = true;
        
        const postSelect = document.getElementById('select-post');
        postSelect.innerHTML = '<option value="">Selecciona una zona</option>';
        postSelect.disabled = true;
        
        const tableSelect = document.getElementById('select-table');
        tableSelect.innerHTML = '<option value="">Selecciona un puesto</option>';
        tableSelect.disabled = true;
        
        if (electoralData && electoralData.hierarchy) {
            renderPostMarkers();
        } else {
            postsLayer.clearLayers();
        }
        document.getElementById('tables-summary-section').style.display = 'none';
        renderMedellinGeneralResults();
    }
}

// Helper to calculate winning candidate and total votes for a post
function getPostElectoralSummary(postInfo) {
    let totals = Array(electoralData.candidates.length).fill(0);
    Object.values(postInfo.tables).forEach(tableVotes => {
        tableVotes.forEach((votes, idx) => {
            totals[idx] += votes;
        });
    });
    
    const totalVotes = totals.reduce((a, b) => a + b, 0);
    let maxVotes = -1;
    let winnerIdx = 0;
    
    totals.forEach((v, idx) => {
        if (v > maxVotes) {
            maxVotes = v;
            winnerIdx = idx;
        }
    });
    
    const winnerName = electoralData.candidates[winnerIdx];
    const winnerPct = totalVotes > 0 ? (maxVotes / totalVotes * 100) : 0;
    
    const blancoIdx = electoralData.candidates.indexOf("VOTOS EN BLANCO");
    const votosBlanco = blancoIdx !== -1 ? totals[blancoIdx] : 0;
    const blancoPct = totalVotes > 0 ? (votosBlanco / totalVotes * 100) : 0;
    
    return {
        winner: winnerName,
        winnerPct: winnerPct,
        totalVotes: totalVotes,
        votosBlanco: votosBlanco,
        blancoPct: blancoPct
    };
}

// Render Comparative Card 2022/2026
function renderComparativeCard(muniName = null, zoneName = null, postId = null) {
    const card = document.getElementById('comparative-card');
    if (!card) return;
    
    // Determine 2022 stats
    let stats2022 = null;
    let stats2026 = { fico: 0, petro: 0, total: 0 };
    let subtitle = '';
    
    if (muniName && zoneName && postId) {
        // Post level
        subtitle = `Puesto: ${electoralData.hierarchy[muniName][zoneName][postId].name}`;
        if (electoralData.comparison_2022_hierarchy && electoralData.comparison_2022_hierarchy[muniName] && electoralData.comparison_2022_hierarchy[muniName][zoneName] && electoralData.comparison_2022_hierarchy[muniName][zoneName][postId]) {
            stats2022 = electoralData.comparison_2022_hierarchy[muniName][zoneName][postId];
        }
        
        let candIdxEspriella = electoralData.candidates.indexOf("ABELARDO DE LA ESPRIELLA");
        let candIdxPaloma = electoralData.candidates.indexOf("PALOMA VALENCIA LASERNA");
        let candIdxCepeda = electoralData.candidates.indexOf("IVÁN CEPEDA CASTRO");
        let postInfo = electoralData.hierarchy[muniName][zoneName][postId];
        
        Object.values(postInfo.tables).forEach(tableVotes => {
            stats2026.fico += (tableVotes[candIdxEspriella] || 0) + (tableVotes[candIdxPaloma] || 0);
            stats2026.petro += tableVotes[candIdxCepeda] || 0;
            stats2026.total += tableVotes.reduce((a, b) => a + b, 0);
        });
        
    } else if (muniName && muniName !== "TODOS") {
        // Municipality level
        subtitle = `Municipio: ${muniName}`;
        if (electoralData.comparison_2022_muni && electoralData.comparison_2022_muni[muniName]) {
            stats2022 = electoralData.comparison_2022_muni[muniName];
        }
        
        let candIdxEspriella = electoralData.candidates.indexOf("ABELARDO DE LA ESPRIELLA");
        let candIdxPaloma = electoralData.candidates.indexOf("PALOMA VALENCIA LASERNA");
        let candIdxCepeda = electoralData.candidates.indexOf("IVÁN CEPEDA CASTRO");
        let muniData = electoralData.hierarchy[muniName];
        
        Object.values(muniData).forEach(zonePosts => {
            Object.values(zonePosts).forEach(postInfo => {
                Object.values(postInfo.tables).forEach(tableVotes => {
                    stats2026.fico += (tableVotes[candIdxEspriella] || 0) + (tableVotes[candIdxPaloma] || 0);
                    stats2026.petro += tableVotes[candIdxCepeda] || 0;
                    stats2026.total += tableVotes.reduce((a, b) => a + b, 0);
                });
            });
        });
    } else {
        // Global Medellin (Default)
        subtitle = "Medellín (Global)";
        const globalMuni = "MEDELLIN";
        if (electoralData.comparison_2022_muni && electoralData.comparison_2022_muni[globalMuni]) {
            stats2022 = electoralData.comparison_2022_muni[globalMuni];
        }
        
        Object.values(electoralData.communes).forEach(commData => {
            commData.results.forEach(res => {
                if (res.candidate === "ABELARDO DE LA ESPRIELLA" || res.candidate === "PALOMA VALENCIA LASERNA") stats2026.fico += res.votes;
                if (res.candidate === "IVÁN CEPEDA CASTRO") stats2026.petro += res.votes;
                stats2026.total += res.votes;
            });
        });
    }
    
    if (!stats2022 || stats2022.TOTAL === 0) {
        card.style.display = 'none';
        return;
    }
    
    card.style.display = 'block';
    const headerTitle = card.querySelector('.results-header span');
    if (headerTitle) {
        headerTitle.innerText = subtitle;
    }
    
    let pctFico2022 = stats2022.TOTAL > 0 ? (stats2022.FICO / stats2022.TOTAL * 100) : 0;
    let pctPetro2022 = stats2022.TOTAL > 0 ? (stats2022.PETRO / stats2022.TOTAL * 100) : 0;
    
    let pctEspriella2026 = stats2026.total > 0 ? (stats2026.fico / stats2026.total * 100) : 0;
    let pctCepeda2026 = stats2026.total > 0 ? (stats2026.petro / stats2026.total * 100) : 0;
    
    let otros2022 = stats2022.TOTAL - stats2022.FICO - stats2022.PETRO;
    let otros2026 = stats2026.total - stats2026.fico - stats2026.petro;
    let pctOtros2022 = stats2022.TOTAL > 0 ? (otros2022 / stats2022.TOTAL * 100) : 0;
    let pctOtros2026 = stats2026.total > 0 ? (otros2026 / stats2026.total * 100) : 0;
    
    document.getElementById('comp-2022-total').innerText = `Participación: ${formatNumber(stats2022.TOTAL)}`;
    document.getElementById('comp-2026-total').innerText = `Participación: ${formatNumber(stats2026.total)}`;

    const diffDer = pctEspriella2026 - pctFico2022;
    const diffIzq = pctCepeda2026 - pctPetro2022;
    const diffOtros = pctOtros2026 - pctOtros2022;

    function getDeltaBadge(delta) {
        if (delta > 0) return `<span style="background:#dcfce7; color:#166534; padding:2px 6px; border-radius:12px; font-size:11px; font-weight:700; margin-left:6px; display:inline-flex; align-items:center; vertical-align: middle;">↑ ${Math.abs(delta).toFixed(1)}%</span>`;
        if (delta < 0) return `<span style="background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:12px; font-size:11px; font-weight:700; margin-left:6px; display:inline-flex; align-items:center; vertical-align: middle;">↓ ${Math.abs(delta).toFixed(1)}%</span>`;
        return `<span style="background:#f1f5f9; color:#475569; padding:2px 6px; border-radius:12px; font-size:11px; font-weight:700; margin-left:6px; display:inline-flex; align-items:center; vertical-align: middle;">= 0.0%</span>`;
    }

    // 2022 Styling
    document.getElementById('comp-2022-der').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Fico + Rodolfo</div>
        <div style="display:flex; justify-content:center; align-items:baseline; margin:4px 0;">
            <span style="font-size:22px; font-weight:800; color:#0284c7;">${pctFico2022.toFixed(1)}%</span>
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(stats2022.FICO)} de ${formatNumber(stats2022.TOTAL)})</div>
    `;
    
    document.getElementById('comp-2022-izq').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Petro</div>
        <div style="display:flex; justify-content:center; align-items:baseline; margin:4px 0;">
            <span style="font-size:22px; font-weight:800; color:#ea580c;">${pctPetro2022.toFixed(1)}%</span>
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(stats2022.PETRO)} de ${formatNumber(stats2022.TOTAL)})</div>
    `;
    
    document.getElementById('comp-2022-otros').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600; margin-top:8px;">Otros/Blanco</div>
        <div style="font-size:14px; font-weight:700; color:#64748b;">${pctOtros2022.toFixed(1)}%</div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(otros2022)} votos)</div>
    `;

    // 2026 Styling with Badges
    document.getElementById('comp-2026-der').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">De La Espriella + Paloma</div>
        <div style="display:flex; justify-content:center; align-items:center; margin:4px 0;">
            <span style="font-size:22px; font-weight:800; color:#0284c7;">${pctEspriella2026.toFixed(1)}%</span>
            ${getDeltaBadge(diffDer)}
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(stats2026.fico)} de ${formatNumber(stats2026.total)})</div>
    `;
    
    document.getElementById('comp-2026-izq').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Cepeda</div>
        <div style="display:flex; justify-content:center; align-items:center; margin:4px 0;">
            <span style="font-size:22px; font-weight:800; color:#ea580c;">${pctCepeda2026.toFixed(1)}%</span>
            ${getDeltaBadge(diffIzq)}
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(stats2026.petro)} de ${formatNumber(stats2026.total)})</div>
    `;
    
    document.getElementById('comp-2026-otros').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600; margin-top:8px;">Otros/Blanco</div>
        <div style="display:flex; justify-content:center; align-items:center; margin:2px 0;">
            <span style="font-size:14px; font-weight:700; color:#64748b;">${pctOtros2026.toFixed(1)}%</span>
            ${getDeltaBadge(diffOtros)}
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(otros2026)} votos)</div>
    `;
    
    const margin2022 = pctFico2022 - pctPetro2022;
    const margin2026 = pctEspriella2026 - pctCepeda2026;
    const shift = margin2026 - margin2022;
    
    let shiftText = '';
    if (shift > 0) {
        shiftText = `El margen de la derecha creció <span style="color:#0284c7;">+${shift.toFixed(1)}%</span> frente a 2022.`;
    } else {
        shiftText = `El margen de la izquierda creció <span style="color:#ea580c;">+${Math.abs(shift).toFixed(1)}%</span> frente a 2022.`;
    }
    document.getElementById('comp-shift-summary').innerHTML = shiftText;

    const diffVotosDer = stats2026.fico - stats2022.FICO;
    const diffVotosIzq = stats2026.petro - stats2022.PETRO;

    const derAction = diffDer >= 0 ? 'subió' : 'cayó';
    const derVotosText = diffVotosDer >= 0 ? `sumando ${formatNumber(diffVotosDer)} votos` : `perdiendo ${formatNumber(Math.abs(diffVotosDer))} votos`;
    const izqAction = diffIzq >= 0 ? 'subió' : 'cayó';
    const izqVotosText = diffVotosIzq >= 0 ? `sumando ${formatNumber(diffVotosIzq)} votos` : `perdiendo ${formatNumber(Math.abs(diffVotosIzq))} votos`;

    let explanation = `Esto se debe a un doble efecto: la derecha <strong>${derAction} ${Math.abs(diffDer).toFixed(1)} puntos</strong> (${derVotosText}), mientras que la izquierda <strong>${izqAction} ${Math.abs(diffIzq).toFixed(1)} puntos</strong> (${izqVotosText}).`;
    
    document.getElementById('comp-shift-explanation').innerHTML = explanation;
}

// Render post circle markers (heatmap) on the map for selected scope
function renderPostMarkers(muni = null, filterZone = null) {
    postsLayer.clearLayers();
    
    const bounds = [];
    
    const renderMuniPosts = (muniName, muniData) => {
        Object.entries(muniData).forEach(([zoneName, posts]) => {
            if (filterZone && zoneName !== filterZone) return;
            
            Object.entries(posts).forEach(([postId, postInfo]) => {
                if (!postInfo.lat || !postInfo.lon) return;
                
                const summary = getPostElectoralSummary(postInfo);
                const winnerColor = getCandidateColor(summary.winner);
                const opacity = 0.4 + ((Math.min(Math.max(summary.winnerPct, 30), 80) - 30) / 50) * 0.55;
                const radius = 4 + (Math.min(summary.totalVotes, 20000) / 20000) * 10;
                
                const marker = L.circleMarker([postInfo.lat, postInfo.lon], {
                    radius: radius,
                    fillColor: winnerColor,
                    color: '#e2e8f0', // Light border
                    weight: 1,
                    opacity: 0.8,
                    fillOpacity: opacity
                });
                
                let abstencionHtml = '';
                if (postInfo.potential && postInfo.potential > 0) {
                    const abstencionPct = Math.max(0, ((postInfo.potential - summary.totalVotes) / postInfo.potential) * 100);
                    abstencionHtml = `<p style="margin:0; font-size:11px; color:#ef4444;"><strong>Abstención: ${abstencionPct.toFixed(2)}%</strong></p>`;
                }

                const popupContent = `
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif;">
                        <h3 style="margin:0 0 5px 0; font-size: 14px; font-weight:700; color:#0f172a;">${postInfo.name}</h3>
                        <p style="margin:0 0 3px 0; font-size:11px; color:#475569;">${zoneName} | ${muniName}</p>
                        <p style="margin:0; font-size:12px; color:#0f172a;">Ganador: <strong style="color:${winnerColor};">${summary.winner}</strong> (${summary.winnerPct.toFixed(2)}%)</p>
                        <p style="margin:0; font-size:11px; color:#64748b;">Votos Totales: ${formatNumber(summary.totalVotes)}</p>
                        <p style="margin:0; font-size:11px; color:#64748b;">Votos en Blanco: ${formatNumber(summary.votosBlanco)} (${summary.blancoPct.toFixed(2)}%)</p>
                        ${abstencionHtml}
                        <hr style="margin:5px 0; border:0; border-top:1px solid #e2e8f0;">
                        <p style="margin:0; font-size:11px; color:#0f172a;"><strong>Potencial Electoral: ${formatNumber(postInfo.potential || 0)}</strong></p>
                        <p style="margin:0; font-size:10px; color:#475569;">Mujeres: ${formatNumber(postInfo.potential_mujeres || 0)} | Hombres: ${formatNumber(postInfo.potential_hombres || 0)}</p>
                    </div>
                `;
                marker.bindPopup(popupContent);
                
                marker.on({
                    mouseover: function(e) {
                        this.openPopup();
                        this.setStyle({ weight: 2.5, color: '#4f46e5' });
                    },
                    mouseout: function(e) {
                        this.closePopup();
                        this.setStyle({ weight: 1, color: '#e2e8f0' });
                    },
                    click: function(e) {
                        const muniSelect = document.getElementById('select-muni');
                        const zoneSelect = document.getElementById('select-zone');
                        const postSelect = document.getElementById('select-post');
                        const tableSelect = document.getElementById('select-table');
                        
                        muniSelect.value = muniName;
                        
                        // Populate zones
                        zoneSelect.innerHTML = '<option value="">-- Selecciona Zona --</option>';
                        zoneSelect.disabled = false;
                        const zones = Object.keys(electoralData.hierarchy[muniName]).sort((a, b) => {
                            const numA = parseInt(a.replace(/\D/g, '')) || 0;
                            const numB = parseInt(b.replace(/\D/g, '')) || 0;
                            return numA - numB;
                        });
                        zones.forEach(z => {
                            const opt = document.createElement('option');
                            opt.value = z;
                            opt.innerText = z;
                            zoneSelect.appendChild(opt);
                        });
                        zoneSelect.value = zoneName;
                        
                        // Populate posts
                        postSelect.innerHTML = '<option value="">-- Selecciona Puesto --</option>';
                        postSelect.disabled = false;
                        const posts = electoralData.hierarchy[muniName][zoneName];
                        Object.entries(posts)
                            .sort((a, b) => a[1].name.localeCompare(b[1].name))
                            .forEach(([pId, pInfo]) => {
                                const opt = document.createElement('option');
                                opt.value = pId;
                                opt.innerText = pInfo.name;
                                postSelect.appendChild(opt);
                            });
                        postSelect.value = postId;
                        
                        // Populate tables
                        tableSelect.innerHTML = '<option value="">-- Selecciona Mesa (General) --</option>';
                        tableSelect.disabled = false;
                        const postInfo = posts[postId];
                        const tables = Object.keys(postInfo.tables).sort((a, b) => parseInt(a) - parseInt(b));
                        tables.forEach(t => {
                            const opt = document.createElement('option');
                            opt.value = t;
                            opt.innerText = `Mesa ${t}`;
                            tableSelect.appendChild(opt);
                        });
                        
                        // Zoom to the clicked post
                        if (postInfo.lat && postInfo.lon) {
                            map.setView([postInfo.lat, postInfo.lon], 16);
                        }
                        
                        // Render results
                        aggregateAndRenderResults({ muni: muniName, zone: zoneName, postId: postId });
                    }
                });
                
                if (postInfo.lat >= 5.0 && postInfo.lat <= 9.0 && postInfo.lon >= -78.0 && postInfo.lon <= -73.0) {
                    postsLayer.addLayer(marker);
                    bounds.push([postInfo.lat, postInfo.lon]);
                }
            });
        });
    };
    
    if (muni) {
        const muniData = electoralData.hierarchy[muni];
        if (muniData) {
            renderMuniPosts(muni, muniData);
        }
    } else if (electoralData && electoralData.hierarchy) {
        Object.entries(electoralData.hierarchy).forEach(([muniName, muniData]) => {
            renderMuniPosts(muniName, muniData);
        });
    }
    
    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50] });
    } else {
        map.setView([6.25, -75.56], 12);
    }
}

// Render the list of tables inside the post
function renderTablesListSummary(muni, zone, postId) {
    const container = document.getElementById('tables-list-container');
    const section = document.getElementById('tables-summary-section');
    
    container.innerHTML = '';
    
    const postInfo = electoralData.hierarchy[muni][zone][postId];
    if (!postInfo) {
        section.style.display = 'none';
        return;
    }
    
    section.style.display = 'block';
    
    const tables = Object.keys(postInfo.tables).sort((a, b) => parseInt(a) - parseInt(b));
    
    tables.forEach(tableId => {
        const votes = postInfo.tables[tableId];
        const total = votes.reduce((a, b) => a + b, 0);
        
        let maxVotes = -1;
        let winnerIdx = 0;
        votes.forEach((v, idx) => {
            if (v > maxVotes) {
                maxVotes = v;
                winnerIdx = idx;
            }
        });
        
        const winnerCand = electoralData.candidates[winnerIdx];
        const winnerColor = getCandidateColor(winnerCand);
        
        const row = document.createElement('div');
        row.style.display = 'flex';
        row.style.justifyContent = 'space-between';
        row.style.alignItems = 'center';
        row.style.background = 'rgba(0, 0, 0, 0.02)';
        row.style.border = '1px solid var(--border-color)';
        row.style.padding = '12px 14px';
        row.style.borderRadius = '12px';
        row.style.fontSize = '12px';
        row.style.transition = 'all 0.2s ease';
        
        const left = document.createElement('div');
        left.innerHTML = `<span style="font-weight: 700; color:#0f172a;">Mesa ${tableId}</span> <span style="font-size: 10px; color: var(--text-secondary); margin-left: 6px;">(${formatNumber(total)} votos)</span>`;
        
        const right = document.createElement('div');
        right.style.display = 'flex';
        right.style.alignItems = 'center';
        right.style.gap = '8px';
        
        const badge = document.createElement('span');
        badge.style.background = `${winnerColor}15`;
        badge.style.border = `1px solid ${winnerColor}40`;
        badge.style.boxShadow = `0 0 8px ${winnerColor}20`;
        badge.style.color = winnerColor;
        badge.style.padding = '4px 10px';
        badge.style.borderRadius = '6px';
        badge.style.fontSize = '11px';
        badge.style.fontWeight = '700';
        badge.innerText = winnerCand.split(' ')[0];
        
        const btn = document.createElement('button');
        btn.className = 'tab-btn';
        btn.style.padding = '6px 12px';
        btn.style.fontSize = '11px';
        btn.style.background = 'rgba(0,0,0,0.05)';
        btn.style.borderColor = 'rgba(0,0,0,0.1)';
        btn.style.color = '#475569';
        btn.style.width = 'auto';
        btn.innerText = '📊 Graficar';
        btn.onclick = () => selectSpecificTable(tableId);
        
        right.appendChild(badge);
        right.appendChild(btn);
        row.appendChild(left);
        row.appendChild(right);
        container.appendChild(row);
    });
}

function selectSpecificTable(tableId) {
    document.getElementById('select-table').value = tableId;
    onTableChange();
}

function onMuniChange() {
    const muniVal = document.getElementById('select-muni').value;
    const zoneSelect = document.getElementById('select-zone');
    const postSelect = document.getElementById('select-post');
    const tableSelect = document.getElementById('select-table');
    
    postsLayer.clearLayers();
    document.getElementById('tables-summary-section').style.display = 'none';
    
    if (!muniVal) {
        resetSelectors();
        return;
    }
    
    if (muniVal === "TODOS") {
        zoneSelect.innerHTML = '<option value="">Selecciona un municipio</option>';
        zoneSelect.disabled = true;
        
        postSelect.innerHTML = '<option value="">Selecciona una zona</option>';
        postSelect.disabled = true;
        
        tableSelect.innerHTML = '<option value="">Selecciona un puesto</option>';
        tableSelect.disabled = true;
        
        renderPostMarkers();
        aggregateAndRenderResultsForAll();
        return;
    }
    
    zoneSelect.innerHTML = '<option value="">-- Selecciona Zona --</option>';
    zoneSelect.disabled = false;
    
    postSelect.innerHTML = '<option value="">Selecciona una zona</option>';
    postSelect.disabled = true;
    
    tableSelect.innerHTML = '<option value="">Selecciona un puesto</option>';
    tableSelect.disabled = true;
    
    const zones = Object.keys(electoralData.hierarchy[muniVal]).sort((a, b) => {
        const numA = parseInt(a.replace(/\D/g, '')) || 0;
        const numB = parseInt(b.replace(/\D/g, '')) || 0;
        return numA - numB;
    });
    
    zones.forEach(z => {
        const opt = document.createElement('option');
        opt.value = z;
        opt.innerText = z;
        zoneSelect.appendChild(opt);
    });
    
    renderPostMarkers(muniVal);
    aggregateAndRenderResults({ muni: muniVal });
}

function aggregateAndRenderResultsForAll() {
    let totals = Array(electoralData.candidates.length).fill(0);
    
    let mData = electoralData.hierarchy["MEDELLIN"];
        if(mData) {
          Object.values(mData).forEach(zones => {
        Object.values(zones).forEach(posts => {
            Object.values(posts).forEach(postInfo => {
                Object.values(postInfo.tables).forEach(tableVotes => {
                    tableVotes.forEach((votes, idx) => {
                        totals[idx] += votes;
                    });
                });
            });
        });
    });
    }
    
    const totalVotes = totals.reduce((a, b) => a + b, 0);
    
    const sorted = electoralData.candidates.map((cand, idx) => ({
        candidate: cand,
        votes: totals[idx],
        pct: totalVotes > 0 ? (totals[idx] / totalVotes * 100) : 0
    })).sort((a, b) => b.votes - a.votes);
    
    document.getElementById('results-title').innerText = "Resultados Consolidados";
    document.getElementById('results-subtitle').innerText = "Acumulado de todos los municipios de Antioquia";
    renderResultsList(sorted, totalVotes, 'bar', null);
}

// Handle zone selection
function onZoneChange() {
    const muniVal = document.getElementById('select-muni').value;
    const zoneVal = document.getElementById('select-zone').value;
    const postSelect = document.getElementById('select-post');
    const tableSelect = document.getElementById('select-table');
    
    document.getElementById('tables-summary-section').style.display = 'none';
    
    if (!zoneVal) {
        postSelect.innerHTML = '<option value="">Selecciona una zona</option>';
        postSelect.disabled = true;
        tableSelect.innerHTML = '<option value="">Selecciona un puesto</option>';
        tableSelect.disabled = true;
        
        renderPostMarkers(muniVal);
        aggregateAndRenderResults({ muni: muniVal });
        return;
    }
    
    postSelect.innerHTML = '<option value="">-- Selecciona Puesto --</option>';
    postSelect.disabled = false;
    
    tableSelect.innerHTML = '<option value="">Selecciona un puesto</option>';
    tableSelect.disabled = true;
    
    const posts = electoralData.hierarchy[muniVal][zoneVal];
    Object.entries(posts)
        .sort((a, b) => a[1].name.localeCompare(b[1].name))
        .forEach(([pId, pInfo]) => {
            const opt = document.createElement('option');
            opt.value = pId;
            opt.innerText = pInfo.name;
            postSelect.appendChild(opt);
        });
        
    renderPostMarkers(muniVal, zoneVal);
    aggregateAndRenderResults({ muni: muniVal, zone: zoneVal });
}

// Handle post selection
function onPostChange() {
    const muniVal = document.getElementById('select-muni').value;
    const zoneVal = document.getElementById('select-zone').value;
    const postIdVal = document.getElementById('select-post').value;
    const tableSelect = document.getElementById('select-table');
    
    if (!postIdVal) {
        tableSelect.innerHTML = '<option value="">Selecciona un puesto</option>';
        tableSelect.disabled = true;
        document.getElementById('tables-summary-section').style.display = 'none';
        renderPostMarkers(muniVal, zoneVal);
        aggregateAndRenderResults({ muni: muniVal, zone: zoneVal });
        return;
    }
    
    const postInfo = electoralData.hierarchy[muniVal][zoneVal][postIdVal];
    
    tableSelect.innerHTML = '<option value="">-- Selecciona Mesa (General) --</option>';
    tableSelect.disabled = false;
    
    const tables = Object.keys(postInfo.tables).sort((a, b) => parseInt(a) - parseInt(b));
    tables.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t;
        opt.innerText = `Mesa ${t}`;
        tableSelect.appendChild(opt);
    });
    
    if (postInfo.lat && postInfo.lon) {
        postsLayer.eachLayer(layer => {
            const latlng = layer.getLatLng();
            if (latlng.lat === postInfo.lat && latlng.lng === postInfo.lon) {
                layer.openPopup();
            }
        });
        map.setView([postInfo.lat, postInfo.lon], 16);
    }
    
    aggregateAndRenderResults({ muni: muniVal, zone: zoneVal, postId: postIdVal });
}

// Handle table selection
function onTableChange() {
    const muniVal = document.getElementById('select-muni').value;
    const zoneVal = document.getElementById('select-zone').value;
    const postIdVal = document.getElementById('select-post').value;
    const tableVal = document.getElementById('select-table').value;
    
    if (!tableVal) {
        aggregateAndRenderResults({ muni: muniVal, zone: zoneVal, postId: postIdVal });
        return;
    }
    
    aggregateAndRenderResults({ muni: muniVal, zone: zoneVal, postId: postIdVal, table: tableVal });
}

// Aggregate electoral results based on selected filters
function aggregateAndRenderResults({ muni, zone, postId, table }) {
    let totals = Array(electoralData.candidates.length).fill(0);
    let title = "";
    let subtitle = "";
    let chartType = 'bar';
    let postInfo = null;
    
    if (table) {
        const votes = electoralData.hierarchy[muni][zone][postId].tables[table];
        totals = [...votes];
        title = `Mesa ${table}`;
        subtitle = `${electoralData.hierarchy[muni][zone][postId].name} | ${muni}`;
        chartType = 'bar';
    } else if (postId) {
        postInfo = electoralData.hierarchy[muni][zone][postId];
        Object.values(postInfo.tables).forEach(tableVotes => {
            tableVotes.forEach((votes, idx) => {
                totals[idx] += votes;
            });
        });
        title = postInfo.name;
        subtitle = `${zone} | ${muni}`;
        chartType = 'line';
        
        renderTablesListSummary(muni, zone, postId);
    } else if (zone) {
        const posts = electoralData.hierarchy[muni][zone];
        Object.values(posts).forEach(postInfo => {
            Object.values(postInfo.tables).forEach(tableVotes => {
                tableVotes.forEach((votes, idx) => {
                    totals[idx] += votes;
                });
            });
        });
        title = zone;
        subtitle = `Acumulado Zona | ${muni}`;
        chartType = 'bar';
    } else if (muni) {
        const zones = electoralData.hierarchy[muni];
        Object.values(zones).forEach(posts => {
            Object.values(posts).forEach(postInfo => {
                Object.values(postInfo.tables).forEach(tableVotes => {
                    tableVotes.forEach((votes, idx) => {
                        totals[idx] += votes;
                    });
                });
            });
        });
        title = muni;
        subtitle = `Acumulado Municipio`;
        chartType = 'bar';
    }
    
    const totalVotes = totals.reduce((a, b) => a + b, 0);
    
    const sorted = electoralData.candidates.map((cand, idx) => ({
        candidate: cand,
        votes: totals[idx],
        pct: totalVotes > 0 ? (totals[idx] / totalVotes * 100) : 0
    })).sort((a, b) => b.votes - a.votes);
    
    document.getElementById('results-title').innerText = title;
    document.getElementById('results-subtitle').innerText = subtitle;
    renderResultsList(sorted, totalVotes, chartType, postInfo);
    
    // Dynamically update comparative card
    renderComparativeCard(muni, zone, postId);
    renderComparativeCard2v(muni, zone, postId, table);
}

// Initial triggers
initMap();
loadData();

// Download Card as PNG Image

  window.downloadCard2v = function() {
      const card = document.getElementById('comparative-card-2v');
      const btnContainer = document.getElementById('download-btn-container-2v');
      
      btnContainer.style.display = 'none';
      
      setTimeout(() => {
          html2canvas(card, {
              scale: 2,
              backgroundColor: '#ffffff',
              useCORS: true
          }).then(canvas => {
              btnContainer.style.display = 'block';
              const link = document.createElement('a');
              link.download = 'analisis_1v_vs_2v_john_alexander_echeverry.png';
              link.href = canvas.toDataURL('image/png');
              link.click();
          }).catch(err => {
              console.error("Error capturing canvas:", err);
              btnContainer.style.display = 'block';
              alert("Hubo un error al generar la imagen. Intenta de nuevo.");
          });
      }, 100);
  };

  window.downloadCard = function() {
    const card = document.getElementById('comparative-card');
    const btnContainer = document.getElementById('download-btn-container');
    
    // Hide the button container so it doesn't appear in the screenshot
    btnContainer.style.display = 'none';
    
    // Slight delay to ensure UI reflows after hiding button
    setTimeout(() => {
        html2canvas(card, {
            scale: 2, // Higher resolution for better quality
            backgroundColor: '#ffffff',
            useCORS: true
        }).then(canvas => {
            // Restore the button container
            btnContainer.style.display = 'block';
            
            // Create a download link and trigger it
            const link = document.createElement('a');
            link.download = 'analisis_electoral_john_charcos.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
        }).catch(err => {
            console.error("Error generating image:", err);
            btnContainer.style.display = 'block'; // Restore even on error
            alert("Hubo un error al generar la imagen.");
        });
    }, 50);
};


// Render Strategy Map (Heatmap of Oportunidad)
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
            if (props.winner && props.winner !== 'Sin Datos' && props.opportunity !== undefined) {
                let opportunity = props.opportunity || 0;
                let potential = props.potential || 0;
                let abstencion = props.abstencion || 0;
                let otros = props.otros || 0;
                
                tops.push({ name: props.nombre, otros: opportunity });
                
                // Color ramp for "opportunity" (Green scale)
                // Proportional to opportunity. Max is 41,295, but we can scale it nicely with a divisor of 8000.
                let intensity = Math.min(opportunity / 8000, 1.0);
                
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
                
                // Bind premium tooltip
                let tooltipContent = `
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif; padding: 4px; color: #0f172a;">
                        <h4 style="margin: 0 0 6px 0; font-size: 14px; font-weight: 800; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px;">${props.nombre}</h4>
                        <div style="display: grid; grid-template-columns: auto auto; gap: 4px 12px; font-size: 11px; font-weight: 500;">
                            <span style="color: #64748b;">Potencial Electoral:</span>
                            <span style="font-weight: 700; text-align: right;">${formatNumber(potential)}</span>
                            
                            <span style="color: #64748b;">Votantes Reales:</span>
                            <span style="font-weight: 700; text-align: right;">${formatNumber(props.total_votes)}</span>
                            
                            <span style="color: #ea580c; font-weight: 600;">Abstención Estimada:</span>
                            <span style="font-weight: 700; color: #ea580c; text-align: right;">${formatNumber(abstencion)}</span>
                            
                            <span style="color: #6366f1; font-weight: 600;">Votos Otros/Blanco/Nulo:</span>
                            <span style="font-weight: 700; color: #6366f1; text-align: right;">${formatNumber(otros)}</span>
                            
                            <span style="color: #166534; font-weight: 700; border-top: 1px dashed #cbd5e1; padding-top: 4px; margin-top: 4px;">Oportunidad Cepeda:</span>
                            <span style="font-weight: 800; color: #166534; text-align: right; border-top: 1px dashed #cbd5e1; padding-top: 4px; margin-top: 4px; font-size: 12px;">${formatNumber(opportunity)}</span>
                        </div>
                    </div>
                `;
                layer.bindTooltip(tooltipContent, {sticky: true});
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

// Function to populate the Top Growth lists
function populateTopGrowth() {
    if (!geoBarriosData || !geoBarriosData.features) return;

    let featuresWithGrowth = geoBarriosData.features.filter(f => 
        f.properties.crecimiento_abelardo !== undefined && f.properties.crecimiento_abelardo !== null
    );

    let abelardoBarrios = [];
    let cepedaBarrios = [];
    let totalCrecimientoAbelardo = 0;
    let totalCrecimientoCepeda = 0;

    featuresWithGrowth.forEach(f => {
        const props = f.properties;
        const ca = props.crecimiento_abelardo || 0;
        const cc = props.crecimiento_cepeda || 0;
        const name = props.nombre || 'Desconocido';
        
        if (ca > 0) {
            abelardoBarrios.push({ name: name, growth: ca, v1: props.votos_1v_abelardo, v2: props.votos_2v_abelardo });
            totalCrecimientoAbelardo += ca;
        } else if (ca < 0) {
            totalCrecimientoAbelardo += ca;
        }

        if (cc > 0) {
            cepedaBarrios.push({ name: name, growth: cc, v1: props.votos_1v_cepeda, v2: props.votos_2v_cepeda });
            totalCrecimientoCepeda += cc;
        } else if (cc < 0) {
            totalCrecimientoCepeda += cc;
        }
    });

    // Update Total Summary
    const elTotalAbelardo = document.getElementById('total-growth-abelardo');
    if(elTotalAbelardo) {
        elTotalAbelardo.textContent = (totalCrecimientoAbelardo > 0 ? '+' : '') + Math.round(totalCrecimientoAbelardo).toLocaleString('es-CO') + ' votos netos';
    }
    
    const elTotalCepeda = document.getElementById('total-growth-cepeda');
    if(elTotalCepeda) {
        elTotalCepeda.textContent = (totalCrecimientoCepeda > 0 ? '+' : '') + Math.round(totalCrecimientoCepeda).toLocaleString('es-CO') + ' votos netos';
    }

    abelardoBarrios.sort((a, b) => b.growth - a.growth);
    cepedaBarrios.sort((a, b) => b.growth - a.growth);

    const topA = abelardoBarrios.slice(0, 10);
    const topC = cepedaBarrios.slice(0, 10);

    const renderList = (list, color, textcolor) => {
        if (list.length === 0) return '<div style="padding: 8px; color: var(--text-secondary);">Sin datos.</div>';
        
        const maxGrowth = list[0].growth; // For progress bar
        
        return list.map((item, index) => {
            const percentage = Math.max(5, (item.growth / maxGrowth) * 100);
            return `
            <div style="margin-bottom: 12px; background: rgba(255,255,255,0.04); padding: 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px;">
                    <div>
                        <strong style="color: #f8fafc; font-size: 14px; display: flex; align-items: center; gap: 6px;">
                            <span style="background: ${color}; color: white; width: 20px; height: 20px; display: inline-flex; align-items: center; justify-content: center; border-radius: 50%; font-size: 11px;">${index + 1}</span> 
                            ${item.name}
                        </strong>
                    </div>
                    <div style="text-align: right;">
                        <span style="color: ${textcolor}; font-weight: 900; font-size: 16px; display: block;">+${Math.round(item.growth).toLocaleString('es-CO')}</span>
                        <span style="font-size: 10px; color: #94a3b8; text-transform: uppercase; font-weight: 600;">Votos Nuevos</span>
                    </div>
                </div>
                <div style="display: flex; gap: 10px; margin-bottom: 10px; font-size: 11px; background: rgba(0,0,0,0.2); padding: 6px; border-radius: 6px;">
                    <div style="flex: 1; text-align: center;">
                        <div style="color: #64748b; margin-bottom: 2px;">1ra Vuelta</div>
                        <strong style="color: #cbd5e1;">${formatNumber(item.v1)}</strong>
                    </div>
                    <div style="display: flex; align-items: center; color: ${color};">➔</div>
                    <div style="flex: 1; text-align: center;">
                        <div style="color: #64748b; margin-bottom: 2px;">2da Vuelta</div>
                        <strong style="color: white;">${formatNumber(item.v2)}</strong>
                    </div>
                </div>
                <div style="width: 100%; background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;">
                    <div style="width: ${percentage}%; background: ${color}; height: 100%; border-radius: 3px;"></div>
                </div>
            </div>`;
        }).join('');
    };

    const containerA = document.getElementById('top-growth-abelardo');
    if (containerA) containerA.innerHTML = renderList(topA, '#9333ea', '#c084fc'); 

    const containerC = document.getElementById('top-growth-cepeda');
    if (containerC) containerC.innerHTML = renderList(topC, '#ea580c', '#fb923c'); 
}


// Render Comparative Card 1v vs 2v
function renderComparativeCard2v(muniName = null, zoneName = null, postId = null, tableName = null) {
    const card = document.getElementById('comparative-card-2v');
    if (!card) return;
    
    let stats1v = { abelardo: 0, cepeda: 0, total: 0 };
    let stats2v = { abelardo: 0, cepeda: 0, total: 0 };
    let subtitle = '';
    
    let candIdxEspriella = electoralData.candidates.indexOf("ABELARDO DE LA ESPRIELLA");
    let candIdxPaloma = electoralData.candidates.indexOf("PALOMA VALENCIA LASERNA");
    let candIdxCepeda = electoralData.candidates.indexOf("IVÁN CEPEDA CASTRO");

    function processTable(tableVotes1v, tableVotes2v) {
        if (tableVotes1v) {
            stats1v.abelardo += (tableVotes1v[candIdxEspriella] || 0) + (tableVotes1v[candIdxPaloma] || 0);
            stats1v.cepeda += tableVotes1v[candIdxCepeda] || 0;
            stats1v.total += tableVotes1v.reduce((a, b) => a + b, 0);
        }
        if (tableVotes2v) {
            stats2v.abelardo += tableVotes2v['ABELARDO DE LA ESPRIELLA'] || 0;
            stats2v.cepeda += tableVotes2v['IVÁN CEPEDA CASTRO'] || 0;
            stats2v.total += Object.values(tableVotes2v).reduce((a, b) => a + b, 0);
        }
    }

    if (muniName && zoneName && postId && tableName) {
        subtitle = `Mesa: ${tableName} | Puesto: ${electoralData.hierarchy[muniName][zoneName][postId].name}`;
        let postInfo = electoralData.hierarchy[muniName][zoneName][postId];
        let t1v = postInfo.tables[tableName];
        let tPad = tableName.padStart(3, '0');
        let t2v = postInfo.tables_2v ? postInfo.tables_2v[tPad] : null;
        processTable(t1v, t2v);
    } else if (muniName && zoneName && postId) {
        subtitle = `Puesto: ${electoralData.hierarchy[muniName][zoneName][postId].name}`;
        let postInfo = electoralData.hierarchy[muniName][zoneName][postId];
        Object.keys(postInfo.tables).forEach(t => {
            let t1v = postInfo.tables[t];
            let tPad = t.padStart(3, '0');
            let t2v = postInfo.tables_2v ? postInfo.tables_2v[tPad] : null;
            processTable(t1v, t2v);
        });
    } else if (muniName && muniName !== "TODOS") {
        subtitle = `Municipio: ${muniName}`;
        let muniData = electoralData.hierarchy[muniName];
        Object.values(muniData).forEach(zonePosts => {
            Object.values(zonePosts).forEach(postInfo => {
                Object.keys(postInfo.tables).forEach(t => {
                    let t1v = postInfo.tables[t];
                    let tPad = t.padStart(3, '0');
                    let t2v = postInfo.tables_2v ? postInfo.tables_2v[tPad] : null;
                    processTable(t1v, t2v);
                });
            });
        });
    } else {
        subtitle = "Medellín (Global)";
        let mData = electoralData.hierarchy["MEDELLIN"];
        if(mData) {
          Object.values(mData).forEach(zones => {
            Object.values(zones).forEach(posts => {
                Object.values(posts).forEach(postInfo => {
                    Object.keys(postInfo.tables).forEach(t => {
                        let t1v = postInfo.tables[t];
                        let tPad = t.padStart(3, '0');
                        let t2v = postInfo.tables_2v ? postInfo.tables_2v[tPad] : null;
                        processTable(t1v, t2v);
                    });
                });
            });
          });
        }
    }

    if (stats1v.total === 0 && stats2v.total === 0) {
        card.style.display = 'none';
        return;
    }
    
    card.style.display = 'block';
    const headerTitle = card.querySelector('#comp-2v-subtitle');
    if (headerTitle) {
        headerTitle.innerText = subtitle;
    }
    
    let pctAbe1v = stats1v.total > 0 ? (stats1v.abelardo / stats1v.total * 100) : 0;
    let pctCep1v = stats1v.total > 0 ? (stats1v.cepeda / stats1v.total * 100) : 0;
    let pctAbe2v = stats2v.total > 0 ? (stats2v.abelardo / stats2v.total * 100) : 0;
    let pctCep2v = stats2v.total > 0 ? (stats2v.cepeda / stats2v.total * 100) : 0;
    
    document.getElementById('comp-1v-total').innerText = `Participación: ${formatNumber(stats1v.total)}`;
    document.getElementById('comp-2v-total').innerText = `Participación: ${formatNumber(stats2v.total)}`;

    function getDeltaBadge(delta) {
        if (delta > 0) return `<span style="background:#dcfce7; color:#166534; padding:2px 6px; border-radius:12px; font-size:11px; font-weight:700; margin-left:6px; display:inline-flex; align-items:center; vertical-align: middle;">↑ ${Math.abs(delta).toFixed(1)}%</span>`;
        if (delta < 0) return `<span style="background:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:12px; font-size:11px; font-weight:700; margin-left:6px; display:inline-flex; align-items:center; vertical-align: middle;">↓ ${Math.abs(delta).toFixed(1)}%</span>`;
        return `<span style="background:#f1f5f9; color:#475569; padding:2px 6px; border-radius:12px; font-size:11px; font-weight:700; margin-left:6px; display:inline-flex; align-items:center; vertical-align: middle;">= 0.0%</span>`;
    }

    document.getElementById('comp-1v-abelardo').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Abelardo</div>
        <div style="display:flex; justify-content:center; align-items:baseline; margin:4px 0;">
            <span style="font-size:22px; font-weight:800; color:#0284c7;">${pctAbe1v.toFixed(1)}%</span>
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(stats1v.abelardo)} de ${formatNumber(stats1v.total)})</div>
    `;
    
    document.getElementById('comp-1v-cepeda').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Cepeda</div>
        <div style="display:flex; justify-content:center; align-items:baseline; margin:4px 0;">
            <span style="font-size:22px; font-weight:800; color:#ea580c;">${pctCep1v.toFixed(1)}%</span>
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(stats1v.cepeda)} de ${formatNumber(stats1v.total)})</div>
    `;

    document.getElementById('comp-2v-abelardo').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Abelardo</div>
        <div style="display:flex; justify-content:center; align-items:baseline; margin:4px 0;">
            <span style="font-size:22px; font-weight:800; color:#0284c7;">${pctAbe2v.toFixed(1)}%</span>
            ${getDeltaBadge(pctAbe2v - pctAbe1v)}
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(stats2v.abelardo)} de ${formatNumber(stats2v.total)})</div>
    `;
    
    document.getElementById('comp-2v-cepeda').innerHTML = `
        <div style="font-size:11px; color:var(--text-secondary); text-transform:uppercase; letter-spacing:0.5px; font-weight:600;">Cepeda</div>
        <div style="display:flex; justify-content:center; align-items:baseline; margin:4px 0;">
            <span style="font-size:22px; font-weight:800; color:#ea580c;">${pctCep2v.toFixed(1)}%</span>
            ${getDeltaBadge(pctCep2v - pctCep1v)}
        </div>
        <div style="font-size:11px; color:var(--text-secondary);">(${formatNumber(stats2v.cepeda)} de ${formatNumber(stats2v.total)})</div>
    `;

    const summaryEl = document.getElementById('comp-2v-shift-summary');
    const expEl = document.getElementById('comp-2v-shift-explanation');
    
    if (stats2v.total > 0) {
        let diffAbe = stats2v.abelardo - stats1v.abelardo;
        let diffCep = stats2v.cepeda - stats1v.cepeda;
        
        summaryEl.innerText = `Crecimiento (1v -> 2v)`;
        summaryEl.style.color = '#334155';
        expEl.innerHTML = `Abelardo sumó <strong style="color:#0284c7;">${diffAbe > 0 ? '+' : ''}${formatNumber(diffAbe)}</strong> votos.<br>
                           Cepeda sumó <strong style="color:#ea580c;">${diffCep > 0 ? '+' : ''}${formatNumber(diffCep)}</strong> votos.<br>
                           Participación: <strong style="color:#64748b;">${stats2v.total > stats1v.total ? '+' : ''}${formatNumber(stats2v.total - stats1v.total)}</strong> votos.`;
    } else {
        summaryEl.innerText = "Sin datos en Segunda Vuelta";
        expEl.innerHTML = "No se ha cargado información de la segunda vuelta para este nivel.";
    }
}

function downloadGrowthAnalysis() {
    const appWrapper = document.querySelector('.main-content') || document.body;
    let tempWatermark = document.getElementById('temp-watermark');
    
    if (!tempWatermark) {
        tempWatermark = document.createElement('div');
        tempWatermark.id = 'temp-watermark';
        tempWatermark.style.cssText = `
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(15, 23, 42, 0.9);
            color: white;
            padding: 16px 32px;
            border-radius: 12px;
            z-index: 9999;
            font-size: 18px;
            font-weight: bold;
            border: 2px solid #3b82f6;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            text-align: center;
            width: max-content;
            backdrop-filter: blur(4px);
        `;
        tempWatermark.innerHTML = `
            📊 Análisis de Segunda Vuelta (Crecimiento)<br>
            <span style="font-size: 15px; font-weight: normal; color: #94a3b8; margin-top: 4px; display: block;">
                Aplicación creada por <strong>John Alexander Echeverry Ocampo</strong><br>
                Politólogo y analista de datos
            </span>
        `;
        appWrapper.appendChild(tempWatermark);
    }
    
    // Hide buttons to make it cleaner
    const dlBtns = document.querySelectorAll('button');
    const hiddenBtns = [];
    dlBtns.forEach(btn => {
        if(btn.style.display !== 'none') {
            hiddenBtns.push(btn);
            btn.style.display = 'none';
        }
    });

    html2canvas(appWrapper, {
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#0f172a',
        scale: 2 // High resolution
    }).then(canvas => {
        // Restore buttons
        hiddenBtns.forEach(btn => {
            btn.style.display = '';
        });
        // Remove temporary watermark
        if (tempWatermark && tempWatermark.parentNode) {
            tempWatermark.parentNode.removeChild(tempWatermark);
        }
        
        // Trigger download
        const link = document.createElement('a');
        link.download = 'Infografia_Crecimiento_2v_Medellin.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    }).catch(err => {
        console.error("Error al generar la imagen", err);
        alert("Hubo un error al generar la imagen infográfica.");
        // Restore buttons
        hiddenBtns.forEach(btn => {
            btn.style.display = '';
        });
        if (tempWatermark && tempWatermark.parentNode) {
            tempWatermark.parentNode.removeChild(tempWatermark);
        }
    });
}
