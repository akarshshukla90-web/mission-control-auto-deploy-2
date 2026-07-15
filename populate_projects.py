import json
import os

def populate_projects():
    proj_file = os.path.expanduser("~/.openclaw/projects.json")
    os.makedirs(os.path.dirname(proj_file), exist_ok=True)
    
    projects = [
        {
            "id": "personal",
            "name": "Personal Profile",
            "context": "This is your personal workspace. Execute tasks directly as requested."
        },
        {
            "id": "jk_forge",
            "name": "JK Forge & Fittings",
            "context": "Context: Build and integrate Hermes AI as a virtual assistant for JK Forge & Fittings. Include an inquiry CTA and WhatsApp contact integration."
        },
        {
            "id": "jk_traders",
            "name": "JK Traders",
            "context": "Context: Build and integrate Hermes AI as a virtual assistant for JK Traders. Include an inquiry CTA and WhatsApp contact integration."
        },
        {
            "id": "omni_route",
            "name": "OmniRoute",
            "context": "Context: OmniRoute AI gateway project. Use local API server on http://localhost:20128/v1 with standard OpenAI client/SDK configurations."
        },
        {
            "id": "demo_project",
            "name": "Demo SaaS Project",
            "context": "Context: You are building a B2B SaaS startup. Focus on acquisition and metrics."
        }
    ]
    
    with open(proj_file, 'w') as f:
        json.dump(projects, f, indent=2)
    print("projects.json successfully populated.")

populate_projects()
