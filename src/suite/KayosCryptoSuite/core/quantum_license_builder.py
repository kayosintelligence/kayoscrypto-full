from .quantum_crypto import QuantumLicenseBuilder

class AdvancedLicenseBuilder:
    """Wrapper para compatibilidade com sistema existente"""
    
    def __init__(self):
        self.quantum_builder = QuantumLicenseBuilder()
    
    def build_and_sign(self, user_data, level, expiration_date, private_key_pem):
        # Usar sistema quântico mas manter compatibilidade
        quantum_license = self.quantum_builder.build_quantum_license(
            user_data, level, expiration_date
        )
        
        # Manter formato original para compatibilidade
        return self._convert_to_legacy_format(quantum_license), quantum_license
    
    def _convert_to_legacy_format(self, quantum_license):
        """Converte licença quântica para formato legado"""
        import json
        return json.dumps({
            "payload_b64": "QUANTUM_UPGRADE",  # Placeholder
            "signature_b64": quantum_license["quantum_signature"],
            "quantum_metadata": quantum_license
        })
