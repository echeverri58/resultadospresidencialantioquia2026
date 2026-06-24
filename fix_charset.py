with open('index.html', 'r', encoding='latin-1', errors='ignore') as f:
    html = f.read()

html = html.replace('<script src="index.js?v=26"></script>', '<script src="index.js?v=26" charset="utf-8"></script>')

with open('index.html', 'w', encoding='latin-1') as f:
    f.write(html)
