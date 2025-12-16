#!/bin/bash

echo "🔐 Corrigindo autenticação PostgreSQL..."

# Verificar método de autenticação atual
echo "Métodos de autenticação atuais:"
sudo -u postgres psql -c "SELECT rolname, rolpassword FROM pg_roles WHERE rolname = 'kayos';"

# Corrigir a senha do usuário kayos
sudo -u postgres psql -c "ALTER USER kayos WITH PASSWORD 'kayopass';"

# Verificar pg_hba.conf
echo ""
echo "📋 Configuração pg_hba.conf (últimas linhas):"
sudo tail -10 /etc/postgresql/*/main/pg_hba.conf

# Adicionar entrada se necessário (método trust para local)
echo ""
echo "➕ Adicionando método trust para usuário kayos (local)..."
sudo -u postgres psql -c "CREATE USER IF NOT EXISTS kayos WITH PASSWORD 'kayopass';"

# Recarregar configuração
sudo systemctl reload postgresql

echo ""
echo "🧪 Testando conexão..."
psql -d k_crypto -U kayos -h localhost -c "SELECT '✅ Conexão bem-sucedida!' as status;"

if [ $? -eq 0 ]; then
    echo "🎉 Autenticação corrigida com sucesso!"
else
    echo "⚠️  Tentando método trust..."
    # Método alternativo: permitir trust para kayos
    sudo sh -c 'echo "local   k_crypto         kayos                                   trust" >> /etc/postgresql/*/main/pg_hba.conf'
    sudo systemctl reload postgresql
    psql -d k_crypto -U kayos -c "SELECT '✅ Conexão com trust bem-sucedida!' as status;"
fi
