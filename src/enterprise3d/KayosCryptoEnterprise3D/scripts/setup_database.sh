#!/bin/bash

# 🎲 KAYOSCRYPTO 3D ENTERPRISE DATABASE SETUP SCRIPT
# Configuração completa do banco de dados PostgreSQL

set -e

echo "🎲 Iniciando setup do KayosCrypto 3D Enterprise Database..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database configuration
DB_NAME="k_crypto"
DB_USER="kayos"
DB_PASS="kayopass"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if PostgreSQL is running
if ! pg_isready > /dev/null 2>&1; then
    print_error "PostgreSQL não está rodando. Inicie o serviço primeiro."
    exit 1
fi

print_status "PostgreSQL está rodando"

# Check if we can connect as postgres user
if ! sudo -u postgres psql -c "\q" > /dev/null 2>&1; then
    print_error "Não é possível conectar como usuário postgres"
    exit 1
fi

print_status "Conectado como usuário postgres"

# Create database and user
print_status "Criando database $DB_NAME e usuário $DB_USER..."

sudo -u postgres psql << EOSQL
-- Create database
CREATE DATABASE $DB_NAME
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Create user
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
GRANT CREATE ON DATABASE $DB_NAME TO $DB_USER;
EOSQL

print_status "Database e usuário criados com sucesso"

# Run the schema creation
print_status "Executando schema enterprise..."

sudo -u postgres psql -d $DB_NAME -f database/schema_enterprise_3d.sql

print_status "Schema enterprise criado com sucesso"

# Create additional indexes for performance
print_status "Otimizando performance com índices adicionais..."

sudo -u postgres psql -d $DB_NAME -U $DB_USER << EOSQL
-- Additional performance indexes
CREATE INDEX CONCURRENTLY idx_crypto_ops_composite ON kayos_enterprise.crypto_operations(cube_id, started_at, operation_type);
CREATE INDEX CONCURRENTLY idx_audit_composite ON kayos_enterprise.audit_trail(event_timestamp, event_type, severity);
CREATE INDEX CONCURRENTLY idx_threats_composite ON kayos_enterprise.threat_events(detected_at, threat_level, status);

-- Vacuum and analyze for optimal performance
VACUUM ANALYZE kayos_enterprise.sator_cubes;
VACUUM ANALYZE kayos_enterprise.cryptographic_keys_4d;
VACUUM ANALYZE kayos_enterprise.crypto_operations;
EOSQL

print_status "Otimizações de performance concluídas"

# Test connection
print_status "Testando conexão com o novo database..."

if psql -d $DB_NAME -U $DB_USER -c "SELECT cube_name FROM kayos_enterprise.sator_cubes LIMIT 1;" > /dev/null 2>&1; then
    print_status "Conexão teste bem-sucedida!"
else
    print_error "Falha na conexão teste"
    exit 1
fi

# Print summary
echo ""
print_status "🎲 KAYOSCRYPTO 3D ENTERPRISE DATABASE CONFIGURADO!"
echo "=========================================================="
echo "📊 Database: $DB_NAME"
echo "👤 Usuário: $DB_USER"
echo "🔐 Schema: kayos_enterprise"
echo "📈 Tabelas: 10 tabelas enterprise"
echo "🚀 Views: 2 views de monitoring"
echo "⚡ Pronto para uso enterprise!"
echo ""
echo "Para conectar:"
echo "  psql -d $DB_NAME -U $DB_USER"
echo ""
echo "Para usar com Python:"
echo "  dbname=$DB_NAME user=$DB_USER password=$DB_PASS host=localhost port=5432"
echo ""

print_warning "Lembre-se de:"
print_warning "1. Configurar backup automático"
print_warning "2. Configurar replicação para alta disponibilidade"
print_warning "3. Monitorar performance regularmente"
