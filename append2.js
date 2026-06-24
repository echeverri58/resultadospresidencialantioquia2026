
window.downloadCard2v = function() {
    const card = document.getElementById('comparative-card-2v');
    const btnContainer = document.getElementById('download-btn-container-2v');
    
    if (btnContainer) btnContainer.style.display = 'none';
    
    html2canvas(card, {
        scale: 2,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
    }).then(canvas => {
        if (btnContainer) btnContainer.style.display = 'block';
        const link = document.createElement('a');
        link.download = 'Comparativo_1v_vs_2v.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    }).catch(err => {
        console.error("Error al generar la imagen", err);
        if (btnContainer) btnContainer.style.display = 'block';
        alert("Hubo un error al generar la imagen.");
    });
};
