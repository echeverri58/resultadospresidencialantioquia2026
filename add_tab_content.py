import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

injection = '''
            <!-- Tab Content: Strategy Info -->
            <div id="content-strategy" class="tab-content">
                <div class="info-card" style="border-top: 3px solid #166534;">
                    <h3 style="color: #166534;">Mapa Estratégico de Captación</h3>
                    <p>En esta vista, los barrios de Medellín se colorean con base en su potencial estratégico para la campaña de Iván Cepeda (voto blanco, nulo, y abstención relativa).</p>
                    <p style="margin-top: 8px; font-weight: 500;">A mayor intensidad del verde, mayor volumen de votos disponibles.</p>
                </div>
            </div>
'''

content = content.replace('            <!-- Tab Content: Hierarchy Filters -->', injection + '\n            <!-- Tab Content: Hierarchy Filters -->')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('content-strategy added.')
