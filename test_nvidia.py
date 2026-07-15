import urllib.request
import json
import time

api_key = "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"
url = "https://integrate.api.nvidia.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
data = {
    "model": "meta/llama-3.1-8b-instruct",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    "temperature": 0.7,
    "max_tokens": 1500
}

req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers, method="POST")
try:
    print("Testing NVIDIA NIM...")
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=30) as res:
        resp = json.loads(res.read().decode("utf-8"))
        print("Success in", round(time.time() - t0, 2), "seconds!")
        print(resp["choices"][0]["message"]["content"])
except Exception as e:
    print("FAILED in", round(time.time() - t0, 2), "seconds!")
    print(e)
