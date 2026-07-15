import urllib.request
import json
import sys

def test_endpoint(path, method="GET", data=None):
    url = f"http://localhost:8000{path}"
    try:
        req = urllib.request.Request(url, method=method)
        if data:
            req.add_header('Content-Type', 'application/json')
            req.data = json.dumps(data).encode('utf-8')
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            print(f"[OK] {method} {path} - {response.status}")
            try:
                parsed = json.loads(res_body)
                return True, parsed
            except:
                return True, res_body
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"[FAIL] {method} {path} - HTTP {e.code}: {body}")
        return False, body
    except Exception as e:
        print(f"[FAIL] {method} {path} - Exception: {e}")
        return False, str(e)

print("Starting Backend Tests...")
endpoints = [
    ("/api/stats", "GET", None),
    ("/api/projects", "GET", None),
    ("/api/squad", "GET", None),
    ("/api/settings", "GET", None),
]

success = True
for ep, method, data in endpoints:
    ok, _ = test_endpoint(ep, method, data)
    if not ok:
        success = False

# Test creating a project
ok, res = test_endpoint("/api/projects/new", "POST", {"name": "Test Project 123"})
if ok and isinstance(res, dict):
    p_id = res.get("project", {}).get("id")
    if p_id:
        test_endpoint("/api/projects/update", "POST", {"id": p_id, "name": "Updated Test Project"})
        test_endpoint("/api/projects/delete", "POST", {"id": p_id})

if success:
    print("All basic endpoints passed!")
else:
    sys.exit(1)
