import re

path = r'c:\antigravity\mission-control\server.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update spawn logic
spawn_old = """
            title = body.get("title", "Specialist")
            skills = body.get("skills", [])
            about = body.get("about", "Custom specialist agent.")
            if not key:
"""
spawn_new = """
            title = body.get("title", "Specialist")
            skills = body.get("skills", [])
            about = body.get("about", "Custom specialist agent.")
            engine = body.get("engine", "OmniRoute (Unified Gateway)")
            if not key:
"""
code = code.replace(spawn_old, spawn_new)

spawn_save_old = """
                active_agents[key] = {
                    "name": name, "role": role, "title": title,
                    "icon": "⚡", "bg": "#f0fdf4", "color": "#166534",
                    "about": about, "skills": skills, "status": "idle"
                }
"""
spawn_save_new = """
                active_agents[key] = {
                    "name": name, "role": role, "title": title,
                    "icon": "⚡", "bg": "#f0fdf4", "color": "#166534",
                    "about": about, "skills": skills, "status": "idle",
                    "engine": engine
                }
"""
code = code.replace(spawn_save_old, spawn_save_new)

# 2. Add /api/agents/update route
update_route = """
        # ── /api/agents/update ────────────────────────────────────────────────
        elif path == "/api/agents/update":
            key = body.get("key", "")
            if not key:
                self.send_json({"error": "key required"}, 400)
                return
            with state_lock:
                if key not in active_agents:
                    self.send_json({"error": "Agent not found"}, 404)
                    return
                # Update fields if provided
                for field in ["name", "title", "role", "about", "engine"]:
                    if field in body:
                        active_agents[key][field] = body[field]
                if "skills" in body:
                    active_agents[key]["skills"] = body["skills"]
                
                save_agents()
            self.send_json({"success": True, "agent": active_agents[key]})
"""

code = code.replace('elif path == "/api/agents/retire":', update_route + '\n        elif path == "/api/agents/retire":')

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
print("server.py updated!")
