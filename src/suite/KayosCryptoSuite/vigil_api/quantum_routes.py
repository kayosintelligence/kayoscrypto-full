from flask import Blueprint, request, jsonify
from datetime import datetime
from core.advanced_license_builder import AdvancedLicenseBuilder
from core.quantum_crypto import QuantumLicenseBuilder

quantum_routes = Blueprint("quantum_api", __name__, url_prefix="/api/quantum")

# Inicializar construtores
advanced_builder = AdvancedLicenseBuilder()
pure_quantum_builder = QuantumLicenseBuilder()

@quantum_routes.route("/generate", methods=["POST"])
def generate_quantum_license():
    """Gera licença usando arquitetura quântica multidimensional"""
    try:
        data = request.get_json()
        user_data = data.get("user_data", {})
        level = data.get("level", "quantum")
        expiration_str = data.get("expiration_date")
        
        # Converter data
        expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d").date()
        
        # Gerar licença quântica pura
        quantum_license = pure_quantum_builder.build_quantum_license(
            user_data, level, expiration_date
        )
        
        return jsonify({
            "status": "success",
            "license_type": "pure_quantum",
            "quantum_license": quantum_license,
            "dimensions": {
                "sator_3d_faces": len(quantum_license.get("sator_3d_faces", [])),
                "fibonacci_points": len(quantum_license.get("fibonacci_sequence", [])),
                "ezekiel_wheels": len(quantum_license.get("ezekiel_wheel_positions", {})),
                "hypercube_vertices": len(quantum_license.get("hypercube_coordinates", []))
            }
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@quantum_routes.route("/generate-hybrid", methods=["POST"])
def generate_hybrid_license():
    """Gera licença híbrida (quântica + tradicional)"""
    try:
        from vigil_api.license_routes import PRIVATE_KEY
        
        data = request.get_json()
        user_data = data.get("user_data", {})
        level = data.get("level", "quantum_hybrid")
        expiration_str = data.get("expiration_date")
        
        expiration_date = datetime.strptime(expiration_str, "%Y-%m-%d").date()
        
        # Gerar licença híbrida
        license_string, quantum_license = advanced_builder.build_and_sign(
            user_data=user_data,
            level=level,
            expiration_date=expiration_date,
            private_key_pem=PRIVATE_KEY
        )
        
        return jsonify({
            "status": "success",
            "license_type": "hybrid",
            "license_string": license_string,
            "quantum_data": quantum_license
        })
        
    except Exception as e:
        return jsonify({
            "status": "error", 
            "error": str(e)
        }), 500

@quantum_routes.route("/validate-quantum", methods=["POST"])
def validate_quantum_license():
    """Valida licença usando sistema quântico"""
    try:
        data = request.get_json()
        quantum_license = data.get("quantum_license")
        original_seed = data.get("original_seed")
        
        if not quantum_license or not original_seed:
            return jsonify({
                "status": "error",
                "error": "quantum_license and original_seed are required"
            }), 400
        
        is_valid = pure_quantum_builder.validate_quantum_license(
            quantum_license, original_seed
        )
        
        return jsonify({
            "status": "success",
            "valid": is_valid,
            "validation_method": "quantum_recreation"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@quantum_routes.route("/system-info", methods=["GET"])
def quantum_system_info():
    """Retorna informações do sistema quântico"""
    return jsonify({
        "status": "online",
        "system": "KayosCryptoSuite Quantum v3.0",
        "architecture": {
            "sator_3d": "6 faces multidimensionais",
            "ezekiel_wheels": "3 rodas concêntricas", 
            "fibonacci_spiral": "25 pontos quânticos",
            "hypercube": "16 vértices 4D"
        },
        "capabilities": [
            "pure_quantum_licenses",
            "hybrid_licenses", 
            "multidimensional_validation",
            "quantum_signature_verification"
        ]
    })
