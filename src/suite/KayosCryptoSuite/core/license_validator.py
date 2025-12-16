# core/license_validator.py

import json
import base64
from datetime import date
from .crypto_core import CryptoCore
from ..infrastructure.db_interface import get_license_status

class LicenseValidator:
    """
    Valida a autenticidade e as regras de negócio de uma licença KayosCryptoSuite.
    """

    @staticmethod
    def validate(license_string: str, public_key_pem: bytes) -> tuple[bool, dict | None]:
        """
        Verifica uma licença completa: assinatura, data de expiração e status no banco de dados.
        """
        try:
            print(f"[Validator]  Iniciando validação da licença")
            license_data = json.loads(license_string)
            payload_b64 = license_data.get("payload_b64")
            signature_b64 = license_data.get("signature_b64")

            if not payload_b64 or not signature_b64:
                print("[Validator]  Payload ou signature faltando")
                return False, None

            payload_bytes = base64.b64decode(payload_b64)
            signature_bytes = base64.b64decode(signature_b64)

            # Verificar assinatura
            is_authentic = CryptoCore.verify_signature(
                public_key_pem=public_key_pem,
                signature=signature_bytes,
                data=payload_bytes
            )

            if not is_authentic:
                print("[Validator]  Assinatura inválida")
                return False, None

            payload = json.loads(payload_bytes)
            print(f"[Validator]  Assinatura válida para licença: {payload.get('license_id')}")
            
            # Checar data de expiração
            expires_at = date.fromisoformat(payload.get("expires_at"))
            if expires_at < date.today():
                print(f"[Validator]  Licença expirada: {expires_at}")
                return False, None

            print(f"[Validator]  Licença não expirada: {expires_at}")

            # Checar status no banco de dados
            license_id = payload.get("license_id")
            status = get_license_status(license_id)
            print(f"[Validator]  Status no banco para {license_id}: '{status}'")
            
            if status != 'active':
                print(f"[Validator]  Status não é 'active': '{status}'")
                return False, None

            print(f"[Validator]  Licença VÁLIDA: {license_id}")
            return True, payload

        except Exception as e:
            print(f"[Validator]  Erro ao processar a licença: {e}")
            return False, None
