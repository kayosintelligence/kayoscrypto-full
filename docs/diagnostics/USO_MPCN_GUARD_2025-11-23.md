# USO: MPC-N Guard e Pipeline de Diagnósticos — 23/11/2025

Este documento descreve, passo a passo, como usar o guardião MPC‑N, os wrappers das suítes de teste (PractRand, Dieharder, TestU01, ENT, rngtest), como gerar e assinar snapshots do ledger, inserir heartbeats automáticos/one‑shot, verificar integridade e arquivar de forma imutável. Não omite etapas operacionais importantes; leia e siga em sequência.

**Aviso**: os comandos abaixo presumem o ambiente do repositório raiz (`/home/kbe/KAYOS_SYSTEMS/KayosCrypto`), Python virtualenv em `.venv`, e `PYTHONPATH=src` quando invocamos módulos internos.

**Pré-requisitos**
- Sistema: Linux (bash).
- Python 3.8+ e virtualenv com dependências do projeto instaladas (`.venv`).
- Ferramentas externas: `gpg` (opcional), `openssl` (opcional), `awscli` (opcional para S3), `sha256sum`, `jq`.
- Permissões: acesso de escrita ao repositório para aplicar patches; acesso à chave privada (GPG/PEM) caso vá assinar; credenciais AWS com permissão para criar buckets com Object Lock se for arquivar em S3 WORM.

**Arquivos e localizações importantes**
- Ledger atual: `mpcn_state.json` (raiz do repositório).
- Script verificador: `scripts/verify_mpcn_ledger.py`.
- Gerador de snapshot encadeado: `scripts/prepare_system_state_export.py` (gera `/tmp/system_state_signed.json`).
- Wrappers das suítes: `scripts/diagnostics/run_*` e `run_practrand.sh`, `run_bigcrush_whitened.sh`, `run_dieharder_whitened.sh`, `run_practrand_raw_stream`, etc.
- Helper heartbeat: `tools/one_shot_heartbeat.sh` (sugerido/instalável).
- Logs e reports: `practrand_logs/`, `logs/`, `../TESTE_COMPARATIVO/sts-2_1_2/reports/`.
- Artefatos de distribuição / assinatura: `artifacts/`.

**Objetivos deste guia**
- Executar e controlar as suítes de teste com o guardião MPC‑N.
- Garantir que eventos (start/complete/failed/heartbeat) sejam persistidos no ledger.
- Gerar snapshot encadeado pronto para assinatura e arquivamento imutável.
- Verificar localmente a integridade do snapshot e da cadeia.
- Automatizar/Inserir heartbeats one‑shot nos wrappers.
- Criar testes unitários básicos para o verificador de ledger.

----------------------------------------------------------------------------- 

**1. Como executar uma suíte controlada pelo guardião (exemplo genérico)**

Passos gerais (wrapper padrão com guard + traps):

1. Abra shell no diretório do repositório:

```bash
cd /home/kbe/KAYOS_SYSTEMS/KayosCrypto
source .venv/bin/activate
export PYTHONPATH=src
```

2. Executar o wrapper (exemplo: BigCrush whitened):

```bash
scripts/diagnostics/run_bigcrush_whitened.sh kayos_entropy_stream.bin
```

O wrapper já deve:
- chamar `tools/mpcn_guard.py --actor <actor> --intent diagnostics.<suite>`;
- publicar `diagnostics.<suite>:start` antes de iniciar a suíte;
- aplicar `set -euo pipefail` e `trap 'mpcn_fail_trap $?' ERR` para garantir persistência de falhas;
- publicar `diagnostics.<suite>:complete` ao término com `status=completed` (ou `failed` em caso de erro);
- registrar `path` do log, parâmetros (chunk size, whiten on/off, tlmax, extra args) e anotações úteis.

3. Verificação rápida do evento no ledger (local):

```bash
jq '.history[-1]' mpcn_state.json | sed -n '1,120p'
# ou buscar pelo actor
jq '.history[] | select(.actor=="run_bigcrush_whitened")' mpcn_state.json | tail -n +1
```

----------------------------------------------------------------------------- 

**2. Heartbeat: quando e como usar**

Objetivo: sinalizar atividade contínua quando o guard detecta inatividade além do limiar configurado (tipicamente 60 min). Pode ser manual (one‑shot) ou automatizado.

- Comando one-shot (manual, via Python):

```bash
PYTHONPATH=src .venv/bin/python -c "from kayoscrypto.mpcn.context import log_event; log_event(actor='bigcrush_run', action='heartbeat', details={'intent':'diagnostics.bigcrush'})"
```

- Helper shell one-shot (recomendado para inserir nos wrappers):

Crie `tools/one_shot_heartbeat.sh` (exemplo):

```bash
#!/usr/bin/env bash
set -euo pipefail
actor="$1"
intent="$2"
PYTHONPATH=src .venv/bin/python - <<PY
from kayoscrypto.mpcn.context import log_event
log_event(actor='$actor', action='heartbeat', details={'intent':'$intent'})
PY

# Uso: tools/one_shot_heartbeat.sh run_bigcrush_whitened diagnostics.bigcrush
```

Permissões:

```bash
chmod +x tools/one_shot_heartbeat.sh
```

Inserir uma chamada one‑shot junto à lógica do wrapper (após `trap` idealmente) evita que o guard considere o contexto obsoleto antes da reexecução.

Comandos para aplicar um patch leve (manual, revise os backups):

```bash
WRAPPER="scripts/diagnostics/run_bigcrush_whitened.sh"
cp "$WRAPPER" "${WRAPPER}.bak"
awk 'BEGIN{ins=0} /^trap / && ins==0 {print; print "tools/one_shot_heartbeat.sh run_bigcrush_whitened diagnostics.bigcrush"; ins=1; next} {print}' "$WRAPPER" > "${WRAPPER}.new" && mv "${WRAPPER}.new" "$WRAPPER" && chmod +x "$WRAPPER"
```

Repita para outros wrappers ou use o loop mostrado nas instruções de assinatura.

----------------------------------------------------------------------------- 

**3. Gerar snapshot encadeado pronto para assinatura**

Se o `mpcn_state.json` exportado não contém `integrity_hash`/`previous_hash` por registro, gere um snapshot encadeado localmente (não modifica o ledger original):

```bash
python3 scripts/prepare_system_state_export.py --input mpcn_state.json --output /tmp/system_state_signed.json
# Resultado: /tmp/system_state_signed.json (cada registro terá 'integrity_hash' e 'previous_hash')
```

Checar resumo:

```bash
jq '.history | length' /tmp/system_state_signed.json
jq '.history[0:3]' /tmp/system_state_signed.json
sha256sum /tmp/system_state_signed.json
```

----------------------------------------------------------------------------- 

**4. Verificar cadeia localmente (script de verificação)**

O verificador (`scripts/verify_mpcn_ledger.py`) suporta dois modos: modo informativo (heurísticas) e modo de verificação de cadeia completa.

Execução (modo cadeia):

```bash
python3 scripts/verify_mpcn_ledger.py --input /tmp/system_state_signed.json --mode verify-chain
```

Retorno:
- Código 0: cadeia íntegra.
- Código !=0: descreve inconsistências (registro(s) com hash inválido, mismatch `previous_hash`).

Se preferir uma checagem rápida (hash canônico por registro):

```bash
python3 - <<'PY'
import json,hashlib
def canonical_hash(obj):
    j = json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False)
    return hashlib.sha256(j.encode()).hexdigest()
data = json.load(open('/tmp/system_state_signed.json'))
for i,r in enumerate(data.get('history',[])):
    print(i, r.get('integrity_hash')[:16], canonical_hash({k:v for k,v in r.items() if k not in ('integrity_hash','previous_hash')})[:16])
PY
```

----------------------------------------------------------------------------- 

**5. Assinar o snapshot (detached signature)**

Opções: GPG (recomendado para auditoria), OpenSSL (PKCS#1) ou cosign (containers). Exemplo GPG:

```bash
# Assinar com GPG (ASCII-armored, detached)
gpg --output /tmp/system_state_signed.json.sig --detach-sign --armor /tmp/system_state_signed.json

# Verificar
gpg --verify /tmp/system_state_signed.json.sig /tmp/system_state_signed.json
```

Se usar OpenSSL (RSA PEM):

```bash
openssl dgst -sha256 -sign private.pem -out /tmp/system_state_signed.json.sig.bin /tmp/system_state_signed.json
base64 /tmp/system_state_signed.json.sig.bin > /tmp/system_state_signed.json.sig.b64
```

Sempre gere e publique (no `artifacts/`) a chave pública correspondente (veja seção 7 abaixo).

----------------------------------------------------------------------------- 

**6. Exportar chave pública do assinante para `artifacts/`**

GPG:

```bash
mkdir -p artifacts
gpg --armor --export YOUR_KEY_ID > artifacts/system_state_signing_pubkey.asc
sha256sum artifacts/system_state_signing_pubkey.asc > artifacts/system_state_signing_pubkey.asc.sha256
```

PEM (OpenSSL):

```bash
cp public.pem artifacts/system_state_signing_pubkey.pem
sha256sum artifacts/system_state_signing_pubkey.pem > artifacts/system_state_signing_pubkey.pem.sha256
```

Inclua `artifacts/*.sha256` no bundle de due diligence.

----------------------------------------------------------------------------- 

**7. Arquivar snapshot de forma imutável (S3 WORM example)**

Criar bucket S3 com Object Lock (apenas no momento da criação):

```bash
aws s3api create-bucket --bucket my-worm-bucket --region us-east-1 --create-bucket-configuration LocationConstraint=us-east-1 --object-lock-enabled-for-bucket
# Enviar arquivo com retenção GOVERNANCE até data desejada
aws s3api put-object --bucket my-worm-bucket --key exports/system_state_signed.json --body /tmp/system_state_signed.json --object-lock-mode GOVERNANCE --object-lock-retain-until-date 2026-11-27T00:00:00Z
aws s3 cp /tmp/system_state_signed.json.sig s3://my-worm-bucket/exports/system_state_signed.json.sig
```

Verifique retenção e metadados:

```bash
aws s3api get-object-retention --bucket my-worm-bucket --key exports/system_state_signed.json
```

Observação: a criação de bucket Object Lock normalmente exige configurações organizacionais; coordene com administração AWS.

----------------------------------------------------------------------------- 

**8. Registrar evento de export no MPC‑N**

Depois de subir o snapshot ao storage imutável, publique um evento no ledger descrevendo o local e o método de assinatura.

```bash
PYTHONPATH=src .venv/bin/python - <<'PY'
from kayoscrypto.mpcn.context import log_event
log_event(actor='diagnostics_exporter', action='export_signed', details={
    'path':'s3://my-worm-bucket/exports/system_state_signed.json',
    'sig_path':'s3://my-worm-bucket/exports/system_state_signed.json.sig',
    'method':'gpg-detached',
})
print('Evento de export registrado no MPC-N')
PY
```

Verifique no `mpcn_state.json` se o evento apareceu.

----------------------------------------------------------------------------- 

**9. Criar e executar unit tests básicos para o verificador**

Exemplo de arquivo de teste (pytest) mínimo para `scripts/verify_mpcn_ledger.py`:

```bash
mkdir -p tests
cat > tests/test_verify_mpcn_ledger.py <<'PY'
import json
from pathlib import Path
import subprocess

def make_chain(tmp_path, n=3):
    chain=[]
    prev='0'*64
    for i in range(n):
        rec={'seq':i,'data':'x'}
        # campo de hash fictício para o teste; o script real deverá calcular canonical hash
        rec['integrity_hash']=f'hash{i}'
        rec['previous_hash']=prev
        prev=rec['integrity_hash']
        chain.append(rec)
    p=tmp_path/'chain.json'
    p.write_text(json.dumps({'history':chain}))
    return str(p)

def test_verify_chain(tmp_path):
    p=make_chain(tmp_path)
    r=subprocess.run(['python3','scripts/verify_mpcn_ledger.py','--input',p,'--mode','verify-chain'], capture_output=True, text=True)
    assert r.returncode==0, r.stdout + r.stderr
PY

# Executar
pytest -q tests/test_verify_mpcn_ledger.py
```

Adapte o conteúdo do teste às opções reais do script.

----------------------------------------------------------------------------- 

**10. Aplicar heartbeat one-shot em lote para todos os wrappers (exemplo seguro)**

Faça backup antes de aplicar:

```bash
for f in scripts/diagnostics/run_*whitened*.sh scripts/diagnostics/run_practrand*.sh; do
  echo "Backup: $f -> ${f}.bak"
  cp "$f" "${f}.bak"
done

for f in scripts/diagnostics/run_*whitened*.sh scripts/diagnostics/run_practrand*.sh; do
  echo "Patching $f"
  awk -v actor="$(basename "$f" .sh)" 'BEGIN{ins=0} /^trap / && ins==0 {print; printf("tools/one_shot_heartbeat.sh %s diagnostics.%s\n", actor, actor); ins=1; next} {print}' "$f" > "${f}.new" && mv "${f}.new" "$f" && chmod +x "$f"
done

echo "Revise os .bak antes de executar os wrappers modificados."
```

----------------------------------------------------------------------------- 

**11. Troubleshooting e dicas operacionais**

- Se o guard reportar `contexto_obsoleto` com frequência: ajuste o intervalo de heartbeat (ou insira chamadas one‑shot nos wrappers long‑running).
- Se `verify-chain` falhar após assinatura: confirme que o `previous_hash` do primeiro registro é a string genesis esperada (`0..0`) ou que a cadeia usada para assinatura corresponde exatamente ao arquivo assinado (checar `sha256sum`).
- Ao usar `gpg --verify` e ocorrer erro de chave desconhecida, importe a chave pública colocada em `artifacts/`:

```bash
gpg --import artifacts/system_state_signing_pubkey.asc
gpg --verify /tmp/system_state_signed.json.sig /tmp/system_state_signed.json
```

- Para logs muito grandes, use `less +F` e pesquise por `unusual`, `failed`, `heartbeat`.

----------------------------------------------------------------------------- 

**12. Checklist pré-auditoria (passo-a-passo)**

1. Verifique que todos os wrappers publicaram eventos start/complete no `mpcn_state.json`.
2. Gere `/tmp/system_state_signed.json` via `scripts/prepare_system_state_export.py`.
3. Calcule `sha256sum` e guarde em `/tmp/system_state_signed.json.sha256`.
4. Assine o arquivo com GPG ou OpenSSL (detached signature).
5. Exporte a chave pública usada para `artifacts/` e registre `sha256` do pubkey.
6. Carregue os artefatos no S3 WORM ou storage imutável do provedor escolhido.
7. Publique evento `export_signed` no MPC‑N apontando para o local em WORM.
8. Execute `scripts/verify_mpcn_ledger.py --input /tmp/system_state_signed.json --mode verify-chain` localmente.

----------------------------------------------------------------------------- 

**13. FAQ rápida**

- P: Posso assinar o snapshot dentro da máquina CI com GPG sem intervenção humana?
  - R: Sim, desde que a chave seja gerida com segurança no CI (secret store/HSM). Prefira HSM/KMS para chaves de produção.

- P: O script `prepare_system_state_export.py` modifica o ledger original?
  - R: Não — cria uma cópia (`--output`) e adiciona campos `integrity_hash`/`previous_hash` apenas na cópia.

- P: O que fazer se encontrar hashes inválidos?
  - R: não sobrescreva nada. Documente os offsets/ranges falhos, capture os arquivos de log, e reporte para o time responsável. Revise se houve export parcial/concorrência de escrita no `mpcn_state.json`.

----------------------------------------------------------------------------- 

**14. Contato & referências**

- Autor desta documentação: equipe de auditoria interna / KayosCrypto.
- Scripts referenciados: `scripts/verify_mpcn_ledger.py`, `scripts/prepare_system_state_export.py`, `tools/mpcn_guard.py`, `tools/one_shot_heartbeat.sh` (exemplo).
- Relatórios principais:
  - `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md` (registro de execução e evidências)
  - `docs/PQC_VALIDATION_REPORT_2025-11-24.md` (PQC stack)

----------------------------------------------------------------------------- 

Se desejar, eu aplico os patches para inserir o `tools/one_shot_heartbeat.sh` e criar os testes `tests/test_verify_mpcn_ledger.py` automaticamente, e então executo os testes; diga se quer que eu faça isso agora. Caso prefira, posso também gerar exemplos de `systemd` user‑timer para heartbeat periódico.
