import sys

with open('index.js', 'r', encoding='utf-8') as f:
    js = f.read()

start_sig = 'function downloadGrowthAnalysis(event)'
start_idx = js.find(start_sig)

end_sig = 'window.downloadCard2v = function()'
end_idx = js.find(end_sig, start_idx)

if start_idx == -1 or end_idx == -1:
    print('Could not find bounds')
    sys.exit(1)

# Find the last closing brace before end_idx
func_body_end = js.rfind('}', start_idx, end_idx)

new_func = """function downloadGrowthAnalysis(event, format = 'png') {
    const originalBtn = event.currentTarget;
    const originalText = originalBtn.innerHTML;
    originalBtn.innerHTML = "⏳ Generando...";
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
            background: #ffffff;
            padding: 40px;
            color: #1e293b;
            font-family: 'Inter', sans-serif;
            z-index: -1;
            border-radius: 8px;
        `;
        
        // Formatear tablas a partir de variables globales
        let abelardoRows = '';
        let cepedaRows = '';
        
        if (window.growthTopA && window.growthTopC) {
            window.growthTopA.forEach((item, index) => {
                abelardoRows += `
                <tr style="background-color: ${index % 2 === 0 ? '#f8fafc' : '#ffffff'}; border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 12px; font-weight: bold; color: #475569;">${index + 1}</td>
                    <td style="padding: 12px; color: #0f172a;">${item.name}</td>
                    <td style="padding: 12px; color: #64748b; font-size: 0.9em;">Comuna ${item.commune}</td>
                    <td style="padding: 12px; font-weight: bold; color: #9333ea;">+${item.growth.toFixed(1)}%</td>
                </tr>`;
            });
            window.growthTopC.forEach((item, index) => {
                cepedaRows += `
                <tr style="background-color: ${index % 2 === 0 ? '#f8fafc' : '#ffffff'}; border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 12px; font-weight: bold; color: #475569;">${index + 1}</td>
                    <td style="padding: 12px; color: #0f172a;">${item.name}</td>
                    <td style="padding: 12px; color: #64748b; font-size: 0.9em;">Comuna ${item.commune}</td>
                    <td style="padding: 12px; font-weight: bold; color: #ea580c;">+${item.growth.toFixed(1)}%</td>
                </tr>`;
            });
        }
        
        // Add header and structure
        snapshotDiv.innerHTML = `
            <div style="text-align: center; margin-bottom: 30px; border-bottom: 3px solid #e2e8f0; padding-bottom: 20px;">
                <h1 style="font-size: 38px; margin: 0; color: #0f172a;">Análisis de Segunda Vuelta (Crecimiento)</h1>
                <p style="font-size: 20px; color: #475569; margin-top: 10px;">Elecciones Presidenciales Antioquia 2026 - Medellín</p>
                <p style="font-size: 16px; color: #64748b; margin-top: 5px;">Autor: <strong>John Alexander Echeverry</strong> (Politólogo y analista de datos)</p>
            </div>
            
            <div id="snapshot-map-container" style="width: 100%; height: auto; border-radius: 12px; overflow: hidden; margin-bottom: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            </div>
            
            <div id="snapshot-stats" style="display: flex; gap: 20px; margin-bottom: 30px;">
                <!-- Se clonan los stats generales aqui -->
            </div>
            
            <h2 style="text-align: center; color: #1e293b; margin-bottom: 20px;">Top 20 Barrios de Mayor Crecimiento</h2>
            <div style="display: flex; gap: 40px; width: 100%;">
                <div style="flex: 1; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="background-color: #9333ea; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 18px;">
                        Crecimiento Abelardo
                    </div>
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <thead>
                            <tr style="background-color: #f1f5f9; color: #475569; font-size: 0.9em;">
                                <th style="padding: 12px;">#</th>
                                <th style="padding: 12px;">Barrio</th>
                                <th style="padding: 12px;">Comuna</th>
                                <th style="padding: 12px;">Crecimiento</th>
                            </tr>
                        </thead>
                        <tbody>${abelardoRows}</tbody>
                    </table>
                </div>
                
                <div style="flex: 1; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                    <div style="background-color: #ea580c; color: white; padding: 15px; text-align: center; font-weight: bold; font-size: 18px;">
                        Crecimiento Cepeda
                    </div>
                    <table style="width: 100%; border-collapse: collapse; text-align: left;">
                        <thead>
                            <tr style="background-color: #f1f5f9; color: #475569; font-size: 0.9em;">
                                <th style="padding: 12px;">#</th>
                                <th style="padding: 12px;">Barrio</th>
                                <th style="padding: 12px;">Comuna</th>
                                <th style="padding: 12px;">Crecimiento</th>
                            </tr>
                        </thead>
                        <tbody>${cepedaRows}</tbody>
                    </table>
                </div>
            </div>
        `;
        
        document.body.appendChild(snapshotDiv);
        
        // Append map image
        const mapImg = document.createElement('img');
        mapImg.src = mapCanvas.toDataURL('image/png');
        mapImg.style.width = '100%';
        mapImg.style.display = 'block';
        document.getElementById('snapshot-map-container').appendChild(mapImg);
        
        // Clone stats safely
        const statA = document.getElementById('growth-summary-abelardo');
        const statC = document.getElementById('growth-summary-cepeda');
        if (statA && statC) {
            const cloneA = statA.cloneNode(true);
            const cloneC = statC.cloneNode(true);
            cloneA.style.flex = '1';
            cloneC.style.flex = '1';
            // Ajustar estilos para la infografia blanca
            cloneA.style.border = '1px solid #e2e8f0';
            cloneA.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
            cloneC.style.border = '1px solid #e2e8f0';
            cloneC.style.boxShadow = '0 2px 4px rgba(0,0,0,0.05)';
            document.getElementById('snapshot-stats').appendChild(cloneA);
            document.getElementById('snapshot-stats').appendChild(cloneC);
        }
        
        // Now capture the whole infographic
        html2canvas(snapshotDiv, {
            useCORS: true,
            allowTaint: true,
            backgroundColor: '#ffffff',
            scale: 2
        }).then(finalCanvas => {
            if (format === 'pdf') {
                const imgData = finalCanvas.toDataURL('image/jpeg', 0.95);
                const { jsPDF } = window.jspdf;
                // orientation, unit, format
                // Auto-scale to single page
                const pdf = new jsPDF({
                    orientation: 'portrait',
                    unit: 'px',
                    format: [finalCanvas.width, finalCanvas.height]
                });
                pdf.addImage(imgData, 'JPEG', 0, 0, finalCanvas.width, finalCanvas.height);
                pdf.save('Infografia_Crecimiento_2v_Medellin.pdf');
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
}"""

js_new = js[:start_idx] + new_func + js[func_body_end+1:]

with open('index.js', 'w', encoding='utf-8') as f:
    f.write(js_new)

print('Success')
