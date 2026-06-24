import sys

with open('index.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re

# We want to replace the `} else {` block of blankItem and the abstencionBadge block

broken_code = """    } else {
        document.getElementById('blank-votes-count').innerText = "0";
        document.getElementById('blank-votes-pct').innerText = "(0%)";
    }

    const abstencionBadge = document.getElementById('abstencion-badge');
    if (postInfo && postInfo.potential && postInfo.potential > 0) {
        const potential = postInfo.potential;
        const abstencionPct = Math.max(0, ((potential - totalVotes) / potential) * 100);
        document.getElementById('abstencion-pct').innerText = `${abstencionPct.toFixed(2)}%`;
        abstencionBadge.style.display = 'flex';
    } else {
        abstencionBadge.style.display = 'none';
    }"""

fixed_code = """    } else {
        const bCount = document.getElementById('blank-votes-count');
        if (bCount) bCount.innerText = "0";
        const bPct = document.getElementById('blank-votes-pct');
        if (bPct) bPct.innerText = "(0%)";
    }

    const abstencionBadge = document.getElementById('abstencion-badge');
    const abstencionPctEl = document.getElementById('abstencion-pct');
    if (abstencionBadge && abstencionPctEl && postInfo && postInfo.potential && postInfo.potential > 0) {
        const potential = postInfo.potential;
        const abstencionPct = Math.max(0, ((potential - totalVotes) / potential) * 100);
        abstencionPctEl.innerText = `${abstencionPct.toFixed(2)}%`;
        abstencionBadge.style.display = 'flex';
    } else if (abstencionBadge) {
        abstencionBadge.style.display = 'none';
    }"""

if broken_code in js:
    js = js.replace(broken_code, fixed_code)
    with open('index.js', 'w', encoding='utf-8') as f:
        f.write(js)
    print("Fixed null checks.")
else:
    print("Could not find exact block to replace.")
