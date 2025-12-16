# TASK 10.1 – NIST STS Local Run (2025-11-17)

## Status Geral
- Execução local do NIST Statistical Test Suite v3.2.7 concluída com sucesso.
- Dados de entrada: `artifacts/nist_sts/kayoscrypto_sequences.bin` (100 seq. x 1 Mbit).
- Resultado oficial do STS (`kayos_NIST/sts-2.1.2/experiments/result.txt`): **184/188 subtestes aprovados**.
- Consolidação interna atualizada em `artifacts/nist_sts/local_run_2025-11-17/` (CSV, Markdown, JSON).

## Comando Executado
```bash
/home/kbe/KAYOS_SYSTEMS/KayosCrypto/kayos_NIST/sts-2.1.2/sts \
 -v 1 -i 100 -I 10 -S 1000000 -F r -s \
 -w /home/kbe/KAYOS_SYSTEMS/KayosCrypto/kayos_NIST/sts-2.1.2/experiments/kayoscrypto_local \
 /home/kbe/KAYOS_SYSTEMS/KayosCrypto/kayos_NIST/sts-2.1.2/data/kayoscrypto_sequences.bin
```

## Artefatos
- `kayos_NIST/sts-2.1.2/experiments/result.txt` – resumo original do STS.
- `kayos_NIST/sts-2.1.2/experiments/kayoscrypto_local/` – estatísticas completas por bateria.
- `artifacts/nist_sts/local_run_2025-11-17/` – consolidação automatizada (CSV, Markdown, JSON).
- `artifacts/nist_sts/local_run_2025-11-17/non_overlapping_template_summary.{csv,md}` – síntese por template com proporções e tolerância.
- `artifacts/nist_sts/local_run_2025-11-17/non_overlapping_failures.txt` – três templates críticos (índices 26, 50, 61) com métricas agregadas.
- `artifacts/nist_sts/local_run_2025-11-17/random_excursions_summary.txt` – análise estado a estado, destacando o estado -4 com 47/50 aprovações.

## Destaques
- Proporção global: 184/188 aprovados; falhas localizadas em 3 templates da bateria **Non-overlapping Template Matching** e em 1 estado da bateria **Random Excursions** (conforme o relatório oficial).
- Parser interno (`tools/parse_nist_sts_results.py`) agora aplica a tolerância binomial do STS, produzindo classificação alinhada com o laudo oficial.
- Todos os `stats.txt` e `results.txt` das 15 baterias foram preservados para auditoria.

## Ajustes Implementados
1. **Parser aprimorado** para reconhecer formatos (`p_value`, `p value`, tabelas) e aplicar tolerância `±3σ` antes de rotular PASS/FAIL.
2. **Consolidação atualizada** (`nist_summary.md/csv/json`) refletindo as novas regras de avaliação.

## Próximos Passos Recomendados
- Investigar os três templates específicos (~Índices 8, 50, 77) e o estado `-4` da Random Excursions para identificar possíveis ajustes na geração de sequências.
- Gerar visualizações sobre o CSV consolidado (heatmap ou ranking) para facilitar apresentação executiva.
- Caso necessário, rodar bateria extendida (ex.: 1 000 iterações) para stress test.

## Referências
- `docs/checkpoints/TASK_10.0_NIST_STS_PIPELINE_START.md`
- `tools/generate_nist_data.py`
- `tools/parse_nist_sts_results.py`
