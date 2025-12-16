# TASK 10.0 – NIST STS PIPELINE START

## Contexto
- Data: 17 de novembro de 2025.
- Objetivo: iniciar a trilha "Alto Risco" garantindo que o KayosCrypto gere insumos auditáveis para o NIST Statistical Test Suite (STS).
- Estado anterior: não havia artefatos NIST armazenados no repositório nem rota configurável para execução em ambientes isolados.

## Entregas nesta sessão
-  Atualização de `tools/generate_nist_data.py` para aceitar o diretório de saída via variável de ambiente (`KAYOS_NIST_OUTPUT_DIR`), com padrão `artifacts/nist_sts/` dentro do repositório.
-  Criação automática da árvore `artifacts/nist_sts/` (incluindo pais) para viabilizar execução em CI/workspaces sandbox.
-  Geração de datasets cifrados prontos para o NIST STS:
  - 10 sequências x 1M bits (1,25 MB) e 100 sequências x 1M bits (12,5 MB).
  - Arquivo consolidado: `artifacts/nist_sts/kayoscrypto_sequences.bin`.
  - Metadados: `artifacts/nist_sts/KAYOSCRYPTO_PARAMS.txt` (engine, versão, nível Fibonacci, contagem de sequências/bits).
  - Exportações ASCII por sequência (`artifacts/nist_sts/ascii/seq_XXXX.txt`) e agregado (`artifacts/nist_sts/kayoscrypto_sequences_ascii.txt`).
-  Parser `tools/parse_nist_sts_results.py` criado para consolidar arquivos `.stats` em CSV/Markdown/JSON (opcional), com cálculo automático de proporção de passes.
-  Logs completos das execuções preservados no terminal para auditoria.

## Próximos passos propostos
1. **Instalar/confirmar o NIST STS** em um diretório acessível (ex.: `/opt/sts-2_1_2` ou container dedicado) e documentar a localização real.
2. **Copiar `kayoscrypto_sequences.bin` (12,5 MB) para `<sts_root>/data/`** e rodar `./assess 1000000` com 100 bitstreams selecionando todos os testes.
3. **Exportar resultados** de `experiments/AlgorithmTesting/` para dentro de `artifacts/nist_sts/` (ex.: compactar os diretórios e mover para `artifacts/nist_sts/results_{data}/`).
4. ~~Construir script auxiliar que parse os relatórios `*.stats` do STS e consolide P-values e pass/fail em um CSV/Markdown.~~  `tools/parse_nist_sts_results.py` disponível.
5. **Documentar checkpoint TASK 10.x COMPLETE** com 15/15 testes aprovados, anexando tabela de evidências.

## Observações
- A execução atual usa somente 10 sequências de 1M bits. Para auditoria formal recomenda-se repetir com 100 sequências (≈12.5 MB) após validar o pipeline completo.
- `tools/generate_nist_data.py` segue compatível com caminhos externos através da variável `KAYOS_NIST_OUTPUT_DIR`, permitindo integração a ambientes pré-existentes.
- A ausência do NIST STS dentro do repositório impede execução automática dos testes neste momento; registrar a instalação torna-se prioridade na próxima sessão.
