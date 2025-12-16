"""
Enterprise Security Engine - Kayos Cloud Licensing
Cryptographic core with military-grade security - LOCAL DEVELOPMENT VERSION
"""

import os
import base64
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple
import secrets
import logging

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import jwt
from bcrypt import hashpw, gensalt, checkpw

# Configure logging
logger = logging.getLogger(__name__)


class EnterpriseCryptoEngine:
    """
    Military-grade cryptographic engine for license generation and validation
    LOCAL DEVELOPMENT VERSION - with enhanced error handling and logging
    """
    
    def __init__(self, keys_dir: str = "security/keys"):
        self.backend = default_backend()
        self.keys_dir = keys_dir
        self._load_or_generate_keys()
        logger.info("EnterpriseCryptoEngine initialized successfully")
    
    def _load_or_generate_keys(self):
        """Load or generate RSA-4096 key pair with enhanced error handling"""
        try:
            os.makedirs(self.keys_dir, exist_ok=True)
            
            private_key_path = f"{self.keys_dir}/private_key.pem"
            public_key_path = f"{self.keys_dir}/public_key.pem"
            
            if os.path.exists(private_key_path) and os.path.exists(public_key_path):
                # Load existing keys
                logger.info("Loading existing RSA keys...")
                with open(private_key_path, "rb") as f:
                    self.private_key = serialization.load_pem_private_key(
                        f.read(), password=None, backend=self.backend
                    )
                with open(public_key_path, "rb") as f:
                    self.public_key = serialization.load_pem_public_key(
                        f.read(), backend=self.backend
                    )
                logger.info("RSA keys loaded successfully")
            else:
                # Generate new keys
                logger.info("Generating new RSA-4096 key pair...")
                self.private_key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=4096,
                    backend=self.backend
                )
                self.public_key = self.private_key.public_key()
                
                # Save keys
                with open(private_key_path, "wb") as f:
                    f.write(self.private_key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.PKCS8,
                        encryption_algorithm=serialization.NoEncryption()
                    ))
                with open(public_key_path, "wb") as f:
                    f.write(self.public_key.public_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PublicFormat.SubjectPublicKeyInfo
                    ))
                logger.info("New RSA-4096 key pair generated and saved")
                
        except Exception as e:
            logger.error(f"Failed to initialize crypto engine: {e}")
            raise
    
    def generate_license_payload(self, 
                               customer_id: str,
                               product_id: str, 
                               features: Dict,
                               expiration_days: int = 365,
                               max_activations: int = 1) -> Dict:
        """
        Generate secure license payload with multiple security layers
        """
        try:
            issued_at = datetime.now(timezone.utc)
            expires_at = issued_at + timedelta(days=expiration_days)
            
            payload = {
                "license_id": self._generate_secure_uuid(),
                "customer_id": customer_id,
                "product_id": product_id,
                "features": features,
                "issued_at": issued_at.isoformat().replace("+00:00", "Z"),
                "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
                "max_activations": max_activations,
                "version": "2.0",
                "algorithm": "RSA-4096-SHA512",
                "security_level": "enterprise",
                "timestamp": int(issued_at.timestamp())
            }
            
            logger.debug(f"Generated license payload for customer: {customer_id}")
            return payload
            
        except Exception as e:
            logger.error(f"Failed to generate license payload: {e}")
            raise
    
    def sign_license(self, payload: Dict) -> Tuple[str, str]:
        """
        Sign license payload and return encoded license + signature
        """
        try:
            # Convert to canonical JSON
            canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            
            # Sign with RSA-4096
            signature = self.private_key.sign(
                canonical_json.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
            
            # Encode payload and signature
            encoded_payload = base64.urlsafe_b64encode(
                canonical_json.encode('utf-8')
            ).decode('utf-8')
            
            encoded_signature = base64.urlsafe_b64encode(signature).decode('utf-8')
            
            logger.debug(f"License signed successfully: {payload['license_id']}")
            return encoded_payload, encoded_signature
            
        except Exception as e:
            logger.error(f"Failed to sign license: {e}")
            raise
    
    def verify_license(self, encoded_payload: str, encoded_signature: str) -> Tuple[bool, Optional[Dict]]:
        """
        Verify license signature and decode payload with comprehensive validation
        """
        try:
            # Decode payload and signature
            payload_bytes = base64.urlsafe_b64decode(encoded_payload.encode('utf-8'))
            signature_bytes = base64.urlsafe_b64decode(encoded_signature.encode('utf-8'))
            
            # Verify signature
            self.public_key.verify(
                signature_bytes,
                payload_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA512()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA512()
            )
            
            # Decode payload
            payload = json.loads(payload_bytes.decode('utf-8'))
            
            # Validate payload structure
            required_fields = ['license_id', 'issued_at', 'expires_at', 'customer_id', 'product_id']
            for field in required_fields:
                if field not in payload:
                    return False, {"error": f"Missing required field: {field}"}
            
            # Check expiration
            expires_at = datetime.fromisoformat(payload['expires_at'].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > expires_at:
                return False, {"error": "License expired"}
            
            # Check issuance time (prevent future-dated licenses)
            issued_at = datetime.fromisoformat(payload['issued_at'].replace('Z', '+00:00'))
            if issued_at > datetime.now(timezone.utc) + timedelta(minutes=5):  # Allow 5 min clock skew
                return False, {"error": "Invalid issuance time"}
            
            logger.debug(f"License verified successfully: {payload['license_id']}")
            return True, payload
            
        except Exception as e:
            logger.warning(f"License verification failed: {e}")
            return False, {"error": f"Verification failed: {str(e)}"}
    
    def encrypt_sensitive_data(self, data: str, key: bytes) -> str:
        """Encrypt sensitive data using AES-256-GCM"""
        try:
            iv = os.urandom(12)  # 96-bit IV for GCM
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=self.backend)
            encryptor = cipher.encryptor()
            
            ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
            
            # Combine IV + ciphertext + tag
            encrypted_data = iv + ciphertext + encryptor.tag
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str, key: bytes) -> str:
        """Decrypt sensitive data using AES-256-GCM"""
        try:
            data = base64.urlsafe_b64decode(encrypted_data.encode())
            
            iv = data[:12]
            ciphertext = data[12:-16]
            tag = data[-16:]
            
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=self.backend)
            decryptor = cipher.decryptor()
            
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext.decode()
            
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def _generate_secure_uuid(self) -> str:
        """Generate cryptographically secure UUID"""
        return f"kayos_{secrets.token_hex(16)}"
    
    def hash_license_key(self, license_data: str) -> str:
        """Create secure hash of license data for storage"""
        return hashpw(license_data.encode(), gensalt()).decode()
    
    def get_public_key_pem(self) -> str:
        """Get public key in PEM format for external verification"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')


class EnterpriseLicenseGenerator:
    """
    High-level license generator with business logic
    """
    
    def __init__(self):
        self.crypto = EnterpriseCryptoEngine()
        logger.info("EnterpriseLicenseGenerator initialized")
    
    def generate_enterprise_license(self,
                                  customer_info: Dict,
                                  product_config: Dict,
                                  license_tier: str = "premium") -> Dict:
        """
        Generate complete enterprise license package
        """
        try:
            # Validate input data
            self._validate_customer_info(customer_info)
            self._validate_product_config(product_config)
            
            # Generate secure payload
            payload = self.crypto.generate_license_payload(
                customer_id=customer_info['id'],
                product_id=product_config['id'],
                features=product_config['features'],
                expiration_days=product_config.get('validity_days', 365),
                max_activations=product_config.get('max_activations', 1)
            )
            
            # Add customer metadata
            payload['customer'] = {
                'name': customer_info['name'],
                'email': customer_info['email'],
                'company': customer_info.get('company'),
                'metadata': customer_info.get('metadata', {})
            }
            
            # Add product metadata
            payload['product'] = {
                'name': product_config['name'],
                'version': product_config['version'],
                'tier': license_tier
            }
            
            # Sign license
            encoded_payload, signature = self.crypto.sign_license(payload)
            
            result = {
                "success": True,
                "license": {
                    "payload": encoded_payload,
                    "signature": signature,
                    "format": "kayos_enterprise_v2"
                },
                "metadata": {
                    "license_id": payload['license_id'],
                    "issued_at": payload['issued_at'],
                    "expires_at": payload['expires_at'],
                    "customer": payload['customer']['name'],
                    "product": payload['product']['name'],
                    "tier": license_tier
                }
            }
            
            logger.info(f"Enterprise license generated: {payload['license_id']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to generate enterprise license: {e}")
            return {
                "success": False,
                "error": str(e),
                "license": None,
                "metadata": None
            }
    
    def _validate_customer_info(self, customer_info: Dict):
        """Validate customer information"""
        required = ['id', 'name', 'email']
        for field in required:
            if field not in customer_info:
                raise ValueError(f"Missing required customer field: {field}")
        
        if not isinstance(customer_info.get('metadata', {}), dict):
            raise ValueError("Customer metadata must be a dictionary")
    
    def _validate_product_config(self, product_config: Dict):
        """Validate product configuration"""
        required = ['id', 'name', 'version', 'features']
        for field in required:
            if field not in product_config:
                raise ValueError(f"Missing required product field: {field}")
        
        if not isinstance(product_config['features'], dict):
            raise ValueError("Product features must be a dictionary")


# Global instances
crypto_engine = EnterpriseCryptoEngine()
license_generator = EnterpriseLicenseGenerator()
