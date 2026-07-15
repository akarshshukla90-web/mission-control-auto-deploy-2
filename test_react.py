import sys
import os

# Set up paths so we can import server and react_engine
sys.path.append(r'c:\antigravity\mission-control')
import server
import react_engine

task = {
    "id": "test-123",
    "message": "Print the current working directory and read server.py.",
    "agent_memory": []
}

target_agent = {
    "name": "Tony",
    "title": "Full-Stack Engineer",
    "about": "You write code."
}

def mock_append(sender, text, agent_key=None):
    print(f"[CHAT] {sender}: {text}")

def mock_save(t_id, sender_name, text, msg_type):
    print(f"[COMMENT] {sender_name}: {text}")

print("Testing execute_agent_loop directly...")
try:
    res = react_engine.execute_agent_loop(
        task=task,
        target_agent=target_agent,
        query_llm_fn=server.query_llm,
        append_chat_fn=mock_append,
        save_comment_fn=mock_save
    )
    print("RESULT:", res)
except Exception as e:
    print("EXCEPTION:", e)
