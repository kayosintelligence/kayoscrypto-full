#!/bin/bash

echo "🔄 CORREÇÃO DA INSTALAÇÃO OQS"
echo "=============================="

# Verificar ambiente virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ ERRO: Não está em ambiente virtual"
    exit 1
fi

echo "✅ Ambiente virtual: $VIRTUAL_ENV"

# Desinstalar pacote errado
echo ""
echo "🗑️  Desinstalando pacote 'oqs' incorreto..."
pip uninstall -y oqs

# Instalar pacote correto
echo ""
echo "📦 Instalando liboqs-python correto..."
pip install liboqs-python

# Verificar instalação correta
echo ""
echo "🧪 Verificando instalação correta..."
python3 -c "
try:
    import oqs
    print('✅ OQS importado com sucesso!')
    
    # Testar funcionalidades do liboqs-python real
    print('🔍 Testando API real...')
    
    # Listar mecanismos KEM disponíveis
    try:
        kems = oqs.get_enabled_KEM_mechanisms()
        print(f'✅ KEMs disponíveis: {len(kems)} algoritmos')
        for kem in sorted(kems)[:3]:
            print(f'   - {kem}')
            
        if 'Kyber1024' in kems:
            print('🎯 Kyber1024: ✅ DISPONÍVEL')
        else:
            print('❌ Kyber1024: NÃO ENCONTRADO')
            
    except Exception as e:
        print(f'❌ Erro ao listar KEMs: {e}')
    
    # Testar KeyEncapsulation
    try:
        with oqs.KeyEncapsulation('Kyber512') as kem:  # Testar com Kyber512 primeiro
            public_key = kem.generate_keypair()
            print(f'✅ KeyEncapsulation funcionando - Chave pública: {len(public_key)} bytes')
    except Exception as e:
        print(f'❌ KeyEncapsulation falhou: {e}')
        
except ImportError as e:
    print('❌ Falha ao importar OQS:', e)
    exit(1)
"

echo ""
echo "=============================="
if [ $? -eq 0 ]; then
    echo "🎉 OQS CORRETO INSTALADO!"
    echo "🚀 Pronto para implementação real"
else
    echo "❌ FALHA NA INSTALAÇÃO"
    exit 1
fi
