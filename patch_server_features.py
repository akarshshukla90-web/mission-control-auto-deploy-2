import re

path = r'c:\antigravity\mission-control\server.py'
try:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Add /api/tasks/{id}/chat endpoint
    task_chat_endpoint = """
        # ── /api/tasks/{id}/chat ───────────────────────────────────────────────
        elif path.startswith("/api/tasks/") and path.endswith("/chat") and method == "POST":
            task_id = path.split("/")[3]
            text = body.get("text", "")
            with state_lock:
                if task_id in tasks_db:
                    # Append as a User message in the agent_memory
                    if "agent_memory" not in tasks_db[task_id]:
                        tasks_db[task_id]["agent_memory"] = []
                    tasks_db[task_id]["agent_memory"].append({"role": "user", "content": f"User guidance: {text}"})
                    
                    # Also log it in the UI comments
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": "jarvis", "sender": "You",
                        "text": f"💬 {text}",
                        "ts": int(time.time()), "type": "note"
                    })
                    
                    # If it was blocked, unblock it so it can process the message
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
        elif path == "/api/chat/message" and method == "POST":
            text = body.get("text", "")
            # Direct LLM call acting as Antigravity Mode
            sys = "You are Antigravity, a helpful AI assistant. Be concise."
            reply = query_llm(text, sys)
            self.send_json({"reply": reply})
"""
    if "/api/tasks/" not in code or "tasks_db[task_id][\"agent_memory\"].append" not in code:
        code = re.sub(r'# ── /api/settings', task_chat_endpoint.strip() + '\n\n        # ── /api/settings', code)

    # 2. Add 24/7 task logic to run_task
    # Replace the trivial check with the new continuous check
    trivial_old = """
        check_sys = "If the prompt is a simple greeting ('hello', 'hi'), reply ONLY with 'TRIVIAL'. Otherwise 'TASK'."
        is_trivial = query_llm(f"Prompt: {message}", check_sys, max_tokens=10) or "TASK"
        
        if "TRIVIAL" in is_trivial.upper():
"""
    
    trivial_new = """
        check_sys = "Analyze the prompt. If it is a simple greeting ('hello', 'hi'), reply ONLY with 'TRIVIAL'. If it asks to run continuously, monitor 24/7, or loop infinitely, reply ONLY with '24_7'. Otherwise reply 'TASK'."
        analysis = query_llm(f"Prompt: {message}", check_sys, max_tokens=10) or "TASK"
        
        is_continuous = "24_7" in analysis.upper()
        with state_lock:
            tasks_db[task_id]["is_continuous"] = is_continuous
        
        if "TRIVIAL" in analysis.upper():
"""
    code = code.replace(trivial_old.strip(), trivial_new.strip())

    # And handle continuous loop at the end of run_task instead of "done"
    end_task_old = """
            tasks_db[task_id]["status"] = "done"
            # Clear memory to save space if desired, but keep for now
            save_tasks()
        append_chat(target_agent["name"], summary_msg, target_key)
"""
    end_task_new = """
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
"""
    code = code.replace(end_task_old.strip(), end_task_new.strip())

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("server.py patched with API routes and 24/7 logic.")
except Exception as e:
    print("Error:", e)
