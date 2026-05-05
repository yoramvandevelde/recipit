import os
from dotenv import load_dotenv
import urllib.request, json

load_dotenv()

url = os.environ.get("HA_URL") + "/api/services/todo/add_item"
token = os.environ.get("HA_TOKEN")

print("URL:", url)
print("Token:", token[:10], "...")

payload = json.dumps({"entity_id": "todo.shopping_list", "item": "test"}).encode()
req = urllib.request.Request(url, data=payload, headers={
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}, method="POST")

try:
    res = urllib.request.urlopen(req, timeout=5)
    print("ok:", res.status)
except Exception as e:
    print("fout:", e)
