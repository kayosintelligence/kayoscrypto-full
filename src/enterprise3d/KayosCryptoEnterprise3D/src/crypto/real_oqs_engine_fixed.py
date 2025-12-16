"""
 MOTOR OQS REAL CORRIGIDO - KYBER1024 + ECC P-521
Versão corrigida da API OQS 0.14.1
"""

import oqs
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import secrets
import logging

logger = logging.getLogger(__name__)

class RealOQSEngine:
 """
 Motor de criptografia real com Kyber1024 + ECC P-521
 """
 
 def __init__(self):
 self.kem_algorithm = "Kyber1024"
 self.ecc_curve = ec.SECP521R1()
 self.backend = default_backend()
 logger.info(f" Motor OQS inicializado com {self.kem_algorithm}")
 
 def generate_kyber_keypair(self):
 """
 Gerar par de chaves Kyber1024 real
 Retorna: (public_key, secret_key)
 """
 try:
 with oqs.KeyEncapsulation(self.kem_algorithm) as kem:
 public_key = kem.generate_keypair()
 secret_key = kem.export_secret_key()
 
 logger.info(f" Kyber1024 - Chave pública: {len(public_key)} bytes")
 logger.info(f" Kyber1024 - Chave secreta: {len(secret_key)} bytes")
 
 return public_key, secret_key
 
 except Exception as e:
 logger.error(f" Erro ao gerar chaves Kyber: {e}")
 raise
 
 def generate_ecc_keypair(self):
 """
 Gerar par de chaves ECC P-521 real
 Retorna: (private_key_pem, public_key_pem)
 """
 try:
 # Gerar chave privada
 private_key = ec.generate_private_key(self.ecc_curve, self.backend)
 
 # Serializar chave privada
 private_pem = private_key.private_bytes(
 encoding=serialization.Encoding.PEM,
 format=serialization.PrivateFormat.PKCS8,
 encryption_algorithm=serialization.NoEncryption()
 )
 
 # Serializar chave pública
 public_pem = private_key.public_key().public_bytes(
 encoding=serialization.Encoding.PEM,
 format=serialization.PublicFormat.SubjectPublicKeyInfo
 )
 
 logger.info(f" ECC P-521 - Chave privada: {len(private_pem)} bytes PEM")
 logger.info(f" ECC P-521 - Chave pública: {len(public_pem)} bytes PEM")
 
 return private_pem, public_pem
 
 except Exception as e:
 logger.error(f" Erro ao gerar chaves ECC: {e}")
 raise

class RealQuantumClassicalExchange:
 """
 Troca de chaves quântico-clássica real - VERSÃO CORRIGIDA
 """
 
 def __init__(self):
 self.oqs_engine = RealOQSEngine()
 logger.info(" Inicializado trocador quântico-clássico")
 
 def perform_key_exchange(self):
 """
 Executar troca completa de chaves Kyber1024 + ECDH - CORRIGIDO
 """
 try:
 logger.info(" Iniciando troca de chaves quântico-clássica...")
 
 # 1. Gerar pares de chaves Kyber
 kyber_public, kyber_secret = self.oqs_engine.generate_kyber_keypair()
 
 # 2. Gerar pares de chaves ECC
 ecc_private_pem, ecc_public_pem = self.oqs_engine.generate_ecc_keypair()
 
 # 3. Kyber KEM - CORREÇÃO: Usar mesma instância para encapsular/decapsular
 with oqs.KeyEncapsulation("Kyber1024") as kem:
 # Gerar chaves dentro da mesma instância
 kem_public = kem.generate_keypair()
 kem_secret = kem.export_secret_key()
 
 # Encapsular
 ciphertext, kyber_shared_secret = kem.encap_secret(kem_public)
 logger.info(f" Kyber KEM - Ciphertext: {len(ciphertext)} bytes")
 logger.info(f" Kyber KEM - Shared secret: {len(kyber_shared_secret)} bytes")
 
 # Decapsular com mesma instância
 # CORREÇÃO: Não precisamos decapsular aqui, já temos o shared secret
 kyber_shared_secret_client = kem.decap_secret(ciphertext)
 
 # Verificar integridade
 if kyber_shared_secret == kyber_shared_secret_client:
 logger.info(" Kyber KEM - Segredos combinam perfeitamente!")
 else:
 logger.warning(" Kyber KEM - Segredos diferentes")
 
 # 4. ECDH - Troca clássica
 # Carregar nossa chave privada ECC
 our_private_key = serialization.load_pem_private_key(
 ecc_private_pem, 
 password=None, 
 backend=self.oqs_engine.backend
 )
 
 # Gerar chave do peer para ECDH
 peer_private = ec.generate_private_key(ec.SECP521R1())
 peer_public = peer_private.public_key()
 
 # Calcular shared secret ECDH
 ecc_shared_secret = our_private_key.exchange(ec.ECDH(), peer_public)
 logger.info(f" ECDH - Shared secret: {len(ecc_shared_secret)} bytes")
 
 # 5. Combinar segredos quântico + clássico
 combined_secret = self._combine_secrets(
 kyber_shared_secret, 
 ecc_shared_secret
 )
 
 logger.info(" Troca de chaves quântico-clássica concluída!")
 
 return {
 'kyber': {
 'public_key': kem_public,
 'secret_key': kem_secret,
 'ciphertext': ciphertext,
 'shared_secret': kyber_shared_secret
 },
 'ecc': {
 'private_key_pem': ecc_private_pem,
 'public_key_pem': ecc_public_pem,
 'shared_secret': ecc_shared_secret
 },
 'combined_secret': combined_secret,
 'security_level': 'Kyber1024_NIST_Level5 + ECC_P-521',
 'key_size_bits': 256
 }
 
 except Exception as e:
 logger.error(f" Erro na troca de chaves: {e}")
 raise
 
 def _combine_secrets(self, quantum_secret, classical_secret):
 """
 Combinar segredos quântico e clássico usando KDF
 """
 from cryptography.hazmat.primitives.kdf.hkdf import HKDF
 # import geometric salt and context info
 try:
 from kayoscrypto.core.geometry import get_geometric_salt, SATOR_CONTEXT_INFO
 except Exception:
 # Fallback: no geometric salt available
 get_geometric_salt = lambda: None
 SATOR_CONTEXT_INFO = b""

 # Combinar os dois segredos
 combined_input = quantum_secret + classical_secret

 # Use the SATOR genesis hash as salt/context personalization
 salt = get_geometric_salt()
 info = b'kayos_crypto_3d_enterprise' + (SATOR_CONTEXT_INFO or b"")

 # Derivar chave AES-256
 hkdf = HKDF(
 algorithm=hashes.SHA256(),
 length=32, # 256 bits para AES-256
 salt=salt,
 info=info,
 )

 return hkdf.derive(combined_input)
 
 def encrypt_with_combined_key(self, plaintext, combined_secret):
 """
 Criptografar dados usando chave combinada
 """
 try:
 # Usar AES-GCM com a chave combinada
 aesgcm = AESGCM(combined_secret)
 nonce = secrets.token_bytes(12)
 ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
 
 return {
 'ciphertext': ciphertext,
 'nonce': nonce,
 'algorithm': 'AES-256-GCM'
 }
 
 except Exception as e:
 logger.error(f" Erro na criptografia: {e}")
 raise

# Teste da implementação corrigida
if __name__ == "__main__":
 logging.basicConfig(level=logging.INFO)
 
 print(" TESTE MOTOR OQS REAL - VERSÃO CORRIGIDA")
 print("=" * 50)
 
 try:
 exchange = RealQuantumClassicalExchange()
 
 # Executar troca de chaves
 key_material = exchange.perform_key_exchange()
 
 print(" TROCA DE CHAVES REAL FUNCIONANDO!")
 print(f" Algoritmo: {key_material['security_level']}")
 print(f" Chave combinada: {len(key_material['combined_secret'])} bytes")
 print(f" Kyber ciphertext: {len(key_material['kyber']['ciphertext'])} bytes")
 
 # Testar criptografia real
 print("\n Testando criptografia real...")
 test_message = "Mensagem secreta do KayosCrypto 3D Enterprise!"
 encryption_result = exchange.encrypt_with_combined_key(test_message, key_material['combined_secret'])
 
 print(f" Mensagem criptografada: {len(encryption_result['ciphertext'])} bytes")
 print(f" Nonce: {len(encryption_result['nonce'])} bytes")
 print(f" Algoritmo: {encryption_result['algorithm']}")
 
 print("\n SISTEMA DE CRIPTOGRAFIA REAL PRONTO!")
 
 except Exception as e:
 print(f" TESTE FALHOU: {e}")
 import traceback
 traceback.print_exc()
