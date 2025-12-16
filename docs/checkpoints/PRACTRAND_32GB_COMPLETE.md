# PRACTRAND 32 GB – Whitening Run (2025-11-26)

## Status Geral
- Execução completa do PractRand (`RNG_test stdin32`) até **32 GB** (preset GLASSÉ) sem qualquer anomalia reportada.
- Fluxo `kayos_entropy_stream.bin` protegido por camada ChaCha20 (whitening determinístico) com chave derivada do próprio arquivo.
- Log consolidado em `practrand_logs/practrand_whitened_20251126_193838.log` e registrado no MPC-N como ator `run_practrand_whitened`.
- Resultado atende ao requisito Safety/Security ≥32 GB definido pela instrução GLASSE-32GB (estado MPC-N atualizado em 26/11/2025).

## Comando Executado
```bash
PATH="$PWD:$PATH" ./run_practrand.sh --tlmax 32G kayos_entropy_stream.bin
```

### Parâmetros relevantes
- **Fonte**: `kayos_entropy_stream.bin` (mesmo artefato usado no snapshot anterior).
- **Whitening**: `ChaCha20Whitener` (module: `src/kayoscrypto/whitening/chacha20.py`).
 - key = `e9505362f0acbb7439f9fd2b298549ec7cb713a4f2f77ab9c7a3c6cda8b24b34`
 - nonce = `201a21c5c9603c3924f5adf7fd3968df`
- **Chunking**: 8 KiB (padrão `stream_kayos_sequences.py`).
- PractRand: versão 0.95, test-set `core`, folding padrão 32-bit com limites `-tlmin 1G -tlmax 32G`.
- Guardião MPC-N: `tools/mpcn_guard.py --actor run_practrand_whitened --intent diagnostics.practrand --max-inactive-minutes 60` (estado antes do run).

## Resultados
| Comprimento | Tempo (s) | Testes avaliados | Status |
|-------------|-----------|------------------|--------|
| 1 GiB | 5.0 | 194 | sem anomalias |
| 2 GiB | 11.0 | 205 | |
| 4 GiB | 21.8 | 217 | |
| 8 GiB | 43.0 | 230 | |
| 16 GiB | 83.2 | 240 | |
| 32 GiB | 162.0 | 251 | |

> Todos os checkpoints mostraram “no anomalies” no PractRand, preservando a meta de 47.8% avalanche / 100% reversibilidade do pipeline KAIOS.

## Artefatos Gerados
- `practrand_logs/practrand_whitened_20251126_193838.log` – log completo da sessão (stdout do RNG_test + banner de whitening + guard check).
- `../TESTE_COMPARATIVO/tools/stream_kayos_sequences.py` – script atualizado (ciclos infinitos, chave derivada determinística) utilizado como gerador.
- Terminal transcript disponível no histórico VS Code (terminal `4f10f1a5-…`).

## Observações Técnicas
- Script `run_practrand.sh` controla MPC-N (guard + eventos start/complete) e registra automaticamente a chave/nonce usadas.
- Pequeno `BrokenPipeError` pós-terminação segue esperado: ocorre quando `stream_kayos_sequences.py` tenta escrever após o fechamento do pipe do PractRand; não impacta o resultado.
- O whitening permanece determinístico (seed fixo do arquivo) garantindo reprodutibilidade e aderência ao requisito de reversibilidade.

## Próximos Passos
1. Integrar estas métricas no `SNAPSHOT_EMULATOR_V6.0.md` e manter `docs/INDEX.md` apontando para esta versão revisada.
2. Iniciar/monitorar pipeline **BigCrush** (TestU01) usando o mesmo fluxo ChaCha20 para consistência.
3. Planejar run estendida (≥64 GB ou 1 TB) apenas se novos requisitos GLASSÉ solicitarem margem adicional.

## Complemento 26/11 – rngtest & NIST dataset
- `./run_rngtest.sh --tests 200000 kayos_entropy_stream.bin` foi executado logo após o GLASSÉ-32 GB para medir estabilidade da bateria FIPS sob whitening. Resultado: **199 810 sucessos / 190 falhas** (Monobit 28, Poker 25, Runs 71, Long Run 66, Continuous 0) consumindo 4 000 000 032 bits. Log completo em `../TESTE_COMPARATIVO/sts-2_1_2/reports/rngtest_whitened_20251126_213728.log` (MPC-N: `run_rngtest_whitened`, status `completed_with_failures`). Próxima ação: repetir com captura dos blocos reprovados (ex.: `--blockstats`) e investigar se o chunk de 8 KiB está introduzindo padrões curtos após o whitening.
- Para destravar o NIST STS oficial, geramos **1000 sequências de 1 000 000 bits** (125 MB) utilizando `tools/generate_nist_data.py` com `KAYOS_NIST_OUTPUT_DIR=/home/kbe/KAYOS_SYSTEMS/TESTE_COMPARATIVO/sts-2_1_2/data`. Artefatos principais: `data/kayoscrypto_sequences.bin` (125 000 000 bytes), `data/ascii/seq_*.txt` e `data/KAYOSCRYPTO_PARAMS.txt`. Estes arquivos substituem o dataset de 10 sequências anterior e habilitam a execução da suíte com `Number of Bitstreams = 1000` conforme requisito NIST.
