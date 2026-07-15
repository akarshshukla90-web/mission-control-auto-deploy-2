import re
import os

filepath = r"c:\antigravity\mission-control\server.py"

with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Replace query_nvidia definition with query_llm
new_query_llm = """
def query_llm(prompt, system_prompt="You are a helpful assistant.", max_tokens=1500, model_override=None):
    settings = load_settings()
    # Try OmniRoute / OpenClaw Gateway first
    try:
        url = "http://localhost:20128/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": "Bearer any_token"}
        data = {
            "model": "claude-3-haiku", # Default OmniRoute model
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens
        }
        import urllib.request, json
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as res:
            resp = json.loads(res.read().decode("utf-8"))
            return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[LLM] OmniRoute failed: {e}. Falling back to NVIDIA NIM.", flush=True)
    
    # Fallback to NVIDIA
    api_key = settings.get("api_key", NVIDIA_API_KEY)
    model = model_override or settings.get("model", NVIDIA_MODEL)
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    try:
        import urllib.request, json
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as res:
            resp = json.loads(res.read().decode("utf-8"))
            usage = resp.get("usage", {})
            token_usage["total"] += usage.get("total_tokens", 0)
            return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[NVIDIA ERROR] model={model} err={e}", flush=True)
        if model != NVIDIA_FALLBACK:
            return query_llm(prompt, system_prompt, max_tokens, model_override=NVIDIA_FALLBACK)
        return None
"""
# Replace the query_nvidia block using regex
code = re.sub(r'def query_nvidia\(.*?\n        return None\n', new_query_llm.strip() + '\n', code, flags=re.DOTALL)


# 2. Rewrite run_task to be dynamic
new_run_task = """
def run_task(task_id):
    import os, uuid, time
    task = tasks_db.get(task_id)
    if not task: return
    message = task["message"]
    print(f"[WORKER] Starting dynamic task {task_id}: {message[:60]}", flush=True)

    try:
        # Check trivial
        check_sys = "If the prompt is a simple greeting ('hello', 'hi'), reply ONLY with 'TRIVIAL'. Otherwise 'TASK'."
        is_trivial = query_llm(f"Prompt: {message}", check_sys, max_tokens=10) or "TASK"
        
        if "TRIVIAL" in is_trivial.upper():
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
        planner_sys = "You are Jarvis. Respond ONLY with the single lowercase key of the best specialist for this task (quill, pepper, loki, fury, groot, rob, shuri, friday, wanda, vision) or 'none'."
        decision_raw = query_llm(f"Task: {message}", planner_sys, max_tokens=10) or "shuri"
        target_key = decision_raw.strip().lower().split()[0]
        if target_key not in active_agents and target_key in SPECIALIST_TEMPLATES:
            with state_lock:
                active_agents[target_key] = dict(SPECIALIST_TEMPLATES[target_key])
                save_agents()
        target_agent = active_agents.get(target_key, CORE_AGENTS.get(target_key, CORE_AGENTS["shuri"]))

        # Jarvis delegation msg
        jarvis_msg = query_llm(f"Write a 1-sentence delegation message assigning '{message}' to {target_agent['name']} ({target_agent['title']}).", "You are Jarvis.")
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

        # 2. Agent executes the task via OmniRoute LLM
        agent_sys = f"You are {target_agent['name']}, {target_agent['title']}. Execute this task comprehensively and professionally."
        agent_result = query_llm(message, agent_sys, max_tokens=3000)
        
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
            tasks_db[task_id]["status"] = "done"
            save_tasks()
        append_chat(target_agent["name"], summary_msg, target_key)

    except Exception as e:
        print(f"[WORKER ERROR] {e}", flush=True)
        with state_lock:
            tasks_db[task_id]["status"] = "error"
            tasks_db[task_id]["error"] = str(e)
            save_tasks()
"""

# Replace the run_task block using regex
# We find the start of run_task up to the end of the try block or another def
code = re.sub(r'def run_task\(task_id\):.*?(?=\ndef [a-zA-Z_])', new_run_task.strip() + '\n', code, flags=re.DOTALL)

# Replace any remaining query_nvidia with query_llm
code = code.replace("query_nvidia", "query_llm")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Backend engine refactored successfully.")
