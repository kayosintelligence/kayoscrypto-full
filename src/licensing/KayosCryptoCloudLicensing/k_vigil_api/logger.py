import os
import json
import hashlib
from datetime import datetime, timezone

def registrar_log(ip, endpoint, metodo, status, dados_extra=None):
    log_dir = "logs/logs_auditaveis"
    os.makedirs(log_dir, exist_ok=True)

    log = {
    "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": ip,
        "endpoint": endpoint,
        "metodo": metodo,
        "status": status,
        "dados_extra": dados_extra or {}
    }

    hash_integridade = hashlib.sha256(
        json.dumps(log, sort_keys=True).encode()
    ).hexdigest()
    log["hash_integridade"] = hash_integridade

    filename = f"log_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}.json"
    filepath = os.path.join(log_dir, filename)

    with open(filepath, "w") as f:
        json.dump(log, f, indent=4)
