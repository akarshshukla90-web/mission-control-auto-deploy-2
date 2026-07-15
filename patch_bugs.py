import re

path = r'c:\antigravity\mission-control\static\index.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Force Dark Mode Default
html = html.replace('<html lang="en" data-theme="light">', '<html lang="en" data-theme="dark">')

# 2. Fix \n in chat feed
chat_old = """<div class="chat-text">${msg.text}</div>"""
chat_new = """<div class="chat-text" style="white-space:pre-wrap;">${(msg.text||'').replace(/\\\\n/g, '\\n')}</div>"""
html = html.replace(chat_old, chat_new)

# 3. Fix \n in Task Drawer comments
comment_old = """<div class="comment-text">${c.text}</div>"""
comment_new = """<div class="comment-text" style="white-space:pre-wrap;">${(c.text||'').replace(/\\\\n/g, '\\n')}</div>"""
html = html.replace(comment_old, comment_new)

# 4. Optional: If the literal \n was written as literal string '\\n', the replace(/\\\\n/g, '\\n') will fix it.
# Let's also do a replace(/\\n/g, '<br>') just in case, but white-space:pre-wrap should handle actual newlines perfectly.
# Wait, if they are actual literal slash n strings, we need `replace(/\\\\n/g, '<br>')` or `replace(/\\\\n/g, '\\n')`.
# With `white-space: pre-wrap`, `\n` character will wrap properly.

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html patched with dark mode default and newline fixes!")
