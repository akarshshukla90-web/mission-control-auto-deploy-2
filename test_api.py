import urllib.request
import json

url = "http://localhost:8888/api/send_chat"
data = json.dumps({"text": "Hello from python", "target": "jarvis"}).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as response:
        print("Response:", response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("Error:", e)
