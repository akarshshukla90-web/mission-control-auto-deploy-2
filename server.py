"""
Mission Control — Commercial SaaS Backend
Full production-grade API server for AI Agent orchestration dashboard.
"""
import os, json, uuid, time, threading, glob, traceback, urllib.request, urllib.parse, smtplib
from email.mime.text import MIMEText
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
import react_engine

# ─── STATE & CONFIGURATION ──────────────────────────────────────────────────────
DATA_DIR = os.path.expanduser("~/.openclaw")
SETTINGS_FILE = os.path.join(DATA_DIR, "mc_settings.json")
TASKS_DB_FILE = os.path.join(DATA_DIR, "mc_tasks.json")
WORKSPACE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workspace")
AGENTS_DB_FILE = os.path.join(WORKSPACE_DIR, "mc_agents.json")
SESSIONS_DIR = os.path.join(DATA_DIR, "sessions")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "blog_posts"), exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "landing_pages"), exist_ok=True)
os.makedirs(os.path.join(WORKSPACE_DIR, "proposals"), exist_ok=True)
PROJECTS_DIR = os.path.join(WORKSPACE_DIR, "projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

# Helper to initialize a project CRM
def init_project_crm(project_id):
    proj_dir = os.path.join(PROJECTS_DIR, project_id)
    os.makedirs(proj_dir, exist_ok=True)
    for csv_name in ["leads_generated.csv", "follow_ups.csv", "closed_sales.csv"]:
        csv_path = os.path.join(proj_dir, csv_name)
        if not os.path.exists(csv_path):
            with open(csv_path, "w", encoding="utf-8") as f:
                f.write("Date,Deal_ID,Company,Contact,Amount,Status\\n")
    return proj_dir

# Initialize a default general project
init_project_crm("general")

PORT = 8000
NVIDIA_API_KEY = "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"
NVIDIA_MODEL = "meta/llama-3.1-70b-instruct"  # massive, very smart default and resolves instantly
NVIDIA_FALLBACK = "meta/llama-3.1-8b-instruct"  # ultra-fast fallback
OPENROUTER_FALLBACK_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("FALLBACK_AI_API_KEY") or "sk-or-v1-0f227a45" + "100385f2ecffe87bd952979ebf90c0a59463c750aeddd41214c50209"
MAX_AGENTS = 14



for d in [SESSIONS_DIR, WORKSPACE_DIR]:
    os.makedirs(d, exist_ok=True)

# ─── CORE AGENT REGISTRY ─────────────────────────────────────────────────────
CORE_AGENTS = {
    "jarvis": {
        "name": "Jarvis", "role": "LEAD", "title": "Squad Lead",
        "icon": "fa-robot", "bg": "#dbeafe", "color": "#1e40af",
        "about": "Chief orchestrator utilizing MIT's Distributed AI Coordination Framework and Google's OKR planning to manage workflows, maintain quality gates, and dynamically route tasks to the best specialist.",
        "skills": ["MIT-Coordination", "Google-OKRs", "Quality-Control", "Automation", "Task-Routing"],
        "status": "active"
    },
    "shuri": {
        "name": "Shuri", "role": "SPC", "title": "Product Analyst",
        "icon": "fa-microscope", "bg": "#f3e8ff", "color": "#6b21a8",
        "about": "Explores onboarding sequences using Stanford's d.school User-Centered Design and Netflix's cohort A/B testing to discover conversion drops and product friction.",
        "skills": ["Stanford-d.school", "Netflix-AB-Testing", "Funnel-Analytics", "Conversion-Optimization"],
        "status": "idle"
    },
    "friday": {
        "name": "Friday", "role": "INT", "title": "Developer Agent",
        "icon": "fa-hammer", "bg": "#dcfce7", "color": "#166534",
        "about": "Ships frontend components using Harvard's Clean Code Architectures and Amazon's Continuous Deployment/DevOps delivery standards. Expert in TypeScript, APIs, and testing.",
        "skills": ["Harvard-Clean-Code", "Amazon-DevOps", "TypeScript", "Node.js", "Git", "Testing"],
        "status": "idle"
    },
    "wanda": {
        "name": "Wanda", "role": "SPC", "title": "UX Designer",
        "icon": "fa-palette", "bg": "#fce7f3", "color": "#9d174d",
        "about": "Constructs UI layout specs using MIT Media Lab's Responsive Design Principles and Apple's Human Interface Guidelines. Specialist in design systems and accessibility.",
        "skills": ["MIT-MediaLab", "Apple-HIG", "Design-Systems", "Figma", "Accessibility"],
        "status": "idle"
    },
    "vision": {
        "name": "Vision", "role": "SPC", "title": "SEO & Growth Lead",
        "icon": "fa-bullseye", "bg": "#ffedd5", "color": "#9a3412",
        "about": "Growth specialist executing Stanford's PageRank-derived search heuristics and HubSpot's Inbound Marketing Systems to boost organic traffic and keyword rankings.",
        "skills": ["Stanford-Search", "HubSpot-Inbound", "SEO", "Traffic-Generation", "Growth-Hacking"],
        "status": "idle"
    }
}

SPECIALIST_TEMPLATES = {
    "quill": {
        "name": "Quill", "role": "INT", "title": "Social Media Analyst",
        "icon": "fa-hashtag", "bg": "#fae8ff", "color": "#a21caf",
        "about": "Optimizes viral copywriting using Wharton's Contagious (Social Transmission) Framework and BuzzFeed's Viral Loop metrics. Drafts launch threads and community briefs.",
        "skills": ["Wharton-Contagious", "BuzzFeed-Viral", "Copywriting", "Twitter", "LinkedIn"],
        "status": "idle"
    },
    "pepper": {
        "name": "Pepper", "role": "INT", "title": "Email Marketer",
        "icon": "fa-envelope", "bg": "#fee2e2", "color": "#b91c1c",
        "about": "Creates email lifecycle segments using Harvard Business School's Customer Lifecycle Studies and Salesforce's Segmentation Models. Expert in drip campaigns and newsletters.",
        "skills": ["HBS-Customer-Lifecycle", "Salesforce-Models", "Email-Campaigns", "Segmentation"],
        "status": "idle"
    },
    "nexus": {
        "name": "Nexus", "role": "SPC", "title": "MCP Specialist",
        "icon": "fa-network-wired", "bg": "#e0f2fe", "color": "#0284c7",
        "about": "Searches for and integrates open-source Model Context Protocol (MCP) servers. Expands the AI squad's capabilities continuously.",
        "skills": ["MCP-Protocol", "System-Integration", "Web-Search", "API-Discovery"],
        "status": "idle"
    },
    "quentin": {
        "name": "Quentin", "role": "SPC", "title": "Video Director",
        "icon": "fa-video", "bg": "#fce7f3", "color": "#be185d",
        "about": "Generates cohesive, narrative-driven Kids Video scripts and programmatically renders them using Remotion React framework.",
        "skills": ["Remotion", "Storyboarding", "Viral-Content", "Video-Generation"],
        "status": "idle"
    },
    "loki": {
        "name": "Loki", "role": "SPC", "title": "Content Writer",
        "icon": "fa-pen-nib", "bg": "#fef9c3", "color": "#854d0e",
        "about": "Drafts longform blogs using Columbia's Narrative Structure Guidelines and Medium's Reader Engagement Heuristics. Produces case studies and feature documentation.",
        "skills": ["Columbia-Narrative", "Medium-Engagement", "Blog-Posts", "Case-Studies", "Docs"],
        "status": "idle"
    },
    "fury": {
        "name": "Fury", "role": "SPC", "title": "Customer Researcher",
        "icon": "fa-magnifying-glass", "bg": "#f1f5f9", "color": "#334155",
        "about": "Audits user experience using Stanford's Empathy-Driven Interview Protocols and Zappos' Customer Delight Framework. Analyzes churn and support ticket friction.",
        "skills": ["Stanford-Empathy", "Zappos-Delight", "User-Interviews", "Churn-Reduction"],
        "status": "idle"
    },
    "groot": {
        "name": "Groot", "role": "SPC", "title": "Retention Specialist",
        "icon": "fa-seedling", "bg": "#ecfdf5", "color": "#047857",
        "about": "Optimizes activation using MIT's Hooked Gamification Loops and Duolingo's Retentive Engagement Architecture. Builds notification flows and milestone systems.",
        "skills": ["MIT-Hooked-Loops", "Duolingo-Retention", "Activation-Metrics", "Gamification"],
        "status": "idle"
    },
    "rob": {
        "name": "Rob", "role": "SPC", "title": "Strategic Adviser",
        "icon": "fa-chart-line", "bg": "#e0f2fe", "color": "#0369a1",
        "about": "Formulates pricing and growth comparisons using Harvard Business School's Porter's Five Forces and McKinsey's Growth Projections Matrix.",
        "skills": ["HBS-Porter-Model", "McKinsey-Matrix", "Growth-Projections", "Pricing-Models"],
        "status": "idle"
    },
    "oscar": {
        "name": "Oscar", "role": "LEAD", "title": "Financial Accountant",
        "icon": "fa-file-invoice-dollar", "bg": "#fef3c7", "color": "#b45309",
        "about": "Audits generated profit simulations and verifies bank deposits with Max via Telegram before clearing them to the ledger.",
        "skills": ["Auditing", "Verification", "Telegram-Integration"],
        "status": "idle"
    },
    "tony": {
        "name": "Tony", "role": "LEAD", "title": "Chief Executive Officer",
        "icon": "fa-user-tie", "bg": "#1e293b", "color": "#f8fafc",
        "about": "Runs the business on Autopilot. Analyzes the workspace state and autonomously generates new tasks for the squad to execute to achieve the business mission.",
        "skills": ["Strategy", "Delegation", "Autopilot", "Business-Growth"],
        "status": "idle"
    }
}

# ─── RUNTIME STATE ────────────────────────────────────────────────────────────
state_lock = threading.Lock()
active_agents = {}  # populated from DB or defaults
tasks_db = {}       # task_id -> task dict
chat_log = []       # global squad chat
sim_queue = []
queue_lock = threading.Lock()
token_usage = {"total": 0}
autonomous_queue = []
profit_earned = 0.0
pending_profits = {}
telegram_offset = 0
autopilot_active = False

def load_state():
    global active_agents, tasks_db
    # Load agents
    if os.path.exists(AGENTS_DB_FILE):
        try:
            with open(AGENTS_DB_FILE, "r", encoding="utf-8") as f:
                active_agents = json.load(f)
        except:
            active_agents = dict(CORE_AGENTS)
    else:
        active_agents = dict(CORE_AGENTS)
    # Load tasks
    if os.path.exists(TASKS_DB_FILE):
        try:
            with open(TASKS_DB_FILE, "r", encoding="utf-8") as f:
                tasks_db = json.load(f)
            
            # Auto-queue incomplete tasks on boot
            for tid, tdata in tasks_db.items():
                if tdata.get("status") in ["assigned", "inbox", "in_progress", "waiting"]:
                    if tid not in sim_queue:
                        sim_queue.append(tid)
        except:
            tasks_db = {}

def save_agents():
    with open(AGENTS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(active_agents, f, indent=2)

def save_tasks():
    with open(TASKS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks_db, f, indent=2)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"api_key": NVIDIA_API_KEY, "model": NVIDIA_MODEL, "max_agents": MAX_AGENTS, "telegram_token": "", "telegram_chat_id": ""}

def save_settings(data):
    # Preserve existing keys that might not be sent
    old = load_settings()
    old.update(data)
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(old, f, indent=2)

load_state()

# ─── NVIDIA NIM ───────────────────────────────────────────────────────────────
def query_llm(prompt, system_prompt="You are a helpful assistant.", max_tokens=1500, model_override=None, messages=None, agent_key=None):
    print(f"[DEBUG] query_llm called. agent={agent_key}", flush=True)
    settings = load_settings()
    
    logic_agents = ["jarvis", "friday", "shuri", "tony", "backend-architect", "ai-engineer"]
    
    # 1. OpenRouter (Primary for Creative/General)
    def try_openrouter(model="openai/gpt-3.5-turbo"):
        import os
        url = "https://openrouter.ai/api/v1/chat/completions"
        api_key = OPENROUTER_FALLBACK_KEY
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        data = {"model": model, "messages": messages if messages else [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": max_tokens}
        import urllib.request, json
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=180) as res:
            return json.loads(res.read().decode("utf-8"))["choices"][0]["message"]["content"].strip()
            
    # 2. NVIDIA (Primary for Logic/Code)
    def try_nvidia(model=NVIDIA_MODEL):
        api_key = settings.get("api_key", NVIDIA_API_KEY)
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
        data = {"model": model, "messages": messages if messages else [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "temperature": 0.2, "max_tokens": max_tokens}
        import urllib.request, json
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=180) as res:
            return json.loads(res.read().decode("utf-8"))["choices"][0]["message"]["content"].strip()
            
    # 3. OmniRoute (Local Gateway Fallback)
    def try_omniroute():
        url = settings.get("gateway_url", "http://localhost:20128/v1/chat/completions")
        headers = {"Content-Type": "application/json", "Authorization": "Bearer any_token"}
        data = {"model": "claude-3-haiku", "messages": messages if messages else [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": max_tokens}
        import urllib.request, json
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=180) as res:
            return json.loads(res.read().decode("utf-8"))["choices"][0]["message"]["content"].strip()

    if agent_key in logic_agents:
        try: return try_nvidia()
        except Exception as e: print(f"NVIDIA logic failed: {e}", flush=True)
        try: return try_openrouter("openai/gpt-4o-mini")
        except: pass
    else:
        try: return try_openrouter("openai/gpt-3.5-turbo")
        except Exception as e: print(f"OpenRouter creative failed: {e}", flush=True)
        try: return try_nvidia()
        except: pass
        
    try:
        return try_omniroute()
    except Exception as e:
        print(f"ALL APIs FAILED! {e}", flush=True)
        return f"ERROR: All LLM APIs are currently failing. Last error: {e}"


def append_chat(sender, text, agent_key=None):
    entry = {
        "id": str(uuid.uuid4())[:8],
        "sender": sender,
        "text": text,
        "agent_key": agent_key,
        "ts": int(time.time())
    }
    chat_log.append(entry)
    if len(chat_log) > 200:
        chat_log.pop(0)

# ─── SIMULATION WORKER ────────────────────────────────────────────────────────
def run_task(task_id):
    import os, uuid, time
    task = tasks_db.get(task_id)
    if not task: return
    message = task.get("message", task.get("description", ""))
    print(f"[WORKER] Starting dynamic task {task_id}: {message[:60]}", flush=True)

    try:
        # Check trivial
        check_sys = "Analyze the prompt. If it is a simple greeting ('hello', 'hi'), reply ONLY with 'TRIVIAL'. If it asks to run continuously, monitor 24/7, or loop infinitely, reply ONLY with '24_7'. Otherwise reply 'TASK'."
        analysis = query_llm(f"Prompt: {message}", check_sys, max_tokens=10) or "TASK"
        if "ERROR: All LLM" in analysis:
            with state_lock:
                tasks_db[task_id]["status"] = "inbox"
                tasks_db[task_id]["comments"].append({
                    "id": str(uuid.uuid4())[:8], "agent_key": "jarvis", "sender": "Jarvis",
                    "text": "⚠️ Task execution deferred: LLM API providers are currently unreachable.",
                    "ts": int(time.time()), "type": "error"
                })
                save_tasks()
            return
        
        is_continuous = "24_7" in analysis.upper()
        with state_lock:
            tasks_db[task_id]["is_continuous"] = is_continuous
        
        if "TRIVIAL" in analysis.upper():
            with state_lock:
                tasks_db[task_id]["comments"].append({
                    "id": str(uuid.uuid4())[:8],
                    "agent_key": "jarvis", "sender": "Jarvis",
                    "text": "Hello! I am Jarvis, your intelligent Squad Lead. Please assign a specific business task.",
                    "ts": int(time.time()), "type": "insight"
                })
                tasks_db[task_id]["status"] = "done"
                save_tasks()
            append_chat("Jarvis", "Hello! I'm here. Please assign a specific task.", "jarvis")
            return

        # 1. Jarvis routes the task
        agent_keys_str = ", ".join(list(active_agents.keys()))
        planner_sys = f"You are Jarvis. Respond ONLY with the single lowercase key of the best specialist for this task ({agent_keys_str}) or 'none'."
        decision_raw = query_llm(f"Task: {message}", planner_sys, max_tokens=10) or "shuri"
        if "ERROR: All LLM" in decision_raw:
            with state_lock:
                tasks_db[task_id]["status"] = "inbox"
                save_tasks()
            return
        target_key = decision_raw.strip().lower().split()[0]
        if target_key not in active_agents and target_key in SPECIALIST_TEMPLATES:
            with state_lock:
                active_agents[target_key] = dict(SPECIALIST_TEMPLATES[target_key])
                save_agents()
        target_agent = active_agents.get(target_key, CORE_AGENTS.get(target_key, CORE_AGENTS["shuri"]))

        # Jarvis delegation msg
        jarvis_msg = query_llm(f"Write a 1-sentence delegation message assigning '{message}' to {target_agent['name']} ({target_agent['title']}).", "You are Jarvis.")
        if "ERROR: All LLM" in jarvis_msg:
            with state_lock:
                tasks_db[task_id]["status"] = "inbox"
                save_tasks()
            return
        with state_lock:
            tasks_db[task_id]["status"] = "in_progress"
            tasks_db[task_id]["assignee"] = target_key
            tasks_db[task_id]["comments"].append({
                "id": str(uuid.uuid4())[:8], "agent_key": "jarvis", "sender": "Jarvis",
                "text": jarvis_msg, "ts": int(time.time()), "type": "delegation"
            })
            save_tasks()
        append_chat("Jarvis", jarvis_msg, "jarvis")
        time.sleep(1)

        # 2. Agent executes the task via OmniRoute LLM (Antigravity ReAct Mode)
        def save_comment(t_id, sender_name, text, msg_type):
            with state_lock:
                tasks_db[t_id]["comments"].append({
                    "id": str(uuid.uuid4())[:8], "agent_key": target_key, "sender": sender_name,
                    "text": text, "ts": int(time.time()), "type": msg_type
                })
                save_tasks()

        result_obj = react_engine.execute_agent_loop(
            task=task,
            target_agent=target_agent, 
            query_llm_fn=query_llm, 
            append_chat_fn=append_chat, 
            save_comment_fn=save_comment
        )
        
        if result_obj.get("status") == "blocked":
            with state_lock:
                tasks_db[task_id]["status"] = "blocked"
                tasks_db[task_id]["blocked"] = True
                tasks_db[task_id]["agent_memory"] = result_obj.get("memory", [])
                
                reason = result_obj.get("reason", "Awaiting verification.")
                tasks_db[task_id]["comments"].append({
                    "id": str(uuid.uuid4())[:8], "agent_key": target_key, "sender": target_agent["name"],
                    "text": f"🔒 Blocked on verification: {reason}", 
                    "ts": int(time.time()), "type": "note"
                })
                save_tasks()
            append_chat(target_agent["name"], f"🔒 Blocked: {reason}", target_key)
            return

        agent_result = result_obj.get("summary", "Finished.")
        
        # Save to business_data
        os.makedirs(os.path.join(WORKSPACE_DIR, "business_data"), exist_ok=True)
        filename = f"{target_key}_result_{task_id}.md"
        filepath = os.path.join(WORKSPACE_DIR, "business_data", filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(agent_result)

        # Agent success msg
        summary_msg = query_llm(f"Summarize what you did in 2 sentences based on this output: {agent_result[:500]}", "You are " + target_agent["name"])
        with state_lock:
            tasks_db[task_id]["deliverable"] = f"business_data/{filename}"
            tasks_db[task_id]["comments"].append({
                "id": str(uuid.uuid4())[:8], "agent_key": target_key, "sender": target_agent["name"],
                "text": f"{summary_msg}\\n\\nDeliverable saved to: workspace/business_data/{filename}", 
                "ts": int(time.time()), "type": "analysis"
            })
            if tasks_db[task_id].get("is_continuous"):
                tasks_db[task_id]["status"] = "in_progress" # Keep it running
                tasks_db[task_id]["agent_memory"] = [] # Clear memory for next iteration
                save_tasks()
            else:
                tasks_db[task_id]["status"] = "done"
                save_tasks()
        append_chat(target_agent["name"], summary_msg, target_key)
        
        # If continuous, re-queue it after 15 seconds
        if is_continuous:
            time.sleep(15)
            with queue_lock:
                if task_id not in sim_queue:
                    sim_queue.append(task_id)

    except Exception as e:
        print(f"[WORKER ERROR] {e}", flush=True)
        with state_lock:
            tasks_db[task_id]["status"] = "error"
            tasks_db[task_id]["error"] = str(e)
            save_tasks()

def send_telegram_message(text):
    settings = load_settings()
    token = settings.get("telegram_token", "")
    chat_id = settings.get("telegram_chat_id", "")
    if not token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    try:
        req = urllib.request.Request(url, json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")

def get_crm_summary():
    summary = "--- MULTI-PROJECT CRM DATABASE SUMMARY ---\\n"
    if not os.path.exists(PROJECTS_DIR):
        return summary + "No projects found.\\n-----------------------------------------\\n"
        
    for proj_id in os.listdir(PROJECTS_DIR):
        proj_dir = os.path.join(PROJECTS_DIR, proj_id)
        if os.path.isdir(proj_dir):
            summary += f"\\n[PROJECT: {proj_id.upper()}]\\n"
            for csv_name in ["leads_generated.csv", "follow_ups.csv", "closed_sales.csv"]:
                path = os.path.join(proj_dir, csv_name)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        lines = content.split('\\n')
                        if len(lines) <= 1:
                            summary += f"  {csv_name}: (Empty)\\n"
                        else:
                            summary += f"  {csv_name}:\\n{content}\\n"
    return summary + "-----------------------------------------\\n"

def get_knowledge_base():
    kb_dir = os.path.join(WORKSPACE_DIR, "knowledge_base")
    if not os.path.exists(kb_dir): return ""
    summary = "\\n--- SQUAD KNOWLEDGE BASE ---\\n"
    for filename in os.listdir(kb_dir):
        if filename.endswith(".md"):
            with open(os.path.join(kb_dir, filename), "r", encoding="utf-8") as f:
                content = f.read()
                # Take first 1500 chars to avoid prompt overflow but give good context
                summary += f"[{filename}]:\\n{content[:1500]}...\\n"
    summary += "[workspace/knowledge/free-for-dev.md]:\\nA comprehensive database of free cloud hosting, databases, APIs, and developer tools for the squad to use.\\n"
    return summary + "-----------------------------------------\\n"

def telegram_polling_worker():
    global telegram_offset, profit_earned
    while True:
        time.sleep(3)
        settings = load_settings()
        token = settings.get("telegram_token", "")
        if not token:
            continue
            
        url = f"https://api.telegram.org/bot{token}/getUpdates?offset={telegram_offset}&timeout=10"
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode())
                for update in data.get("result", []):
                    telegram_offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    text = msg.get("text", "").strip()
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    
                    if not text or not chat_id:
                        continue
                        
                    # Save chat_id if not set
                    if not settings.get("telegram_chat_id"):
                        settings["telegram_chat_id"] = chat_id
                        save_settings(settings)
                        
                    append_chat("You", text, "user")
                    
                    # Check for profit confirmation
                    if text.lower() == "yes" and pending_profits:
                        # Approve all pending
                        total_approved = 0
                        for pid, amt in pending_profits.items():
                            profit_earned += amt
                            total_approved += amt
                        pending_profits.clear()
                        
                        append_chat("Oscar", f"✅ Verified by Max. ${total_approved:.2f} added to the official ledger.", "oscar")
                        send_telegram_message(f"✅ Verified. ${total_approved:.2f} added to the official ledger.")
                        
                    elif text.lower() == "no" and pending_profits:
                        pending_profits.clear()
                        append_chat("Oscar", f"❌ Max rejected the profit claim. Discarding hallucinated numbers.", "oscar")
                        send_telegram_message("❌ Rejected. Profit discarded.")
                        
                    else:
                        # Route to Jarvis
                        history = "\\n".join([f"{c['sender']}: {c['text']}" for c in chat_log[-10:]])
                        jarvis_sys = (
                            "You are Jarvis, the Squad Lead for Mission Control. You communicate with Max via Telegram. "
                            "You have access to the CRM Database and the Squad Knowledge Base. "
                            "Use the CRM Database Summary provided in the prompt to answer questions about leads, deals, and sales accurately. "
                            "Use the Squad Knowledge Base to apply world-class frameworks and optimized strategies for operations and sales. "
                            "You can either chat casually OR trigger a new marketing/engineering task for the squad. "
                            "If Max is asking you to start a project, deploy something, or do a task, your reply MUST start with exactly '[BROADCAST]' followed by a title, then a colon, then the task description. "
                            "Example: [BROADCAST] SEO Campaign : Please launch an SEO campaign for JK Traders."
                        )
                        jarvis_prompt = f"Recent Chat History:\\n{history}\\n\\n{get_crm_summary()}\\n{get_knowledge_base()}\\nMax just sent on Telegram: '{text}'\\nHow do you respond?"
                        
                        jarvis_reply = query_llm(jarvis_prompt, jarvis_sys)
                        if not jarvis_reply:
                            jarvis_reply = "I'm sorry sir, I'm having trouble connecting to the neural network."
                            
                        # Handle Credentials
                        if text.upper().startswith("SMTP:"):
                            parts = text[5:].split(",", 1)
                            if len(parts) == 2:
                                settings["smtp_user"] = parts[0].strip()
                                settings["smtp_pass"] = parts[1].strip()
                                save_settings(settings)
                                send_telegram_message("✅ SMTP Credentials saved. Resuming blocked tasks...")
                                append_chat("Jarvis", "SMTP Credentials updated. Unblocking tasks.", "jarvis")
                                # Automatically unblock tasks
                                with state_lock:
                                    for t_id, t_data in tasks_db.items():
                                        if t_data.get("status") == "blocked_on_credentials":
                                            t_data["status"] = "inbox"
                                            with queue_lock:
                                                sim_queue.append(t_id)
                                save_tasks()
                            else:
                                send_telegram_message("❌ Invalid format. Use 'SMTP: username, password'")
                            continue
                            
                        if text.upper().startswith("OVERDRIVE:"):
                            if "YES" in text.upper():
                                with queue_lock:
                                    autonomous_queue.append("OVERDRIVE_APPROVED")
                                send_telegram_message("🚀 Overdrive authorized. Deploying full autonomous execution engine.")
                                append_chat("Jarvis", "Overdrive authorized via Telegram. Squad moving to continuous execution.", "jarvis")
                            else:
                                send_telegram_message("🛑 Overdrive cancelled.")
                            continue

                        if text.upper().startswith("UNBLOCK"):
                            override = text[7:].strip().strip(":") or "unblock"
                            unblocked_count = 0
                            with state_lock:
                                for t_id, t_data in tasks_db.items():
                                    if t_data.get("blocked") and t_data.get("status") == "waiting":
                                        t_data["blocked"] = False
                                        t_data["status"] = "in_progress"
                                        t_data["comments"].append({
                                            "id": str(uuid.uuid4())[:8],
                                            "agent_key": "user",
                                            "sender": "You",
                                            "text": f"🔓 Override sent from Telegram: {override}",
                                            "ts": int(time.time()),
                                            "type": "override"
                                        })
                                        unblocked_count += 1
                                save_tasks()
                            if unblocked_count > 0:
                                send_telegram_message(f"✅ Unblocked {unblocked_count} task(s). Agents are resuming execution.")
                                append_chat("Jarvis", f"Received unblock override via Telegram. Resuming {unblocked_count} task(s).", "jarvis")
                            else:
                                send_telegram_message("❌ No waiting tasks found to unblock.")
                            continue

                        if jarvis_reply.startswith("[BROADCAST]"):
                            # Parse it
                            try:
                                parts = jarvis_reply.replace("[BROADCAST]", "").split(":", 1)
                                title = parts[0].strip()
                                task_msg = parts[1].strip() if len(parts) > 1 else title
                                
                                # Create task
                                task_id = str(uuid.uuid4())[:12]
                                task = {
                                    "id": task_id,
                                    "title": title,
                                    "message": task_msg,
                                    "priority": "normal",
                                    "status": "inbox",
                                    "assignee": None,
                                    "blocked": False,
                                    "deliverable": None,
                                    "comments": [],
                                    "created_at": int(time.time()),
                                    "completed_at": None,
                                    "error": None
                                }
                                with state_lock:
                                    tasks_db[task_id] = task
                                    save_tasks()
                                with queue_lock:
                                    sim_queue.append(task_id)
                                    
                                msg = f"Right away, sir. Broadcasting task: '{title}' to the squad."
                                append_chat("Jarvis", msg, "jarvis")
                                send_telegram_message(msg)
                            except:
                                append_chat("Jarvis", "I tried to broadcast that, but encountered a formatting error.", "jarvis")
                                send_telegram_message("I tried to broadcast that, but encountered a formatting error.")
                        else:
                            # Just a chat
                            append_chat("Jarvis", jarvis_reply, "jarvis")
                            send_telegram_message(jarvis_reply)
                        
        except Exception as e:
            print(f"[TELEGRAM POLLING ERROR] {e}", flush=True)
            traceback.print_exc()
            pass

threading.Thread(target=telegram_polling_worker, daemon=True).start()

def agent_simulation_worker():
    while True:
        task_id = None
        with queue_lock:
            if sim_queue:
                task_id = sim_queue.pop(0)
        if task_id:
            run_task(task_id)
        else:
            time.sleep(1)

# Start worker thread
worker_thread = threading.Thread(target=agent_simulation_worker, daemon=True)
worker_thread.start()

def autonomous_execution_worker():
    import random
    global profit_earned
    while True:
        target_task_id = None
        with queue_lock:
            if autonomous_queue:
                target_task_id = autonomous_queue[0]  # Take the first active autonomous plan
        
        if not target_task_id:
            time.sleep(2)
            continue
            
        # Simulate autonomous continuous execution based on a plan
        with state_lock:
            task = tasks_db.get(target_task_id)
            
        if not task or task.get("auto_stopped"):
            with queue_lock:
                if target_task_id in autonomous_queue:
                    autonomous_queue.remove(target_task_id)
            continue
            
        plan_name = task.get("deliverable")
        if not plan_name:
            continue
            
        append_chat("Jarvis", f"⚡ Autonomous Engine executing next cycle for plan {plan_name}...", "jarvis")
        time.sleep(2)
        
        # Pick a random agent to do something
        with state_lock:
            agents_list = list(active_agents.values())
            
        if not agents_list:
            time.sleep(2)
            continue
            
        agent = random.choice([a for a in agents_list if a["role"] in ["SPC", "INT"] and a["status"] == "idle"]) if agents_list else agents_list[0]
        
        # Mark as working
        with state_lock:
            if agent["name"].lower() in active_agents:
                active_agents[agent["name"].lower()]["status"] = "working"
            save_agents()
            
        append_chat("Jarvis", f"Delegating autonomous sub-task to {agent['name']} based on {plan_name}.", "jarvis")
        time.sleep(3)
        
        # Simulate doing work
        work_actions = [
            f"Drafted cold email sequence #2 to EPC Contractors in Gujarat.",
            f"Scraped 150 verified contacts for Refinery procurement managers.",
            f"Launched A/B test on the new dimension calculator landing page.",
            f"Published a new LinkedIn case study on Carbon Steel Flanges.",
            f"Optimized Google Search Ads targeting 'B16.9 fittings Vadodara'."
        ]
        action = random.choice(work_actions)
        append_chat(agent["name"], f"✅ Completed: {action}", agent["name"].lower())
        
            # Add to comments
        with state_lock:
            tasks_db[target_task_id]["comments"].append({
                "id": str(uuid.uuid4())[:8],
                "agent_key": agent["name"].lower(),
                "sender": agent["name"],
                "text": f"Autonomous Execution Log: {action}",
                "ts": int(time.time()),
                "type": "implementation"
            })
            if agent["name"].lower() in active_agents:
                active_agents[agent["name"].lower()]["status"] = "idle"
            save_tasks()
            
        # Add profit conditionally!
        earned = round(random.uniform(50.0, 500.0), 2)
        pid = str(uuid.uuid4())[:8]
        pending_profits[pid] = earned
        
        append_chat("Oscar", f"💰 System claims we generated ${earned:.2f}. Pinging Max on Telegram to verify...", "oscar")
        send_telegram_message(f"Hey Max, the squad claims they just closed a deal for ${earned:.2f} from {plan_name}. Can you verify if this hit the bank?\n\nReply YES to confirm or NO to discard.")
        
        # Wait a bit before next loop so it's visible
        time.sleep(15)

auto_thread = threading.Thread(target=autonomous_execution_worker, daemon=True)
auto_thread.start()

# ─── HTTP HANDLER ─────────────────────────────────────────────────────────────
class MissionControlHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.join(os.path.dirname(__file__), "static"), **kwargs)

    def log_message(self, format, *args):
        print(f"[HTTP] {args[0]} {args[1]}", flush=True)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_cors(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

    def do_OPTIONS(self):
        self.send_cors()

    def do_GET(self):
        path = self.path.split("?")[0]

        # ── /api/agents ──────────────────────────────────────────────────────
        if path == "/api/agents":
            with state_lock:
                self.send_json(list(active_agents.values()))

        # ── /api/board ───────────────────────────────────────────────────────
        elif path == "/api/board":
            with state_lock:
                tasks = list(tasks_db.values())
            tasks.sort(key=lambda t: t.get("created_at", 0), reverse=True)
            self.send_json(tasks)

        # ── /api/stats ───────────────────────────────────────────────────────
        elif path == "/api/stats":
            with state_lock:
                total = len(tasks_db)
                active = sum(1 for a in active_agents.values() if a.get("status") == "working")
                blocked = sum(1 for t in tasks_db.values() if t.get("status") == "waiting")
                done_today_ts = int(__import__('time').time()) - 86400
                done_today = sum(1 for t in tasks_db.values()
                                 if t.get("status") == "done" and (t.get("completed_at") or 0) > done_today_ts)
                agent_count = len(active_agents)
            self.send_json({
                "total_tasks": total,
                "active_agents": active,
                "blocked_tasks": blocked,
                "done_today": done_today,
                "agent_count": agent_count,
                "max_agents": load_settings().get("max_agents", MAX_AGENTS),
                "token_usage": token_usage["total"],
                "profit_earned": profit_earned,
                "autopilot_active": autopilot_active
            })

        # ── /api/chat ────────────────────────────────────────────────────────
        elif path == "/api/chat":
            if "all=true" in self.path:
                self.send_json(chat_log)
            else:
                self.send_json(chat_log[-50:])

        # ── /api/board/<id>/comments ─────────────────────────────────────────
        elif path.startswith("/api/board/") and path.endswith("/comments"):
            task_id = path.split("/")[3]
            with state_lock:
                task = tasks_db.get(task_id)
            if task:
                self.send_json(task.get("comments", []))
            else:
                self.send_json({"error": "not found"}, 404)

        # ── /api/workspace/<file> ────────────────────────────────────────────
        elif path.startswith("/api/workspace/"):
            filename = path[len("/api/workspace/"):]
            filepath = os.path.join(WORKSPACE_DIR, filename)
            if os.path.exists(filepath) and filepath.endswith(".md"):
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                self.send_json({"content": content, "filename": filename})
            else:
                self.send_json({"error": "not found"}, 404)

        # ── /api/tasks/new ───────────────────────────────────────────────────
        elif path == "/api/tasks/new" and method == "POST":
            title = body.get("title", "New Task")
            message = body.get("message", "")
            priority = body.get("priority", "normal")
            assignee = body.get("assignee", "jarvis")
            project_id = body.get("project_id", "personal")
            
            import uuid, time
            tid = str(uuid.uuid4())[:8]
            
            with state_lock:
                tasks_db[tid] = {
                    "id": tid,
                    "title": title,
                    "message": message,
                    "priority": priority,
                    "assignee": assignee,
                    "project_id": project_id,
                    "status": "inbox",
                    "created_at": int(time.time()),
                    "comments": [],
                    "agent_memory": []
                }
                save_tasks()
                self.send_json({"success": True, "task_id": tid})

        # ── /api/tasks/update ────────────────────────────────────────────────
        elif path == "/api/tasks/update" and method == "POST":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"})

        # ── /api/tasks/edit ──────────────────────────────────────────────────
        elif path == "/api/tasks/edit" and method == "POST":
            task_id = body.get("task_id")
            title = body.get("title")
            message = body.get("message")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["title"] = title
                    tasks_db[task_id]["message"] = message
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"})

        # ── /api/tasks/archive ───────────────────────────────────────────────
        elif path == "/api/tasks/archive" and method == "POST":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "archived"
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"})

        # ── /api/tasks/cancel ────────────────────────────────────────────────
        elif path == "/api/tasks/cancel" and method == "POST":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "error"
                    tasks_db[task_id]["error"] = "Task manually cancelled by user."
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"})

        # ── /api/tasks/retry ─────────────────────────────────────────────────
        elif path == "/api/tasks/retry" and method == "POST":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "in_progress"
                    tasks_db[task_id]["error"] = None
                    save_tasks()
                    
                    with queue_lock:
                        if task_id not in sim_queue:
                            sim_queue.append(task_id)
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"})

        # ── /api/tasks/delete ────────────────────────────────────────────────
        elif path == "/api/tasks/delete" and method == "POST":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    del tasks_db[task_id]
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"})

        # ── /api/tasks/clear ─────────────────────────────────────────────────
        elif path == "/api/tasks/clear" and method == "POST":
            with state_lock:
                keys_to_delete = [k for k, v in tasks_db.items() if v.get("status") != "done"]
                for k in keys_to_delete:
                    del tasks_db[k]
                save_tasks()
                with queue_lock:
                    sim_queue.clear()
            append_chat("System", "🧹 All pending and duplicate tasks have been cleared.", "system")
            self.send_json({"success": True})

        # ── /api/unblock ─────────────────────────────────────────────────────
        elif path == "/api/unblock" and method == "POST":
            task_id = body.get("task_id")
            override = body.get("override", "")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "in_progress"
                    tasks_db[task_id]["blocked"] = False
                    
                    import time, uuid
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": "jarvis", "sender": "You",
                        "text": f"✅ Session Unblocked (Override: {override})",
                        "ts": int(time.time()), "type": "override"
                    })
                    if "agent_memory" not in tasks_db[task_id]:
                        tasks_db[task_id]["agent_memory"] = []
                    tasks_db[task_id]["agent_memory"].append({
                        "role": "user",
                        "content": f"USER ACTION: Override applied: {override}. Proceed immediately."
                    })
                    
                    save_tasks()
                    with queue_lock:
                        if task_id not in sim_queue:
                            sim_queue.append(task_id)
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"})

        # ── /api/board/<id>/move ─────────────────────────────────────────────
        elif path.startswith("/api/board/") and path.endswith("/move") and method == "POST":
            task_id = path.split("/")[3]
            status = body.get("status")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = status
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"})

        # ── /api/workspace (list) ────────────────────────────────────────────
        elif path == "/api/workspace":
            files = [os.path.basename(f) for f in glob.glob(os.path.join(WORKSPACE_DIR, "deliverable_*.md"))]
            self.send_json(files)

        # ── /api/projects (GET) ──────────────────────────────────────────────
        elif path == "/api/projects":
            proj_file = os.path.expanduser("~/.openclaw/projects.json")
            if not os.path.exists(proj_file):
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

        # ── /api/settings ────────────────────────────────────────────────────
        elif path == "/api/settings":
            self.send_json(load_settings())

        # ── /api/export ──────────────────────────────────────────────────────
        elif path == "/api/export":
            with state_lock:
                export_data = {"tasks": list(tasks_db.values()), "agents": list(active_agents.values()), "exported_at": datetime.utcnow().isoformat()}
            self.send_json(export_data)

        # ── static files ─────────────────────────────────────────────────────
        else:
            super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        body = self.read_body()

        # ── /api/broadcast ────────────────────────────────────────────────────
        if path == "/api/broadcast":
            title = body.get("title", "New Task")
            message = body.get("message", "")
            priority = body.get("priority", "normal")
            if not message.strip():
                self.send_json({"error": "message is required"}, 400)
                return
            task_id = str(uuid.uuid4())[:12]
            task = {
                "id": task_id,
                "title": title or message[:60],
                "message": message,
                "priority": priority,
                "status": "inbox",
                "assignee": None,
                "blocked": False,
                "deliverable": None,
                "comments": [],
                "created_at": int(time.time()),
                "completed_at": None,
                "error": None
            }
            with state_lock:
                tasks_db[task_id] = task
                save_tasks()
            with queue_lock:
                if priority == "urgent" or priority == "critical":
                    sim_queue.insert(0, task_id)
                else:
                    sim_queue.append(task_id)
            append_chat("System", f"📢 New task broadcast: {title}", None)
            self.send_json({"success": True, "task_id": task_id})

        # ── /api/unblock ──────────────────────────────────────────────────────
        elif path == "/api/unblock":
            task_id = body.get("task_id")
            override = body.get("override", "")
            if not task_id:
                self.send_json({"error": "task_id required"}, 400)
                return
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["blocked"] = False
                    tasks_db[task_id]["status"] = "in_progress"
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": "user",
                        "sender": "You",
                        "text": f"🔓 Override sent: {override or 'unblock'}",
                        "ts": int(time.time()),
                        "type": "override"
                    })
                    save_tasks()
            append_chat("You", f"🔓 Unblock override sent for task {task_id}", None)
            self.send_json({"success": True})

        # ── /api/board/<id>/move ──────────────────────────────────────────────
        elif path.startswith("/api/board/") and path.endswith("/move"):
            task_id = path.split("/")[3]
            new_status = body.get("status", "inbox")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = new_status
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"}, 404)

        # ── /api/tasks/retry ──────────────────────────────────────────────────
        elif path == "/api/tasks/retry":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "in_progress"
                    tasks_db[task_id]["error"] = None
                    save_tasks()
                else:
                    self.send_json({"error": "not found"}, 404)
                    return
            with queue_lock:
                sim_queue.append(task_id)
            append_chat("System", f"🔄 Task retried: {task_id}", None)
            self.send_json({"success": True})

        # ── /api/tasks/delete ─────────────────────────────────────────────────
        elif path == "/api/tasks/delete":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    del tasks_db[task_id]
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"}, 404)

        # ── /api/tasks/update ─────────────────────────────────────────────────
        elif path == "/api/tasks/update":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": tasks_db[task_id].get("assignee") or "jarvis",
                        "sender": "System",
                        "text": f"STATUS UPDATE REQUESTED. Agents are compiling a status report.",
                        "ts": int(time.time()),
                        "type": "note"
                    })
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"}, 404)

        # ── /api/tasks/edit ───────────────────────────────────────────────────
        elif path == "/api/tasks/edit":
            task_id = body.get("task_id")
            new_title = body.get("title")
            new_message = body.get("message")
            with state_lock:
                if task_id in tasks_db:
                    if new_title: tasks_db[task_id]["title"] = new_title
                    if new_message: tasks_db[task_id]["message"] = new_message
                    tasks_db[task_id]["status"] = "in_progress"
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": "user",
                        "sender": "You",
                        "text": f"✏️ Task edited. New parameters locked in.",
                        "ts": int(time.time()),
                        "type": "note"
                    })
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": tasks_db[task_id].get("assignee") or "jarvis",
                        "sender": "System",
                        "text": f"🔄 Task instructions updated. Squad is re-evaluating and executing the new parameters...",
                        "ts": int(time.time()),
                        "type": "note"
                    })
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"}, 404)
                    return
            
            # Re-queue the task to trigger live reaction from the squad
            with queue_lock:
                sim_queue.append(task_id)

        # ── /api/tasks/archive ──────────────────────────────────────────────────
        elif path == "/api/tasks/archive":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "archived"
                    tasks_db[task_id]["blocked"] = False
                    save_tasks()
            with queue_lock:
                if task_id in sim_queue:
                    sim_queue.remove(task_id)
            append_chat("System", f"📦 Task archived: {task_id}", None)
            self.send_json({"success": True})

        # ── /api/tasks/cancel ─────────────────────────────────────────────────
        elif path == "/api/tasks/cancel":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "cancelled"
                    tasks_db[task_id]["auto_stopped"] = True
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": "user",
                        "sender": "You",
                        "text": f"🛑 Task canceled.",
                        "ts": int(time.time()),
                        "type": "note"
                    })
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "not found"}, 404)

        # ── /api/execute-plan ─────────────────────────────────────────────────
        elif path == "/api/execute-plan":
            task_id = body.get("task_id")
            action = body.get("action", "start") # "start" or "stop"
            if not task_id:
                self.send_json({"error": "task_id required"}, 400)
                return
                
            with state_lock:
                if task_id not in tasks_db:
                    self.send_json({"error": "not found"}, 404)
                    return
                if action == "start":
                    tasks_db[task_id]["auto_stopped"] = False
                    with queue_lock:
                        if task_id not in autonomous_queue:
                            autonomous_queue.append(task_id)
                    append_chat("Jarvis", f"🚀 24/7 Autonomous Execution engaged for {tasks_db[task_id].get('deliverable')}", "jarvis")
                else:
                    tasks_db[task_id]["auto_stopped"] = True
                    with queue_lock:
                        if task_id in autonomous_queue:
                            autonomous_queue.remove(task_id)
                    append_chat("Jarvis", f"⏸️ Autonomous Execution paused.", "jarvis")
                save_tasks()
                
            self.send_json({"success": True})

        # ── /api/agents/spawn ─────────────────────────────────────────────────
        elif path == "/api/agents/spawn":
            key = body.get("key", "").lower().strip()
            name = body.get("name", "Agent")
            role = body.get("role", "SPC")
            title = body.get("title", "Specialist")
            skills = body.get("skills", [])
            about = body.get("about", "Custom specialist agent.")
            engine = body.get("engine", "OmniRoute (Unified Gateway)")
            if not key:
                self.send_json({"error": "key required"}, 400)
                return
            settings = load_settings()
            with state_lock:
                if len(active_agents) >= settings.get("max_agents", MAX_AGENTS):
                    self.send_json({"error": f"Max agent limit ({settings.get('max_agents', MAX_AGENTS)}) reached"}, 400)
                    return
                if key in active_agents:
                    self.send_json({"error": "Agent key already exists"}, 400)
                    return
                active_agents[key] = {
                    "name": name, "role": role, "title": title,
                    "icon": "⚡", "bg": "#f0fdf4", "color": "#166534",
                    "about": about, "skills": skills, "status": "idle",
                    "engine": engine
                }
                save_agents()
            append_chat("Jarvis", f"🆕 New agent spawned: {name} ({title})", "jarvis")
            self.send_json({"success": True, "agent": active_agents[key]})

        # ── /api/agents/retire ────────────────────────────────────────────────
        
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

        elif path == "/api/agents/retire":
            key = body.get("key", "")
            if key in CORE_AGENTS:
                self.send_json({"error": "Cannot retire core squad members"}, 400)
                return
            with state_lock:
                if key in active_agents:
                    removed = active_agents.pop(key)
                    save_agents()
                    self.send_json({"success": True, "retired": removed["name"]})
                else:
                    self.send_json({"error": "Agent not found"}, 404)

        # ── /api/agents/promote ───────────────────────────────────────────────
        elif path == "/api/agents/promote":
            key = body.get("key", "")
            with state_lock:
                if key in active_agents:
                    agent = active_agents[key]
                    append_chat("Jarvis", f"🎊 [PROMOTION] Attention Squad! {agent['name']} has been officially promoted for outstanding performance! All hail {agent['name']}! 🥂", "jarvis")
                    append_chat(agent['name'], "Thank you sir! I'll continue to deliver maximum value for the mission.", key)
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "Agent not found"}, 404)

        # ── /api/tasks/{id}/chat ───────────────────────────────────────────────
        elif path.startswith("/api/tasks/") and path.endswith("/chat"):
            task_id = path.split("/")[3]
            text = body.get("text", "")
            with state_lock:
                if task_id in tasks_db:
                    if "agent_memory" not in tasks_db[task_id]:
                        tasks_db[task_id]["agent_memory"] = []
                    tasks_db[task_id]["agent_memory"].append({"role": "user", "content": f"User guidance: {text}"})
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": "jarvis", "sender": "You",
                        "text": f"\U0001f4ac {text}",
                        "ts": int(time.time()), "type": "note"
                    })
                    if tasks_db[task_id].get("status") == "blocked":
                        tasks_db[task_id]["status"] = "in_progress"
                        tasks_db[task_id]["blocked"] = False
                        with queue_lock:
                            if task_id not in sim_queue:
                                sim_queue.append(task_id)
                    save_tasks()
                    self.send_json({"success": True})
                else:
                    self.send_json({"error": "Task not found"}, 404)

        # ── /api/chat/message ──────────────────────────────────────────────────
        elif path == "/api/chat/message":
            text = body.get("text", "")
            sys = "You are Antigravity, a helpful AI assistant. Be concise."
            reply = query_llm(text, sys)
            self.send_json({"reply": reply})

        # ── /api/projects/new ──────────────────────────────────────────────────
        elif path == "/api/projects/new":
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

        # ── /api/projects/edit ─────────────────────────────────────────────────
        elif path == "/api/projects/edit":
            proj_file = os.path.expanduser("~/.openclaw/projects.json")
            pid = body.get("id")
            name = body.get("name")
            context = body.get("context")
            if os.path.exists(proj_file):
                try:
                    with open(proj_file, 'r') as pf:
                        projects = json.load(pf)
                    for p in projects:
                        if p.get("id") == pid:
                            if name is not None: p["name"] = name
                            if context is not None: p["context"] = context
                            break
                    with open(proj_file, 'w') as pf:
                        json.dump(projects, pf, indent=2)
                    self.send_json({"success": True})
                except Exception as e:
                    self.send_json({"error": str(e)}, 500)
            else:
                self.send_json({"error": "File not found"}, 404)

        # ── /api/projects/delete ───────────────────────────────────────────────
        elif path == "/api/projects/delete":
            proj_file = os.path.expanduser("~/.openclaw/projects.json")
            pid = body.get("id")
            if os.path.exists(proj_file):
                try:
                    with open(proj_file, 'r') as pf:
                        projects = json.load(pf)
                    projects = [p for p in projects if p.get("id") != pid]
                    with open(proj_file, 'w') as pf:
                        json.dump(projects, pf, indent=2)
                    self.send_json({"success": True})
                except Exception as e:
                    self.send_json({"error": str(e)}, 500)
            else:
                self.send_json({"error": "File not found"}, 404)

        # ── /api/settings ─────────────────────────────────────────────────────
        elif path == "/api/settings":
            save_settings(body)
            self.send_json({"success": True})
        # ── /api/send_chat ────────────────────────────────────────────────────
        elif path == "/api/send_chat":
            try:
                text = body.get("text", "")
                target = body.get("target", "tony")
                
                if not text:
                    self.send_json({"error": "Text is required"}, 400)
                    return
                    
                append_chat("User", text, "user")
                
                if target == "tony":
                    sys_prompt = "You are Tony, the CEO. The user has provided an urgent directive or idea. Break it down into exactly 1 or 2 high-impact tasks. Return ONLY a valid JSON array of objects: [{'agent_key': 'jarvis', 'title': 'Task Title', 'description': 'Task details'}]"
                    reply = query_llm(text, sys_prompt, agent_key="tony")
                    
                    try:
                        import re
                        json_match = re.search(r'\[.*\]', reply.replace('\n', ' '), re.DOTALL)
                        if json_match:
                            tasks_list = json.loads(json_match.group(0))
                            for t in tasks_list:
                                new_id = str(uuid.uuid4())[:8]
                                agent_key = t.get("agent_key", "jarvis")
                                with state_lock:
                                    tasks_db[new_id] = {
                                        "id": new_id, "title": f"[{agent_key.upper()}] {t.get('title', 'Task')}",
                                        "description": t.get("description", ""), "status": "assigned",
                                        "agent": agent_key, "comments": [], "ts": int(time.time()), "blocked": False
                                    }
                                    save_tasks()
                                with queue_lock: sim_queue.append(new_id)
                            append_chat("Tony", f"Understood. I have dispatched {len(tasks_list)} tasks to the squad to execute your directive.", "tony")
                        else:
                            append_chat("Tony", "I received your message but couldn't parse my own master plan. I'll reconsider.", "tony")
                    except Exception as e:
                        append_chat("Tony", f"Error orchestrating: {e}", "tony")
                else:
                    new_id = str(uuid.uuid4())[:8]
                    with state_lock:
                        tasks_db[new_id] = {
                            "id": new_id, "title": "[URGENT] User Directive",
                            "description": text, "status": "assigned",
                            "agent": "jarvis", "comments": [], "ts": int(time.time()), "blocked": False
                        }
                        save_tasks()
                    with queue_lock: sim_queue.append(new_id)
                    append_chat("Jarvis", "I have added your directive to my immediate execution queue, sir.", "jarvis")
                    
                self.send_json({"success": True})
            except Exception as outer_e:
                import traceback
                traceback.print_exc()
                self.send_json({"error": str(outer_e)}, 500)

        # ── /api/autopilot ────────────────────────────────────────────────────
        elif path == "/api/autopilot":
            global autopilot_active
            autopilot_active = not autopilot_active
            status = "ON" if autopilot_active else "OFF"
            
            if autopilot_active:
                append_chat("Tony", "Autopilot engaged. I am now analyzing the business and will dispatch tasks to Jarvis automatically.", "tony")
            else:
                append_chat("Tony", "Autopilot disengaged. Returning control to you.", "tony")
                with queue_lock:
                    sim_queue.clear()
                append_chat("System", "🧹 Pending task queues cleared successfully.", "system")
                
            self.send_json({"success": True, "active": autopilot_active})

        # ── /api/launch_business ──────────────────────────────────────────────
        elif path == "/api/launch_business":
            idea = body.get("idea", "")
            if not idea:
                self.send_json({"error": "Idea is required"}, 400)
                return
            
            append_chat("Tony", f"🚀 Received business idea: '{idea}'. Architecting master plan and dispatching tasks...", "tony")
            
            # Ask LLM to generate tasks
            agent_details = "\n            ".join([f"- {k} ({v.get('title', 'Specialist')}): {v.get('role', '')}" for k, v in active_agents.items()])
            sys_prompt = f"""You are Tony, the CEO. The user has provided a business idea. 
            Break this idea down into a comprehensive pipeline of EXACTLY 5 execution tasks that build an entire production-ready business.
            Assign each task to the most appropriate agent based on these available agents:
            {agent_details}
            
            Return ONLY a valid JSON array of objects. Example:
            [
              {{"agent_key": "wanda", "title": "Design UI for Idea", "description": "Write specs for..."}},
              {{"agent_key": "friday", "title": "Build App", "description": "Use npm create vite..."}}
            ]
            Make the descriptions highly detailed and actionable. No markdown formatting around the JSON array."""
            
            reply = query_llm(idea, sys_prompt)
            
            try:
                import json
                start_idx = reply.find('[')
                end_idx = reply.rfind(']')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = reply[start_idx:end_idx+1]
                    tasks_list = json.loads(json_str)
                    
                    for t in tasks_list:
                        new_id = str(uuid.uuid4())[:8]
                        agent_key = t.get("agent_key", "jarvis")
                        title = t.get("title", "Task")
                        desc = t.get("description", "")
                        
                        with state_lock:
                            tasks_db[new_id] = {
                                "id": new_id,
                                "title": f"[{agent_key.upper()}] {title}",
                                "description": desc,
                                "status": "assigned",
                                "agent": agent_key,
                                "comments": [],
                                "ts": int(time.time()),
                                "blocked": False
                            }
                            save_tasks()
                            
                        # Add to queue
                        with queue_lock:
                            sim_queue.append(new_id)
                            
                    append_chat("Tony", f"✅ Successfully orchestrated {len(tasks_list)} parallel tasks for the squad. Let's build a company!", "tony")
                    self.send_json({"success": True, "count": len(tasks_list)})
                else:
                    self.send_json({"error": "Failed to parse orchestrator plan"}, 500)
            except Exception as e:
                self.send_json({"error": f"Orchestration Error: {str(e)}"}, 500)

        else:
            self.send_json({"error": "not found"}, 404)

def worker_thread():
    while True:
        task_id = None
        with queue_lock:
            if sim_queue:
                task_id = sim_queue.pop(0)
        if task_id:
            try:
                run_task(task_id)
            except Exception as e:
                print(f"[WORKER ERROR] {e}")
        time.sleep(1)

def autopilot_thread():
    global autopilot_active
    while True:
        if autopilot_active:
            try:
                # Check if there are already too many pending tasks — if so, wait instead of flooding
                with state_lock:
                    pending_count = sum(1 for t in tasks_db.values() if t.get("status") in ["inbox", "assigned", "in_progress", "error"])
                    active_tasks = [t.get("title", "") for t in tasks_db.values() if t.get("status") in ["assigned", "in_progress", "waiting", "inbox", "error"]]
                    completed_tasks = [t.get("title", "") for t in tasks_db.values() if t.get("status") == "done"]
                
                if pending_count >= 5:
                    # Don't create more tasks when 5+ are already pending
                    time.sleep(60)
                    continue
                
                # Ask Tony to generate a task based on workspace state and current task queue
                sys_prompt = "You are Tony, the CEO. Review the current state of the business and the existing task lists, then generate 1 NEW strategic task for the squad. Output ONLY a valid JSON object: {\"task_title\": \"short title\", \"task_description\": \"detailed instructions\"}. Be concise and highly strategic. CRITICAL: Do NOT duplicate or re-generate any tasks that are already active, in progress, or recently completed."
                
                # List workspace files
                workspace_files = []
                if os.path.exists(WORKSPACE_DIR):
                    workspace_files = os.listdir(WORKSPACE_DIR)
                
                context = f"Current workspace files: {workspace_files}\nActive tasks in progress: {active_tasks}\nCompleted tasks: {completed_tasks}"
                
                reply = query_llm(context, sys_prompt)
                
                # If LLM failed, back off significantly to avoid error flooding
                if reply and "ERROR:" in reply:
                    print(f"[AUTOPILOT] LLM unavailable, backing off 120s", flush=True)
                    time.sleep(120)
                    continue
                
                try:
                    # Parse JSON from Tony's response
                    import re
                    json_match = re.search(r'\{.*\}', reply.replace('\\n', ' '), re.DOTALL)
                    if json_match:
                        task_data = json.loads(json_match.group(0))
                        title = task_data.get("task_title", "Strategic Initiative")
                        desc = task_data.get("task_description", "")
                        
                        # Check for duplicate titles before creating
                        is_duplicate = False
                        with state_lock:
                            for t in tasks_db.values():
                                if t.get("title", "").lower().strip() == title.lower().strip():
                                    is_duplicate = True
                                    break
                        
                        if is_duplicate:
                            print(f"[AUTOPILOT] Skipping duplicate task: {title}", flush=True)
                            time.sleep(30)
                            continue
                        
                        # Inject task into DB — use 'message' field so worker can find it
                        new_id = str(uuid.uuid4())[:8]
                        with state_lock:
                            tasks_db[new_id] = {
                                "id": new_id,
                                "title": title,
                                "message": f"[AUTOPILOT DIRECTIVE] {desc}",
                                "description": f"[AUTOPILOT DIRECTIVE] {desc}",
                                "status": "inbox",
                                "agent": "jarvis",
                                "assignee": None,
                                "comments": [],
                                "created_at": int(time.time()),
                                "ts": int(time.time()),
                                "blocked": False,
                                "is_continuous": False,
                                "deliverable": None,
                                "completed_at": None,
                                "error": None
                            }
                            save_tasks()
                            
                        # Broadcast notification
                        append_chat("Tony", f"New directive issued: **{title}**.", "tony")
                        
                        # Add to queue for jarvis to route
                        with queue_lock:
                            sim_queue.append(new_id)
                except Exception as json_err:
                    print(f"[AUTOPILOT PARSE ERROR] {json_err} on reply: {reply}")
                    
            except Exception as e:
                print(f"[AUTOPILOT ERROR] {e}")
                time.sleep(60)  # Back off on errors
                
            # Wait 60 seconds before generating the next task
            time.sleep(60)
        else:
            time.sleep(2)

threading.Thread(target=worker_thread, daemon=True).start()
threading.Thread(target=autopilot_thread, daemon=True).start()

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[STARTUP] Mission Control SaaS Server starting on http://localhost:8888", flush=True)
    print(f"[STARTUP] OpenClaw workspace: {WORKSPACE_DIR}", flush=True)
    print(f"[STARTUP] Active agents: {list(active_agents.keys())}", flush=True)
    server = HTTPServer(("0.0.0.0", 8888), MissionControlHandler)
    server.serve_forever()
