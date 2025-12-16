-- 🎲 KAYOSCRYPTO 3D ENTERPRISE DATABASE SETUP
-- Banco de dados multidimensional para Cubo Sator 3D

-- Criar database
CREATE DATABASE k_crypto
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Conectar ao database k_crypto
\c k_crypto;

-- Criar usuário kayos com senha
CREATE USER kayos WITH PASSWORD 'kayopass';

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE k_crypto TO kayos;
GRANT CREATE ON DATABASE k_crypto TO kayos;

-- Criar schema enterprise
CREATE SCHEMA IF NOT EXISTS kayos_enterprise;
GRANT USAGE ON SCHEMA kayos_enterprise TO kayos;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA kayos_enterprise TO kayos;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA kayos_enterprise TO kayos;

-- Configurar search_path
ALTER DATABASE k_crypto SET search_path TO kayos_enterprise, public;
