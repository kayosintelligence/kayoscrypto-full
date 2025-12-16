# sync/sync_controller.py

import requests

def heartbeat_check(api_url: str, license_id: str) -> dict:
    try:
        response = requests.get(f"{api_url}/heartbeat/{license_id}")
        return response.json()
    except Exception:
        return {"status": "offline"}
