import urllib.request
import json
import time

def broadcast_task(message):
    url = "http://localhost:8888/api/broadcast"
    data = {
        "title": "Automated Test",
        "message": message,
        "priority": "high",
        "assignee": "jarvis",
        "project_id": "test_env"
    }
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={'Content-Type': 'application/json'}, method="POST")
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        print(f"Error broadcasting task: {e}")
        return None

def run_tests():
    tasks = [
        "Write a 10 line python script that calculates the fibonacci sequence and execute it to verify it works.",
        "Analyze the dashboard CSS for contrast issues and tell me the findings.",
        "List 3 open source MCP servers from github."
    ]
    
    print("Starting Software Company Simulation...")
    for t in tasks:
        print(f"Broadcasting: {t}")
        res = broadcast_task(t)
        print(f"Result: {res}")
        time.sleep(2)
        
    print("Tasks broadcasted successfully. Check the Mission Control dashboard for agent activity.")

if __name__ == "__main__":
    run_tests()
