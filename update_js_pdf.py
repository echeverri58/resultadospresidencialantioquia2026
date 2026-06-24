import re

with open('index.js', 'r', encoding='utf-8') as f:
    js = f.read()

new_func = '''function downloadGrowthAnalysis(event, format = 'png') {
    const originalBtn = event.currentTarget;
    const originalText = originalBtn.innerHTML;
    originalBtn.innerHTML = "⏳ Generando " + format.toUpperCase() + "...";
    originalBtn.disabled = true;

    // 1. Capture the map first
    const mapWrapper = document.querySelector('.map-wrapper');
    
    html2canvas(mapWrapper, {
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#0f172a'
    }).then(mapCanvas => {
        // 2. Create the infographic container off-screen
        const snapshotDiv = document.createElement('div');
        snapshotDiv.id = 'infographic-export';
        snapshotDiv.style.cssText = `
            position: absolute;
            top: -50000px;
            left: 0;
            width: 1400px;
            background: #0f172a;
            padding: 40px;
            color: white;
            font-family: 'Inter', sans-serif;
            z-index: -1;
        `;
        
        let tableRowsA = '';
        let tableRowsC = '';
        const maxLen = Math.max((window.growthTopA || []).length, (window.growthTopC || []).length);
        
        for (let i = 0; i < maxLen; i++) {
            const itemA = (window.growthTopA && window.growthTopA[i]) ? window.growthTopA[i] : null;
            const itemC = (window.growthTopC && window.growthTopC[i]) ? window.growthTopC[i] : null;
            
            const renderCell = (item, color) => {
                if (!item) return `<td style="border: 1px solid rgba(255,255,255,0.1); padding: 8px;"></td>`;
                return `<td style="border: 1px solid rgba(255,255,255,0.1); padding: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: bold; font-size: 14px;">${i+1}. ${item.name}</span>
                        <span style="color: ${color}; font-weight: 900; font-size: 15px;">+${Math.round(item.growth).toLocaleString('es-CO')}</span>
                    </div>
                    <div style="font-size: 11px; color: #94a3b8; margin-top: 4px;">
                        1ra: ${item.v1.toLocaleString('es-CO')} &rarr; 2da: ${item.v2.toLocaleString('es-CO')}
                    </div>
                </td>`;
            };
            
            tableRowsA += renderCell(itemA, '#c084fc');
            tableRowsC += renderCell(itemC, '#fb923c');
        }

        // Add header
        snapshotDiv.innerHTML = `
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="font-size: 36px; margin: 0; color: #f8fafc;">Análisis de Segunda Vuelta (Crecimiento)</h1>
                <p style="font-size: 18px; color: #94a3b8; margin-top: 10px;">Elecciones Presidenciales Antioquia 2026 - Medellín</p>
                <p style="font-size: 14px; color: #64748b; margin-top: 5px;">Aplicación creada por <strong>John Alexander Echeverry</strong>, Politólogo y analista de datos</p>
            </div>
            
            <div id="snapshot-map-container" style="width: 100%; height: auto; border-radius: 12px; overflow: hidden; margin-bottom: 30px; border: 2px solid rgba(255,255,255,0.1);">
            </div>
            
            <div id="snapshot-stats" style="display: flex; gap: 20px; margin-bottom: 30px;">
            </div>
            
            <div id="snapshot-table" style="background: rgba(255,255,255,0.02); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.05);">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th style="width: 50%; color: #9333ea; font-size: 18px; text-align: left; padding: 12px; border-bottom: 2px solid #9333ea;">⬆️ Top Crecimiento Abelardo</th>
                            <th style="width: 50%; color: #ea580c; font-size: 18px; text-align: left; padding: 12px; border-bottom: 2px solid #ea580c;">⬆️ Top Crecimiento Cepeda</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="vertical-align: top; padding: 0;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    ${tableRowsA.replace(/<td /g, '<tr><td ').replace(/<\/td>/g, '</td></tr>')}
                                </table>
                            </td>
                            <td style="vertical-align: top; padding: 0;">
                                <table style="width: 100%; border-collapse: collapse;">
                                    ${tableRowsC.replace(/<td /g, '<tr><td ').replace(/<\/td>/g, '</td></tr>')}
                                </table>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        `;
        
        document.body.appendChild(snapshotDiv);
        
        // Append map image
        const mapImg = document.createElement('img');
        mapImg.src = mapCanvas.toDataURL('image/png');
        mapImg.style.width = '100%';
        mapImg.style.display = 'block';
        document.getElementById('snapshot-map-container').appendChild(mapImg);
        
        // Clone stats
        const statA = document.getElementById('growth-summary-abelardo').cloneNode(true);
        const statC = document.getElementById('growth-summary-cepeda').cloneNode(true);
        statA.style.flex = '1';
        statC.style.flex = '1';
        document.getElementById('snapshot-stats').appendChild(statA);
        document.getElementById('snapshot-stats').appendChild(statC);
        
        // Now capture the whole infographic
        html2canvas(snapshotDiv, {
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#0f172a',
            scale: format === 'pdf' ? 1.5 : 2
        }).then(finalCanvas => {
            if (format === 'pdf') {
                try {
                    const imgData = finalCanvas.toDataURL('image/jpeg', 0.95);
                    const { jsPDF } = window.jspdf;
                    
                    const pdf = new jsPDF({
                        orientation: 'portrait',
                        unit: 'px',
                        format: [finalCanvas.width, finalCanvas.height]
                    });
                    
                    pdf.addImage(imgData, 'JPEG', 0, 0, finalCanvas.width, finalCanvas.height);
                    pdf.save('Infografia_Crecimiento_2v_Medellin.pdf');
                } catch(e) {
                    console.error(e);
                    alert("Error al generar PDF. Verifique que jsPDF esté cargado.");
                }
            } else {
                const link = document.createElement('a');
                link.download = 'Infografia_Crecimiento_2v_Medellin.png';
                link.href = finalCanvas.toDataURL('image/png');
                link.click();
            }
            
            // Cleanup
            document.body.removeChild(snapshotDiv);
            originalBtn.innerHTML = originalText;
            originalBtn.disabled = false;
        }).catch(err => {
            console.error("Error en snapshotDiv", err);
            document.body.removeChild(snapshotDiv);
            originalBtn.innerHTML = originalText;
            originalBtn.disabled = false;
            alert("Error generando infografía.");
        });
        
    }).catch(err => {
        console.error("Error capturando mapa", err);
        originalBtn.innerHTML = originalText;
        originalBtn.disabled = false;
        alert("Error capturando el mapa.");
    });
}'''

js_new = re.sub(r'function downloadGrowthAnalysis\(event\) \{[\s\S]*?\}(?=\n\n\nwindow\.downloadCard2v)', new_func, js)

with open('index.js', 'w', encoding='utf-8') as f:
    f.write(js_new)
