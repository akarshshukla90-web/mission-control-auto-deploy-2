import re

# Patch server.py
with open(r"c:\antigravity\mission-control\server.py", "r", encoding="utf-8") as f:
    server_code = f.read()

cancel_route = """
        # ── /api/tasks/cancel ──────────────────────────────────────────────────
        elif path == "/api/tasks/cancel":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "cancelled"
                    tasks_db[task_id]["blocked"] = False
                    save_tasks()
            with queue_lock:
                if task_id in sim_queue:
                    sim_queue.remove(task_id)
            append_chat("System", f"🚫 Task cancelled: {task_id}", None)
            self.send_json({"success": True})
"""

if "/api/tasks/cancel" not in server_code:
    server_code = server_code.replace("# ── /api/tasks/delete", cancel_route.strip() + "\n\n        # ── /api/tasks/delete")
    with open(r"c:\antigravity\mission-control\server.py", "w", encoding="utf-8") as f:
        f.write(server_code)

# Patch index.html
with open(r"c:\antigravity\mission-control\static\index.html", "r", encoding="utf-8") as f:
    html_code = f.read()

cancel_js = """
async function cancelTask(taskId) {
  if (!confirm('Are you sure you want to cancel this task? It will stop execution.')) return;
  const res = await api('/api/tasks/cancel', 'POST', { task_id: taskId });
  if (res.success) {
    toast('✅ Task cancelled.');
    closeDrawers();
    await refreshAll();
  } else {
    toast('❌ ' + res.error);
  }
}
"""

if "function cancelTask" not in html_code:
    html_code = html_code.replace("async function deleteTask", cancel_js.strip() + "\n\nasync function deleteTask")
    with open(r"c:\antigravity\mission-control\static\index.html", "w", encoding="utf-8") as f:
        f.write(html_code)

print("UI fixes applied successfully.")
