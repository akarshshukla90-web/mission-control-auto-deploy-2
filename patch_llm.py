import re

# --- 1. PATCH SERVER.PY ---
path = r'c:\antigravity\mission-control\server.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

old_func_def = 'def query_llm(prompt, system_prompt="You are a helpful assistant.", max_tokens=1500, model_override=None):'
new_func_def = 'def query_llm(prompt, system_prompt="You are a helpful assistant.", max_tokens=1500, model_override=None, messages=None):'
code = code.replace(old_func_def, new_func_def)

# Patch the messages list construction for OmniRoute
old_msgs = """            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],"""
new_msgs = """            "messages": messages if messages else [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],"""
code = code.replace(old_msgs, new_msgs) # Note: replaces both OmniRoute and NVIDIA block since they are identical!

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)


# --- 2. PATCH REACT_ENGINE.PY ---
path_engine = r'c:\antigravity\mission-control\react_engine.py'
with open(path_engine, 'r', encoding='utf-8') as f:
    engine_code = f.read()

# Replace the loop call inside execute_agent_loop
old_loop_code = """        full_prompt = ""
        for m in messages:
            if m["role"] != "system":
                full_prompt += f"\\n\\n[{m['role'].upper()}]:\\n{m['content']}"
        
        try:
            response = query_llm_fn(full_prompt, system_prompt=system_prompt, max_tokens=1500)"""

new_loop_code = """        try:
            # We now pass the native messages array directly instead of stringifying!
            response = query_llm_fn(prompt=None, system_prompt=system_prompt, max_tokens=1500, messages=messages)"""
engine_code = engine_code.replace(old_loop_code, new_loop_code)

# Replace the tool parsing to enforce it
old_tool_parsing = """        # Extract <tool_call>
        if "<tool_call>" in response:
            try:
                start = response.find("<tool_call>") + len("<tool_call>")
                end = response.find("</tool_call>")
                tool_json_str = response[start:end].strip()
                tool_call = json.loads(tool_json_str)
                name = tool_call.get("name")
                args = tool_call.get("args", {})
                
                # Chat UI update
                append_chat_fn(target_agent["name"], f"🔧 Running tool: {name}", "dev")
                save_comment_fn(task_id, target_agent["name"], f"Executing tool: {name}\\nArguments: {json.dumps(args)[:100]}...", "dev")

                obs = ""
                if name == "finish":
                    final_summary = args.get("summary", "Finished.")
                    return {"status": "finished", "summary": final_summary}
                    
                elif name == "request_unblock":
                    reason = args.get("reason", "Awaiting human verification.")
                    return {"status": "blocked", "reason": reason, "memory": messages}

                elif name == "run_command":
                    cmd = args.get("command", "")
                    try:
                        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                        obs = f"STDOUT:\\n{res.stdout}\\nSTDERR:\\n{res.stderr}"
                    except Exception as e:
                        obs = f"Command failed: {e}"
                        
                elif name == "write_file":
                    path = args.get("path", "")
                    content = args.get("content", "")
                    try:
                        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(content)
                        obs = f"Successfully wrote to {path}"
                    except Exception as e:
                        obs = f"Failed to write file: {e}"
                        
                elif name == "read_file":
                    path = args.get("path", "")
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            obs = f.read()
                    except Exception as e:
                        obs = f"Failed to read file: {e}"
                else:
                    obs = f"Unknown tool: {name}"

                messages.append({"role": "user", "content": f"<tool_response>\\n{obs}\\n</tool_response>"})
                save_comment_fn(task_id, "System", f"Tool Output:\\n{obs[:200]}...", "note")
            except Exception as e:
                messages.append({"role": "user", "content": f"Failed to parse or execute tool_call: {e}"})
                save_comment_fn(task_id, "System", f"Tool Error: {e}", "note")"""

new_tool_parsing = """        # Extract <tool_call>
        if "<tool_call>" in response:
            try:
                start = response.find("<tool_call>") + len("<tool_call>")
                end = response.find("</tool_call>")
                tool_json_str = response[start:end].strip()
                tool_call = json.loads(tool_json_str)
                name = tool_call.get("name")
                args = tool_call.get("args", {})
                
                # Chat UI update
                append_chat_fn(target_agent["name"], f"🔧 Running tool: {name}", "dev")
                save_comment_fn(task_id, target_agent["name"], f"Executing tool: {name}\\nArguments: {json.dumps(args)[:100]}...", "dev")

                obs = ""
                if name == "finish":
                    final_summary = args.get("summary", "Finished.")
                    return {"status": "finished", "summary": final_summary}
                    
                elif name == "request_unblock":
                    reason = args.get("reason", "Awaiting human verification.")
                    return {"status": "blocked", "reason": reason, "memory": messages}

                elif name == "run_command":
                    cmd = args.get("command", "")
                    try:
                        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd="workspace")
                        obs = f"STDOUT:\\n{res.stdout}\\nSTDERR:\\n{res.stderr}"
                    except Exception as e:
                        obs = f"Command failed: {e}"
                        
                elif name == "write_file":
                    path = args.get("path", "")
                    content = args.get("content", "")
                    try:
                        full_path = os.path.join("workspace", path)
                        os.makedirs(os.path.dirname(os.path.abspath(full_path)) or ".", exist_ok=True)
                        with open(full_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        obs = f"Successfully wrote to {full_path}"
                    except Exception as e:
                        obs = f"Failed to write file: {e}"
                        
                elif name == "read_file":
                    path = args.get("path", "")
                    try:
                        full_path = os.path.join("workspace", path)
                        with open(full_path, "r", encoding="utf-8") as f:
                            obs = f.read()
                    except Exception as e:
                        obs = f"Failed to read file: {e}"
                else:
                    obs = f"Unknown tool: {name}"

                messages.append({"role": "user", "content": f"<tool_response>\\n{obs}\\n</tool_response>"})
                save_comment_fn(task_id, "System", f"Tool Output:\\n{obs[:200]}...", "note")
            except Exception as e:
                messages.append({"role": "user", "content": f"SYSTEM ERROR: Failed to parse or execute tool_call: {e}. Please ensure your output contains a valid JSON string inside <tool_call> tags."})
                save_comment_fn(task_id, "System", f"Tool Error: {e}", "note")
        else:
            # STRICT ENFORCEMENT
            messages.append({
                "role": "user", 
                "content": "SYSTEM ERROR: You did not output a <tool_call> block. You MUST use a tool to proceed. If you have finished the task, use the 'finish' tool. Do not just reply with text."
            })
            save_comment_fn(task_id, "System", f"Warning: Agent failed to use a tool. Retrying...", "note")"""

engine_code = engine_code.replace(old_tool_parsing, new_tool_parsing)

with open(path_engine, 'w', encoding='utf-8') as f:
    f.write(engine_code)

print("Patch applied to server.py and react_engine.py successfully.")
