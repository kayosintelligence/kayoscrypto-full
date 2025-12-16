#!/bin/bash

echo "🎲 Setup SUPER SIMPLE do KayosCrypto Database..."

# Executar o SQL completo de uma vez
sudo -u postgres psql -f database/setup_complete.sql

# Testar a conexão
echo ""
echo "🧪 Testando conexão..."
psql -d k_crypto -U kayos -c "SELECT cube_name FROM kayos_enterprise.sator_cubes;"

echo ""
echo "✅ Setup completo! Database pronto para uso."
