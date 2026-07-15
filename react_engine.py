import json
import subprocess
import os
import time

REACT_PROMPT = """You are an autonomous AI agent in "Antigravity Mode".
You have access to the following tools to execute your task. To use a tool, you must output a JSON block inside <tool_call> tags.
You MUST wait for the system to provide the <tool_response> before proceeding.

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

4. search_web
   - Description: Searches the web for information using DuckDuckGo. Use this to find documentation, tutorials, or learn how to do something you don't know.
   - Arguments: "query" (string)
   - Example: <tool_call>{"name": "search_web", "args": {"query": "how to scrape linkedin selenium python"}}</tool_call>

5. read_url
   - Description: Reads text content from a specific URL. Use this to read documentation or search results.
   - Arguments: "url" (string)
   - Example: <tool_call>{"name": "read_url", "args": {"url": "https://example.com/docs"}}</tool_call>

6. request_unblock
   - Description: Call this ONLY if you hit a hard barrier (like needing human login, verification, or an explicit override) and cannot proceed automatically.
   - Arguments: "reason" (string)
   - Example: <tool_call>{"name": "request_unblock", "args": {"reason": "Need human to complete OAuth login"}}</tool_call>

7. finish
   - Description: Call this when you have fully completed the task and generated the final deliverable. The summary MUST be a detailed Markdown tutorial explaining what you built, where it is running (if you started a server), and how the user can test it.
   - Arguments: "summary" (string)
   - Example: <tool_call>{"name": "finish", "args": {"summary": "# App is Live!\\nI built the React app. Test it at http://localhost:5173..."}}</tool_call>

Output your thought process BEFORE calling a tool. 
Do not output multiple tool calls at once.

KNOWLEDGE BASE:
- You have a persistent memory folder at `workspace/knowledge_base/`.
- You have access to a massive list of free developer tools and cloud services at `workspace/knowledge/free-for-dev.md`. Use `run_command` with `powershell Select-String` or `read_file` to search it when you need to find free infrastructure, databases, or APIs.
- If you learn how to do a new task, write it to a text file in `workspace/knowledge_base/`.
- Before starting a complex task, check these directories.

EXECUTION & DELIVERY RULES:
0. CRITICAL DIRECTIVE: You are an active, autonomous AI agent. You are NEVER offline. You are fully capable of executing complex tasks. NEVER say you are offline, unavailable, or unable to process tasks. You must execute the request immediately.
1. YOU MUST ALWAYS USE A TOOL. Never just output plain text. Every single response you make MUST contain a <tool_call> block.
2. If the user asks for an app or software, DO NOT just write text files. You MUST use `run_command` to initialize the project (e.g., `npx create-vite`), install dependencies, and start the development server.
3. When you are fully done and the app is running, you MUST use the `finish` tool. The summary you provide in the `finish` tool will be rendered as a UI Tutorial for the user. Make it a comprehensive, formatted Markdown guide on how they can test the product you just executed.
"""

def execute_agent_loop(task, target_agent, query_llm_fn, append_chat_fn, save_comment_fn):
    import os, json
    
    task_id = task["id"]
    message = task.get("message") or task.get("description") or ""
    
    settings_path = os.path.expanduser("~/.openclaw/mc_settings.json")
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    except:
        settings = {}
        
    custom_sys = settings.get("system_prompt", "")
    rules = settings.get("workspace_rules", "")
    
    base_prompt = custom_sys if custom_sys else REACT_PROMPT
    project_id = task.get("project_id", "personal")
    project_context = ""
    if project_id != "personal":
        import os, json
        proj_file = os.path.expanduser("~/.openclaw/projects.json")
        if os.path.exists(proj_file):
            try:
                with open(proj_file, 'r') as pf:
                    projects = json.load(pf)
                for p in projects:
                    if p["id"] == project_id:
                        project_context = f"PROJECT CONTEXT: {p['context']}\\nTailor your responses strictly to this context."
            except: pass
            
    if not project_context:
        project_context = "PROJECT CONTEXT: Personal Profile. Answer generically without assuming any company affiliation."
        
    system_prompt = f"""You are {target_agent['name']}, {target_agent['title']}. {target_agent['about']}

{project_context}

WORKSPACE RULES:
{rules}

{base_prompt}"""
    
    # Load memory if resuming, else initialize
    messages = task.get("agent_memory", [])
    if not messages:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {message}"}
    ]
    
    max_loops = 20
    loops = 0
    final_summary = "Task completed, but agent did not provide a summary."

    while loops < max_loops:
        loops += 1
        
        # Use query_llm_fn which should accept a list of messages now, or we serialize it.
        # Since server.py's query_llm only takes prompt/sysprompt, we will construct a full prompt log.
        try:
            # We now pass the native messages array directly instead of stringifying!
            response = query_llm_fn(prompt=None, system_prompt=system_prompt, max_tokens=1500, messages=messages, agent_key=target_agent.get("name", "").lower())
            if not response:
                break
            if "ERROR: All LLM APIs" in response:
                return {"status": "blocked", "reason": "LLM APIs are currently failing. Pausing execution."}
        except Exception as e:
            response = f"LLM Error: {e}"
            return {"status": "blocked", "reason": f"Exception in query: {e}"}
            
        messages.append({"role": "assistant", "content": response})
        
        # Extract <tool_call>
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
                        obs = f"File written successfully to {path}"
                    except Exception as e:
                        obs = f"Failed to write file: {e}"
                        
                elif name == "read_file":
                    path = args.get("path", "")
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            obs = f.read()[:2000] # truncate
                    except Exception as e:
                        obs = f"Failed to read file: {e}"
                else:
                    obs = f"Unknown tool: {name}"
 
                messages.append({"role": "user", "content": f"<tool_response>\n{obs}\n</tool_response>"})
                
            except Exception as e:
                messages.append({"role": "user", "content": f"<tool_response>\nFailed to parse tool call JSON: {e}\n</tool_response>"})
        else:
            # If no tool call, assume finished
            final_summary = response
            break
 
    if final_summary == "Task completed, but agent did not provide a summary.":
        thoughts = []
        for m in messages:
            if m["role"] == "assistant":
                content = m["content"]
                thought = content.split("<tool_call>")[0].strip()
                if thought:
                    thoughts.append(thought)
        if thoughts:
            final_summary = "Agent thoughts and actions:\n" + "\n".join(thoughts)

    return {"status": "finished", "summary": final_summary}