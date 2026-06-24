with open('index.html', 'r', encoding='latin-1') as f:
    html = f.read()

# 1. Insert jsPDF script if not there
if 'jspdf' not in html.lower():
    html = html.replace('</head>', '<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>\n</head>')

# 2. Add Crecimiento Tab Button
if 'switchTab(\'crecimiento\')' not in html:
    tab_btn = '''<button class="tab-btn" id="tab-crecimiento" onclick="switchTab('crecimiento')" style="color: #6366f1;">
                    &#128200; Crecimiento 2V
                </button>
            </div>'''
    html = html.replace('</div>\n\n            <!-- Tab Content: Communes Map Info -->', tab_btn + '\n\n            <!-- Tab Content: Communes Map Info -->')

# 3. Add Crecimiento Content Div
if 'content-crecimiento' not in html:
    content_div = '''<!-- Tab Content: Crecimiento -->
            <div id="content-crecimiento" class="tab-content">
                <div class="info-card" style="border-top: 3px solid #6366f1;">
                    <h3 style="color: #6366f1;">Análisis de Crecimiento (1ra vs 2da Vuelta)</h3>
                    <p>Los barrios de Medellín se colorean según la variación neta de votos entre la primera y la segunda vuelta.</p>
                    <div style="display: flex; gap: 10px; margin-top: 16px;">
                        <button onclick="downloadGrowthAnalysis(event, 'png')" style="flex: 1; padding: 12px; background: linear-gradient(135deg, #6366f1, #9333ea); color: white; border: none; border-radius: 12px; font-weight: bold; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;">
                            &#128248; Descargar PNG
                        </button>
                        <button onclick="downloadGrowthAnalysis(event, 'pdf')" style="flex: 1; padding: 12px; background: linear-gradient(135deg, #ea580c, #dc2626); color: white; border: none; border-radius: 12px; font-weight: bold; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;">
                            &#128196; Descargar PDF
                        </button>
                    </div>
                </div>
                <div id="crecimiento-container" style="padding: 16px;">
                    <div style="display: flex; gap: 16px; margin-bottom: 16px;">
                        <div id="growth-summary-abelardo" style="flex: 1; background: #ffffff; border-radius: 12px; border: 1px solid #f1f5f9; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); text-align: center;"></div>
                        <div id="growth-summary-cepeda" style="flex: 1; background: #ffffff; border-radius: 12px; border: 1px solid #f1f5f9; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.02); text-align: center;"></div>
                    </div>
                    <div style="display: flex; gap: 16px;">
                        <div style="flex: 1;">
                            <h4 style="color: #9333ea; margin-bottom: 8px;">Top Barrios Abelardo</h4>
                            <div id="top-growth-abelardo" style="display: flex; flex-direction: column; gap: 8px;"></div>
                        </div>
                        <div style="flex: 1;">
                            <h4 style="color: #ea580c; margin-bottom: 8px;">Top Barrios Cepeda</h4>
                            <div id="top-growth-cepeda" style="display: flex; flex-direction: column; gap: 8px;"></div>
                        </div>
                    </div>
                </div>
            </div>\n\n'''
    html = html.replace('<!-- Tab Content: Hierarchy Filters -->', content_div + '<!-- Tab Content: Hierarchy Filters -->')

# 4. Bump version
html = html.replace('index.js?v=25', 'index.js?v=26')
html = html.replace('index.js?v=12', 'index.js?v=26')
html = html.replace('index.js?v=24', 'index.js?v=26')

with open('index.html', 'w', encoding='latin-1') as f:
    f.write(html)
