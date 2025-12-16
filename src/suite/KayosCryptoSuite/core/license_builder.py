# core/license_builder.py

import json
import uuid
import base64
from datetime import date

from .crypto_core import CryptoCore

class LicenseBuilder:
    """
    Constrói e assina digitalmente as licenças do KayosCryptoSuite.
    """

    @staticmethod
    # A 'assinatura' ou definição desta função deve incluir todos estes parâmetros
    def build_and_sign(
        user_data: dict,
        level: str,
        expiration_date: date,
        private_key_pem: bytes,
        metadata: dict = None
    ) -> tuple[str, dict]:
        """
        Cria uma estrutura de licença, a assina e retorna a string JSON e o payload.
        """
        if not user_data.get("name") or not user_data.get("email"):
            raise ValueError("Nome e e-mail do usuário são obrigatórios.")

        license_payload = {
            "license_id": str(uuid.uuid4()),
            "issued_at": date.today().isoformat(),
            "user_data": user_data,
            "license_level": level,
            "expires_at": expiration_date.isoformat(),
            "metadata": metadata or {}
        }
        
        # Usamos `separators` para criar a forma JSON mais compacta e canônica possível.
        payload_json_bytes = json.dumps(
            license_payload,
            sort_keys=True,
            separators=(',', ':')
        ).encode('utf-8')

        signature = CryptoCore.sign_data(private_key_pem, payload_json_bytes)

        final_license = {
            "payload_b64": base64.b64encode(payload_json_bytes).decode('utf-8'),
            "signature_b64": signature.decode('utf-8')
        }
        
        # Retorna tanto a string JSON final quanto o dicionário do payload original
        return json.dumps(final_license), license_payload
