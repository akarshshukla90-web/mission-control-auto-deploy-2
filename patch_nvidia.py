import re

path = r'c:\antigravity\mission-control\server.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Fix NVIDIA block
old_nvidia = """        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],"""
new_nvidia = """        "messages": messages if messages else [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],"""

code = code.replace(old_nvidia, new_nvidia)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("NVIDIA block patched successfully!")
