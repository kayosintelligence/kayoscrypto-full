"""
 FASTAPI ENTERPRISE - KAYOSCRYPTO 3D ENTERPRISE API
API REST completa para operações multidimensionais
"""

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
import os
import sys

# Configurar path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from database.postgresql_manager import PostgreSQLManager
from cube.sator_cube_3d import SatorCube3D, CubeRotation
from cube.quantum_engine import QuantumClassicalEngine

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KayosAPI")

# Inicializar FastAPI
app = FastAPI(
 title="KayosCrypto 3D Enterprise API",
 description="API REST para criptografia multidimensional enterprise",
 version="3.0.0",
 docs_url="/docs",
 redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
 CORSMiddleware,
 allow_origins=["*"], # Em produção, especificar domínios
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
 rotations: List[str] # ['X_AXIS', 'Y_AXIS', etc]

class EncryptionRequest(BaseModel):
 cube_name: str
 plaintext: str
 key_id: Optional[str] = None

class DecryptionRequest(BaseModel):
 cube_name: str
 ciphertext_data: Dict[str, Any]

class KeyGenerationRequest(BaseModel):
 cube_name: str

# Dependencies
def get_db():
 db = PostgreSQLManager()
 if db.connect():
 return db
 raise HTTPException(status_code=500, detail="Database connection failed")

def authenticate(credentials: HTTPAuthorizationCredentials = Security(security)):
 # Em produção, validar JWT ou API key
 token = credentials.credentials
 if token != "kayos_enterprise_token": # Token simples para desenvolvimento
 raise HTTPException(status_code=401, detail="Invalid token")
 return token

# Routes
@app.get("/")
async def root():
 return {
 "message": " KayosCrypto 3D Enterprise API",
 "version": "3.0.0",
 "status": "operational"
 }

@app.get("/health")
async def health_check(db: PostgreSQLManager = Depends(get_db)):
 """Health check endpoint"""
 try:
 # Testar conexão com banco
 cubes = db.execute_query("SELECT COUNT(*) as count FROM kayos_enterprise.sator_cubes;")
 return {
 "status": "healthy",
 "database": "connected",
 "cubes_count": cubes[0]['count'] if cubes else 0
 }
 except Exception as e:
 raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@app.post("/cubes/create", dependencies=[Depends(authenticate)])
async def create_cube(
 request: CubeCreateRequest,
 db: PostgreSQLManager = Depends(get_db)
):
 """Criar novo Cubo Sator 3D"""
 try:
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
 if cube_id:
 db.log_audit_event({
 'event_type': 'cube_created',
 'severity': 'INFO',
 'cube_id': cube_id,
 'event_data': cube_data
 })
 
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

@app.post("/cubes/{cube_name}/rotate", dependencies=[Depends(authenticate)])
async def rotate_cube(
 cube_name: str,
 request: RotationRequest,
 db: PostgreSQLManager = Depends(get_db)
):
 """Rotacionar Cubo Sator 3D"""
 try:
 # Buscar cubo
 cube = db.get_cube_by_name(cube_name)
 if not cube:
 raise HTTPException(status_code=404, detail="Cube not found")
 
 # Inicializar cubo Python
 sator_cube = SatorCube3D(security_level=cube['security_level'])
 
 # Converter rotações para enum
 rotations = []
 for rotation in request.rotations:
 try:
 rotations.append(CubeRotation(rotation))
 except ValueError:
 raise HTTPException(status_code=400, detail=f"Invalid rotation: {rotation}")
 
 # Executar rotações
 rotation_result = sator_cube.rotate_cube(rotations)
 
 # Atualizar no banco
 db.update_cube_rotation(cube['cube_id'], rotation_result)
 
 # Registrar auditoria
 db.log_audit_event({
 'event_type': 'cube_rotated',
 'severity': 'INFO',
 'cube_id': cube['cube_id'],
 'event_data': {
 'rotations': request.rotations,
 'result': rotation_result
 }
 })
 
 return {
 "status": "success",
 "cube_name": cube_name,
 "rotations": request.rotations,
 "new_orientation": rotation_result['current_orientation'],
 "tenet_signature": rotation_result['tenet_signature'].hex()[:16] + "..."
 }
 
 except Exception as e:
 logger.error(f"Error rotating cube: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@app.post("/keys/generate", dependencies=[Depends(authenticate)])
async def generate_keys(
 request: KeyGenerationRequest,
 db: PostgreSQLManager = Depends(get_db)
):
 """Gerar chaves 4D para um cubo"""
 try:
 cube = db.get_cube_by_name(request.cube_name)
 if not cube:
 raise HTTPException(status_code=404, detail="Cube not found")
 
 # Inicializar motor criptográfico
 sator_cube = SatorCube3D(security_level=cube['security_level'])
 quantum_engine = QuantumClassicalEngine(sator_cube)
 
 # Gerar material de chaves
 key_material = quantum_engine.generate_4d_key_exchange()
 key_material['cube_id'] = cube['cube_id']
 
 # Armazenar no banco
 key_id = db.store_4d_key_material(key_material)
 
 # Registrar auditoria
 db.log_audit_event({
 'event_type': 'keys_generated',
 'severity': 'INFO',
 'cube_id': cube['cube_id'],
 'key_id': key_id,
 'event_data': {
 'meeting_point': key_material['meeting_point'],
 'security_level': key_material['meeting_point']['security_level']
 }
 })
 
 return {
 "status": "success",
 "key_id": key_id,
 "cube_name": request.cube_name,
 "meeting_point": key_material['meeting_point'],
 "message": "Chaves 4D geradas com sucesso"
 }
 
 except Exception as e:
 logger.error(f"Error generating keys: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@app.post("/crypto/encrypt", dependencies=[Depends(authenticate)])
async def encrypt_data(
 request: EncryptionRequest,
 db: PostgreSQLManager = Depends(get_db)
):
 """Criptografar dados usando Cubo Sator 3D"""
 try:
 cube = db.get_cube_by_name(request.cube_name)
 if not cube:
 raise HTTPException(status_code=404, detail="Cube not found")
 
 # Buscar chave ativa
 active_keys = db.get_active_keys_for_cube(cube['cube_id'])
 if not active_keys:
 raise HTTPException(status_code=400, detail="No active keys found for cube")
 
 # Usar chave específica ou a primeira ativa
 key_to_use = None
 if request.key_id:
 key_to_use = next((k for k in active_keys if k['key_id'] == request.key_id), None)
 if not key_to_use:
 raise HTTPException(status_code=404, detail="Key not found")
 else:
 key_to_use = active_keys[0]
 
 # Simular criptografia (em produção, usar QuantumClassicalEngine)
 # Esta é uma simulação - em produção integrar com o motor real
 
 encrypted_result = {
 "ciphertext": f"encrypted_{request.plaintext}",
 "key_id": key_to_use['key_id'],
 "algorithm": key_to_use['algorithm_combination'],
 "security_level": key_to_use['security_level']
 }
 
 # Registrar operação
 db.log_crypto_operation({
 'key_id': key_to_use['key_id'],
 'cube_id': cube['cube_id'],
 'operation_type': 'encrypt',
 'cube_rotation_state': cube['current_rotation_state'],
 'tenet_signature': b'simulated_signature',
 'data_size_bytes': len(request.plaintext),
 'status': 'completed'
 })
 
 return {
 "status": "success",
 "encrypted_data": encrypted_result,
 "message": "Dados criptografados com sucesso"
 }
 
 except Exception as e:
 logger.error(f"Error encrypting data: {e}")
 raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/security")
async def security_dashboard(db: PostgreSQLManager = Depends(get_db)):
 """Dashboard de segurança enterprise"""
 try:
 dashboard = db.get_security_dashboard()
 compliance = db.get_compliance_report()
 
 return {
 "status": "success",
 "dashboard": dashboard,
 "compliance_report": compliance,
 "timestamp": "2024-01-01T00:00:00Z" # Em produção, usar datetime atual
 }
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

@app.get("/cubes")
async def list_cubes(db: PostgreSQLManager = Depends(get_db)):
 """Listar todos os cubos"""
 try:
 cubes = db.execute_query("SELECT cube_id, cube_name, security_level, rotation_count FROM kayos_enterprise.sator_cubes WHERE is_active = true;")
 return {
 "status": "success",
 "cubes": cubes,
 "total": len(cubes)
 }
 except Exception as e:
 raise HTTPException(status_code=500, detail=str(e))

# Startup event
@app.on_event("startup")
async def startup_event():
 logger.info(" KayosCrypto 3D Enterprise API iniciada!")

# Shutdown event 
@app.on_event("shutdown")
async def shutdown_event():
 logger.info(" KayosCrypto 3D Enterprise API finalizada!")

if __name__ == "__main__":
 import uvicorn
 uvicorn.run(
 "fastapi_enterprise:app",
 host=os.getenv('FLASK_HOST', '127.0.0.1'),
 port=8000,
 reload=True,
 log_level="info"
 )
