import re

path = r'c:\antigravity\mission-control\react_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

old_kb = """KNOWLEDGE BASE:
- You have a persistent memory folder at `workspace/knowledge_base/`.
- If you learn how to do a new task or figure out a solution, write it to a text file in that directory so you don't forget it (e.g., `write_file` to `workspace/knowledge_base/linkedin_scraping.txt`).
- Before starting a complex task, `read_file` from that directory if you suspect you might have notes on it.
\"\"\""""

new_kb = """KNOWLEDGE BASE:
- You have a persistent memory folder at `workspace/knowledge_base/`.
- If you learn how to do a new task or figure out a solution, write it to a text file in that directory so you don't forget it (e.g., `write_file` to `workspace/knowledge_base/linkedin_scraping.txt`).
- Before starting a complex task, `read_file` from that directory if you suspect you might have notes on it.

EXECUTION & DELIVERY RULES:
1. YOU MUST ALWAYS USE A TOOL. Never just output plain text. Every single response you make MUST contain a <tool_call> block.
2. If you write an automation or a script, YOU MUST EXECUTE IT using `run_command` to verify that it works. Do not just write it and stop. Run it!
3. When you are fully done and the automation has successfully executed, you MUST use the `finish` tool to provide a summary and complete the task.
\"\"\""""

code = code.replace(old_kb, new_kb)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Added execution rules to prompt.")
