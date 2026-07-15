import re

path = r'c:\antigravity\mission-control\react_engine.py'
try:
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()

    new_prompt = """
AVAILABLE TOOLS:
1. run_command
   - Description: Executes a terminal command on the host machine.
   - Arguments: "command" (string)
   - Example: <tool_call>{"name": "run_command", "args": {"command": "npm install"}}</tool_call>

2. write_file
   - Description: Creates or overwrites a file.
   - Arguments: "path" (string), "content" (string)
   - Example: <tool_call>{"name": "write_file", "args": {"path": "workspace/script.py", "content": "print('hello')"}}</tool_call>

3. read_file
   - Description: Reads a file from the host machine.
   - Arguments: "path" (string)
   - Example: <tool_call>{"name": "read_file", "args": {"path": "workspace/data.json"}}</tool_call>

4. request_unblock
   - Description: Call this ONLY if you hit a hard barrier (like needing human login, verification, or an explicit override) and cannot proceed automatically.
   - Arguments: "reason" (string)
   - Example: <tool_call>{"name": "request_unblock", "args": {"reason": "Need human to complete OAuth login"}}</tool_call>

5. finish
   - Description: Call this when you have fully completed the task and generated the final deliverable.
   - Arguments: "summary" (string)
   - Example: <tool_call>{"name": "finish", "args": {"summary": "I have completed the task."}}</tool_call>
"""
    code = re.sub(r'AVAILABLE TOOLS:.*?5\. finish.*?<\/tool_call>', new_prompt.strip(), code, flags=re.DOTALL)
    if 'request_unblock' not in code:
        code = re.sub(r'AVAILABLE TOOLS:.*?4\. finish.*?<\/tool_call>', new_prompt.strip(), code, flags=re.DOTALL)

    loop_patch = """
def execute_agent_loop(task, target_agent, query_llm_fn, append_chat_fn, save_comment_fn):
    import os, json
    
    task_id = task["id"]
    message = task["message"]
    
    settings_path = os.path.expanduser("~/.openclaw/mc_settings.json")
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    except:
        settings = {}
        
    custom_sys = settings.get("system_prompt", "")
    rules = settings.get("workspace_rules", "")
    
    base_prompt = custom_sys if custom_sys else REACT_PROMPT
    system_prompt = f"You are {target_agent['name']}, {target_agent['title']}. {target_agent['about']}\\n\\nWORKSPACE RULES:\\n{rules}\\n\\n{base_prompt}"
    
    # Load memory if resuming, else initialize
    messages = task.get("agent_memory", [])
    if not messages:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {message}"}
        ]
"""
    code = re.sub(r'def execute_agent_loop\(task_id, message, target_agent.*?\]', loop_patch.strip(), code, flags=re.DOTALL)

    exec_patch = """
                if name == "finish":
                    final_summary = args.get("summary", "Finished.")
                    return {"status": "finished", "summary": final_summary}
                    
                elif name == "request_unblock":
                    reason = args.get("reason", "Awaiting human verification.")
                    return {"status": "blocked", "reason": reason, "memory": messages}

                elif name == "run_command":
"""
    code = re.sub(r'if name == "finish":.*?elif name == "run_command":', exec_patch.strip(), code, flags=re.DOTALL)

    # Return finished instead of string at the end
    ret_patch = """
    return {"status": "finished", "summary": final_summary}
"""
    code = re.sub(r'return final_summary\s*$', ret_patch.strip(), code, flags=re.DOTALL)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print('React engine patched.')
except Exception as e:
    print('Error:', e)
