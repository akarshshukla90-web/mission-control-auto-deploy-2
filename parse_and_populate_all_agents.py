import os
import json
import re
import pathlib

DATA_DIR = os.path.expanduser("~/.openclaw")
AGENTS_DB_FILE = os.path.join(DATA_DIR, "mc_agents.json")
AGENCY_DIR = pathlib.Path("c:/antigravity/agency-agents")

# Map Lucide icons from divisions.json to FontAwesome equivalents used in the dashboard
LUCIDE_TO_FA = {
    "GraduationCap": "fa-graduation-cap",
    "PenTool": "fa-pen-nib",
    "Code": "fa-code",
    "DollarSign": "fa-dollar-sign",
    "Gamepad2": "fa-gamepad",
    "Map": "fa-map",
    "Stethoscope": "fa-stethoscope",
    "Megaphone": "fa-bullhorn",
    "Target": "fa-bullseye",
    "Box": "fa-box",
    "ClipboardList": "fa-clipboard-list",
    "TrendingUp": "fa-chart-line",
    "ShieldCheck": "fa-shield-halved",
    "Boxes": "fa-cubes",
    "Sparkles": "fa-wand-magic-sparkles",
    "LifeBuoy": "fa-life-ring",
    "FlaskConical": "fa-flask"
}

# Helper to convert bright hex color to soft background tint
def get_soft_bg(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return "#f1f5f9"
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    # Blend with white (0.9 white, 0.1 color)
    nr = int(255 * 0.92 + r * 0.08)
    ng = int(255 * 0.92 + g * 0.08)
    nb = int(255 * 0.92 + b * 0.08)
    return f"#{nr:02x}{ng:02x}{nb:02x}"

def parse_frontmatter(content):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content
    yaml_text, body = match.groups()
    metadata = {}
    for line in yaml_text.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            metadata[key.strip()] = val.strip().strip('"').strip("'")
    return metadata, body

def main():
    # 1. Load divisions metadata
    divisions_file = AGENCY_DIR / "divisions.json"
    if not divisions_file.exists():
        print("Error: divisions.json not found.")
        return
        
    with open(divisions_file, "r", encoding="utf-8") as f:
        div_data = json.load(f)
    divisions = div_data.get("divisions", {})

    # Load existing active agents if any
    existing_agents = {}
    if os.path.exists(AGENTS_DB_FILE):
        try:
            with open(AGENTS_DB_FILE, "r", encoding="utf-8") as f:
                existing_agents = json.load(f)
        except Exception:
            pass

    # 2. Iterate through divisions and files
    agent_count = 0
    for div_name, div_meta in divisions.items():
        div_dir = AGENCY_DIR / div_name
        if not div_dir.is_dir():
            continue
            
        color = div_meta.get("color", "#3B82F6")
        bg_color = get_soft_bg(color)
        default_fa = LUCIDE_TO_FA.get(div_meta.get("icon"), "fa-user-cog")
        
        for md_file in div_dir.glob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                metadata, body = parse_frontmatter(content)
                if not metadata or "name" not in metadata:
                    continue
                
                # Derive agent key from file base name
                # e.g., 'engineering-backend-architect.md' -> 'backend-architect'
                # or 'design-ui-designer.md' -> 'ui-designer'
                file_stem = md_file.stem
                agent_id = file_stem.replace(f"{div_name}-", "", 1)
                
                # If there's an intersection with existing manually tuned keys, keep them
                if agent_id in existing_agents and agent_id in ("jarvis", "tony", "friday", "shuri", "wanda", "vision", "loki"):
                    continue
                    
                name = metadata.get("name")
                desc = metadata.get("description", "")
                vibe = metadata.get("vibe", "")
                
                # Role: Developers/engineers/testers are Integrators ("INT"), others are Specialists ("SPC")
                role = "SPC"
                if div_name in ("engineering", "testing", "game-development"):
                    role = "INT"
                
                # Skills extraction: grab main topics or divide name
                skills = [div_meta.get("label")]
                # Extract second-level bullet points or skills from body
                skill_matches = re.findall(r"-\s*\*\*([^*]+)\*\*", body)
                if skill_matches:
                    skills.extend([s.strip() for s in skill_matches[:4]])
                else:
                    skills.extend([w.capitalize() for w in agent_id.split("-") if len(w) > 2])
                
                # Unique skills only
                skills = list(dict.fromkeys(skills))[:5]
                
                about = vibe if vibe else desc
                if desc and desc != about:
                    about = f"{about} Focuses on {desc}" if about else desc
                
                existing_agents[agent_id] = {
                    "name": name,
                    "role": role,
                    "title": name,
                    "icon": default_fa,
                    "bg": bg_color,
                    "color": color,
                    "about": about[:300] + ("..." if len(about) > 300 else ""),
                    "skills": skills,
                    "status": "idle"
                }
                agent_count += 1
            except Exception as e:
                print(f"Skipping {md_file.name} due to error: {e}")

    # 3. Write back the complete registry
    with open(AGENTS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_agents, f, indent=2)

    print(f"SUCCESS: Parsed and loaded {agent_count} personas from agency-agents into {AGENTS_DB_FILE}.")
    print(f"Total agents in OpenClaw database: {len(existing_agents)}")

if __name__ == "__main__":
    main()
