let currentMode = "results"; // "results" or "strategy"

window.setMode = function(mode) {
    currentMode = mode;
    
    const rightPanel = document.getElementById("right-panel");
    const resultsModeBtn = document.getElementById("btn-results-mode");
    const stratModeBtn = document.getElementById("btn-strategy-mode");
    
    if (mode === "results") {
        if (resultsModeBtn) resultsModeBtn.classList.add("active");
        if (stratModeBtn) stratModeBtn.classList.remove("active");
        if (rightPanel) rightPanel.style.display = "none";
    } else {
        if (resultsModeBtn) resultsModeBtn.classList.remove("active");
        if (stratModeBtn) stratModeBtn.classList.add("active");
        if (rightPanel) rightPanel.style.display = "flex";
    }
    
    // Refresh UI logic
    if (typeof renderComparativeCard !== "undefined") {
        const muniSelect = document.getElementById("select-muni");
        if (muniSelect && muniSelect.value) {
            const zoneSelect = document.getElementById("select-zone");
            const postSelect = document.getElementById("select-post");
            if (postSelect && postSelect.value) {
                renderComparativeCard(muniSelect.value, zoneSelect.value, postSelect.value);
            } else if (zoneSelect && zoneSelect.value) {
                renderComparativeCard(muniSelect.value, zoneSelect.value);
            } else {
                renderComparativeCard(muniSelect.value);
            }
        } else {
            renderComparativeCard();
        }
    }
};

