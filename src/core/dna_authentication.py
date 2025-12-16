#!/usr/bin/env python3
"""
 DNA-BASED AUTHENTICATION SYSTEM - KAYOSCRYPTO
Sistema de autenticação multi-fator com DNA vitalício

Integra:
 Autenticação JWT tradicional
 Validação de DNA Ezekiel 8D
 MFA com DNA + senha + biometria
 Logging detalhado no MPC-N

© 2025 KAYOS SYSTEMS - DNA Authentication v1.0
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass

from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

# Adicionar paths necessários
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../../'))

# Import dinâmico para KayosID (opcional - funcionalidade específica)
try:
    from kayosid_integration import validate_user_dna, get_kayosid_registry
    KAYOSID_AVAILABLE = True
except ImportError:
    KAYOSID_AVAILABLE = False
    validate_user_dna = None
    get_kayosid_registry = None

# Import MPC-N (opcional - logging avançado)
try:
    from src.kayoscrypto.mpcn.context import log_event
    MPCN_AVAILABLE = True
except ImportError:
    MPCN_AVAILABLE = False
    log_event = None

# --- CONFIGURAÇÃO ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DNAAuthentication")

SECRET_KEY = os.getenv("SECRET_KEY", "a_secret_key_that_is_very_long_and_secure_for_kayos_crypto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- MODELS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    dna_id: Optional[str] = None

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    dna_id: Optional[str] = None
    is_active: bool = True

class MFAAuthenticationRequest(BaseModel):
    username: str
    password: str
    dna_id: str
    biometric_token: Optional[str] = None

class AuthenticationResult(BaseModel):
    success: bool
    token: Optional[str] = None
    mfa_required: bool = False
    dna_valid: bool = False
    errors: list = []

# --- DNA AUTHENTICATION ENGINE ---
@dataclass
class DNAAuthResult:
    """Resultado da autenticação com DNA"""
    success: bool
    user_data: Optional[Dict[str, Any]] = None
    dna_valid: bool = False
    mfa_required: bool = False
    errors: list = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class DNAAuthenticationEngine:
    """Engine de autenticação com DNA"""

    def __init__(self):
        if KAYOSID_AVAILABLE:
            self.kayosid_registry = get_kayosid_registry()
        else:
            self.kayosid_registry = None

    def authenticate_with_dna(
        self,
        username: str,
        password: str,
        dna_id: str,
        biometric_token: Optional[str] = None
    ) -> DNAAuthResult:
        """
        Autenticação completa: senha + DNA + biometria opcional
        """

        errors = []
        user_data = None
        dna_valid = False

        # 1. Validar DNA primeiro (mais seguro)
        if dna_id:
            if KAYOSID_AVAILABLE and self.kayosid_registry:
                dna_validation = self.kayosid_registry.validate_dna(dna_id)
                dna_valid = dna_validation.is_valid

                if not dna_valid:
                    errors.extend(dna_validation.errors)
                    self._log_auth_attempt(username, "dna_invalid", dna_id)
                else:
                    # Recuperar dados do usuário pelo DNA
                    dna_info = self.kayosid_registry.get_dna_info(dna_id)
                    if dna_info:
                        user_data = dna_info.get('identity_data', {})
                        self._log_auth_attempt(username, "dna_valid", dna_id)
            else:
                # Modo offline - aceitar DNA como válido para demo
                dna_valid = True
                user_data = {"username": username, "source": "offline_mode"}
                self._log_auth_attempt(username, "dna_offline_mode", dna_id)
        else:
            errors.append("DNA ID obrigatório para autenticação")
            self._log_auth_attempt(username, "dna_missing", None)

        # 2. Validar senha (se DNA passou)
        password_valid = False
        if dna_valid:
            # Simulação - em produção, verificar hash do banco
            password_valid = password == "kayopass"

            if not password_valid:
                errors.append("Senha incorreta")
                self._log_auth_attempt(username, "password_invalid", dna_id)

        # 3. Validar biometria (opcional)
        biometric_valid = True  # Simulação
        if biometric_token:
            # Em produção: validar token biométrico
            biometric_valid = len(biometric_token) > 10  # Simulação básica

            if not biometric_valid:
                errors.append("Token biométrico inválido")
                self._log_auth_attempt(username, "biometric_invalid", dna_id)

        # Resultado final
        success = dna_valid and password_valid and biometric_valid
        mfa_required = dna_valid and password_valid and not biometric_token

        if success:
            self._log_auth_success(username, dna_id)

        return DNAAuthResult(
            success=success,
            user_data=user_data,
            dna_valid=dna_valid,
            mfa_required=mfa_required,
            errors=errors
        )

    def _log_auth_attempt(self, username: str, event_type: str, dna_id: str):
        """Log detalhado de tentativas de autenticação"""
        if not MPCN_AVAILABLE or not log_event:
            logger.info(f"Auth attempt: {username} - {event_type} - DNA: {dna_id}")
            return

        try:
            log_event(
                actor=f"user_{username}",
                action=f"auth_attempt_{event_type}",
                details={
                    "timestamp": datetime.now().isoformat(),
                    "username": username,
                    "dna_id": dna_id,
                    "event_type": event_type,
                    "ip_address": "system",  # Em produção, capturar IP real
                    "user_agent": "KayosCrypto-API"
                }
            )
        except Exception as e:
            logger.error(f"Erro no logging MPC-N: {e}")

    def _log_auth_success(self, username: str, dna_id: str):
        """Log de autenticação bem-sucedida"""
        if not MPCN_AVAILABLE or not log_event:
            logger.info(f"Auth success: {username} - DNA: {dna_id}")
            return

        try:
            log_event(
                actor=f"user_{username}",
                action="auth_success_dna",
                details={
                    "timestamp": datetime.now().isoformat(),
                    "username": username,
                    "dna_id": dna_id,
                    "authentication_type": "dna_mfa",
                    "security_level": "high"
                }
            )
        except Exception as e:
            logger.error(f"Erro no logging MPC-N: {e}")

# --- FUNÇÕES DE UTILIDADE ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar senha com hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any]) -> str:
    """Criar token JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Obter usuário atual do token JWT"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        dna_id: str = payload.get("dna_id")

        if username is None:
            raise credentials_exception

        return {"username": username, "dna_id": dna_id}

    except JWTError:
        raise credentials_exception

def get_current_user_with_dna_validation(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Obter usuário atual com validação adicional de DNA"""
    user = get_current_user(token)

    # Validar DNA se presente no token
    if user.get("dna_id"):
        dna_valid = validate_user_dna(user["dna_id"])
        if not dna_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="DNA validation failed",
            )

    return user

# --- INSTÂNCIA GLOBAL ---
dna_auth_engine = DNAAuthenticationEngine()

def get_dna_auth_engine() -> DNAAuthenticationEngine:
    """Obter instância global do engine de autenticação DNA"""
    return dna_auth_engine