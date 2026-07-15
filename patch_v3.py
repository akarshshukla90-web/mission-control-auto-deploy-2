import os, re

def patch_server():
    path = r'c:\antigravity\mission-control\server.py'
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    agent_code = """    "nexus": {
        "name": "Nexus", "role": "SPC", "title": "MCP Specialist",
        "icon": "fa-network-wired", "bg": "#e0f2fe", "color": "#0284c7",
        "about": "Searches for and integrates open-source Model Context Protocol (MCP) servers. Expands the AI squad's capabilities continuously.",
        "skills": ["MCP-Protocol", "System-Integration", "Web-Search", "API-Discovery"],
        "status": "idle"
    },"""

    if '"nexus": {' not in code:
        code = code.replace('"loki": {', agent_code + '\n    "loki": {')
        # add to jarvis prompt
        code = code.replace('(quill, pepper, loki, fury, groot, rob, shuri, friday, wanda, vision)', 
                            '(quill, pepper, loki, fury, groot, rob, shuri, friday, wanda, vision, nexus)')
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print("Server patched with Nexus agent.")
    else:
        print("Nexus already in server.py")

def patch_engine():
    path = r'c:\antigravity\mission-control\react_engine.py'
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Remove sandbox constraints
    sandbox_read = 'full_path = os.path.join("workspace", path)'
    if sandbox_read in code:
        # replace it with absolute resolution based on mission-control root
        new_path_logic = 'full_path = os.path.abspath(path) if os.path.isabs(path) else os.path.abspath(os.path.join(os.getcwd(), path))'
        code = code.replace(sandbox_read, new_path_logic)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print("Sandbox removed in react_engine.py")
    else:
        print("Sandbox already removed.")

def patch_frontend():
    path = r'c:\antigravity\mission-control\static\index.html'
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Check if we already patched refreshAll
    if 'document.querySelector(".drawer.open")' not in code:
        # The function refreshAll is likely: async function refreshAll() { or const refreshAll = async () => {
        # Using regex to inject a guard clause at the start of refreshAll
        
        code = code.replace('async function refreshAll() {', 
                            'async function refreshAll() {\\n  if (document.querySelector(".drawer.open") || document.querySelector(".modal-overlay.open")) return;')
        
        code = code.replace('const refreshAll = async () => {', 
                            'const refreshAll = async () => {\\n  if (document.querySelector(".drawer.open") || document.querySelector(".modal-overlay.open")) return;')
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print("Frontend patched.")
    else:
        print("Frontend already patched.")

if __name__ == "__main__":
    patch_server()
    patch_engine()
    patch_frontend()
