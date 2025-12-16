# Python Example

```python
import requests

TOKEN = "<enterprise-token>"
BASE_URL = "https://api.kayoscrypto.dev/v1"

resp = requests.post(
    f"{BASE_URL}/entropy/stream",
    headers={"Authorization": f"Bearer {TOKEN}"},
    json={"bytes": 4096}
)
resp.raise_for_status()

payload = resp.json()
print("entropy", payload["data"])  # base64 encoded stream
print("sator_score", payload["sator"]["score"])
```
