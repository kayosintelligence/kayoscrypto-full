from flask import Blueprint, request, jsonify
from datetime import datetime, date
from ..core.license_builder import LicenseBuilder
from ..core.license_validator import LicenseValidator
from ..core.crypto_core import CryptoCore
from ..infrastructure.db_interface import init_db, insert_license_log

license_routes = Blueprint("license_api", __name__, url_prefix="/api")

# Carregar chaves
try:
    with open('keys/private_key.pem', 'rb') as f:
        PRIVATE_KEY = f.read()
    with open('keys/public_key.pem', 'rb') as f:
        PUBLIC_KEY = f.read()
except:
    PRIVATE_KEY, PUBLIC_KEY = CryptoCore.generate_key_pair()
    import os
    os.makedirs('keys', exist_ok=True)
    with open('keys/private_key.pem', 'wb') as f:
        f.write(PRIVATE_KEY)
    with open('keys/public_key.pem', 'wb') as f:
        f.write(PUBLIC_KEY)

# INICIALIZAR BANCO APENAS UMA VEZ
try:
    init_db()
    print(" Banco de dados inicializado com sucesso!")
except Exception as e:
    print(f"  Banco não inicializado: {e}")

@license_routes.route("/generate", methods=["POST"])
def generate_license():
    try:
        data = request.get_json()
        user_data = data.get("user_data", {})
        level = data.get("level", "standard")
        expiration_str = data.get("expiration_date")
        
        expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d").date()
        
        license_string, license_payload = LicenseBuilder.build_and_sign(
            user_data=user_data,
            level=level,
            expiration_date=expiration_date,
            private_key_pem=PRIVATE_KEY
        )
        
        # Registrar no banco
        insert_license_log(
            license_id=license_payload["license_id"],
            operation="generate",
            user_name=user_data.get("name", ""),
            email=user_data.get("email", ""),
            level=level,
            expiration=expiration_date
        )
        
        return jsonify({
            "license_string": license_string,
            "license_data": license_payload
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@license_routes.route("/validate", methods=["POST"])
def validate_license():
    try:
        data = request.get_json()
        license_string = data.get("license_string")
        
        is_valid, payload = LicenseValidator.validate(license_string, PUBLIC_KEY)
        
        return jsonify({
            "valid": is_valid,
            "payload": payload if is_valid else None
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@license_routes.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "KayosCryptoSuite API"})
