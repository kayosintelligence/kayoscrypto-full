import random
import string
from datetime import datetime, timezone

# Roda de Ezequiel aplicada ao núcleo KayosCrypto: algoritmo simbiótico de entropia funcional
def rodar_quantum(entropia_nivel=8):
    base = string.ascii_uppercase + string.digits + "@#&*"
    chave_simbolica = ''.join(random.choices(base, k=entropia_nivel))
    timestamp = datetime.now(timezone.utc).isoformat()
    
    return {
        "roda": chave_simbolica,
        "timestamp": timestamp
    }
