# Inventário de Testes — 2025-11-27

Este documento lista os artefatos principais das campanhas diagnósticas e o estado do ledger MPC-N encontrado.

- **mpcn_state.json**: `/home/kbe/KAYOS_SYSTEMS/KayosCrypto/mpcn_state.json` — presente; contém múltiplos eventos `heartbeat` e registros de runs PractRand/TestU01/Dieharder.
- **system_state.json**: não encontrado no workspace (arquivo referenciado na documentação, ausente localmente).

Arquivos de log e checksums (seleção representativa):

- `logs/bigcrush_whitened_20251123_053419.log` — sha256: `6e927fa454882e0731a3ba7375799737969e12f877daa40bac3bd199c018efa`
- `logs/dieharder_whitened_20251123_005753.log` — sha256: `c9bc8634421e31a0b2c0fd1db38e868c34f5833c2c4f780a3638f07c3826474b`
- `practrand_logs/practrand_whitened_20251124_011640.log` — sha256: `30d6343f9cb9ffaf2fc4dbd05b682a55ad38e27fb8a848c7f8e7dd8078100cce`
- `practrand_logs/practrand_whitened_20251123_152247.log` — sha256: `83bfd872552d3349e5df801a0685568ec517c191e36e4d46a73c7cb616edfbdd`
- `TESTE_COMPARATIVO/sts-2_1_2/reports/testu01_bigcrush.log` — sha256: `933a8ec4bae54a94ebdef20d96734c863494582c63bfee057f1876a8da933f4c`
- `TESTE_COMPARATIVO/sts-2_1_2/reports/ent_whitened_20251123_132304.log` — sha256: `7e9a4ab10c239c5dec7d2230181b7e3eb58e02e470771c519716934aedebc427`
- `TESTE_COMPARATIVO/sts-2_1_2/reports/rngtest_whitened_20251123_150555.log` — sha256: `bef532fd0f15f425d44018a1bcaf78f03c8b284eb7abc1b8cf98921f9fb24ce5`
- `logs/nist_output_full_1000streams_latest.log` — sha256: `c09dcd79b08e80090308d877abb640547b810c73797b7e9392f7ea56d9bf5097`

Observações:

- O `mpcn_state.json` contém eventos `heartbeat` usados manual e programaticamente. O script `scripts/verify_mpcn_ledger.py` pode ser usado para validar a integridade da cadeia de eventos.
- A ausência de `system_state.json` prejudica a validação completa do estado do guardião conforme descrito em `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md` e em `docs/diagnostics/PRE_AUDIT_FIPS_ISO_EXPECTATIVA_2025-11-26.md`.
- Recomenda-se centralizar cópia exportada de `system_state.json` na pasta `docs/diagnostics/exports/` para auditoria (apenas sugestão; não criar ou mover sem autorização).

Next steps (sugestões):

- Rodar `python3 scripts/verify_mpcn_ledger.py /home/kbe/KAYOS_SYSTEMS/KayosCrypto/mpcn_state.json` para checar integridade agora.
- Buscar possíveis backups/exportações externas que contenham `system_state.json` (ex.: drives USB, backups S3, pastas `archive/`, `exports/`).
- Automatizar heartbeats para runs > 60 minutos usando `tools/auto_heartbeat.py` (ex.: systemd timer ou cronjob).
