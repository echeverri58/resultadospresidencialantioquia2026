with open('index.html', 'r', encoding='latin-1') as f:
    html = f.read()

# 1. Insert jsPDF
if 'jspdf' not in html.lower():
    html = html.replace('</head>', '<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>\n</head>')

# 2. Replace the button
# We'll just look for 'downloadGrowthAnalysis' and replace the whole button HTML manually
start_btn = html.find('<button onclick="downloadGrowthAnalysis(')
if start_btn != -1:
    end_btn = html.find('</button>', start_btn) + len('</button>')
    
    new_btns = """<div style="display: flex; gap: 10px; margin-bottom: 16px;">
                    <button onclick="downloadGrowthAnalysis(event, 'png')" style="flex: 1; padding: 12px; background: linear-gradient(135deg, #6366f1, #9333ea); color: white; border: none; border-radius: 12px; font-weight: bold; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;">
                        &#128248; Descargar PNG
                    </button>
                    <button onclick="downloadGrowthAnalysis(event, 'pdf')" style="flex: 1; padding: 12px; background: linear-gradient(135deg, #ea580c, #dc2626); color: white; border: none; border-radius: 12px; font-weight: bold; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 8px;">
                        &#128196; Descargar PDF
                    </button>
                </div>"""
                
    html = html[:start_btn] + new_btns + html[end_btn:]

# 3. Update version
html = html.replace('index.js?v=25', 'index.js?v=26')

with open('index.html', 'w', encoding='latin-1') as f:
    f.write(html)
