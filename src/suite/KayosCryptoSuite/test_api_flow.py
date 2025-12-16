import requests
import json

BASE_URL = "http://localhost:5000/api"

def run_test():
    print("--- INICIANDO TESTE DE FLUXO COMPLETO ---")

    # ETAPA 1: Gerar uma nova licença
    print("\n[ETAPA 1] Gerando uma nova licença...")
    generate_payload = {
        "user_data": {
            "name": "Automated Test User",
            "email": "test@kayoscrypto.com"
        },
        "level": "enterprise",
        "expiration_date": "2035-01-01"
    }
    
    try:
        response_gen = requests.post(f"{BASE_URL}/generate", json=generate_payload)
        response_gen.raise_for_status()
        
        # CORREÇÃO: Extrair APENAS a license_string da resposta
        response_data = response_gen.json()
        license_string_to_validate = response_data["license_string"]
        
        print(" Sucesso! Licença gerada.")
        print(f"   License ID: {response_data['license_data']['license_id']}")

    except requests.exceptions.RequestException as e:
        print(f" FALHA na Etapa 1: Não foi possível gerar a licença.")
        print(f"   Erro: {e}")
        return

    # ETAPA 2: Validar a licença que acabamos de gerar
    print("\n[ETAPA 2] Validando a licença recém-criada...")
    validate_payload = {
        "license_string": license_string_to_validate
    }

    try:
        response_val = requests.post(f"{BASE_URL}/validate", json=validate_payload)
        validation_result = response_val.json()
        
        print(f" Sucesso! Endpoint de validação respondeu com status: {response_val.status_code}")
        
        if validation_result.get("valid") is True:
            print("\n TESTE CONCLUÍDO COM SUCESSO! A licença foi validada corretamente.")
            print(f"    License ID: {validation_result['payload']['license_id']}")
        else:
            print("\n FALHA NO TESTE! A licença gerada foi considerada INVÁLIDA.")
            print(f"    Resposta do servidor: {validation_result}")

    except requests.exceptions.RequestException as e:
        print(f" FALHA na Etapa 2: Não foi possível validar a licença.")
        print(f"   Erro: {e}")
        print(f"   Resposta do servidor: {response_val.text}")


if __name__ == "__main__":
    run_test()
