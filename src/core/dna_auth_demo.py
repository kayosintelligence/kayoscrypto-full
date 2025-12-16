#!/usr/bin/env python3
"""
 DNA AUTHENTICATION API DEMO - KAYOSCRYPTO
Demonstração da API de autenticação com DNA vitalício

Endpoints:
 POST /auth/dna-login - Login com DNA + senha
 POST /auth/mfa-complete - Completar MFA
 GET /auth/me - Perfil do usuário autenticado

© 2025 KAYOS SYSTEMS - DNA Auth API Demo
"""

import sys
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Adicionar paths
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from dna_authentication import (
    DNAAuthenticationEngine,
    get_dna_auth_engine,
    get_current_user_with_dna_validation,
    create_access_token,
    AuthenticationResult,
    MFAAuthenticationRequest
)

# --- CONFIGURAÇÃO DA API ---
app = FastAPI(
    title="DNA Authentication API Demo",
    description="Demonstração de autenticação multi-fator com DNA vitalício Ezekiel",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class UserProfile(BaseModel):
    username: str
    dna_id: Optional[str]
    authenticated_at: str
    auth_method: str

# --- ENDPOINTS ---

@app.post("/auth/dna-login", response_model=AuthenticationResult)
async def dna_login(request: MFAAuthenticationRequest):
    """
    Login com autenticação DNA + senha + biometria opcional
    """
    try:
        engine = get_dna_auth_engine()

        auth_result = engine.authenticate_with_dna(
            username=request.username,
            password=request.password,
            dna_id=request.dna_id,
            biometric_token=request.biometric_token
        )

        response_data = {
            "success": auth_result.success,
            "mfa_required": auth_result.mfa_required,
            "dna_valid": auth_result.dna_valid,
            "errors": auth_result.errors
        }

        # Gerar token se autenticação completa
        if auth_result.success and not auth_result.mfa_required:
            token_data = {
                "sub": request.username,
                "dna_id": request.dna_id
            }
            token = create_access_token(token_data)
            response_data["token"] = token

        return AuthenticationResult(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na autenticação: {str(e)}")

@app.post("/auth/mfa-complete", response_model=AuthenticationResult)
async def complete_mfa(request: MFAAuthenticationRequest):
    """
    Completar autenticação MFA com biometria
    """
    if not request.biometric_token:
        raise HTTPException(status_code=400, detail="Token biométrico obrigatório")

    # Mesmo processo, mas agora com biometria
    return await dna_login(request)

@app.get("/auth/me", response_model=UserProfile)
async def get_user_profile(current_user: dict = Depends(get_current_user_with_dna_validation)):
    """
    Obter perfil do usuário autenticado (com validação DNA)
    """
    return UserProfile(
        username=current_user["username"],
        dna_id=current_user.get("dna_id"),
        authenticated_at=datetime.now().isoformat(),
        auth_method="dna_mfa"
    )

@app.get("/auth/health")
async def health_check():
    """Verificação de saúde da API DNA Auth"""
    engine = get_dna_auth_engine()

    return {
        "status": "healthy",
        "dna_system": "operational" if engine.kayosid_registry.manager else "offline",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# --- DEMONSTRAÇÃO ---
def demo_dna_authentication():
    """Demonstração da autenticação com DNA"""
    print("=" * 80)
    print(" DNA AUTHENTICATION SYSTEM - DEMONSTRAÇÃO")
    print("Autenticação Multi-Fator com DNA Vitalício")
    print("=" * 80)

    engine = get_dna_auth_engine()

    # Simular dados de usuário
    test_users = [
        {
            "username": "joao_silva",
            "password": "kayopass",
            "dna_id": "ce2f277d-19f1-5f85-a051-663d877e1859",  # DNA real gerado antes
            "biometric": "biometric_token_12345"
        },
        {
            "username": "maria_santos",
            "password": "kayopass",
            "dna_id": "invalid_dna_id",
            "biometric": None
        }
    ]

    for i, user in enumerate(test_users, 1):
        print(f"\n TESTE {i}: Autenticação para {user['username']}")

        # Teste 1: Apenas DNA + senha
        print("    Fase 1: DNA + Senha...")
        result1 = engine.authenticate_with_dna(
            user['username'], user['password'], user['dna_id']
        )

        print(f"    Sucesso: {result1.success}")
        print(f"    DNA Válido: {result1.dna_valid}")
        print(f"    MFA Necessário: {result1.mfa_required}")

        if result1.errors:
            print(f"    Erros: {', '.join(result1.errors)}")

        # Teste 2: DNA + senha + biometria (se disponível)
        if user['biometric']:
            print("    Fase 2: DNA + Senha + Biometria...")
            result2 = engine.authenticate_with_dna(
                user['username'], user['password'], user['dna_id'], user['biometric']
            )

            print(f"    Autenticação Completa: {result2.success}")
            if result2.success:
                print("    MFA Concluído com sucesso!")

    print("\n" + "=" * 80)
    print(" DEMONSTRAÇÃO CONCLUÍDA!")
    print(" Sistema de autenticação DNA operacional")
    print("=" * 80)

if __name__ == "__main__":
    demo_dna_authentication()