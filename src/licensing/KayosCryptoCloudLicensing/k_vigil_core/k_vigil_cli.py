#  Arquivo: k_vigil_core/k_vigil_cli.py

import sys
import uuid
from core_license_engine import gerar_chave_licenca, validar_licenca

def exibir_ajuda():
    print("""
Uso:
  python3 k_vigil_cli.py gerar <uuid>
  python3 k_vigil_cli.py validar <uuid> <chave>

Exemplos:
  python3 k_vigil_cli.py gerar 123e4567-e89b-12d3-a456-426614174000
  python3 k_vigil_cli.py validar 123e4567-e89b-12d3-a456-426614174000 abcdef...

""")

if len(sys.argv) < 3:
    exibir_ajuda()
    sys.exit(1)

comando = sys.argv[1]
uuid_input = sys.argv[2]

if comando == "gerar":
    chave = gerar_chave_licenca(uuid_input)
    print(f"[] Chave gerada para UUID {uuid_input}:\n{chave}")

elif comando == "validar":
    if len(sys.argv) != 4:
        exibir_ajuda()
        sys.exit(1)
    chave_input = sys.argv[3]
    valido = validar_licenca(uuid_input, chave_input)
    print(f"[] Licença válida: {valido}")

else:
    exibir_ajuda()
