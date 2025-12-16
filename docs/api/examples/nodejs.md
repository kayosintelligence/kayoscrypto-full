# Node.js Example

```javascript
import fetch from "node-fetch";

const TOKEN = process.env.KAYOSCRYPTO_TOKEN;
const BASE_URL = "https://api.kayoscrypto.dev/v1";

const response = await fetch(`${BASE_URL}/entropy/stream`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${TOKEN}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({ bytes: 4096 })
});

if (!response.ok) {
  throw new Error(`Request failed: ${response.status}`);
}

const payload = await response.json();
console.log("entropy", payload.data);
console.log("sator_score", payload.sator.score);
```
