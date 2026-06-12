import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove mode-toggles
content = re.sub(r'<!-- Mode Toggles -->.*?</div>\s*<!-- Tab Content:', '<!-- Tab Content:', content, flags=re.DOTALL)

# 2. Add 'strategy' tab button
tab_injection = '''<button class="tab-btn" id="tab-hierarchy" onclick="switchTab('hierarchy')">
                    Puestos y Mesas
                </button>
                <button class="tab-btn" id="tab-strategy" onclick="switchTab('strategy')" style="color: #166534;">
                    🎯 Estrategia
                </button>'''
content = content.replace('<button class="tab-btn" id="tab-hierarchy" onclick="switchTab(\'hierarchy\')">\n                    Puestos y Mesas\n                </button>', tab_injection)

# 3. Remove right-panel
content = re.sub(r'<!-- Right Panel for Top 50 -->.*?</aside>', '', content, flags=re.DOTALL)

# 4. Inject overlay into map-wrapper
overlay_html = '''<!-- Map Area -->
        <main class="map-wrapper" style="position: relative;">
            <div id="map"></div>
            
            <!-- Strategy Overlay Panel -->
            <div id="strategy-overlay-panel" class="strategy-overlay" style="display: none;">
                <div class="strategy-overlay-header" style="padding: 16px; border-bottom: 1px solid #e2e8f0; background: #f8fafc;">
                    <h2 style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 0 0 4px 0;">Top 50 Oportunidades</h2>
                    <p style="font-size: 12px; color: #64748b; margin: 0;">Mejores zonas para captar votos para Iván Cepeda</p>
                </div>
                
                <div style="padding: 12px 16px; background: #fff; border-bottom: 1px solid #e2e8f0;">
                    <p style="font-size: 11px; color: #475569; margin: 0; line-height: 1.5; text-align: justify;">
                        <strong>¿Por qué estas zonas?</strong> Este ranking identifica los lugares con mayor volumen de <strong>voto en blanco, nulos y electores abstencionistas relativos</strong> (votos que no fueron captados por las candidaturas principales de derecha). Estas zonas representan la oportunidad estratégica más grande y directa para que la campaña de <strong>Iván Cepeda</strong> movilice y capte nuevo apoyo popular.
                    </p>
                </div>
                
                <div id="strat-top-list-total" style="padding: 12px 16px; font-size: 14px; font-weight: 700; color: #0f172a; background: #eef2ff; border-bottom: 1px solid #e2e8f0; text-align: center;">
                    Potencial en el Top 50: <span style="color: #166534; font-size: 16px;">0 votos</span>
                </div>
                
                <div id="strat-top-list-container" style="flex: 1; overflow-y: auto; background: rgba(255, 255, 255, 0.9);">
                    <div id="strat-top-list" style="padding: 0; margin: 0;">
                        <!-- Top items will be injected here -->
                    </div>
                </div>
                
                <div class="strategy-overlay-footer" style="padding: 16px; background: #f8fafc; border-top: 1px solid #e2e8f0; text-align: center;">
                    <p style="font-size: 10px; color: #64748b; margin: 0 0 8px 0; font-weight: 600; text-transform: uppercase;">
                        Creada por John Alexander Echeverry<br>Politólogo y Analista de Datos
                    </p>
                    <button onclick="downloadStrategy()" id="btn-download-strategy" style="width: 100%; background: #166534; color: white; border: none; padding: 10px 16px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; transition: background 0.2s;">
                        <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                        Descargar Mapa y Top 50
                    </button>
                </div>
            </div>'''

content = content.replace('<!-- Map Area -->\n        <main class="map-wrapper">', overlay_html)

# Bump JS version
content = re.sub(r'index\.js\?v=\d+', 'index.js?v=8', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('HTML modifications complete.')
