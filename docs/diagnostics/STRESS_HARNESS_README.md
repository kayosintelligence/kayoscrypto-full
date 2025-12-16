# Stress Harness README

Este README descreve como usar o harness de stress adicionado em `scripts/harness/`.

1) Smoke test (rápido, recomendado antes de rodar long jobs):

```bash
cd /home/kbe/KAYOS_SYSTEMS/KayosCrypto
./scripts/harness/run_full_stress_harness.sh
```

2) Full mode (apenas quando operador aprovar recursos):

```bash
./scripts/harness/run_full_stress_harness.sh --full --outdir /var/tmp/kayos_stress_$(date -u +%Y%m%dT%H%M%SZ)
```

Observações:
- O script faz um "smoke" de PractRand 1G por padrão; `--full` habilita exemplos de long runs (PractRand 1.5T). Esses comandos são intencionados como exemplos — para campanhas reais, use os wrappers existentes `scripts/diagnostics/*` que já integram o guard MPC-N.
- Antes de rodar campanhas longas, execute `scripts/harness/anchor_artifact.py` para registar artefatos críticos (tarballs, logs) no ledger MPC-N.

Anchoring example:

```bash
tar czf artifacts/stress_bundle_${TS}.tar.gz practrand_logs/ logs/ reports/
python3 scripts/harness/anchor_artifact.py artifacts/stress_bundle_${TS}.tar.gz
```

Key-sensitivity (local quick run):

```bash
python3 scripts/harness/key_sensitivity.py --outdir artifacts/ks_$(date -u +%Y%m%dT%H%M%SZ) --samples 256
```

Segurança operacional:
- Garanta `set -euo pipefail` e `trap` em wrappers long-running (os scripts em `scripts/diagnostics/` já fazem isso).
- Verifique espaço em disco, política de logs e limites de ulimit antes de executar campanhas longas.

Notas finais:
- Este harness é um ponto de partida — mantenha o uso das ferramentas guardadas (`tools/mpcn_guard.py`) e das wrappers já existentes para garantir ancoragem e rastreabilidade completa.
