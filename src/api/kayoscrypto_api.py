"""
 KAYOSCRYPTO API REST - Core Integration
API RESTful com FastAPI integrada ao core do KayosCrypto

ARQUITETURA KAIOS:
- Velho Maturo: API como "porta de entrada" unificada para todos os Ribs
- Sator: Endpoints equilibrados (criptografia + steganografia + assinatura)
- Ezequiel: 3 dimensões de operação (encrypt/sign/stego)
- Relojoeiro: Otimizado para baixa latência (<100ms por operação)

FILOSOFIA:
"Uma só entrada para o templo" (Ezequiel 46:2)
- API única expõe TODAS as funcionalidades
- Não há necessidade de múltiplos sistemas
- Integração transparente com sistemas legados via HTTP

ENDPOINTS:
POST /api/v1/encrypt        - Criptografar payload
POST /api/v1/decrypt        - Descriptografar payload
POST /api/v1/sign           - Assinar mensagem (Ed25519)
POST /api/v1/verify         - Verificar assinatura
POST /api/v1/keygen         - Gerar keypair (hybrid ou Ed25519)
POST /api/v1/stego/embed    - Embutir em imagem
POST /api/v1/stego/extract  - Extrair de imagem
GET  /api/v1/health         - Health check
GET  /api/v1/stats          - Estatísticas de uso
GET  /api/v1/info           - Informações do sistema
GET  /api/v1/certifications/latest - Snapshot de certificação (Quantum Assurance)

Autor: KAYOS SYSTEMS
Data: 15 de Novembro de 2025
Versão: v6.4 - REST API Core
"""

import sys
import os
import io
import base64
import hashlib
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from dataclasses import dataclass, asdict

# Instalar FastAPI automaticamente
try:
    from fastapi import FastAPI, HTTPException, File, UploadFile, Form
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print(" [API] FastAPI não instalado. Instalando...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn[standard]", "python-multipart", "-q"])
        from fastapi import FastAPI, HTTPException, File, UploadFile, Form
        from fastapi.responses import JSONResponse, StreamingResponse
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel
        FASTAPI_AVAILABLE = True
        print(" [API] FastAPI instalado!")
    except Exception as e:
        print(f" [API] Falha ao instalar FastAPI: {e}")
        raise RuntimeError("FastAPI é obrigatório para a API REST")

# Importar módulos KayosCrypto
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.kayoscrypto_ultimate import KayosCryptoUltimate
    KAYOS_AVAILABLE = True
except ImportError as e:
    KAYOS_AVAILABLE = False
    print(f" [API] kayoscrypto_ultimate não encontrado: {e}")
    raise

try:
    from quantum import get_quantum_hook
    from quantum.resistance_manager import QuantumResistanceManager
    from quantum.entropy_pool import GeometricEntropyPool
    QUANTUM_ASSURANCE_AVAILABLE = True
except ImportError:
    try:
        from src.quantum import get_quantum_hook  # type: ignore
        from src.quantum.resistance_manager import QuantumResistanceManager  # type: ignore
        from src.quantum.entropy_pool import GeometricEntropyPool  # type: ignore
        QUANTUM_ASSURANCE_AVAILABLE = True
    except ImportError:
        QUANTUM_ASSURANCE_AVAILABLE = False
        print(" [API] Quantum Assurance modules não disponíveis")

try:
    from core.quantum.entropy_pool import (
        build_entropy_snapshot,
        persist_entropy_snapshot,
    )
except ImportError:
    try:
        from src.core.quantum.entropy_pool import (  # type: ignore
            build_entropy_snapshot,
            persist_entropy_snapshot,
        )
    except ImportError:
        build_entropy_snapshot = None  # type: ignore
        persist_entropy_snapshot = None  # type: ignore

try:
    from core.quantum.certification_tracker import CertificationTracker
    CERT_TRACKER_AVAILABLE = True
except ImportError:
    try:
        from src.core.quantum.certification_tracker import CertificationTracker  # type: ignore
        CERT_TRACKER_AVAILABLE = True
    except ImportError:
        CERT_TRACKER_AVAILABLE = False
        CertificationTracker = None  # type: ignore

try:
    from hybrid_key_exchange import HybridKeyExchange, HybridKeyPair
    HYBRID_AVAILABLE = True
except ImportError:
    HYBRID_AVAILABLE = False
    print(" [API] hybrid_key_exchange não encontrado")

try:
    from visual_steganography import VisualSteganography, SteganographyMetadata
    STEGO_AVAILABLE = True
except ImportError:
    STEGO_AVAILABLE = False
    print(" [API] visual_steganography não encontrado")

try:
    from suite.KayosCryptoSuite.core.license_builder import LicenseBuilder
    from suite.KayosCryptoSuite.core.license_validator import LicenseValidator
    from suite.KayosCryptoSuite.core.crypto_core import CryptoCore
    from suite.KayosCryptoSuite.infrastructure import db_interface as licensing_db
    LICENSING_AVAILABLE = True
except Exception as exc:  # pragma: no cover - optional dependency
    LICENSING_AVAILABLE = False
    LicenseBuilder = None  # type: ignore
    LicenseValidator = None  # type: ignore
    CryptoCore = None  # type: ignore
    licensing_db = None  # type: ignore
    print(f" [API] Licenciamento KayosCryptoSuite indisponível: {exc}")

LICENSE_KEYS_DIR = (Path(__file__).resolve().parent.parent / "suite" / "KayosCryptoSuite" / "keys")
LICENSE_PRIVATE_KEY: Optional[bytes] = None
LICENSE_PUBLIC_KEY: Optional[bytes] = None
LICENSE_DB_AVAILABLE = False

REPORTS_DIR = Path(__file__).resolve().parents[2] / "reports"
QUANTUM_DASHBOARD_JSON = REPORTS_DIR / "quantum" / "dashboard_summary.json"
HIGH_RISK_JSON = REPORTS_DIR / "quantum" / "high_risk_readiness.json"

if LICENSING_AVAILABLE:
    try:
        LICENSE_KEYS_DIR.mkdir(parents=True, exist_ok=True)
        private_key_path = LICENSE_KEYS_DIR / "private_key.pem"
        public_key_path = LICENSE_KEYS_DIR / "public_key.pem"
        if private_key_path.exists() and public_key_path.exists():
            LICENSE_PRIVATE_KEY = private_key_path.read_bytes()
            LICENSE_PUBLIC_KEY = public_key_path.read_bytes()
        else:
            LICENSE_PRIVATE_KEY, LICENSE_PUBLIC_KEY = CryptoCore.generate_key_pair()  # type: ignore[arg-type]
            private_key_path.write_bytes(LICENSE_PRIVATE_KEY)
            public_key_path.write_bytes(LICENSE_PUBLIC_KEY)

        if licensing_db is not None:
            try:
                licensing_db.init_db()  # type: ignore[attr-defined]
                LICENSE_DB_AVAILABLE = True
            except Exception as exc:  # pragma: no cover - optional infrastructure
                print(f" [API] Banco de licenças indisponível: {exc}")
    except Exception as exc:  # pragma: no cover - optional infrastructure
        print(f" [API] Falha ao inicializar chaves de licenciamento: {exc}")
        LICENSING_AVAILABLE = False
        LICENSE_PRIVATE_KEY = None
        LICENSE_PUBLIC_KEY = None


# =====================================================================
# MODELOS PYDANTIC (Request/Response)
# =====================================================================

class EncryptRequest(BaseModel):
    """Request para criptografar"""
    plaintext: str  # Base64 encoded
    password: str
    level: Optional[int] = 3
    quantum_mode: Optional[str] = 'off'
    quantum_assurance: Optional[bool] = False
    quantum_hooks: Optional[List[str]] = None

class EncryptResponse(BaseModel):
    """Response de criptografia"""
    ciphertext: str  # Base64 encoded
    size_bytes: int
    algorithm: str
    quantum_mode: Optional[str] = None
    quantum_metadata: Optional[Dict[str, str]] = None
    quantum_assurance: Optional[Dict[str, Any]] = None

class DecryptRequest(BaseModel):
    """Request para descriptografar"""
    ciphertext: str  # Base64 encoded
    password: str
    level: Optional[int] = 3
    quantum_mode: Optional[str] = 'off'
    quantum_metadata: Optional[Dict[str, str]] = None

class DecryptResponse(BaseModel):
    """Response de descriptografia"""
    plaintext: str  # Base64 encoded
    size_bytes: int

class SignRequest(BaseModel):
    """Request para assinar"""
    message: str  # Base64 encoded
    private_key: str  # Base64 encoded

class SignResponse(BaseModel):
    """Response de assinatura"""
    signature: str  # Base64 encoded
    algorithm: str = "Ed25519"
    version: int = 2

class VerifyRequest(BaseModel):
    """Request para verificar assinatura"""
    message: str  # Base64 encoded
    signature: str  # Base64 encoded
    public_key: str  # Base64 encoded

class VerifyResponse(BaseModel):
    """Response de verificação"""
    valid: bool
    algorithm: str = "Ed25519"

class KeygenRequest(BaseModel):
    """Request para gerar keypair"""
    algorithm: str = "ed25519"  # ed25519 | hybrid

class KeygenResponse(BaseModel):
    """Response de geração de chaves"""
    private_key: str  # Base64 encoded
    public_key: str  # Base64 encoded
    algorithm: str
    created_at: str

class HealthResponse(BaseModel):
    """Response de health check"""
    status: str
    version: str
    uptime_seconds: float
    modules_available: Dict[str, bool]

class StatsResponse(BaseModel):
    """Response de estatísticas"""
    total_requests: int
    encrypt_count: int
    decrypt_count: int
    sign_count: int
    verify_count: int
    keygen_count: int
    stego_embed_count: int
    stego_extract_count: int
    uptime_seconds: float

class InfoResponse(BaseModel):
    """Response de informações do sistema"""
    name: str
    version: str
    description: str
    algorithms: Dict[str, list]
    capabilities: list
    documentation: str


class LicenseGenerateRequest(BaseModel):
    """Request para geração de licença"""
    user_data: Dict[str, Any]
    level: str = "standard"
    expiration_date: str
    metadata: Optional[Dict[str, Any]] = None


class LicenseGenerateResponse(BaseModel):
    """Response de geração de licença"""
    license_string: str
    license_data: Dict[str, Any]


class LicenseValidateRequest(BaseModel):
    """Request para validação de licença"""
    license_string: str


class LicenseValidateResponse(BaseModel):
    """Response de validação de licença"""
    valid: bool
    payload: Optional[Dict[str, Any]] = None


class CertificationSnapshotResponse(BaseModel):
    """Snapshot mais recente do CertificationTracker"""
    available: bool
    snapshot: Optional[Dict[str, Any]] = None


class QuantumDashboardSummaryResponse(BaseModel):
    """Resumo agregado do dashboard quântico"""
    available: bool
    summary: Optional[Dict[str, Any]] = None
    generated_at: Optional[str] = None
    artifact_path: Optional[str] = None
    error: Optional[str] = None
    high_risk: Optional[Dict[str, Any]] = None


# =====================================================================
# API APPLICATION
# =====================================================================

app = FastAPI(
    title="KayosCrypto API",
    description="API RESTful para criptografia geométrica multicamada, esteganografia e assinatura digital",
    version="6.4.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# CORS (permitir requisições de qualquer origem)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Estatísticas globais
stats = {
    'start_time': datetime.now(),
    'total_requests': 0,
    'encrypt_count': 0,
    'decrypt_count': 0,
    'sign_count': 0,
    'verify_count': 0,
    'keygen_count': 0,
    'stego_embed_count': 0,
    'stego_extract_count': 0
}

# Instâncias dos engines (inicializadas sob demanda)
cipher_cache = {}
stego_cache = {}
hybrid_kex = None


# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def get_cipher(password: str) -> KayosCryptoUltimate:
    """Retorna instância de cipher (com cache)"""
    if not KAYOS_AVAILABLE:
        raise HTTPException(500, "KayosCrypto não disponível")
    
    # Cache por hash de senha (evita recriar objetos)
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()[:16]
    
    if pwd_hash not in cipher_cache:
        cipher_cache[pwd_hash] = KayosCryptoUltimate(
            use_quantum=False,  # Workaround bug quantum mode
            use_ed25519=True,
            use_concentric=True,
            use_direction=False
        )
    
    return cipher_cache[pwd_hash]

def parse_license_expiration(value: str) -> date:
    """Converte string de data em objeto date aceitando múltiplos formatos."""
    if not value:
        raise HTTPException(400, "expiration_date é obrigatório")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise HTTPException(400, "Formato de expiration_date inválido; use YYYY-MM-DD")

def get_stego(password: str) -> VisualSteganography:
    """Retorna instância de steganography (com cache)"""
    if not STEGO_AVAILABLE:
        raise HTTPException(500, "Visual Steganography não disponível")
    
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()[:16]
    
    if pwd_hash not in stego_cache:
        stego_cache[pwd_hash] = VisualSteganography(
            encrypt_payload=True,
            password=password
        )
    
    return stego_cache[pwd_hash]

def get_hybrid_kex():
    """Retorna instância de hybrid key exchange"""
    global hybrid_kex
    if not HYBRID_AVAILABLE:
        raise HTTPException(500, "Hybrid Key Exchange não disponível")
    
    if hybrid_kex is None:
        hybrid_kex = HybridKeyExchange(use_kyber=True, use_ecdh=True, use_fibonacci=True)
    
    return hybrid_kex

def base64_encode(data: bytes) -> str:
    """Encode bytes para base64 string"""
    return base64.b64encode(data).decode('utf-8')

def base64_decode(data: str) -> bytes:
    """Decode base64 string para bytes"""
    return base64.b64decode(data.encode('utf-8'))


# =====================================================================
# ENDPOINTS
# =====================================================================

@app.post("/api/v1/encrypt", response_model=EncryptResponse, tags=["Criptografia"])
async def encrypt_endpoint(request: EncryptRequest):
    """
    Criptografa payload usando KayosCrypto geométrico
    
    - **plaintext**: Dados em base64
    - **password**: Senha de criptografia
    - **level**: Nível de segurança (1-5, padrão 3)
    """
    try:
        stats['total_requests'] += 1
        stats['encrypt_count'] += 1

        start_time = time.perf_counter()
        plaintext = base64_decode(request.plaintext)
        quantum_mode = (request.quantum_mode or 'off').lower()
        use_quantum = quantum_mode in ('compatible', 'enhanced')
        selected_hooks = [hook.strip() for hook in (request.quantum_hooks or []) if hook and hook.strip()]
        use_assurance = bool(request.quantum_assurance) or bool(selected_hooks)
        if use_assurance and not QUANTUM_ASSURANCE_AVAILABLE:
            raise HTTPException(503, "Quantum Assurance não disponível neste ambiente")
        manager = QuantumResistanceManager() if use_assurance and QUANTUM_ASSURANCE_AVAILABLE else None
        pool = GeometricEntropyPool() if use_assurance and QUANTUM_ASSURANCE_AVAILABLE else None
        tracker = CertificationTracker() if use_assurance and CERT_TRACKER_AVAILABLE else None
        assurance_payload = None

        if use_quantum:
            if not KAYOS_AVAILABLE:
                raise HTTPException(500, "KayosCrypto Ultimate não disponível para modo quantum")
            try:
                cipher = KayosCryptoUltimate(
                    use_quantum=True,
                    quantum_entropy_mode=quantum_mode,
                    use_quantum_assurance=use_assurance,
                )
            except TypeError:
                cipher = KayosCryptoUltimate(use_quantum=True, quantum_entropy_mode=quantum_mode)
            encrypted_payload = cipher.encrypt(plaintext, request.password, level=request.level)
            ciphertext_bytes, quantum_meta = cipher.prepare_encryption_package(
                encrypted_payload,
                salt_encoding='hex'
            )
            metadata = quantum_meta if quantum_meta else None
        else:
            cipher = get_cipher(request.password)
            ciphertext_bytes = cipher.encrypt(plaintext, request.password, level=request.level)
            metadata = None
            quantum_mode = 'off'

        entropy_snapshot = None
        if use_assurance and manager and pool:
            key_bytes = hashlib.sha256(request.password.encode()).digest()
            snapshot = {
                "plaintext_bytes": plaintext,
                "ciphertext_bytes": ciphertext_bytes,
                "key_bytes": key_bytes,
            }
            report = manager.assess_vulnerability(snapshot)
            report_payload = manager.build_report(report)
            suggestions = manager.recommend_improvements(report)
            metrics_payload = getattr(report, "metrics", None) or getattr(report, "raw_metrics", {})
            scorecard_payload = None
            if hasattr(report, "scorecard"):
                scorecard_obj = getattr(report, "scorecard")
                if scorecard_obj is not None:
                    if hasattr(scorecard_obj, "to_dict"):
                        scorecard_payload = scorecard_obj.to_dict()
                    elif isinstance(scorecard_obj, dict):
                        scorecard_payload = scorecard_obj
            findings_payload = list(getattr(report, "findings", [])) if hasattr(report, "findings") else None
            entropy_key = pool.generate_quantum_safe_key(32, metrics_payload)
            if build_entropy_snapshot:
                try:
                    entropy_snapshot = build_entropy_snapshot(
                        entropy_key,
                        context={
                            "source": "api",
                            "endpoint": "encrypt",
                            "quantum_mode": quantum_mode,
                            "hooks": selected_hooks,
                            "metrics": metrics_payload,
                        },
                    )
                    if persist_entropy_snapshot:
                        persisted_path = persist_entropy_snapshot(entropy_snapshot)
                        if persisted_path:
                            entropy_snapshot['persisted_to'] = persisted_path
                except Exception as exc:  # pragma: no cover - telemetria best-effort
                    entropy_snapshot = {"error": str(exc)}
            hook_results: Dict[str, Any] = {}
            if selected_hooks:
                base_state: Dict[str, Any] = {
                    "phase": "encrypt",
                    "quantum_snapshot": dict(snapshot),
                    "ciphertext": ciphertext_bytes,
                }
                for hook_name in selected_hooks:
                    hook = get_quantum_hook(hook_name) if QUANTUM_ASSURANCE_AVAILABLE else None
                    if hook is None:
                        hook_results[hook_name] = {"error": "hook_not_found"}
                        continue
                    state = dict(base_state)
                    try:
                        hook.update(state)
                        hook_results[hook_name] = {
                            key: value
                            for key, value in state.items()
                            if key not in {"ciphertext", "quantum_snapshot", "phase"}
                        }
                    except Exception as exc:  # pragma: no cover
                        hook_results[hook_name] = {"error": str(exc)}
            assurance_payload = {
                "report": report_payload,
                "suggestions": suggestions,
                "metrics": metrics_payload,
                "hooks": selected_hooks,
                "entropy_key": entropy_key.hex(),
                "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            }
            if entropy_snapshot:
                assurance_payload["entropy_snapshot"] = entropy_snapshot
            if scorecard_payload:
                assurance_payload["scorecard"] = scorecard_payload
            if findings_payload:
                assurance_payload["findings"] = findings_payload
            if hook_results:
                assurance_payload["hook_results"] = hook_results
            if tracker:
                certification_snapshot = tracker.update_from_assurance(
                    metrics_payload,
                    hooks=hook_results or None,
                    context={
                        "source": "api",
                        "quantum_mode": quantum_mode,
                        "hooks": selected_hooks,
                        "entropy_snapshot": entropy_snapshot.get('persisted_to') if isinstance(entropy_snapshot, dict) else None,
                    },
                    suggestions=suggestions,
                    performance_kbps=(
                        (len(plaintext) / max((time.perf_counter() - start_time), 1e-9)) / 1024
                    ),
                    scorecard=scorecard_payload,
                    findings=findings_payload,
                )
                assurance_payload["certification"] = certification_snapshot
        
        total_elapsed = time.perf_counter() - start_time
        performance_kbps = (
            (len(plaintext) / total_elapsed) / 1024
            if total_elapsed > 0 else None
        )

        response_payload = EncryptResponse(
            ciphertext=base64_encode(ciphertext_bytes),
            size_bytes=len(ciphertext_bytes),
            algorithm="KayosCrypto-Geometric-v6.4",
            quantum_mode=quantum_mode,
            quantum_metadata=metadata,
            quantum_assurance=assurance_payload,
        )
        if assurance_payload is not None and performance_kbps is not None:
            assurance_payload.setdefault("performance_kbps", performance_kbps)
        elif performance_kbps is not None and response_payload.quantum_assurance is None:
            response_payload.quantum_assurance = {"performance_kbps": performance_kbps}

        return response_payload
    except Exception as e:
        raise HTTPException(500, f"Erro na criptografia: {str(e)}")

@app.post("/api/v1/decrypt", response_model=DecryptResponse, tags=["Criptografia"])
async def decrypt_endpoint(request: DecryptRequest):
    """
    Descriptografa payload usando KayosCrypto
    
    - **ciphertext**: Dados cifrados em base64
    - **password**: Senha de descriptografia
    - **level**: Nível usado na criptografia
    """
    try:
        stats['total_requests'] += 1
        stats['decrypt_count'] += 1
        
        ciphertext = base64_decode(request.ciphertext)
        quantum_mode = (request.quantum_mode or 'off').lower()
        use_quantum = quantum_mode in ('compatible', 'enhanced')

        if use_quantum:
            if not KAYOS_AVAILABLE:
                raise HTTPException(500, "KayosCrypto Ultimate não disponível para modo quantum")
            decrypt_metadata = request.quantum_metadata or {}
            if quantum_mode == 'enhanced' and 'quantum_salt' not in decrypt_metadata:
                raise HTTPException(400, "quantum_salt obrigatório para descriptografia enhanced")
            cipher = KayosCryptoUltimate(use_quantum=True, quantum_entropy_mode=quantum_mode)
            plaintext = cipher.decrypt(ciphertext, request.password, level=request.level, metadata=decrypt_metadata)
        else:
            cipher = get_cipher(request.password)
            plaintext = cipher.decrypt(ciphertext, request.password, level=request.level)
        
        return DecryptResponse(
            plaintext=base64_encode(plaintext),
            size_bytes=len(plaintext)
        )
    except Exception as e:
        raise HTTPException(500, f"Erro na descriptografia: {str(e)}")

@app.post("/api/v1/sign", response_model=SignResponse, tags=["Assinatura Digital"])
async def sign_endpoint(request: SignRequest):
    """
    Assina mensagem usando Ed25519
    
    - **message**: Mensagem em base64
    - **private_key**: Chave privada Ed25519 em base64 (32 bytes)
    """
    try:
        stats['total_requests'] += 1
        stats['sign_count'] += 1
        
        message = base64_decode(request.message)
        private_key = base64_decode(request.private_key)
        
        cipher = get_cipher("dummy")  # Password não usado para assinatura
        signature = cipher.sign_message(message, private_key)
        
        # Serializar signature (objeto PalindromeSignature)
        sig_bytes = signature.signature  # Ed25519 signature bytes
        
        return SignResponse(
            signature=base64_encode(sig_bytes),
            algorithm="Ed25519",
            version=signature.version
        )
    except Exception as e:
        raise HTTPException(500, f"Erro na assinatura: {str(e)}")

@app.post("/api/v1/verify", response_model=VerifyResponse, tags=["Assinatura Digital"])
async def verify_endpoint(request: VerifyRequest):
    """
    Verifica assinatura Ed25519
    
    - **message**: Mensagem original em base64
    - **signature**: Assinatura em base64
    - **public_key**: Chave pública Ed25519 em base64 (32 bytes)
    """
    try:
        stats['total_requests'] += 1
        stats['verify_count'] += 1
        
        message = base64_decode(request.message)
        sig_bytes = base64_decode(request.signature)
        public_key = base64_decode(request.public_key)
        
        cipher = get_cipher("dummy")
        
        # Reconstruir PalindromeSignature
        from palindrome_signatures import PalindromeSignature
        signature = PalindromeSignature(
            signature=sig_bytes,
            version=2,
            timestamp=datetime.now().isoformat()
        )
        
        valid = cipher.verify_signature(message, signature, public_key)
        
        return VerifyResponse(
            valid=valid,
            algorithm="Ed25519"
        )
    except Exception as e:
        raise HTTPException(500, f"Erro na verificação: {str(e)}")

@app.post("/api/v1/keygen", response_model=KeygenResponse, tags=["Gerenciamento de Chaves"])
async def keygen_endpoint(request: KeygenRequest):
    """
    Gera par de chaves (Ed25519 ou Hybrid)
    
    - **algorithm**: "ed25519" ou "hybrid" (ECDH + Fibonacci + Kyber)
    """
    try:
        stats['total_requests'] += 1
        stats['keygen_count'] += 1
        
        if request.algorithm.lower() == "ed25519":
            cipher = get_cipher("dummy")
            private_key, public_key = cipher.generate_keypair()
            
            return KeygenResponse(
                private_key=base64_encode(private_key),
                public_key=base64_encode(public_key),
                algorithm="Ed25519",
                created_at=datetime.now().isoformat()
            )
        
        elif request.algorithm.lower() == "hybrid":
            kex = get_hybrid_kex()
            keypair = kex.generate_keypair()
            
            # Serializar keypair híbrido (simplificado)
            import json
            private_data = {
                'ecdh_private': base64_encode(keypair.ecdh_private) if keypair.ecdh_private else None,
                'fibonacci_seed': keypair.fibonacci_seed
            }
            public_data = {
                'ecdh_public': base64_encode(keypair.ecdh_public) if keypair.ecdh_public else None,
                'fibonacci_level': keypair.fibonacci_level
            }
            
            return KeygenResponse(
                private_key=base64_encode(json.dumps(private_data).encode()),
                public_key=base64_encode(json.dumps(public_data).encode()),
                algorithm="Hybrid-ECDH-Fibonacci",
                created_at=keypair.created_at
            )
        
        else:
            raise HTTPException(400, f"Algoritmo desconhecido: {request.algorithm}")
    
    except Exception as e:
        raise HTTPException(500, f"Erro na geração de chaves: {str(e)}")


@app.post(
    "/api/v1/licenses/generate",
    response_model=LicenseGenerateResponse,
    tags=["Licenças"],
)
async def license_generate_endpoint(request: LicenseGenerateRequest):
    """Gera uma nova licença assinada para o KayosCryptoSuite."""
    if not LICENSING_AVAILABLE or LicenseBuilder is None or CryptoCore is None:
        raise HTTPException(503, "Módulo de licenças não disponível neste ambiente")
    if LICENSE_PRIVATE_KEY is None:
        raise HTTPException(503, "Chaves de licenciamento não inicializadas")

    try:
        expiration = parse_license_expiration(request.expiration_date)
        license_string, license_payload = LicenseBuilder.build_and_sign(
            user_data=request.user_data,
            level=request.level,
            expiration_date=expiration,
            private_key_pem=LICENSE_PRIVATE_KEY,
            metadata=request.metadata or {},
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(500, f"Erro ao gerar licença: {exc}")

    if LICENSE_DB_AVAILABLE and licensing_db is not None:
        try:
            licensing_db.insert_license_log(  # type: ignore[attr-defined]
                license_id=license_payload.get("license_id", ""),
                operation="generate",
                user_name=request.user_data.get("name", ""),
                email=request.user_data.get("email", ""),
                level=request.level,
                expiration=expiration,
            )
        except Exception as exc:  # pragma: no cover - optional persistence
            print(f" [API] Falha ao registrar licença no banco: {exc}")

    return LicenseGenerateResponse(
        license_string=license_string,
        license_data=license_payload,
    )


@app.post(
    "/api/v1/licenses/validate",
    response_model=LicenseValidateResponse,
    tags=["Licenças"],
)
async def license_validate_endpoint(request: LicenseValidateRequest):
    """Valida uma licença emitida anteriormente."""
    if not LICENSING_AVAILABLE or LicenseValidator is None or LICENSE_PUBLIC_KEY is None:
        raise HTTPException(503, "Módulo de licenças não disponível neste ambiente")

    try:
        is_valid, payload = LicenseValidator.validate(
            request.license_string,
            LICENSE_PUBLIC_KEY,
        )
    except Exception as exc:  # pragma: no cover - defensive guard
        raise HTTPException(500, f"Erro ao validar licença: {exc}")

    return LicenseValidateResponse(valid=bool(is_valid), payload=payload if is_valid else None)


@app.post("/api/v1/stego/embed", tags=["Esteganografia"])
async def stego_embed_endpoint(
    password: str = Form(...),
    payload: str = Form(...),  # Base64
    cover_image: UploadFile = File(...)
):
    """
    Embute payload criptografado em imagem (LSB)
    
    - **password**: Senha para criptografar payload
    - **payload**: Dados a ocultar (base64)
    - **cover_image**: Imagem PNG (upload)
    
    Retorna imagem com payload oculto
    """
    try:
        stats['total_requests'] += 1
        stats['stego_embed_count'] += 1
        
        # Decodificar payload
        payload_bytes = base64_decode(payload)
        
        # Salvar cover image temporariamente
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as cover_tmp:
            cover_tmp.write(await cover_image.read())
            cover_path = cover_tmp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as stego_tmp:
            stego_path = stego_tmp.name
        
        # Embed
        stego = get_stego(password)
        metadata = stego.embed(cover_path, payload_bytes, stego_path)
        
        # Ler stego image
        with open(stego_path, 'rb') as f:
            stego_bytes = f.read()
        
        # Limpar arquivos temporários
        os.unlink(cover_path)
        os.unlink(stego_path)
        
        # Retornar imagem como stream
        return StreamingResponse(
            io.BytesIO(stego_bytes),
            media_type="image/png",
            headers={
                "Content-Disposition": "attachment; filename=stego.png",
                "X-Payload-Size": str(metadata.payload_size_bytes),
                "X-Capacity": str(metadata.capacity_bytes),
                "X-Utilization": f"{metadata.utilization_percent:.2f}%"
            }
        )
    
    except Exception as e:
        raise HTTPException(500, f"Erro no embedding: {str(e)}")

@app.post("/api/v1/stego/extract", tags=["Esteganografia"])
async def stego_extract_endpoint(
    password: str = Form(...),
    stego_image: UploadFile = File(...)
):
    """
    Extrai payload oculto de imagem
    
    - **password**: Senha usada no embedding
    - **stego_image**: Imagem com payload oculto (PNG)
    
    Retorna payload descriptografado (base64)
    """
    try:
        stats['total_requests'] += 1
        stats['stego_extract_count'] += 1
        
        # Salvar stego image temporariamente
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as stego_tmp:
            stego_tmp.write(await stego_image.read())
            stego_path = stego_tmp.name
        
        # Extract
        stego = get_stego(password)
        payload_bytes = stego.extract(stego_path)
        
        # Limpar
        os.unlink(stego_path)
        
        return JSONResponse({
            "payload": base64_encode(payload_bytes),
            "size_bytes": len(payload_bytes)
        })
    
    except Exception as e:
        raise HTTPException(500, f"Erro na extração: {str(e)}")

@app.get("/api/v1/health", response_model=HealthResponse, tags=["Sistema"])
async def health_endpoint():
    """Health check da API"""
    uptime = (datetime.now() - stats['start_time']).total_seconds()
    
    return HealthResponse(
        status="healthy",
        version="6.4.0",
        uptime_seconds=uptime,
        modules_available={
            "kayoscrypto": KAYOS_AVAILABLE,
            "hybrid_kex": HYBRID_AVAILABLE,
            "steganography": STEGO_AVAILABLE
        }
    )

@app.get("/api/v1/stats", response_model=StatsResponse, tags=["Sistema"])
async def stats_endpoint():
    """Estatísticas de uso da API"""
    uptime = (datetime.now() - stats['start_time']).total_seconds()

    return StatsResponse(
        total_requests=stats['total_requests'],
        encrypt_count=stats['encrypt_count'],
        decrypt_count=stats['decrypt_count'],
        sign_count=stats['sign_count'],
        verify_count=stats['verify_count'],
        keygen_count=stats['keygen_count'],
        stego_embed_count=stats['stego_embed_count'],
        stego_extract_count=stats['stego_extract_count'],
        uptime_seconds=uptime
    )

@app.get(
    "/api/v1/certifications/latest",
    response_model=CertificationSnapshotResponse,
    tags=["Certificações"],
)
async def certification_latest_endpoint():
    """Retorna snapshot mais recente gerado pelo CertificationTracker."""
    if not CERT_TRACKER_AVAILABLE or CertificationTracker is None:
        raise HTTPException(503, "CertificationTracker não disponível neste ambiente")

    snapshot = CertificationTracker.latest_snapshot()
    if snapshot is None:
        return CertificationSnapshotResponse(available=False, snapshot=None)
    return CertificationSnapshotResponse(available=True, snapshot=snapshot)


@app.get(
    "/api/v1/telemetry/quantum-dashboard",
    response_model=QuantumDashboardSummaryResponse,
    tags=["Quantum Telemetry"],
)
async def quantum_dashboard_summary_endpoint():
    """Retorna o resumo agregado do dashboard quântico gerado pelos scripts de telemetria."""
    if not QUANTUM_DASHBOARD_JSON.exists():
        return QuantumDashboardSummaryResponse(
            available=False,
            artifact_path=str(QUANTUM_DASHBOARD_JSON),
            error="dashboard_summary.json não encontrado; execute tools/generate_quantum_dashboard.py",
        )

    try:
        with QUANTUM_DASHBOARD_JSON.open("r", encoding="utf-8") as handler:
            payload = json.load(handler)
    except json.JSONDecodeError as exc:
        raise HTTPException(500, f"dashboard_summary.json inválido: {exc}") from exc
    except OSError as exc:  # pragma: no cover - IO failure edge case
        raise HTTPException(500, f"Erro ao ler dashboard_summary.json: {exc}") from exc

    generated_at = payload.get("generated_at")
    high_risk_payload: Optional[Dict[str, Any]] = None
    if HIGH_RISK_JSON.exists():
        try:
            with HIGH_RISK_JSON.open("r", encoding="utf-8") as handler:
                high_risk_payload = json.load(handler)
        except (json.JSONDecodeError, OSError):  # pragma: no cover - tolerar snapshot inválido
            high_risk_payload = None
    return QuantumDashboardSummaryResponse(
        available=True,
        summary=payload,
        generated_at=generated_at,
        artifact_path=str(QUANTUM_DASHBOARD_JSON),
        high_risk=high_risk_payload,
    )

@app.get("/api/v1/info", response_model=InfoResponse, tags=["Sistema"])
async def info_endpoint():
    """Informações sobre o sistema"""
    return InfoResponse(
        name="KayosCrypto",
        version="6.4.0",
        description="Sistema de criptografia geométrica multicamada com esteganografia e assinatura digital",
        algorithms={
            "symmetric": ["KayosCrypto-Geometric", "Fibonacci", "Ezekiel", "Core"],
            "asymmetric": ["Ed25519", "ECDH-P521", "Fibonacci-Geometric"],
            "post_quantum": ["Kyber1024 (opcional)"],
            "steganography": ["LSB-RGB"],
            "hash": ["SHA-256", "SHA-512"]
        },
        capabilities=[
            "Criptografia simétrica geométrica (47.80% avalanche)",
            "Assinatura digital Ed25519",
            "Troca híbrida de chaves (ECDH + Fibonacci + Kyber)",
            "Esteganografia visual LSB em PNG",
            "95.6% resistência quântica",
            "100% reversibilidade garantida"
        ],
        documentation="/api/v1/docs"
    )


# =====================================================================
# MAIN (para teste local)
# =====================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║           KAYOSCRYPTO API REST - CORE INTEGRATION            ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    print(" Iniciando servidor API...")
    print("├─ Host: http://localhost:8000")
    print("├─ Docs: http://localhost:8000/api/v1/docs")
    print("├─ ReDoc: http://localhost:8000/api/v1/redoc")
    print("└─ Health: http://localhost:8000/api/v1/health\n")
    
    uvicorn.run(app, host=os.getenv('FLASK_HOST', '127.0.0.1'), port=8000, log_level="info")
