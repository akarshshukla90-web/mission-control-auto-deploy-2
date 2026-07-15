import re

path = r'c:\antigravity\mission-control\server.py'
try:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    worker_code = """
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

threading.Thread(target=worker_thread, daemon=True).start()

# ─── MAIN
"""
    if "def worker_thread" not in code:
        code = code.replace("# ─── MAIN", worker_code.strip())
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        print('Worker thread restored.')
    else:
        print('Worker thread already exists.')
except Exception as e:
    print('Error:', e)
