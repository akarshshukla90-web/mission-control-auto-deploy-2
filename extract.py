import re
html = open('c:/antigravity/mission-control/index_step_1696.html', encoding='utf-8').read()
for m in re.finditer(r'<nav.*?</nav>', html, re.DOTALL):
    print(m.group(0))
