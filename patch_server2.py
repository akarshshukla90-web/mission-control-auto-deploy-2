import re

path = r'c:\antigravity\mission-control\server.py'
try:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Update run_task call
    old_call = """
        agent_result = react_engine.execute_agent_loop(
            task_id=task_id, 
            message=message, 
            target_agent=target_agent, 
            query_llm_fn=query_llm, 
            append_chat_fn=append_chat, 
            save_comment_fn=save_comment
        )
        
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
"""

    new_call = """
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
            tasks_db[task_id]["status"] = "done"
            # Clear memory to save space if desired, but keep for now
            save_tasks()
        append_chat(target_agent["name"], summary_msg, target_key)
"""
    # Replace run_task block using exact match or regex
    # Wait, the exact block can have slight whitespace differences, so I will use a regex replacing everything after `save_comment` function def inside run_task
    regex_run_task = r'agent_result = react_engine\.execute_agent_loop\(.*?append_chat\(target_agent\["name"\], summary_msg, target_key\)'
    code = re.sub(regex_run_task, new_call.strip(), code, flags=re.DOTALL)


    # 2. Update override route
    old_override = """
        elif path == "/api/tasks/override":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "in_progress"
                    tasks_db[task_id]["blocked"] = False
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": "jarvis", "sender": "You",
                        "text": f"🔓 Unblock override sent for task {task_id[:12]}",
                        "ts": int(time.time()), "type": "override"
                    })
                    save_tasks()
            append_chat("Max", f"unblock {task_id[:6]}", None)
            append_chat("Jarvis", f"Received unblock override. Resuming task.", "jarvis")
            self.send_json({"success": True})
"""

    new_override = """
        elif path == "/api/tasks/override":
            task_id = body.get("task_id")
            with state_lock:
                if task_id in tasks_db:
                    tasks_db[task_id]["status"] = "in_progress"
                    tasks_db[task_id]["blocked"] = False
                    tasks_db[task_id]["comments"].append({
                        "id": str(uuid.uuid4())[:8],
                        "agent_key": "jarvis", "sender": "You",
                        "text": f"🔓 Unblock override sent for task {task_id[:12]}",
                        "ts": int(time.time()), "type": "override"
                    })
                    save_tasks()
            with queue_lock:
                if task_id not in sim_queue:
                    sim_queue.append(task_id)
            append_chat("Max", f"unblock {task_id[:6]}", None)
            append_chat("Jarvis", f"Received unblock override. Resuming task.", "jarvis")
            self.send_json({"success": True})
"""
    code = re.sub(r'elif path == "/api/tasks/override":.*?self\.send_json\({"success": True}\)', new_override.strip(), code, flags=re.DOTALL)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print('Server patched.')
except Exception as e:
    print('Error:', e)
