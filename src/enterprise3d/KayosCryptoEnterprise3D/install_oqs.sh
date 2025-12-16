#!/bin/bash

echo "🔬 INSTALAÇÃO OPEN QUANTUM SAFE (OQS)"
echo "======================================"

# Verificar se estamos no ambiente virtual
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ ERRO: Não está em ambiente virtual"
    echo "Execute: source kayos_venv/bin/activate"
    exit 1
fi

echo "✅ Ambiente virtual: $VIRTUAL_ENV"

# Instalar OQS
echo ""
echo "📦 Instalando liboqs-python..."
pip install oqs

# Verificar instalação
echo ""
echo "🧪 Verificando instalação OQS..."
python3 -c "
try:
    import oqs
    print('✅ OQS importado com sucesso!')
    print('📚 Versão disponível:', oqs.__version__ if hasattr(oqs, '__version__') else 'N/A')
    
    # Listar algoritmos disponíveis
    print('🔍 Algoritmos KEM disponíveis:')
    kem_algos = oqs.get_enabled_KEM_mechanisms()
    for algo in sorted(kem_algos)[:5]:  # Mostrar primeiros 5
        print(f'   - {algo}')
    
    if 'Kyber1024' in kem_algos:
        print('🎯 Kyber1024: ✅ DISPONÍVEL')
    else:
        print('❌ Kyber1024: NÃO DISPONÍVEL')
        
except ImportError as e:
    print('❌ Falha ao importar OQS:', e)
    exit(1)
except Exception as e:
    print('⚠️  Erro na verificação:', e)
"

echo ""
echo "🔍 Testando funcionalidade básica OQS..."
python3 -c "
import oqs

def test_kyber_basic():
    '''Teste básico do Kyber'''
    try:
        with oqs.KeyEncapsulation('Kyber1024') as kem:
            # Gerar par de chaves
            public_key = kem.generate_keypair()
            secret_key = kem.export_secret_key()
            
            # Encapsular
            ciphertext, shared_secret_encap = kem.encap_secret(public_key)
            
            # Decapsular (com outra instância)
            with oqs.KeyEncapsulation('Kyber1024') as kem2:
                kem2.import_secret_key(secret_key)
                shared_secret_decap = kem2.decap_secret(ciphertext)
            
            # Verificar se os segredos combinam
            if shared_secret_encap == shared_secret_decap:
                print('✅ Kyber1024: Funcionando corretamente!')
                print(f'   - Tamanho chave pública: {len(public_key)} bytes')
                print(f'   - Tamanho segredo compartilhado: {len(shared_secret_encap)} bytes')
                return True
            else:
                print('❌ Kyber1024: Segredos não combinam!')
                return False
                
    except Exception as e:
        print(f'❌ Kyber1024: Erro no teste - {e}')
        return False

# Executar teste
success = test_kyber_basic()
if not success:
    exit(1)
"

echo ""
echo "======================================"
if [ $? -eq 0 ]; then
    echo "🎉 OQS INSTALADO E VALIDADO COM SUCESSO!"
    echo "🚀 Pronto para a Fase 2: Implementação Kyber1024 + ECC P-521"
else
    echo "❌ FALHA NA INSTALAÇÃO/VERIFICAÇÃO OQS"
    exit 1
fi
