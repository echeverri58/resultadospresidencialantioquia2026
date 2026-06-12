import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add mode toggles
mode_toggles = """            <!-- Mode Toggles -->
            <div class="mode-toggles" style="display: flex; gap: 8px; margin-bottom: 16px; padding: 0 20px;">
                <button class="mode-btn active" id="btn-results-mode" onclick="setMode('results')" style="flex: 1; padding: 8px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; font-weight: 600; cursor: pointer; transition: all 0.2s; color: #0f172a;">📊 Resultados</button>
                <button class="mode-btn" id="btn-strategy-mode" onclick="setMode('strategy')" style="flex: 1; padding: 8px; border-radius: 8px; border: 1px solid #e2e8f0; background: #fff; font-weight: 600; cursor: pointer; transition: all 0.2s; color: #0f172a;">🎯 Estrategia</button>
            </div>

            <!-- Tab Content: Communes Map Info -->"""

content = content.replace("            <!-- Tab Content: Communes Map Info -->", mode_toggles)

# Add CSS for mode buttons
css_injection = """
        <style>
            .mode-btn.active {
                background: #f1f5f9 !important;
                border-color: #cbd5e1 !important;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
            }
            .mode-btn:hover:not(.active) {
                background: #f8fafc !important;
                border-color: #cbd5e1 !important;
            }
        </style>
    </head>"""

content = content.replace("</head>", css_injection)

# bump cache
content = re.sub(r'index\.js\?v=\d+', 'index.js?v=5', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Mode buttons injected.")
