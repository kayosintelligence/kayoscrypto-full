# TASK 10.5 – NIST STS (1000 Streams, 2025-11-26)

**Responsável:** GitHub Copilot • **Objetivo:** executar a bateria NIST STS com o novo dataset de 1000 × 1 000 000 bits, registrar o fluxo no MPC-N e identificar as pendências para fechar o requisito de validação estatística.

---

## 1. Contexto
- Dataset recém-gerado (`TESTE_COMPARATIVO/sts-2_1_2/data/kayoscrypto_sequences.bin`, 125 000 000 bytes) cobre exatamente 1000 streams de 1 000 000 bits cada, conforme solicitado nas diretrizes de 26/11.
- A automação `run_nist_auto.sh` estava limitada a 10 streams. Atualizamos o script para utilizar constantes `STREAM_COUNT=1000`, `STREAM_LENGTH_BITS=1_000_000`, detectar automaticamente o diretório `AlgorithmTesting*` mais recente e salvar logs com timestamp.
- Guardião MPC-N executado (`tools/mpcn_guard.py --actor nist_auto_runner --intent diagnostics.nist --max-inactive-minutes 60`) antes do disparo. Eventos `diagnostics.nist:start` e `diagnostics.nist:complete` registrados com detalhes do dataset e arquivos gerados.

---

## 2. Execução Automatizada
| Item | Detalhe |
|------|---------|
| Comando | `/home/kbe/KAYOS_SYSTEMS/KayosCrypto/.venv/bin/python /home/kbe/KAYOS_SYSTEMS/TESTE_COMPARATIVO/run_nist_auto.sh` |
| Input para `assess` | `Generator=0`, `StreamLength=1_000_000`, `NumberOfStreams=1000`, `File=data/kayoscrypto_sequences.bin`, `Tests=0 (todos)` |
| Log principal | `TESTE_COMPARATIVO/sts-2_1_2/nist_output_full_1000streams_20251126_221255.log` |
| Diretório de resultados | `TESTE_COMPARATIVO/sts-2_1_2/experiments/AlgorithmTesting/` |
| Relatório final | `finalAnalysisReport.txt` (mesmo diretório) |
| MPC-N Start | `actor='nist_auto_runner', action='diagnostics.nist:start'` |
| MPC-N Complete | `actor='nist_auto_runner', action='diagnostics.nist:complete', status='completed_with_failures'` |

---

## 3. Resultado Observado
- `finalAnalysisReport.txt` indica `0/1000` sequências aprovadas em todos os testes listados (Frequency, Block Frequency, Cumulative Sums, Runs, Longest Run, Rank, FFT, Serial, Linear Complexity etc.). As colunas C1–C10 concentram 1000 ocorrências na primeira faixa e `P-VALUE = 0.000000` em cada linha.
- Random Excursions/Variant aparecem como “----” por não terem sido executados (STS só roda esses testes quando a soma cumulativa cruza zero ≥1 vez por stream).
- O log da automação confirma que o NIST STS concluiu sem erro de processo; o retorno do `assess` foi `0` e o diretório `experiments/AlgorithmTesting` foi populado normalmente.
- Interpretação atual: o STS tratou o dataset como um único stream repetido ou criou buckets inválidos, resultando em “p-value = 0” por falta de distribuição. Necessário revisar `input_1000seq.txt`, `config.par` e a rotina que informa o número de bitstreams.

---

## 4. Hipóteses para o 0/1000
1. **Arquivo `input_1000seq.txt` sobrescrito** – O STS gera este arquivo com blocos `[numerOfBitStreams, streamLength, nStreamsRead]`. Precisamos confirmar se a rotina de automation atualiza o campo *Number of Bitstreams* dentro do experimento (não apenas no prompt).
2. **Modo de leitura sequencial** – Se `assess` detecta que o arquivo binário acabou antes de completar todos os streams, ele replica a última sequência e produz `0/1000`. Verificar se os 125 MB foram lidos integralmente (o log não mostra warnings, mas o script pode validar `stdout` procurando por “insufficient data”).
3. **Resíduos de execuções anteriores** – O diretório `experiments/AlgorithmTesting` talvez contenha `finalAnalysisReport.txt` de uma execução anterior (10 streams) e não tenha sido limpo. Contudo, o cabeçalho atual mostra `generator is <input_1000seq.txt>`, indicando que a nova execução realmente rodou mas gerou buckets degenerados.

---

## 5. Ações Recomendadas
1. **Validar o arquivo de parâmetros do STS**: abrir `experiments/AlgorithmTesting/input_1000seq.txt` (ou equivalente) e garantir que a segunda linha é `1000` (NumberOfBitstreams). Se não for, editar `run_nist_auto.sh` para sobrescrever explicitamente antes da execução ou remover diretórios antigos.
2. **Limpar o diretório `experiments/AlgorithmTesting` antes da próxima rodada** para evitar reaproveitar relatórios antigos. Podemos remover/arquivar o diretório antes de chamar `./assess`.
3. **Rodar `assess 1000000` manualmente** (sem wrapper) alimentando o mesmo input para confirmar se o problema vem do dataset ou da automação.
4. **Adicionar validação pós-processo** no script: verificar se o arquivo `finalAnalysisReport.txt` contém proporções >0 e abortar com erro caso todas sejam zero. Isso evita confundir o resultado com sucesso operacional.
5. **Documentar o estado no snapshot** (feito) e manter o MPC-N no status `completed_with_failures` até resolvermos o preset.

---

## 6. Referências e Próximos Passos
- `run_nist_auto.sh` (patch em 26/11) – constants `STREAM_COUNT`, `STREAM_LENGTH_BITS`, detecção de `AlgorithmTesting*`, log com timestamp.
- `docs/checkpoints/SNAPSHOT_EMULATOR_V6.0.md` atualizado com o status .
- Próxima iteração deverá:
  1. Ajustar o preset do STS (ver Ações acima).
  2. Reexecutar `run_nist_auto.sh` e garantir `>=980/1000` aprovações por teste.
  3. Atualizar este checkpoint com o novo relatório, anexando p-values médios e proporções.

> Este documento serve como evidência da primeira execução de 1000 streams e explica por que o resultado foi marcado como **completed_with_failures** no MPC-N. Nenhum dado foi descartado; tanto o log quanto o relatório final estão preservados para auditoria.
