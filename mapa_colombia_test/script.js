// Inicializar el mapa (los límites se ajustarán automáticamente al cargar los datos)
const map = L.map('map');

// Agregar la capa de mapa base (OpenStreetMap)
// L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//     maxZoom: 18,
//     attribution: '© OpenStreetMap contributors'
// }).addTo(map);

// Estilo por defecto para los departamentos
function style(feature) {
    let weight = 2;
    let color = '#2c3e50';
    let fillColor = '#3498db';
    let fillOpacity = 0.5;
    
    // Resaltar San Andrés
    if (feature.properties && feature.properties.DPTO_CNMBR && feature.properties.DPTO_CNMBR.includes('SAN ANDR')) {
        weight = 3;
        color = '#e74c3c';
        fillOpacity = 0.8;
    }

    return {
        fillColor: fillColor,
        weight: weight,
        opacity: 1,
        color: color,
        fillOpacity: fillOpacity
    };
}

// Estilo cuando se pasa el mouse por encima (hover)
function highlightFeature(e) {
    const layer = e.target;
    layer.setStyle({
        fillColor: '#e74c3c', // Color de resalte rojo
        weight: 2,
        color: '#fff',
        fillOpacity: 0.8
    });
    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
}

// Restaurar el estilo original
function resetHighlight(e) {
    geojsonLayer.resetStyle(e.target);
}

// Variables de UI
const offcanvas = document.getElementById('info-panel');
const closeBtn = document.getElementById('close-btn');
const deptTitle = document.getElementById('dept-title');
const politicosList = document.getElementById('politicos-list');
const politicoDetail = document.getElementById('politico-detail');
const tabBtns = document.querySelectorAll('.tab-btn');
const backBtn = document.getElementById('back-btn');

let datosActuales = null;
let tabActual = 'senadores';

// Cierra el panel
closeBtn.addEventListener('click', () => {
    offcanvas.classList.remove('open');
});

// Volver a la lista
backBtn.addEventListener('click', () => {
    politicoDetail.classList.add('hidden');
    politicoDetail.style.display = 'none';
    
    politicosList.classList.remove('hidden');
    politicosList.style.display = 'flex';
});

// Cambiar pestañas
tabBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
        tabBtns.forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        tabActual = e.target.getAttribute('data-tab');
        
        // Volver a la lista y renderizar
        politicoDetail.classList.add('hidden');
        politicoDetail.style.display = 'none';
        
        politicosList.classList.remove('hidden');
        politicosList.style.display = 'flex';
        renderizarLista();
    });
});

function getLogoForPartido(partido) {
    if (!partido) return null;
    const p = partido.toLowerCase();
    
    if (p.includes('pacto histórico') || p.includes('pacto historico')) {
        return 'Logos parditos/Pacto_historico.png';
    }
    if (p.includes('centro democrático') || p.includes('centro democratico')) {
        return 'Logos parditos/Centro_Democrático.png';
    }
    if (p.includes('conservador')) {
        return 'Logos parditos/Partido_Conservador_Colombiano.png';
    }
    if (p.includes('liberal') && !p.includes('nuevo liberalismo')) {
        return 'Logos parditos/Partido_Liberal_Colombiano.png';
    }
    if (p.includes('cambio radical')) {
        return 'Logos parditos/Cambio_Radical.png';
    }
    if (p.includes('partido de la u') || p === 'de la u') {
        return 'Logos parditos/Logo_Partido_U_Colombia.png';
    }
    if (p.includes('salvación nacional') || p.includes('salvacion nacional')) {
        return 'Logos parditos/Movimiento_de_Salvación_Nacional_2026.png';
    }
    if (p.includes('ahora colombia') || p.includes('nuevo liberalismo') || p.includes('dignidad y compromiso') || p.includes('mira')) {
        return 'Logos parditos/Coalicion-Ahora-Mira-Nuevo-Liberalismo-Dignidad-y-compromiso.jpg';
    }
    if (p.includes('alianza por colombia') || p.includes('alianza por casanare') || p.includes('alianza verde')) {
        return 'Logos parditos/Alianza_por_Colombia.png';
    }
    if (p.includes('aico')) {
        return 'Logos parditos/AICO.png';
    }
    if (p.includes('creemos')) {
        return 'Logos parditos/creemos.png';
    }
    if (p.includes('mais')) {
        return 'Logos parditos/MAIS.png';
    }
    if (p.includes('minga por colombia')) {
        return 'Logos parditos/Minga por Colombia.png';
    }
    if (p.includes('asi') || p.includes('alianza social independiente')) {
        return 'Logos parditos/Alianza-social-independiente.png';
    }
    if (p.includes('la fuerza')) {
        return 'Logos parditos/Partido_Fuerza_de_La_Paz.png';
    }
    if (p.includes('avancemos nariño') || p.includes('avancemos narino')) {
        return 'Logos parditos/Avancemos-nariño.png';
    }
    if (p.includes('liga de gobernantes')) {
        return 'Logos parditos/Liga de Gobernantes.png';
    }
    
    // Fallback para cualquier otra coalición o la coalición Caquetá
    if (p.includes('coalición') || p.includes('coalicion')) {
        return 'Logos parditos/Coalicion Caqueta.png';
    }
    
    return null;
}

// Renderiza la lista de políticos
function renderizarLista() {
    politicosList.innerHTML = '';
    
    if (!datosActuales || !datosActuales[tabActual] || datosActuales[tabActual].length === 0) {
        politicosList.innerHTML = '<p>No hay datos disponibles para este departamento.</p>';
        return;
    }

    datosActuales[tabActual].forEach(politico => {
        const item = document.createElement('div');
        item.className = 'politico-item';
        
        const logoUrl = getLogoForPartido(politico.partido);
        let logoHtml = '';
        if (logoUrl) {
            logoHtml = `<img src="${logoUrl}" alt="Logo" class="logo-partido-small" />`;
        }
        
        item.innerHTML = `<div class="politico-name-container">${logoHtml}<h4>${politico.nombre}</h4></div> <i class="fa-solid fa-chevron-right"></i>`;
        
        item.addEventListener('click', () => {
            mostrarDetalle(politico);
        });
        
        politicosList.appendChild(item);
    });
}

// Muestra la tarjeta de detalle de un político
function mostrarDetalle(politico) {
    politicosList.classList.add('hidden');
    politicosList.style.display = 'none'; // Forzar ocultado vía inline CSS
    
    politicoDetail.classList.remove('hidden');
    politicoDetail.style.display = 'block'; // Forzar mostrado vía inline CSS
    
    // Auto-scroll al inicio del panel para que la tarjeta sea visible inmediatamente
    offcanvas.scrollTop = 0;
    
    document.getElementById('pol-nombre').textContent = politico.nombre;
    document.getElementById('pol-partido').textContent = politico.partido;
    
    // Si no es "N/A", mostrar votos, si no, ocultar
    const votosContainer = document.getElementById('pol-votos-container');
    if (politico.votos && politico.votos !== 'N/A') {
        document.getElementById('pol-votos').textContent = politico.votos;
        votosContainer.style.display = 'block';
    } else {
        votosContainer.style.display = 'none';
    }
    
    // Datos adicionales para los senadores
    const extraInfo = document.getElementById('pol-extra-info');
    if (politico.profesion || politico.trayectoria || politico.estatus) {
        document.getElementById('pol-profesion').textContent = politico.profesion || 'No registra';
        document.getElementById('pol-estatus').textContent = politico.estatus || 'No registra';
        document.getElementById('pol-trayectoria').textContent = politico.trayectoria || 'No registra';
        extraInfo.style.display = 'block';
    } else {
        extraInfo.style.display = 'none';
    }
    
    // Configurar foto
    const imgEl = document.getElementById('pol-foto');
    imgEl.src = politico.foto_path;
    // Si la imagen no carga, poner un placeholder
    imgEl.onerror = () => {
        imgEl.src = 'https://via.placeholder.com/400x400.png?text=Sin+Foto';
    };
}

// Evento al hacer click en un departamento
function clickDepartamento(e) {
    const layer = e.target;
    const nombreDepto = layer.feature.properties.DPTO_CNMBR;
    
    // Zoom al departamento
    map.fitBounds(layer.getBounds(), { padding: [50, 50] });
    
    // Actualizar UI
    deptTitle.textContent = nombreDepto;
    
    // Obtener datos (usando la función del archivo datos_politicos.js)
    if (typeof obtenerPoliticos === 'function') {
        datosActuales = obtenerPoliticos(nombreDepto);
        
        // Actualizar el texto de las pestañas con las cantidades
        const btnSenadores = document.querySelector('.tab-btn[data-tab="senadores"]');
        const btnRepresentantes = document.querySelector('.tab-btn[data-tab="representantes"]');
        
        if (btnSenadores && datosActuales.senadores) {
            btnSenadores.textContent = `Senadores (${datosActuales.senadores.length})`;
        }
        if (btnRepresentantes && datosActuales.representantes) {
            btnRepresentantes.textContent = `Representantes (${datosActuales.representantes.length})`;
        }
    }
    
    // Asegurar que volvemos a la vista de lista
    politicoDetail.classList.add('hidden');
    politicoDetail.style.display = 'none';
    
    politicosList.classList.remove('hidden');
    politicosList.style.display = 'flex';
    
    renderizarLista();
    offcanvas.classList.add('open');
}

// Agregar interacciones a cada departamento
function onEachFeature(feature, layer) {
    if (feature.properties && feature.properties.DPTO_CNMBR) {
        layer.bindTooltip(feature.properties.DPTO_CNMBR, {
            sticky: true,
            className: 'departamento-tooltip'
        });
    }

    layer.on({
        mouseover: highlightFeature,
        mouseout: resetHighlight,
        click: clickDepartamento
    });
}

let geojsonLayer;

// Cargar el archivo GeoJSON desde la variable cargada en el HTML
geojsonLayer = L.geoJSON(colombiaGeoJSON, {
    style: style,
    onEachFeature: onEachFeature
}).addTo(map);

// Centrar y ajustar el mapa exactamente a los límites de Colombia (responsive)
map.fitBounds(geojsonLayer.getBounds());

// Agregar nombres de los departamentos en el mapa
function addLabels() {
    const smallDeptsConfig = {
        'ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA': { offsetLat: 1.5, offsetLng: 2, name: "San Andrés" },
        'QUINDIO': { offsetLat: 0, offsetLng: -2.5, name: "Quindío" },
        'RISARALDA': { offsetLat: 0.8, offsetLng: -2.5, name: "Risaralda" },
        'CALDAS': { offsetLat: 1.5, offsetLng: -2.2, name: "Caldas" },
        'ATLÁNTICO': { offsetLat: 1.5, offsetLng: -1.5, name: "Atlántico" },
        'SUCRE': { offsetLat: 1.5, offsetLng: -2.5, name: "Sucre" },
        'BOGOTÁ, D.C.': { offsetLat: -0.5, offsetLng: 2.5, name: "Bogotá" }
    };

    geojsonLayer.eachLayer(layer => {
        if (!layer.feature.properties || !layer.feature.properties.DPTO_CNMBR) return;
        
        let dptoName = layer.feature.properties.DPTO_CNMBR;
        let bounds = layer.getBounds();
        let center = bounds.getCenter();
        let displayLatLng = center;
        let displayName = dptoName;
        
        // Simplificar nombres muy largos para que quepan mejor
        if (dptoName === 'VALLE DEL CAUCA') displayName = "Valle del<br>Cauca";
        else if (dptoName === 'NORTE DE SANTANDER') displayName = "Norte de<br>Santander";
        else if (dptoName === 'LA GUAJIRA') displayName = "La Guajira";
        else if (dptoName === 'CUNDINAMARCA') displayName = "Cundinamarca";
        else if (dptoName === 'ANTIOQUIA') displayName = "Antioquia";
        // Si no es un caso especial, usar modo capitalizado simple
        else displayName = dptoName.charAt(0) + dptoName.slice(1).toLowerCase();
        
        let isSmall = smallDeptsConfig[dptoName];
        
        if (isSmall) {
            displayLatLng = L.latLng(center.lat + isSmall.offsetLat, center.lng + isSmall.offsetLng);
            displayName = isSmall.name;
            
            // Dibujar conector
            L.polyline([center, displayLatLng], {
                color: '#2c3e50',
                weight: 1.5,
                dashArray: '4, 4',
                opacity: 0.8,
                interactive: false
            }).addTo(map);
        }
        
        // Crear el icono de texto
        let icon = L.divIcon({
            className: 'dpto-label-icon',
            html: `<div class="dpto-label-text ${isSmall ? 'small-dpto' : ''}">${displayName}</div>`,
            iconSize: [0, 0], // Tamaño cero, el css controlará la expansión y centrado
            iconAnchor: [0, 0] // El centrado se hará con transform: translate(-50%, -50%)
        });
        
        L.marker(displayLatLng, {
            icon: icon,
            interactive: false // Para no bloquear clics al polígono
        }).addTo(map);
    });
}

// Llamar la función
addLabels();

// Lógica para Rankings
const btnSenado = document.getElementById('btn-ranking-senado');
const btnCamara = document.getElementById('btn-ranking-camara');
const rankingPanel = document.getElementById('ranking-panel');
const btnCloseRanking = document.getElementById('close-ranking-btn');
const rankingList = document.getElementById('ranking-list');
const rankingTitle = document.getElementById('ranking-title');

function mostrarRanking(tipo) {
    rankingPanel.classList.remove('hidden');
    rankingList.innerHTML = '';
    
    if (tipo === 'senado') {
        rankingTitle.innerHTML = '<i class="fa-solid fa-landmark"></i> Ranking Senado';
        btnSenado.classList.add('active');
        btnCamara.classList.remove('active');
    } else {
        rankingTitle.innerHTML = '<i class="fa-solid fa-users"></i> Ranking Cámara';
        btnCamara.classList.add('active');
        btnSenado.classList.remove('active');
    }

    const conteos = [];
    const normalizar = (texto) => texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    
    geojsonLayer.eachLayer(layer => {
        const nombreDepto = layer.feature.properties.DPTO_CNMBR;
        const depNormalizado = normalizar(nombreDepto);
        let cantidad = 0;
        
        if (tipo === 'senado') {
            let depMatchSen = Object.keys(window.senadoresPorDepartamento || {}).find(k => {
                let excelDep = normalizar(k).replace(/_/g, ' ');
                return excelDep === depNormalizado || 
                       (depNormalizado.includes("bogota") && excelDep.includes("bogota")) ||
                       (depNormalizado.includes("san andres") && excelDep.includes("san andres")) ||
                       (depNormalizado.includes("valle") && excelDep.includes("valle"));
            });
            if (depMatchSen && window.senadoresPorDepartamento[depMatchSen]) {
                // Contar todos los senadores de este departamento
                cantidad = window.senadoresPorDepartamento[depMatchSen].filter(s => !s.nombre.includes('No hay datos')).length;
            }
        } else {
            let depMatch = Object.keys(window.datosReales || {}).find(k => {
                let excelDep = normalizar(k);
                return excelDep === depNormalizado || 
                       (depNormalizado.includes("bogota") && excelDep.includes("bogota")) ||
                       (depNormalizado.includes("san andres") && excelDep.includes("san andres")) ||
                       (depNormalizado.includes("valle") && excelDep.includes("valle"));
            });
            if (depMatch && window.datosReales[depMatch]) {
                // Contar representantes
                cantidad = window.datosReales[depMatch].filter(r => !r.nombre.includes('No hay datos')).length;
            }
        }
        
        // Agregar siempre, incluso si es 0, para mostrar todos los departamentos
        conteos.push({ depto: nombreDepto, cantidad: cantidad, layer: layer });
    });

    // Ordenar de mayor a menor cantidad
    // Si hay empate en cantidad, ordenar alfabéticamente por nombre de departamento para mejor presentación
    conteos.sort((a, b) => {
        if (b.cantidad !== a.cantidad) {
            return b.cantidad - a.cantidad;
        }
        return a.depto.localeCompare(b.depto);
    });

    if (conteos.length === 0) {
        rankingList.innerHTML = '<p style="padding:15px; color:#7f8c8d;">No hay datos para mostrar.</p>';
        return;
    }

    conteos.forEach((item, index) => {
        const div = document.createElement('div');
        div.className = 'ranking-item';
        div.innerHTML = `
            <div class="ranking-item-name"><span style="color:#7f8c8d; font-weight:normal; margin-right:5px;">${index + 1}.</span> ${item.depto}</div>
            <div class="ranking-item-count">${item.cantidad}</div>
        `;
        
        // Al hacer clic, simular clic en el mapa
        div.addEventListener('click', () => {
            map.fitBounds(item.layer.getBounds(), { padding: [50, 50] });
            item.layer.fire('click');
        });
        
        rankingList.appendChild(div);
    });
}

if (btnSenado) btnSenado.addEventListener('click', () => mostrarRanking('senado'));
if (btnCamara) btnCamara.addEventListener('click', () => mostrarRanking('camara'));

if (btnCloseRanking) {
    btnCloseRanking.addEventListener('click', () => {
        rankingPanel.classList.add('hidden');
        btnSenado.classList.remove('active');
        btnCamara.classList.remove('active');
    });
}
