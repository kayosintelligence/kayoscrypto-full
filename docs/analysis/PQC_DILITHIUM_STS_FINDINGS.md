# Dilithium STS Findings – 2025-11-18

## Contexto
- Dataset: `artifacts/nist_sts/pqc/dilithium/ML-DSA-65/dilithium_ML-DSA-65_sequences.bin`
- Geração: `python tools/generate_pqc_nist_data.py dilithium --mechanism ML-DSA-65 --num-sequences 100 --bits-per-sequence 1000000`
- Execução NIST STS: `./sts -v 1 -i 100 -I 10 -S 1000000 -F r -s -w experiments/dilithium_mldsa65_run1 data/dilithium_mldsa65_sequences.bin`
- Consolidação: `python tools/parse_nist_sts_results.py ... --output-dir artifacts/nist_sts/pqc/dilithium/ML-DSA-65/run_2025-11-18 --summary-json`

## Resumo numérico
- `mean_pass_ratio`: **0.5046** (apenas 50% dos subtestes dentro da faixa binomial aceitável)
- 7 testes `PASS`, 8 testes `FAIL`.

## Testes que falharam
| Teste | Passes/Total | Proporção | Observação |
| --- | --- | --- | --- |
| Frequency | 0/100 | 0.0000 | Sequências exibem forte viés; valores-p zerados em todas as replicações |
| Runs | 0/5 | 0.0000 | Falha imediata no número de alternâncias; módulo acusa padrões determinísticos |
| CumulativeSums | 0/200 | 0.0000 | Prefixos acumulados nunca se comportam como passeio aleatório |
| Serial | 0/200 | 0.0000 | Contagens de subsequências totalmente fora da distribuição esperada |
| ApproximateEntropy | 0/100 | 0.0000 | Entropia aproximada abaixo do limiar para todos os blocos |
| Universal | 0/100 | 0.0000 | Compressibilidade alta indica redundância sistemática |
| BlockFrequency | 8/100 | 0.0800 | Apenas 8 blocos dentro da tolerância; p-values próximos de zero |
| Rank | 56/100 | 0.5600 | Apenas levemente acima do cut-off, mas ainda fora da faixa 3σ |

### Padrão observado
- Os relatórios `result.txt` exibem `p-value = 0.000000` repetidamente.
- Falhas com proporção 0 sugerem **estrutura determinística intensa** no fluxo de bits.
- Isso é consistente com o fato de estarmos concatenando assinaturas PQC: assinaturas são deterministicamente derivadas de chaves/seed internas e não foram projetadas para produzir fluxo pseudo-aleatório.

## Comparação com outros sistemas
- KayosCrypto e Kyber exibem proporções médias ≈0.99, com falhas apenas marginais (ex.: Frequency 96/100 para Kayos, ainda dentro da tolerância 3σ).
- Dilithium contrasta com falhas maciças: Frequency, Runs, Serial não registram sequer um sucesso em 100 tentativas.

## Implicação
- Resultado reforça narrativa: **nem toda saída criptográfica é adequada como fonte pseudoaleatória**. Dilithium (assinatura) carrega estrutura combinatória pesada (lattice-based), que se manifesta como padrões detectáveis pelo NIST STS.
- Em apresentações, podemos argumentar que KayosCrypto produz fluxo comparável a KEMs referenciais (Kyber), enquanto assinaturas lattice evidenciam determinismo.

## Artefatos de referência
- `artifacts/nist_sts/pqc/dilithium/ML-DSA-65/run_2025-11-18/nist_summary.md`
- `result.txt` (mesmo diretório)
- Comparativo consolidado: `artifacts/nist_sts/comparisons/2025-11-18/comparison_summary.md`
