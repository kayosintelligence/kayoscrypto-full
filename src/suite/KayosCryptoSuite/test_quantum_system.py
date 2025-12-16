import requests
import json

BASE_URL = "http://localhost:5000/api/quantum"

def test_quantum_system():
    print(" INICIANDO TESTE DO SISTEMA QUÂNTICO")
    
    # 1. Testar informações do sistema
    print("\n[1] Obtendo informações do sistema quântico...")
    response = requests.get(f"{BASE_URL}/system-info")
    print(f"   Status: {response.status_code}")
    print(f"   Sistema: {response.json().get('system')}")
    
    # 2. Testar geração de licença quântica pura
    print("\n[2] Gerando licença quântica pura...")
    quantum_payload = {
        "user_data": {
            "name": "Quantum Test User",
            "email": "quantum@kayoscrypto.com"
        },
        "level": "quantum_enterprise",
        "expiration_date": "2035-12-31"
    }
    
    response = requests.post(f"{BASE_URL}/generate", json=quantum_payload)
    if response.status_code == 200:
        result = response.json()
        license_data = result.get("quantum_license", {})
        print(f"    Licença quântica gerada!")
        print(f"   License ID: {license_data.get('license_id')}")
        print(f"   Dimensões: {result.get('dimensions')}")
        
        # 3. Testar validação quântica
        print("\n[3] Validando licença quântica...")
        validate_payload = {
            "quantum_license": license_data,
            "original_seed": f"{quantum_payload['user_data']}{quantum_payload['level']}{quantum_payload['expiration_date']}"
        }
        
        val_response = requests.post(f"{BASE_URL}/validate-quantum", json=validate_payload)
        if val_response.status_code == 200:
            val_result = val_response.json()
            print(f"    Validação quântica: {val_result.get('valid')}")
        else:
            print(f"    Erro na validação: {val_response.text}")
            
    else:
        print(f"    Erro na geração: {response.text}")
    
    # 4. Testar licença híbrida
    print("\n[4] Gerando licença híbrida...")
    hybrid_response = requests.post(f"{BASE_URL}/generate-hybrid", json=quantum_payload)
    if hybrid_response.status_code == 200:
        hybrid_result = hybrid_response.json()
        print(f"    Licença híbrida gerada!")
        print(f"   Tipo: {hybrid_result.get('license_type')}")
    else:
        print(f"    Erro na geração híbrida: {hybrid_response.text}")

if __name__ == "__main__":
    test_quantum_system()
