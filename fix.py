import sys

with open('index.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '// Render Comparative Card 1v vs 2v' in line:
        break
    new_lines.append(line)

card_2v_func = r'''
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
        let t2v = postInfo.tables_2v ? postInfo.tables_2v[tableName] : null;
        processTable(t1v, t2v);
    } else if (muniName && zoneName && postId) {
        subtitle = `Puesto: ${electoralData.hierarchy[muniName][zoneName][postId].name}`;
        let postInfo = electoralData.hierarchy[muniName][zoneName][postId];
        Object.keys(postInfo.tables).forEach(t => {
            let t1v = postInfo.tables[t];
            let t2v = postInfo.tables_2v ? postInfo.tables_2v[t] : null;
            processTable(t1v, t2v);
        });
    } else if (muniName && muniName !== "TODOS") {
        subtitle = `Municipio: ${muniName}`;
        let muniData = electoralData.hierarchy[muniName];
        Object.values(muniData).forEach(zonePosts => {
            Object.values(zonePosts).forEach(postInfo => {
                Object.keys(postInfo.tables).forEach(t => {
                    let t1v = postInfo.tables[t];
                    let t2v = postInfo.tables_2v ? postInfo.tables_2v[t] : null;
                    processTable(t1v, t2v);
                });
            });
        });
    } else {
        subtitle = "Medellín (Global)";
        Object.values(electoralData.hierarchy).forEach(zones => {
            Object.values(zones).forEach(posts => {
                Object.values(posts).forEach(postInfo => {
                    Object.keys(postInfo.tables).forEach(t => {
                        let t1v = postInfo.tables[t];
                        let t2v = postInfo.tables_2v ? postInfo.tables_2v[t] : null;
                        processTable(t1v, t2v);
                    });
                });
            });
        });
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
'''

new_lines.append(card_2v_func)

with open('index.js', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done!')
