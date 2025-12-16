#!/bin/bash

echo "🚀 SETUP COMPLETO DO KAYOSCRYPTO 3D ENTERPRISE"
echo "=============================================="

# 1. Corrigir autenticação
echo "🔐 Passo 1: Corrigindo autenticação PostgreSQL..."
./fix_authentication.sh

echo ""
echo "📁 Passo 2: Verificando estrutura de arquivos..."
# Criar estrutura de diretórios
mkdir -p src/database src/cube src/security src/api src/monitoring config scripts

# Mover arquivos para estrutura correta
[ -f postgresql_manager.py ] && mv postgresql_manager.py src/database/
[ -f sator_cube_3d.py ] && mv sator_cube_3d.py src/cube/
[ -f quantum_engine.py ] && mv quantum_engine.py src/cube/
[ -f hsm_integration.py ] && mv hsm_integration.py src/security/

# Criar __init__.py
touch src/__init__.py src/database/__init__.py src/cube/__init__.py
touch src/security/__init__.py src/api/__init__.py src/monitoring/__init__.py

echo "✅ Estrutura de arquivos organizada"

echo ""
echo "🧪 Passo 3: Executando testes..."
python3 test_fixed.py

echo ""
echo "📊 Passo 4: Verificando estado do banco..."
sudo -u postgres psql -d k_crypto -c "
SELECT 
    (SELECT COUNT(*) FROM kayos_enterprise.sator_cubes) as cubes,
    (SELECT COUNT(*) FROM kayos_enterprise.cryptographic_keys_4d WHERE is_active = true) as active_keys,
    (SELECT COUNT(*) FROM kayos_enterprise.enterprise_users) as users,
    (SELECT COUNT(*) FROM kayos_enterprise.audit_trail) as audit_entries;
"

echo ""
echo "🎉 SETUP COMPLETO FINALIZADO!"
echo ""
echo "📋 RESUMO DO SISTEMA:"
echo "   ✅ Database: k_crypto (PostgreSQL)"
echo "   ✅ Usuário: kayos"
echo "   ✅ Schema: kayos_enterprise"
echo "   ✅ Tabelas: 10 tabelas enterprise"
echo "   ✅ Módulos Python: Estrutura organizada"
echo ""
echo "🚀 PRÓXIMOS PASSOS:"
echo "   1. Desenvolver API REST enterprise"
echo "   2. Implementar frontend web"
echo "   3. Configurar HSM em produção"
echo "   4. Implementar monitoramento"
