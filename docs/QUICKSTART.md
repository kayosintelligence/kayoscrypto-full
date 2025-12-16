# KAYOSCRYPTO - QUICKSTART COMPLETO

**Versão**: v5.0.1 ULTIMATE 
**Tempo**: 10-15 minutos 
**Objetivo**: Do zero ao uso produtivo

---

## PRÉ-REQUISITOS

```bash
# Verificar Python
python3 --version # Mínimo: 3.8+

# Verificar NumPy
python3 -c "import numpy; print(numpy.__version__)"

# Se não tiver NumPy:
pip3 install numpy
```

---

## TESTE RÁPIDO (2 MINUTOS)

### Passo 1: Entrar no diretório

```bash
cd /home/kbe/KAYOS_SYSTEMS/KayosCrypto
```

### Passo 2: Rodar teste automático

```bash
python3 kayoscrypto_evolved_final.py
```

**Saída esperada:**

```
 KAYOSCRYPTO ULTIMATE - SUITE DE TESTES
==================================================

 Teste 1/5: Compatibilidade de Versões - PASSOU
 Teste 2/5: Reversibilidade - PASSOU 
 Teste 3/5: Avalanche Effect - PASSOU (47.80%)
 Teste 4/5: Performance - PASSOU (494 KB/s)
 Teste 5/5: Consistência - PASSOU

==================================================
 SISTEMA ULTIMATE APROVADO!
==================================================
```

** Se viu isso, está FUNCIONANDO!**

---

## USO BÁSICO (5 MINUTOS)

### Exemplo 1: Encriptar/Decriptar Texto

Crie `teste_basico.py`:

```python
from kayoscrypto_evolved_final import KayosCryptoUltimate

# 1. Criar instância
cipher = KayosCryptoUltimate(password="minha_senha_secreta")

# 2. Encriptar
mensagem = b"Este eh um teste de criptografia"
print(f"Original: {mensagem}")

encrypted = cipher.encrypt(mensagem)
print(f"Encrypted (hex): {encrypted.hex()[:50]}...")

# 3. Decriptar
decrypted = cipher.decrypt(encrypted)
print(f"Decrypted: {decrypted}")

# 4. Validar
assert mensagem == decrypted
print("\n SUCESSO: Reversibilidade perfeita!")
```

**Rodar:**

```bash
python3 teste_basico.py
```

**Saída esperada:**

```
Original: b'Este eh um teste de criptografia'
Encrypted (hex): 7a3f9c2e8b1d4f6a9e2c7b5d3f8a1c4e6b9d2f7a3c...
Decrypted: b'Este eh um teste de criptografia'

 SUCESSO: Reversibilidade perfeita!
```

---

### Exemplo 2: Encriptar Arquivo

Crie `teste_arquivo.py`:

```python
from kayoscrypto_evolved_final import KayosCryptoUltimate
import os

# Criar arquivo de teste
with open('documento.txt', 'w') as f:
 f.write('Dados confidenciais da empresa\n')
 f.write('Projeto secreto X\n')
 f.write('Budget: $1,000,000\n')

print(" Arquivo criado: documento.txt")

# Encriptar
cipher = KayosCryptoUltimate(password="senha_empresa_2025")

with open('documento.txt', 'rb') as f:
 data = f.read()

encrypted = cipher.encrypt(data)

with open('documento.txt.kayos', 'wb') as f:
 f.write(encrypted)

print(f" Arquivo encriptado: documento.txt.kayos ({len(encrypted)} bytes)")

# Decriptar (para validar)
with open('documento.txt.kayos', 'rb') as f:
 encrypted_read = f.read()

decrypted = cipher.decrypt(encrypted_read)

with open('documento_decrypted.txt', 'wb') as f:
 f.write(decrypted)

print(" Arquivo decriptado: documento_decrypted.txt")

# Comparar
with open('documento.txt', 'rb') as f1:
 original = f1.read()
with open('documento_decrypted.txt', 'rb') as f2:
 restored = f2.read()

if original == restored:
 print(" SUCESSO: Arquivos idênticos!")
else:
 print(" ERRO: Arquivos diferentes!")

# Cleanup
os.remove('documento_decrypted.txt')
```

**Rodar:**

```bash
python3 teste_arquivo.py
```

**Saída esperada:**

```
 Arquivo criado: documento.txt
 Arquivo encriptado: documento.txt.kayos (XXX bytes)
 Arquivo decriptado: documento_decrypted.txt
 SUCESSO: Arquivos idênticos!
```

---

### Exemplo 3: Múltiplas Senhas (Importante!)

```python
from kayoscrypto_evolved_final import KayosCryptoUltimate

data = b"Mensagem secreta"

# Senha 1
cipher1 = KayosCryptoUltimate(password="senha1")
encrypted1 = cipher1.encrypt(data)

# Senha 2 (DIFERENTE)
cipher2 = KayosCryptoUltimate(password="senha2")
encrypted2 = cipher2.encrypt(data)

# Comparar resultados
print(f"Encrypted com senha1: {encrypted1.hex()[:30]}...")
print(f"Encrypted com senha2: {encrypted2.hex()[:30]}...")

if encrypted1 != encrypted2:
 print("\n CORRETO: Senhas diferentes = resultados diferentes")
else:
 print("\n ERRO: Resultados iguais (problema!)")

# Tentar decriptar com senha errada
try:
 wrong_cipher = KayosCryptoUltimate(password="senha_errada")
 wrong_decrypt = wrong_cipher.decrypt(encrypted1)
 
 if wrong_decrypt != data:
 print(" CORRETO: Senha errada = resultado incorreto")
 else:
 print(" ERRO: Senha errada funcionou (problema!)")
except Exception as e:
 print(f" CORRETO: Senha errada causou erro: {e}")
```

---

## USO AVANÇADO (10 MINUTOS)

### Exemplo 4: Ativar/Desativar Camadas

```python
from kayoscrypto_evolved_final import KayosCryptoUltimate

data = b"Teste de configuracao"

# Configuração 1: TUDO LIGADO (padrão)
cipher_full = KayosCryptoUltimate(
 password="senha",
 use_concentric=True, # Ezequiel Wheels
 use_direction=True # Fibonacci Direction
)
enc_full = cipher_full.encrypt(data)
print(f"Full (tudo ligado): {len(enc_full)} bytes")

# Configuração 2: SÓ CONCENTRIC
cipher_conc = KayosCryptoUltimate(
 password="senha",
 use_concentric=True,
 use_direction=False
)
enc_conc = cipher_conc.encrypt(data)
print(f"Concentric only: {len(enc_conc)} bytes")

# Configuração 3: SÓ DIRECTION
cipher_dir = KayosCryptoUltimate(
 password="senha",
 use_concentric=False,
 use_direction=True
)
enc_dir = cipher_dir.encrypt(data)
print(f"Direction only: {len(enc_dir)} bytes")

# Configuração 4: SÓ BASE (Feistel + Geometric)
cipher_base = KayosCryptoUltimate(
 password="senha",
 use_concentric=False,
 use_direction=False
)
enc_base = cipher_base.encrypt(data)
print(f"Base only: {len(enc_base)} bytes")

print("\n Use configurações diferentes para casos específicos:")
print(" - Full: Máxima segurança")
print(" - Concentric: Foco em filosofia Ezequiel")
print(" - Direction: Foco em Fibonacci")
print(" - Base: Performance máxima")
```

### Exemplo 5: Quantum Enhanced com Metadata Persistida

```python
from pathlib import Path
from kayoscrypto_ultimate import KayosCryptoUltimate
import json

mensagem = b"Relatorio confidencial v6.0"

# Instanciar com suporte quântico (modo enhanced)
cipher = KayosCryptoUltimate(use_quantum=True, quantum_entropy_mode="enhanced")

# Criptografar: retorna pacote com ciphertext + quantum_salt
quantum_result = cipher.encrypt(mensagem, password="SenhaUltraSegura!", level=3)

# Empacotar para armazenamento em disco ou transporte (JSON amigável)
payload, metadata = cipher.prepare_encryption_package(quantum_result)

Path("relatorio.quantum.bin").write_bytes(payload)
Path("relatorio.quantum.meta.json").write_text(json.dumps(metadata, indent=2))

print("Ciphertext armazenado em:", Path("relatorio.quantum.bin").resolve())
print("Metadata gerada:")
print(json.dumps(metadata, indent=2))

# Reconstruir pacote antes da descriptografia (consome quantum_salt automaticamente)
stored_payload = Path("relatorio.quantum.bin").read_bytes()
stored_metadata = json.loads(Path("relatorio.quantum.meta.json").read_text())

reconstructed = cipher.reconstruct_ciphertext(stored_payload, stored_metadata)

decrypted = cipher.decrypt(reconstructed, password="SenhaUltraSegura!", level=3)

assert decrypted == mensagem
print(" Quantum enhanced reversível com metadata persistida!")
```

**Metadata gerada (exemplo real):**

```json
{
 "quantum_salt": "71f5c7c2c8b5497f9e59bc9c9a1f63de"
}
```

---

### Exemplo 6: Benchmark Personalizado

```python
from kayoscrypto_evolved_final import KayosCryptoUltimate
import time

# Tamanhos para testar
sizes = [1_000, 10_000, 100_000, 1_000_000] # 1KB, 10KB, 100KB, 1MB

cipher = KayosCryptoUltimate(password="benchmark")

print(" BENCHMARK PERSONALIZADO")
print("=" * 50)

for size in sizes:
 # Criar dados aleatórios
 import os
 data = os.urandom(size)
 
 # Encriptar
 start = time.time()
 encrypted = cipher.encrypt(data)
 enc_time = time.time() - start
 
 # Decriptar
 start = time.time()
 decrypted = cipher.decrypt(encrypted)
 dec_time = time.time() - start
 
 # Calcular velocidades
 enc_speed = size / enc_time / 1024 # KB/s
 dec_speed = size / dec_time / 1024 # KB/s
 
 print(f"\n{size:>10} bytes:")
 print(f" Encrypt: {enc_speed:>8.2f} KB/s ({enc_time:.4f}s)")
 print(f" Decrypt: {dec_speed:>8.2f} KB/s ({dec_time:.4f}s)")
 print(f" Overhead: {len(encrypted) - size:>5} bytes")
 
 # Validar
 assert data == decrypted, "Reversibilidade falhou!"

print("\n Todos os benchmarks validados!")
```

---

## USO VIA CLI (5 MINUTOS)

### Encriptar arquivo

```bash
python3 kayoscrypto_cli.py encrypt meu_arquivo.txt
# Resultado: meu_arquivo.txt.kayos
```

### Decriptar arquivo

```bash
python3 kayoscrypto_cli.py decrypt meu_arquivo.txt.kayos
# Resultado: meu_arquivo.txt
```

### Benchmark rápido

```bash
python3 kayoscrypto_cli.py benchmark
```

### Help completo

```bash
python3 kayoscrypto_cli.py --help
```

---

## BOAS PRÁTICAS

### FAÇA

```python
# 1. Use senhas fortes
cipher = KayosCryptoUltimate(password="S3nh@F0rt3!2025")

# 2. Valide sempre após decriptar
decrypted = cipher.decrypt(encrypted)
assert decrypted == original_data

# 3. Use a mesma configuração para enc/dec
cipher_enc = KayosCryptoUltimate(password="x", use_concentric=True)
encrypted = cipher_enc.encrypt(data)

cipher_dec = KayosCryptoUltimate(password="x", use_concentric=True)
decrypted = cipher_dec.decrypt(encrypted) # Funciona

# 4. Trate exceções
try:
 decrypted = cipher.decrypt(possibly_corrupted_data)
except Exception as e:
 print(f"Erro ao decriptar: {e}")
```

### NÃO FAÇA

```python
# 1. Senhas fracas
cipher = KayosCryptoUltimate(password="123") # 

# 2. Configurações diferentes entre enc/dec
cipher_enc = KayosCryptoUltimate(password="x", use_concentric=True)
encrypted = cipher_enc.encrypt(data)

cipher_dec = KayosCryptoUltimate(password="x", use_concentric=False)
decrypted = cipher_dec.decrypt(encrypted) # Resultado errado!

# 3. Ignorar validação
decrypted = cipher.decrypt(encrypted)
# ... usar decrypted sem verificar # 

# 4. Hardcoded passwords em código público
PASSWORD = "minha_senha_123" # NUNCA!
```

---

## TROUBLESHOOTING

### Problema 1: "ModuleNotFoundError: No module named 'numpy'"

**Solução:**

```bash
pip3 install numpy
```

### Problema 2: Decryption retorna lixo

**Causas possíveis:**

1. **Senha diferente**: Use exatamente a mesma senha
2. **Configuração diferente**: `use_concentric` e `use_direction` devem ser iguais
3. **Dados corrompidos**: Verifique se o arquivo encrypted está intacto

**Debug:**

```python
# Teste simples
cipher = KayosCryptoUltimate(password="teste")
data = b"test"
enc = cipher.encrypt(data)
dec = cipher.decrypt(enc)

if data == dec:
 print(" Sistema funcionando")
else:
 print(" Problema no sistema")
 print(f"Original: {data}")
 print(f"Decrypted: {dec}")
```

### Problema 3: Performance muito lenta

**Soluções:**

```python
# 1. Desabilitar camadas extras
cipher = KayosCryptoUltimate(
 password="x",
 use_concentric=False, # +20% velocidade
 use_direction=False # +20% velocidade
)

# 2. Processar em chunks (arquivos grandes)
CHUNK_SIZE = 64 * 1024 # 64KB
with open('grande.bin', 'rb') as f:
 while chunk := f.read(CHUNK_SIZE):
 encrypted_chunk = cipher.encrypt(chunk)
 # ... processar chunk

# 3. Considerar implementação Rust (futuro)
# Ver: ROADMAP_ALTO_RISCO.md
```

---

## PRÓXIMOS PASSOS

### Nível 1: Básico (você já sabe!)

```
 Encriptar/decriptar texto
 Encriptar/decriptar arquivos
 Usar CLI básico
```

### Nível 2: Intermediário

```
⏰ Integrar com sua aplicação
⏰ Criar wrapper personalizado
⏰ Adicionar logging
⏰ Implementar key management
```

### Nível 3: Avançado

```
⏰ Contribuir para o projeto
⏰ Rodar testes completos
⏰ Benchmarks personalizados
⏰ Otimizações específicas
```

### Nível 4: Expert

```
⏰ Análise de segurança
⏰ Implementar novas camadas
⏰ Versão Cython/Rust
⏰ Certificação
```

---

## DOCUMENTAÇÃO ADICIONAL

| Documento | Objetivo | Tempo |
|-----------|----------|-------|
| [README.md](README.md) | Overview do projeto | 5 min |
| [INDICE_MASTER.md](INDICE_MASTER.md) | Navegação completa | 10 min |
| [STATUS_FINAL_CONSOLIDADO.md](STATUS_FINAL_CONSOLIDADO.md) | Status e decisões | 15 min |
| [RELATORIO_ULTIMATE_FINAL.md](RELATORIO_ULTIMATE_FINAL.md) | Detalhes técnicos | 1h |
| [PLANO_SEM_INVESTIMENTO.md](PLANO_SEM_INVESTIMENTO.md) | Como começar grátis | 20 min |

---

## CHECKLIST DE VALIDAÇÃO

Antes de usar em produção, valide:

```
[ ] Teste básico passou (kayoscrypto_evolved_final.py)
[ ] Encriptou e decriptou texto corretamente
[ ] Encriptou e decriptou arquivo corretamente
[ ] Senhas diferentes = resultados diferentes
[ ] Mesma senha = resultado consistente
[ ] Performance aceitável (>100 KB/s)
[ ] Leu documentação de boas práticas
[ ] Entendeu casos de uso aprovados
```

**Se todos → PRONTO PARA USAR!** 

---

## 🆘 SUPORTE

- **Bugs**: Ver issues no GitHub
- **Dúvidas**: Ver [INDICE_MASTER.md](INDICE_MASTER.md)
- **Contribuir**: Ver [CONTRIBUTING.md](CONTRIBUTING.md)
- **Documentação**: Ver documentos listados acima

---

** PARABÉNS! Você está pronto para usar KayosCrypto!**

**Próxima ação sugerida:** 
Crie seu primeiro script de produção usando os exemplos acima como base!

---

**Versão**: 1.0 
**Data**: 13 de Outubro de 2025 
**Autor**: KAYOS Systems
