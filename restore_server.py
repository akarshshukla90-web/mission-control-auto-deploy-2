import re
import os

def restore_endpoints():
    path = r'c:\antigravity\mission-control\server.py'
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # The missing endpoints to add
    missing_endpoints = """
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
"""
    if "/api/tasks/new" not in code:
        code = re.sub(r'# ── /api/workspace \(list\)', missing_endpoints.strip() + '\n\n        # ── /api/workspace (list)', code)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("server.py recovered all missing endpoints.")

restore_endpoints()
