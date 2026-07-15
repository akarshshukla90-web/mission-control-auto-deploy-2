import re

path = r'c:\antigravity\mission-control\react_engine.py'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update REACT_PROMPT
old_tools = """4. request_unblock"""
new_tools = """4. search_web
   - Description: Searches the web for information using DuckDuckGo. Use this to find documentation, tutorials, or learn how to do something you don't know.
   - Arguments: "query" (string)
   - Example: <tool_call>{"name": "search_web", "args": {"query": "how to scrape linkedin selenium python"}}</tool_call>

5. read_url
   - Description: Reads text content from a specific URL. Use this to read documentation or search results.
   - Arguments: "url" (string)
   - Example: <tool_call>{"name": "read_url", "args": {"url": "https://example.com/docs"}}</tool_call>

6. request_unblock"""

code = code.replace(old_tools, new_tools)

# 2. Add tool handling logic
old_logic = """                elif name == "read_file":
                    path = args.get("path", "")
                    try:
                        full_path = os.path.join("workspace", path)
                        with open(full_path, "r", encoding="utf-8") as f:
                            obs = f.read()
                    except Exception as e:
                        obs = f"Failed to read file: {e}"
                else:"""
new_logic = """                elif name == "read_file":
                    path = args.get("path", "")
                    try:
                        full_path = os.path.join("workspace", path)
                        with open(full_path, "r", encoding="utf-8") as f:
                            obs = f.read()
                    except Exception as e:
                        obs = f"Failed to read file: {e}"
                elif name == "search_web":
                    query = args.get("query", "")
                    try:
                        from duckduckgo_search import DDGS
                        with DDGS() as ddgs:
                            results = [r for r in ddgs.text(query, max_results=5)]
                        if results:
                            obs = "\\n".join([f"[{i+1}] {r['title']} ({r['href']})\\n{r['body']}" for i, r in enumerate(results)])
                        else:
                            obs = "No results found."
                    except Exception as e:
                        obs = f"Web search failed: {e}"
                elif name == "read_url":
                    url = args.get("url", "")
                    try:
                        import urllib.request
                        from bs4 import BeautifulSoup
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=10) as response:
                            soup = BeautifulSoup(response.read(), 'html.parser')
                            text = soup.get_text(separator=' ', strip=True)
                            obs = text[:5000] + ("...[TRUNCATED]" if len(text) > 5000 else "")
                    except Exception as e:
                        obs = f"Failed to read URL: {e}"
                else:"""

code = code.replace(old_logic, new_logic)

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)

print("react_engine.py patched with web search tools.")
