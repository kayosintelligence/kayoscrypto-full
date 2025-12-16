# core/crypto_core.py

import hashlib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64

class CryptoCore:
    """
    Núcleo de operações criptográficas para o KayosCryptoSuite.
    """

    @staticmethod
    def generate_key_pair() -> tuple[bytes, bytes]:
        """
        Gera um par de chaves ECC (privada e pública) para assinatura digital.
        """
        private_key = ec.generate_private_key(ec.SECP384R1())
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_pem, public_pem

    @staticmethod
    def sign_data(private_key_pem: bytes, data: bytes) -> bytes:
        """
        Assina um conjunto de dados usando uma chave privada ECC.
        """
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
        return base64.b64encode(signature)

    @staticmethod
    def verify_signature(public_key_pem: bytes, signature: bytes, data: bytes) -> bool:
        """
        Verifica a validade de uma assinatura digital usando a chave pública.
        """
        try:
            public_key = serialization.load_pem_public_key(public_key_pem)
            
            # --- CORREÇÃO APLICADA ---
            # A decodificação de Base64 já foi feita no LicenseValidator.
            # A função agora recebe os bytes da assinatura diretamente.
            # A linha "decoded_signature = base64.b64decode(signature)" foi removida.
            public_key.verify(
                signature, # Usamos os bytes da assinatura diretamente
                data,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except (InvalidSignature, ValueError):
            return False

    @staticmethod
    def generate_hash(data: bytes) -> str:
        """
        Gera um hash SHA-256 de um conjunto de dados.
        """
        return hashlib.sha256(data).hexdigest()
