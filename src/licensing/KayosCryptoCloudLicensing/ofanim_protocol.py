import hashlib
import time

def ativar_ofanim():
    timestamp = str(time.time()).encode()
    hash_digest = hashlib.sha256(timestamp).hexdigest().upper()
    return hash_digest[:8]  # Retorna os 8 primeiros caracteres do hash
