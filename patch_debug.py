import re

# PATCH SERVER
path = r'c:\antigravity\mission-control\server.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# Add debug to query_llm
old_q = 'def query_llm(prompt, system_prompt="You are a helpful assistant.", max_tokens=1500, model_override=None, messages=None):\n    settings = load_settings()'
new_q = 'def query_llm(prompt, system_prompt="You are a helpful assistant.", max_tokens=1500, model_override=None, messages=None):\n    print(f"[DEBUG] query_llm called. messages={bool(messages)} prompt={bool(prompt)}", flush=True)\n    settings = load_settings()'
code = code.replace(old_q, new_q)

# Add debug to OmniRoute success
old_omni = 'resp = json.loads(res.read().decode("utf-8"))\n            return resp["choices"][0]["message"]["content"].strip()'
new_omni = 'resp = json.loads(res.read().decode("utf-8"))\n            print("[DEBUG] OmniRoute success!", flush=True)\n            return resp["choices"][0]["message"]["content"].strip()'
code = code.replace(old_omni, new_omni)

# Add debug to NVIDIA success
old_nvi = 'usage = resp.get("usage", {})\n            token_usage["total"] += usage.get("total_tokens", 0)\n            return resp["choices"][0]["message"]["content"].strip()'
new_nvi = 'usage = resp.get("usage", {})\n            print("[DEBUG] NVIDIA success!", flush=True)\n            token_usage["total"] += usage.get("total_tokens", 0)\n            return resp["choices"][0]["message"]["content"].strip()'
code = code.replace(old_nvi, new_nvi)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Debug patched in server.py")
