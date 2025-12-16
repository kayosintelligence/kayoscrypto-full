"""
 FASTAPI ENTERPRISE CORRIGIDA - KAYOSCRYPTO 3D ENTERPRISE API
Versão com lifespan events e correções
"""

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import os
import sys

# Configurar path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
 from database.postgresql_manager import PostgreSQLManager
 from cube.sator_cube_3d import SatorCube3D, CubeRotation
 from cube.quantum_engine import QuantumClassicalEngine
 HAS_CRYPTO_DEPS = True
except ImportError as e:
 print(f" Dependências criptográficas não disponíveis: {e}")
 HAS_CRYPTO_DEPS = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KayosAPI")

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
 # Startup
 logger.info(" KayosCrypto 3D Enterprise API iniciando...")
 yield
 # Shutdown
 logger.info(" KayosCrypto 3D Enterprise API finalizando...")

# Inicializar FastAPI
app = FastAPI(
 title="KayosCrypto 3D Enterprise API",
 description="API REST para criptografia multidimensional enterprise",
 version="3.0.0",
 docs_url="/docs",
 redoc_url="/redoc",
 lifespan=lifespan
)

# CORS middleware
app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"],
 allow_credentials=True,
 allow_methods=["*"],
 allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Models Pydantic
class CubeCreateRequest(BaseModel):
 cube_name: str
 security_level: str = "enterprise"

class RotationRequest(BaseModel):
 cube_name: str
 rotations: List[str]

class EncryptionRequest(BaseModel):
 cube_name: str
 plaintext: str
 key_id: Optional[str] = None

# Dependencies
def get_db():
 db = PostgreSQLManager()
 if db.connect():
 return db
 raise HTTPException(status_code=500, detail="Database connection failed")

def authenticate(credentials: HTTPAuthorizationCredentials = Security(security)):
 token = credentials.credentials
 if token != "kayos_enterprise_token":
 raise HTTPException(status_code=401, detail="Invalid token")
 return token

# Routes
@app.get("/")
async def root():
 return {
 "message": " KayosCrypto 3D Enterprise API",
 "version": "3.0.0",
 "status": "operational",
 "crypto_available": HAS_CRYPTO_DEPS
 }

@app.get("/health")
async def health_check():
 """Health check simplificado"""
 try:
 db = PostgreSQLManager()
 if db.connect():
 cubes = db.execute_query("SELECT COUNT(*) as count FROM kayos_enterprise.sator_cubes;")
 db.disconnect()
 return {
 "status": "healthy",
 "database": "connected",
 "cubes_count": cubes[0]['count'] if cubes else 0,
 "crypto_engine": "available" if HAS_CRYPTO_DEPS else "simulated"
 }
 except Exception as e:
 return {
 "status": "degraded",
 "database": "error",
 "error": str(e)
 }

@app.get("/cubes")
async def list_cubes():
 """Listar cubos disponíveis"""
 try:
 db = PostgreSQLManager()
 if db.connect():
 cubes = db.execute_query(
 "SELECT cube_id, cube_name, security_level, rotation_count, created_at "
 "FROM kayos_enterprise.sator_cubes WHERE is_active = true;"
 )
 db.disconnect()
 return {
 "status": "success",
 "cubes": cubes,
 "total": len(cubes)
 }
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.post("/cubes/create")
async def create_cube(request: CubeCreateRequest):
 """Criar novo Cubo Sator 3D"""
 try:
 db = PostgreSQLManager()
 if not db.connect():
 raise HTTPException(status_code=500, detail="Database connection failed")
 
 cube_data = {
 'cube_name': request.cube_name,
 'security_level': request.security_level,
 'rotation_state': {'x': 0, 'y': 0, 'z': 0, 'w': 0},
 'tenet_center_hash': b'default_tenet_center',
 'faces_configuration': {
 'north': {'verso': 'Kyber512', 'anverso': 'Kyber1024'},
 'south': {'verso': 'P-256', 'anverso': 'P-521'},
 'east': {'verso': 'AES-128-GCM', 'anverso': 'AES-256-GCM'},
 'west': {'verso': 'SHA-256', 'anverso': 'SHA3-512'},
 'top': {'verso': 'ChaCha20', 'anverso': 'XChaCha20'},
 'bottom': {'verso': 'HMAC-SHA256', 'anverso': 'BLAKE2b'}
 }
 }
 
 cube_id = db.create_sator_cube(cube_data)
 db.disconnect()
 
 if cube_id:
 return {
 "status": "success",
 "cube_id": cube_id,
 "cube_name": request.cube_name,
 "message": "Cubo Sator 3D criado com sucesso"
 }
 else:
 raise HTTPException(status_code=500, detail="Failed to create cube")
 
 except Exception as e:
 logger.error(f"Error creating cube: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/security")
async def security_dashboard():
 """Dashboard de segurança"""
 try:
 db = PostgreSQLManager()
 if db.connect():
 dashboard_data = db.execute_query("SELECT * FROM kayos_enterprise.security_dashboard;")
 compliance_data = db.execute_query("SELECT * FROM kayos_enterprise.compliance_report;")
 db.disconnect()
 
 return {
 "status": "success",
 "dashboard": dashboard_data,
 "compliance": compliance_data
 }
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.post("/demo/encrypt")
async def demo_encrypt(request: EncryptionRequest):
 """Demo de criptografia (simulado)"""
 try:
 db = PostgreSQLManager()
 if not db.connect():
 raise HTTPException(status_code=500, detail="Database connection failed")
 
 # Simular operação de criptografia
 encrypted_text = f"encrypted_{request.plaintext}_kayos3d"
 
 # Buscar cubo
 cube = db.execute_query(
 "SELECT cube_id FROM kayos_enterprise.sator_cubes WHERE cube_name = %s;",
 (request.cube_name,)
 )
 
 if cube:
 # Registrar operação simulada
 db.log_crypto_operation({
 'key_id': request.key_id or 'demo_key',
 'cube_id': cube[0]['cube_id'],
 'operation_type': 'encrypt',
 'cube_rotation_state': {'x': 0, 'y': 0, 'z': 0, 'w': 0},
 'tenet_signature': b'demo_signature',
 'data_size_bytes': len(request.plaintext),
 'status': 'completed'
 })
 
 db.disconnect()
 
 return {
 "status": "success",
 "original": request.plaintext,
 "encrypted": encrypted_text,
 "algorithm": "AES-256-GCM (Simulated)",
 "security_level": "quantum_256+classical_521"
 }
 
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
 import uvicorn
 uvicorn.run(
 "fastapi_enterprise_fixed:app",
 host=os.getenv('FLASK_HOST', '127.0.0.1'),
 port=8000,
 reload=True,
 log_level="info"
 )
