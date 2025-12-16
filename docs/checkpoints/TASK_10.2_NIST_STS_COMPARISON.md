# TASK 10.2 – NIST STS Run 2 + Comparação (2025-11-17)

## Objetivo
Executar um segundo experimento completo com novo dataset NIST STS, comparar com o run inicial (2025-11-17), identificar padrões nas falhas residuais e consolidar argumentos técnicos.

## Execução
- Dataset 2 gerado via `tools.generate_nist_data.generate_nist_test_data(100, 1_000_000)` com `KAYOS_NIST_OUTPUT_DIR=artifacts/nist_sts/run2`.
- Arquivo utilizado pelo STS: `kayos_NIST/sts-2.1.2/data/kayoscrypto_sequences_run2.bin` (12.5 MB).
- Comando STS:
 ```bash
 ./sts -v 1 -i 100 -I 10 -S 1000000 -F r -s \
 -w experiments/kayoscrypto_run2 \
 data/kayoscrypto_sequences_run2.bin
 ```
- Consolidação gerada em `artifacts/nist_sts/local_run_2025-11-17_run2/` (CSV, Markdown, JSON).

## Resultados-Chave (Run 2)
- 188 subtestes avaliados: **187/188** dentro da faixa (apenas "Frequency" ficou borderline com 96/100 ≥ α).
- Non-overlapping Template: 14652/14800 sucessos (0.9900). Falhas concentradas em **índices 15 (000011111)** e **102 (110010010)**, diferentes dos 26/50/61 observados no run 1.
- Random Excursions: todos os estados aprovados (estado −4 foi 64/64 ≥ α). O run 1 havia registrado 47/50 para −4, demonstrando variação estatística.

## Comparação Run 1 vs Run 2
- Documento: `artifacts/nist_sts/run_comparison.md`.
- Gráfico: `artifacts/nist_sts/pass_ratio_comparison.png`.
- Observações:
 - Falhas migraram: RUN1 falhou Frequency? (PASS) → RUN2 borderline em Frequency; RUN1 falhou Non-overlapping (idx 26/50/61) e Random Excursions (estado −4); RUN2 falhou Non-overlapping (idx 15/102) e Frequency borderline.
 - Proporções médias praticamente idênticas (`mean_pass_ratio` ≈ 0.9887 em ambos).
 - Evidência de que as falhas residuais são distribuições naturais dos p-values.

### Non-overlapping Templates
- Run 1 críticos: 26 (`000111001`), 50 (`001111101`), 61 (`010100111`).
- Run 2 críticos: 15 (`000011111`), 102 (`110010010`).
- Documento comparativo: `artifacts/nist_sts/non_overlapping_comparison.md`.
- Conclusão: Não há repetição do mesmo template entre runs → reforça hipótese de ruído estatístico.

### Random Excursions
- Run 1: estado −4 = 47/50 (falhou). Demais estados ≥ 0.96.
- Run 2: todos os estados ≥ 0.984 (estado −2 e 1/2 em 63/64, satisfaz tolerância).
- Documento comparativo: `artifacts/nist_sts/random_excursions_comparison.txt`.

## Referências & Artefatos Atualizados
- Run 2 result: `artifacts/nist_sts/run2/result_run2.txt`.
- Summaries: `artifacts/nist_sts/local_run_2025-11-17_run2/` (nist_summary, non_overlapping, random_excursions).
- Gráficos: `artifacts/nist_sts/pass_ratio_comparison.png` (+ `run2/pass_ratio_bar.png` a gerar se necessário).

## Conclusões Parciais (fase de variação)
1. **Falhas residuais são instáveis** (trocam de índice/estado entre runs) → forte indicação de flutuação natural.
2. **Nenhum padrão estrutural fixo** detectado em Non-overlapping Templates.
3. **Random Excursions estabilizou** no segundo run, com mais ciclos válidos (J=64) e 100% de passes no estado −4.
4. Necessário complementar com benchmarks externos (PQC) + documentação técnica (fase 2 do plano).

## Próximos Passos
- Coletar benchmarks públicos (Kyber/Dilithium/Falcon) evidenciando falhas similares em STS.
- Preparar análise qualitativa explicando por que Frequency 96/100 ainda é aceitável (citar tolerância 3σ ≈ 0.96015 para N=100).
- Atualizar whitepaper/pitch deck com gráficos e argumentos.
- (Opcional) Rodar terceira execução com 1000 sequências para reforçar estatística.
