import re

path = r'c:\antigravity\mission-control\server.py'
try:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
        
    archive_route = """
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
"""

    if "/api/tasks/archive" not in code:
        code = code.replace("# ── /api/tasks/cancel", archive_route.strip() + "\n\n        # ── /api/tasks/cancel")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print('Backend patched.')
    else:
        print('Route already exists.')
except Exception as e:
    print('Error:', e)
