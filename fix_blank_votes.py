import sys
with open('index.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
pattern = "        document.getElementById('blank-votes-count').innerText = formatNumber(blankItem.votes);\n        document.getElementById('blank-votes-pct').innerText = `(${blankItem.pct.toFixed(2)}%)`;"

replacement = """        let elCount = document.getElementById('blank-votes-count');
        if (elCount) elCount.innerText = formatNumber(blankItem.votes);
        let elPct = document.getElementById('blank-votes-pct');
        if (elPct) elPct.innerText = `(${blankItem.pct.toFixed(2)}%)`;"""

if pattern in js:
    js = js.replace(pattern, replacement)
    with open('index.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print('Replaced exact string.')
else:
    print('Exact string not found')
