#!/bin/bash

echo "📦 Instalando dependências do KayosCrypto 3D Enterprise..."

# Atualizar sistema
sudo apt update

# Instalar dependências do sistema
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib

# Criar ambiente virtual
python3 -m venv kayos_venv
source kayos_venv/bin/activate

# Instalar dependências Python
pip install --upgrade pip

# Dependências básicas
pip install psycopg2-binary fastapi uvicorn python-dotenv cryptography

# Tentar instalar OQS (Open Quantum Safe)
echo "🔬 Instalando Open Quantum Safe..."
pip install oqs

# Se OQS falhar, instalar versão alternativa
if [ $? -ne 0 ]; then
    echo "⚠️  OQS não disponível, instalando dependências alternativas..."
    pip install pycryptodome
fi

# Dependências enterprise
pip install pydantic jinja2 python-multipart

echo "✅ Dependências instaladas!"
echo ""
echo "🔧 Para ativar o ambiente virtual:"
echo "   source kayos_venv/bin/activate"
echo ""
echo "🚀 Para executar o sistema:"
echo "   python3 start_enterprise_system.py"
