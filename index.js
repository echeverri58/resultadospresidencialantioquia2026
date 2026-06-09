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
        subdomains: 'abcd'
    }).addTo(map);

    postsLayer = L.layerGroup().addTo(map);
}

// Load App Data
async function loadData() {
    try {
        const [electoralRes, geojsonRes, barriosRes] = await Promise.all([
            fetch('electoral_data.json'),
            fetch('medellin.geojson'),
            fetch('barrios_resultados.geojson')
        ]);
        
        electoralData = await electoralRes.json();
        geojsonData = await geojsonRes.json();
        geoBarriosData = await barriosRes.json();
        
        // Render general results
        renderMedellinGeneralResults();
        renderComparativeCard();
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
            const winner = feature.properties.winner;
            let color = defaultColor;
            let opacity = 0.2;
            
            if (winner && winner !== 'Sin Datos' && feature.properties.results && feature.properties.results.length > 0) {
                color = getCandidateColor(winner);
                const pct = feature.properties.results[0].pct;
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
            const nombre = feature.properties.nombre || "Sin Nombre";
            const winner = feature.properties.winner;
            
            let popupContent = `<h3>${nombre}</h3>`;
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
    });
}

// Switch Tabs
function switchTab(tab) {
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
    
    return {
        winner: winnerName,
        winnerPct: winnerPct,
        totalVotes: totalVotes
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
    
    document.getElementById('comp-2022-total').innerText = `Total Votantes: ${formatNumber(stats2022.TOTAL)}`;
    document.getElementById('comp-2026-total').innerText = `Total Votantes: ${formatNumber(stats2026.total)}`;

    document.getElementById('comp-2022-der').innerHTML = `Fico + Rodolfo: ${pctFico2022.toFixed(1)}% <br><span style="font-size: 11px; font-weight: normal; color: var(--text-secondary);">(${formatNumber(stats2022.FICO)} de ${formatNumber(stats2022.TOTAL)} votos)</span>`;
    document.getElementById('comp-2022-izq').innerHTML = `Petro: ${pctPetro2022.toFixed(1)}% <br><span style="font-size: 11px; font-weight: normal; color: var(--text-secondary);">(${formatNumber(stats2022.PETRO)} de ${formatNumber(stats2022.TOTAL)} votos)</span>`;
    document.getElementById('comp-2022-otros').innerHTML = `Otros/Blanco: ${pctOtros2022.toFixed(1)}% <br><span style="font-size: 11px; font-weight: normal; color: var(--text-secondary);">(${formatNumber(otros2022)} de ${formatNumber(stats2022.TOTAL)} votos)</span>`;
    
    document.getElementById('comp-2026-der').innerHTML = `De La Espriella + Paloma: ${pctEspriella2026.toFixed(1)}% <br><span style="font-size: 11px; font-weight: normal; color: var(--text-secondary);">(${formatNumber(stats2026.fico)} de ${formatNumber(stats2026.total)} votos)</span>`;
    document.getElementById('comp-2026-izq').innerHTML = `Cepeda: ${pctCepeda2026.toFixed(1)}% <br><span style="font-size: 11px; font-weight: normal; color: var(--text-secondary);">(${formatNumber(stats2026.petro)} de ${formatNumber(stats2026.total)} votos)</span>`;
    document.getElementById('comp-2026-otros').innerHTML = `Otros/Blanco: ${pctOtros2026.toFixed(1)}% <br><span style="font-size: 11px; font-weight: normal; color: var(--text-secondary);">(${formatNumber(otros2026)} de ${formatNumber(stats2026.total)} votos)</span>`;
    
    const margin2022 = pctFico2022 - pctPetro2022;
    const margin2026 = pctEspriella2026 - pctCepeda2026;
    const shift = margin2026 - margin2022;
    
    let shiftText = '';
    if (shift > 0) {
        shiftText = `El margen de la derecha creció <strong>+${shift.toFixed(1)}%</strong> frente a 2022.`;
    } else {
        shiftText = `El margen de la izquierda creció <strong>+${Math.abs(shift).toFixed(1)}%</strong> frente a 2022.`;
    }
    
    document.getElementById('comp-shift-summary').innerHTML = shiftText;
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
                
                const popupContent = `
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif;">
                        <h3 style="margin:0 0 5px 0; font-size: 14px; font-weight:700; color:#0f172a;">${postInfo.name}</h3>
                        <p style="margin:0 0 3px 0; font-size:11px; color:#475569;">${zoneName} | ${muniName}</p>
                        <p style="margin:0; font-size:12px; color:#0f172a;">Ganador: <strong style="color:${winnerColor};">${summary.winner}</strong> (${summary.winnerPct.toFixed(2)}%)</p>
                        <p style="margin:0; font-size:11px; color:#64748b;">Votos Totales: ${formatNumber(summary.totalVotes)}</p>
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
    
    Object.values(electoralData.hierarchy).forEach(zones => {
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
}

// Initial triggers
initMap();
loadData();
