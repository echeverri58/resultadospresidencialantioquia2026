import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

explanation_html = '''
            <div style="padding: 12px 16px; background: #fff; border-bottom: 1px solid #e2e8f0;">
                <p style="font-size: 11px; color: #475569; margin: 0; line-height: 1.5; text-align: justify;">
                    <strong>¿Por qué estas zonas?</strong> Este ranking identifica los lugares con mayor volumen de <strong>voto en blanco, nulos y electores abstencionistas relativos</strong> (votos que no fueron captados por las candidaturas principales de derecha). Estas zonas representan la oportunidad estratégica más grande y directa para que la campaña de <strong>Iván Cepeda</strong> movilice y capte nuevo apoyo popular, expandiendo su base electoral más allá de sus fortines tradicionales.
                </p>
            </div>
'''

search_str = '<div id="strat-top-list-total"'
if search_str in content and '¿Por qué estas zonas?' not in content:
    content = content.replace(search_str, explanation_html + '            <div id="strat-top-list-total"')

# bump cache
content = re.sub(r'index\.js\?v=\d+', 'index.js?v=7', content)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Explanation added.')
