import re
import os

def patch_server():
    path = r'c:\antigravity\mission-control\server.py'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()

        # Remove PROJECT_CONTEXT
        code = re.sub(r'# ─── PROJECT CONTEXT.*?COMMISSION MODEL:.*?\"\"\"', '', code, flags=re.DOTALL)
        
        # We need a new endpoint for getting/setting active project
        api_project = """
        # ── /api/projects ──────────────────────────────────────────────────────
        elif path == "/api/projects" and method == "GET":
            # Just return a hardcoded list for now with Personal Profile as default
            projects = [
                {"id": "personal", "name": "Personal Profile", "context": "This is your personal workspace. Execute tasks directly as requested."},
                {"id": "demo_project", "name": "Demo SaaS Project", "context": "Context: You are building a B2B SaaS startup. Focus on acquisition and metrics."}
            ]
            self.send_json({"projects": projects, "active": "personal"})
"""
        if "/api/projects" not in code:
            code = re.sub(r'# ── /api/settings', api_project.strip() + '\n\n        # ── /api/settings', code)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print("server.py scrubbed of JK Forge.")
    except Exception as e:
        print("Error patching server.py:", e)

def patch_index():
    path = r'c:\antigravity\mission-control\static\index.html'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Replace topbar sub
        sub_old = '<div class="topbar-sub" id="topbar-sub">JK Forge &amp; Fittings · JK Traders — B2B Marketing</div>'
        sub_new = """
      <div class="topbar-sub" style="display:flex; align-items:center; gap:8px;">
        <i class="fa-solid fa-folder-tree"></i>
        <select id="active-project-select" onchange="changeProject()" style="background:transparent; color:var(--text3); border:none; outline:none; font-size:12px; font-family:inherit; cursor:pointer;">
          <option value="personal">Personal Profile</option>
          <option value="demo_project">Demo SaaS Project</option>
        </select>
      </div>
"""
        html = html.replace(sub_old, sub_new.strip())

        # Replace textarea placeholder
        ta_old = 'placeholder="Describe the marketing task. Context: Our clients are JK Forge &amp; Fittings (Carbon steel pipe fittings/flanges manufacturer, Vadodara) and JK Traders (Industrial steel stockist). We earn commission on sales generated..."'
        ta_new = 'placeholder="Describe the task or objective... (Runs on active project context)"'
        html = html.replace(ta_old, ta_new)

        # Add changeProject JS
        js_patch = """
let activeProjectId = 'personal';
function changeProject() {
  activeProjectId = document.getElementById('active-project-select').value;
  toast('Switched active project context');
}

"""
        if "changeProject()" not in html:
            html = html.replace('// ─── UTILS', js_patch + '// ─── UTILS')

        # Pass project_id when creating a new task
        html = re.sub(r"const payload = \{\s*title: title.value,\s*message: message.value\s*\};", "const payload = { title: title.value, message: message.value, project_id: activeProjectId };", html)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print("index.html scrubbed of JK Forge.")
    except Exception as e:
        print("Error patching index.html:", e)

def patch_engine():
    path = r'c:\antigravity\mission-control\react_engine.py'
    try:
        with open(path, 'r', encoding='utf-8') as f:
            code = f.read()
            
        context_patch = """
    project_id = task.get("project_id", "personal")
    project_context = ""
    if project_id != "personal":
        project_context = "PROJECT CONTEXT:\\nThis task belongs to a specific project. Tailor your responses to this context."
    else:
        project_context = "PROJECT CONTEXT: Personal Profile. Answer generically without assuming any company affiliation."
        
    system_prompt = f"You are {target_agent['name']}, {target_agent['title']}. {target_agent['about']}\\n\\n{project_context}\\n\\nWORKSPACE RULES:\\n{rules}\\n\\n{base_prompt}"
"""
        # Replace the old system_prompt line
        code = re.sub(r'system_prompt = f"You are \{target_agent\[\'name\'\]\}.*?\{base_prompt\}"', context_patch.strip(), code, flags=re.DOTALL)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print("react_engine.py updated to handle project context.")
    except Exception as e:
        print("Error patching react_engine.py:", e)

patch_server()
patch_index()
patch_engine()
