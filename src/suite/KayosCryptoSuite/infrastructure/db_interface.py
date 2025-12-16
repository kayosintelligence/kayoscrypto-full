# infrastructure/db_interface.py

import os
import time
from sqlalchemy import create_engine, insert, update, select
from datetime import date
from .license_model import metadata, license_logs

# --- CONFIGURAÇÃO POSTGRESQL ---
DB_USER = "kayos"
DB_PASSWORD = os.getenv("KAYOS_DB_PASSWORD", "")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "K_suite"
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
MAX_RETRIES = 3
RETRY_DELAY = 2

_db_engine = None

def init_db():
    global _db_engine
    if _db_engine:
        return

    for attempt in range(MAX_RETRIES):
        try:
            engine = create_engine(DATABASE_URL, pool_pre_ping=True)
            connection = engine.connect()
            connection.close()
            
            _db_engine = engine
            print("[DB Interface]  Conexão PostgreSQL estabelecida com sucesso.")
            
            metadata.create_all(_db_engine)
            print("[DB Interface]  Tabelas PostgreSQL verificadas/criadas com sucesso.")
            return

        except Exception as e:
            print(f"[DB Interface]  Tentativa {attempt + 1}/{MAX_RETRIES} falhou: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                print("[DB Interface]  Não foi possível conectar ao PostgreSQL.")
                raise

def insert_license_log(license_id: str, operation: str, user_name: str, email: str, level: str, expiration: date):
    if not _db_engine:
        print("[DB Interface]  Erro: PostgreSQL não inicializado.")
        return False
    
    try:
        with _db_engine.connect() as connection:
            stmt = insert(license_logs).values(
                license_id=license_id,
                operation=operation,
                user_name=user_name,
                email=email,
                level=level,
                expiration=expiration,
                status='active'
            )
            connection.execute(stmt)
            connection.commit()
            print(f"[DB Interface]  Licença {license_id} registrada no PostgreSQL.")
            return True
    except Exception as e:
        print(f"[DB Interface]  Erro ao inserir no PostgreSQL: {e}")
        return False

def get_license_status(license_id: str) -> str:
    if not _db_engine: 
        print("[DB Interface]   PostgreSQL não inicializado, retornando 'active'")
        return 'active'
    
    try:
        with _db_engine.connect() as connection:
            stmt = select(license_logs.c.status).where(license_logs.c.license_id == license_id)
            result = connection.execute(stmt).scalar_one_or_none()
            status = result if result else 'active'
            print(f"[DB Interface]  Status da licença {license_id}: {status}")
            return status
    except Exception as e:
        print(f"[DB Interface]  Erro ao buscar status no PostgreSQL: {e}")
        return 'active'

def revoke_license(license_id: str) -> bool:
    if not _db_engine: 
        return False
    
    try:
        with _db_engine.connect() as connection:
            stmt = update(license_logs).where(license_logs.c.license_id == license_id).values(status='revoked')
            result = connection.execute(stmt)
            connection.commit()
            success = result.rowcount > 0
            print(f"[DB Interface]  Licença {license_id} revogada: {success}")
            return success
    except Exception as e:
        print(f"[DB Interface]  Erro ao revogar no PostgreSQL: {e}")
        return False
