import json

try:
    with open('C:/Users/DELL/.openclaw/mc_tasks.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
    t = db.get('bbcb85e9-5d5', {})
    print(f"Status: {t.get('status')}")
    print(f"Error: {t.get('error')}")
    for c in t.get('comments', []):
        print(f"- {c['sender']}: {c['text'][:150]}")
except Exception as e:
    print(e)
