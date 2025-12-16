"""
LicenseBuilder Avançado com Criptografia Quântica Multidimensional
Mantém compatibilidade com sistema legado enquanto implementa nova arquitetura
"""

import json
import base64
from datetime import date
from .quantum_crypto import QuantumLicenseBuilder
from .crypto_core import CryptoCore

class AdvancedLicenseBuilder:
    """Construtor que une sistemas legado e quântico"""
    
    def __init__(self):
        self.quantum_builder = QuantumLicenseBuilder()
        self.legacy_builder = None  # Será injetado se necessário
    
    def build_and_sign(self, user_data, level, expiration_date, private_key_pem):
        """
        Constrói licença em modo híbrido: quântico + assinatura tradicional
        """
        # 1. Gerar licença quântica
        quantum_license = self.quantum_builder.build_quantum_license(
            user_data, level, expiration_date
        )
        
        # 2. Criar payload compatível com sistema legado
        legacy_payload = self._create_legacy_payload(quantum_license)
        
        # 3. Assinar com sistema tradicional (para compatibilidade)
        payload_json = json.dumps(legacy_payload, sort_keys=True, separators=(',', ':'))
        signature = CryptoCore.sign_data(private_key_pem, payload_json.encode('utf-8'))
        
        # 4. Retornar formato híbrido
        final_license = {
            "payload_b64": base64.b64encode(payload_json.encode()).decode(),
            "signature_b64": signature.decode(),
            "quantum_metadata": quantum_license  # Dados quânticos extras
        }
        
        return json.dumps(final_license), quantum_license
    
    def _create_legacy_payload(self, quantum_license):
        """Cria payload compatível com sistema legado"""
        return {
            "license_id": quantum_license["license_id"],
            "issued_at": date.today().isoformat(),
            "user_data": quantum_license["user_data"],
            "license_level": quantum_license["level"],
            "expires_at": quantum_license["expiration_date"],
            "metadata": {
                "quantum_enhanced": True,
                "sator_3d": True,
                "ezekiel_wheels": True,
                "fibonacci_spiral": True
            }
        }
    
    def build_pure_quantum_license(self, user_data, level, expiration_date):
        """Constrói licença puramente quântica (sem compatibilidade legada)"""
        return self.quantum_builder.build_quantum_license(user_data, level, expiration_date)
    
    def validate_hybrid_license(self, license_string, public_key_pem, original_seed):
        """Valida licença híbrida (quântica + tradicional)"""
        try:
            license_data = json.loads(license_string)
            
            # Validar assinatura tradicional
            payload_b64 = license_data.get("payload_b64")
            signature_b64 = license_data.get("signature_b64")
            
            if not payload_b64 or not signature_b64:
                return False, None
            
            payload_bytes = base64.b64decode(payload_b64)
            signature_bytes = base64.b64decode(signature_b64)
            
            # Verificar assinatura tradicional
            is_authentic = CryptoCore.verify_signature(
                public_key_pem=public_key_pem,
                signature=signature_bytes,
                data=payload_bytes
            )
            
            if not is_authentic:
                return False, None
            
            # Validar componente quântico
            quantum_metadata = license_data.get("quantum_metadata", {})
            is_quantum_valid = self.quantum_builder.validate_quantum_license(
                quantum_metadata, original_seed
            )
            
            payload = json.loads(payload_bytes)
            return (is_authentic and is_quantum_valid), payload
            
        except Exception as e:
            print(f"[AdvancedValidator] Erro na validação híbrida: {e}")
            return False, None
