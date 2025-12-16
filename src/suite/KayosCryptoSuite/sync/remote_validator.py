# sync/remote_validator.py

import requests

def validate_license_remotely(api_url: str, license_data: dict) -> bool:
    try:
        response = requests.post(f"{api_url}/validate", json=license_data)
        return response.status_code == 200 and response.json().get("valid", False)
    except Exception:
        return False
