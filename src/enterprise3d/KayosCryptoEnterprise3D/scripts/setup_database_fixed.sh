#!/bin/bash

# 🎲 KAYOSCRYPTO 3D ENTERPRISE DATABASE SETUP - FIXED VERSION
# Versão corrigida para problemas de locale

set -e

echo "🎲 Iniciando setup do KayosCrypto 3D Enterprise Database (Fixed)..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

# Check PostgreSQL
if ! pg_isready > /dev/null 2>&1; then
    print_error "PostgreSQL não está rodando"
    exit 1
fi

print_status "PostgreSQL está rodando"

# Create database without locale issues
print_status "Criando database k_crypto..."

sudo -u postgres psql << EOSQL
-- Drop if exists and recreate
DROP DATABASE IF EXISTS k_crypto;
CREATE DATABASE k_crypto ENCODING 'UTF8';

-- Create user if not exists
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'kayos') THEN
        CREATE USER kayos WITH PASSWORD 'kayopass';
    END IF;
END
\$\$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE k_crypto TO kayos;
GRANT CREATE ON DATABASE k_crypto TO kayos;
EOSQL

print_status "Database criado com sucesso"

# Now create the schema
print_status "Criando schema enterprise..."

# First, create the setup file without locale issues
cat > database/setup_kayos_crypto_simple.sql << 'EOSQL'
-- 🎲 KAYOSCRYPTO DATABASE SETUP - SIMPLIFIED
CREATE DATABASE k_crypto ENCODING 'UTF8';

\c k_crypto;

CREATE USER kayos WITH PASSWORD 'kayopass';
GRANT ALL PRIVILEGES ON DATABASE k_crypto TO kayos;
GRANT CREATE ON DATABASE k_crypto TO kayos;

CREATE SCHEMA IF NOT EXISTS kayos_enterprise;
GRANT USAGE ON SCHEMA kayos_enterprise TO kayos;
GRANT ALL ON ALL TABLES IN SCHEMA kayos_enterprise TO kayos;
GRANT ALL ON ALL SEQUENCES IN SCHEMA kayos_enterprise TO kayos;

ALTER DATABASE k_crypto SET search_path TO kayos_enterprise, public;
EOSQL

# Execute schema creation as kayos user
print_status "Executando schema principal..."

sudo -u postgres psql -d k_crypto -f database/schema_enterprise_3d.sql

print_status "Schema enterprise criado com sucesso"

# Test the connection
print_status "Testando conexão..."

if psql -d k_crypto -U kayos -c "SELECT '🎲 KayosCrypto 3D Enterprise - Database OK!' as status;" > /dev/null 2>&1; then
    print_status "Conexão teste bem-sucedida!"
else
    print_error "Falha na conexão teste"
    exit 1
fi

# Final summary
echo ""
print_status "🎲 KAYOSCRYPTO 3D ENTERPRISE DATABASE CONFIGURADO COM SUCESSO!"
echo "=========================================================="
echo "📊 Database: k_crypto"
echo "👤 Usuário: kayos"
echo "🔐 Senha: kayopass"
echo "🏗️ Schema: kayos_enterprise"
echo ""
echo "Para conectar:"
echo "  psql -d k_crypto -U kayos"
echo ""
echo "Para uso Python:"
echo "  dbname=k_crypto user=kayos password=kayopass host=localhost port=5432"
