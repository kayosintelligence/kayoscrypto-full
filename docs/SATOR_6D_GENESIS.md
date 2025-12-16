# SATOR 6D Genesis — Registro e Verificação

Resumo curto
- Hipercubo SATOR 6D validado: todas as 15 projeções 2D podem ser o quadrado SATOR com UMA orientação global (t=7).
- Artefato mestre: `artifacts/sator_6d_master/hypercube_complete.json`
- Análise de entropia: `artifacts/sator_6d_master/entropy_analysis.json` (Shannon = 3.875 bits/byte)
- Hash do artefato: `58f21e174a20717ea7f7d3f8ad0c90cea032c85c5e9c5bcb3203610807777ce4`

Arquivos gerados
- `artifacts/sator_6d_master/hypercube_complete.json` — dump completo das 15 projeções (letras + bits hex)
- `artifacts/sator_6d_master/entropy_analysis.json` — estatísticas e hash

Como verificar localmente
1. Ative o ambiente Python do projeto:
```
source .venv/bin/activate
```
2. Gere (ou regenere) o artefato mestre:
```
PYTHONPATH=. .venv/bin/python scripts/hyper_sator_complete_dump.py
```
3. Rode a análise estatística:
```
PYTHONPATH=. .venv/bin/python scripts/hyper_sator_entropy_analysis.py
```
4. Verifique o hash SHA256:
```
sha256sum artifacts/sator_6d_master/hypercube_complete.json
# deve corresponder ao registrado: 58f21e174a20717e...
```

Registro no MPC-N
- O evento foi registrado via `scripts/sator_mpcn_registry.py`. Para reemitir:
```
PYTHONPATH=. .venv/bin/python scripts/sator_mpcn_registry.py
```

Uso como salt de personalização (integração)
- O módulo `src/kayoscrypto/core/geometry.py` contém a constante `SATOR_GENESIS_HASH` e `get_geometric_salt()`.
- O motor que combina segredos foi atualizado para usar essa constante como `salt`/`info` no HKDF (ver `src/enterprise3d/.../real_oqs_engine_fixed.py`).

Notas de segurança e auditoria
- O SATOR 6D é uma estrutura determinística (entropia estrutural ~3.875 bits/byte). NÃO o trate como fonte de aleatoriedade.
- Use a saída convertida (bits) como ingrediente de derivação (HKDF) junto com uma fonte de entropia verdadeira (ex.: `os.urandom`) para gerar chaves de produção.
- Mantenha o artefato mestre versionado e registado no ledger MPC-N para auditoria e não republique a chave derivada de produção em texto.

Contato
- Para ampliar a integração (PR, testes, documentação formal), abra uma issue ou me peça para criar o PR com os patches.
