import re

def patch_server():
    path = r'c:\antigravity\mission-control\server.py'
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    projects_api = """
        # ── /api/projects ──────────────────────────────────────────────────────
        elif path == "/api/projects" and method == "GET":
            import os
            proj_file = os.path.expanduser("~/.openclaw/projects.json")
            if not os.path.exists(proj_file):
                # Default init
                projects = [
                    {"id": "personal", "name": "Personal Profile", "context": "This is your personal workspace. Execute tasks directly as requested."},
                ]
                os.makedirs(os.path.dirname(proj_file), exist_ok=True)
                with open(proj_file, 'w') as pf:
                    json.dump(projects, pf)
            else:
                try:
                    with open(proj_file, 'r') as pf:
                        projects = json.load(pf)
                except:
                    projects = [{"id": "personal", "name": "Personal Profile", "context": "This is your personal workspace. Execute tasks directly as requested."}]
            
            self.send_json({"projects": projects, "active": "personal"})

        elif path == "/api/projects/new" and method == "POST":
            import os, uuid
            proj_file = os.path.expanduser("~/.openclaw/projects.json")
            new_id = str(uuid.uuid4())[:8]
            name = body.get("name", "New Project")
            context = body.get("context", "")
            
            if os.path.exists(proj_file):
                try:
                    with open(proj_file, 'r') as pf:
                        projects = json.load(pf)
                except:
                    projects = []
            else:
                projects = [{"id": "personal", "name": "Personal Profile", "context": "This is your personal workspace. Execute tasks directly as requested."}]
                
            projects.append({"id": new_id, "name": name, "context": context})
            with open(proj_file, 'w') as pf:
                json.dump(projects, pf, indent=2)
                
            self.send_json({"success": True, "id": new_id})
"""
    # Replace the existing /api/projects block that was hardcoded
    # In my previous script, I inserted # ── /api/projects ──────...
    # I will replace it using regex
    code = re.sub(r'# ── /api/projects .*?self\.send_json\(\{"projects": projects, "active": "personal"\}\)', projects_api.strip(), code, flags=re.DOTALL)

    # I also need to update react_engine.py to read from projects.json
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("server.py updated for dynamic projects.")

def patch_engine():
    path = r'c:\antigravity\mission-control\react_engine.py'
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
        
    engine_patch = """
    project_id = task.get("project_id", "personal")
    project_context = ""
    if project_id != "personal":
        import os, json
        proj_file = os.path.expanduser("~/.openclaw/projects.json")
        if os.path.exists(proj_file):
            try:
                with open(proj_file, 'r') as pf:
                    projects = json.load(pf)
                for p in projects:
                    if p["id"] == project_id:
                        project_context = f"PROJECT CONTEXT: {p['context']}\\nTailor your responses strictly to this context."
            except: pass
            
    if not project_context:
        project_context = "PROJECT CONTEXT: Personal Profile. Answer generically without assuming any company affiliation."
        
    system_prompt = f"You are {target_agent['name']}, {target_agent['title']}. {target_agent['about']}\\n\\n{project_context}\\n\\nWORKSPACE RULES:\\n{rules}\\n\\n{base_prompt}"
"""
    code = re.sub(r'project_id = task\.get\("project_id", "personal"\).*?\{base_prompt\}"', engine_patch.strip(), code, flags=re.DOTALL)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("react_engine.py updated to read dynamic projects.")

patch_server()
patch_engine()
