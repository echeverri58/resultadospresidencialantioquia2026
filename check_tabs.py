import re
with open('index.html', 'r', encoding='latin-1') as f:
    html = f.read()

for match in re.finditer(r'<button[^>]*class="[^"]*tab-btn[^"]*"[^>]*>', html):
    print(match.group())
