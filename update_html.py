import sys

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

part_to_remove = """                <div id="strat-top-list-container" style="display: none; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
                    <div style="background: #f8fafc; padding: 10px 12px; font-size: 13px; font-weight: 800; color: #334155; border-bottom: 1px solid #e2e8f0; text-align: center;">
                        Top 50 de mejores barrios para captar votos para Ivan Cepeda
                    </div>
                    <div style="background: #f1f5f9; padding: 6px 12px; font-size: 10px; font-weight: 600; color: #64748b; border-bottom: 1px solid #e2e8f0; text-align: center; text-transform: uppercase; letter-spacing: 0.5px;">
                        Creada por John Alexander Echeverry, politólogo y analista de datos
                    </div>
                    <div id="strat-top-list-total" style="padding: 8px 12px; font-size: 13px; font-weight: 700; color: #0f172a; background: #eef2ff; border-bottom: 1px solid #e2e8f0; text-align: center;">
                        Potencial en el Top 50: <span style="color: #166534; font-size: 15px;">0 votos</span>
                    </div>
                    <div id="strat-top-list" style="padding: 0; margin: 0; max-height: 220px; overflow-y: auto;">
                        <!-- Top items will be injected here -->
                    </div>
                </div>"""

if part_to_remove in content:
    content = content.replace(part_to_remove, '')
else:
    print("Could not find part to remove")

right_panel = """
        <!-- Right Panel for Top 50 -->
        <aside id="right-panel" style="display: none; width: 350px; background: white; border-left: 1px solid #e2e8f0; flex-direction: column; height: 100vh; overflow: hidden; box-shadow: -4px 0 15px rgba(0,0,0,0.05); z-index: 1000; position: absolute; right: 0; top: 0;">
            <div style="padding: 16px; border-bottom: 1px solid #e2e8f0; background: #f8fafc;">
                <h2 style="font-size: 16px; font-weight: 800; color: #0f172a; margin: 0 0 4px 0;">Top 50 Oportunidades</h2>
                <p style="font-size: 12px; color: #64748b; margin: 0;">Mejores barrios para captar votos para Iván Cepeda</p>
            </div>
            
            <div style="background: #f1f5f9; padding: 8px 16px; font-size: 10px; font-weight: 600; color: #64748b; border-bottom: 1px solid #e2e8f0; text-align: center; text-transform: uppercase; letter-spacing: 0.5px;">
                Creada por John Alexander Echeverry<br>Politólogo y Analista de Datos
            </div>
            
            <div id="strat-top-list-total" style="padding: 12px 16px; font-size: 14px; font-weight: 700; color: #0f172a; background: #eef2ff; border-bottom: 1px solid #e2e8f0; text-align: center;">
                Potencial en el Top 50: <span style="color: #166534; font-size: 16px;">0 votos</span>
            </div>
            
            <div id="strat-top-list-container" style="flex: 1; overflow-y: auto;">
                <div id="strat-top-list" style="padding: 0; margin: 0;">
                    <!-- Top items will be injected here -->
                </div>
            </div>
        </aside>
"""

content = content.replace('<!-- Map Area -->', right_panel + '\n        <!-- Map Area -->')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done!')
