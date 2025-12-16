#!/bin/bash

echo "🚀 KAYOSCRYPTO 3D ENTERPRISE - INICIALIZAÇÃO COMPLETA"
echo "===================================================="

# Ativar ambiente virtual se existir
if [ -d "kayos_venv" ]; then
    echo "🔧 Ativando ambiente virtual..."
    source kayos_venv/bin/activate
fi

# Verificar dependências
echo "📦 Verificando dependências..."
python3 -c "
import importlib
deps = ['psycopg2', 'fastapi', 'uvicorn', 'cryptography', 'pydantic']
missing = []
for dep in deps:
    try:
        importlib.import_module(dep)
        print(f'✅ {dep}')
    except ImportError:
        missing.append(dep)
        print(f'❌ {dep}')
if missing:
    print(f'\\n⚠️  Dependências faltantes: {missing}')
    print('Execute: ./install_dependencies.sh')
else:
    print('\\n✅ Todas dependências instaladas!')
"

# Iniciar API
echo ""
echo "🌐 Iniciando API REST Enterprise..."
python3 src/api/fastapi_enterprise.py &

# Aguardar API iniciar
sleep 5

# Iniciar Web Dashboard
echo ""
echo "📊 Iniciando Web Dashboard..."
python3 web_dashboard.py &

echo ""
echo "🎉 SISTEMA KAYOSCRYPTO 3D ENTERPRISE INICIADO!"
echo ""
echo "🌐 URLs de Acesso:"
echo "   API REST: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Web Dashboard: http://localhost:5000"
echo ""
echo "🔑 Token de Autenticação: kayos_enterprise_token"
echo ""
echo "🛑 Para parar o sistema: pkill -f 'python3'"
