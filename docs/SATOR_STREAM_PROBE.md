# SATOR Stream Probe

Resumo das ferramentas e comandos usados para gerar e avaliar fluxos a partir do artefato SATOR 6D.

- `scripts/run_sator_stream_probe.py`: gera um stream bruto concatenando `bits_hex` das 15 projeções e grava `artifacts/sator_6d_master/sator_stream.bin`; executa `ent` e `RNG_test` e registra eventos MPC-N.
- `scripts/sator_postprocess_whiten.py`: deriva um fluxo pós-processado (HKDF-SHA256 expand) usando o `SATOR_GENESIS_HASH`/contexto (quando disponível) e grava `sator_stream_whitened.bin`; executa `ent` e `RNG_test` e registra eventos MPC-N.
- `scripts/sator_attach_artifacts.py`: computa SHA256 dos artefatos e registra `diagnostics.sator_probe:attach_artifacts` no MPC-N.

Recomendações:
- Para avaliações que demandam propriedades estatísticas reais, use o stream pós-processado (`sator_stream_whitened.bin`) ou aplique o whitening ChaCha20 padrão (`stream_kayos_sequences.py -w`) antes das suites.
- Arquivos importantes: `artifacts/sator_6d_master/*` (logs, binários, summary.json).
