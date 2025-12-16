# Processo de Gestão de Mudanças — KayosCrypto

## Objetivo
Garantir que qualquer alteração em código, scripts diagnósticos, documentação regulatória ou infraestrutura MPC-N seja revisada, aprovada e registrada com rastreabilidade completa antes de impactar ambientes auditáveis.

## Escopo
- Código-fonte (`src/`, `core/`, `cli/`).
- Scripts `run_*`, ferramentas `tools/`, Makefile.
- Documentos críticos (Security Policy, Threat Model, SoA, Incident Response, PRE_AUDIT).
- Configurações do guardião MPC-N.

## Fluxo
1. **Proposição**
   - Abrir item em checklist interno ou issue tracker descrevendo: motivo, arquivos afetados, riscos.
   - Registrar intenção no MPC-N (`log_event(actor='change', action='change.requested', details={...})`).
2. **Avaliação**
   - Auditor Interno revisa impacto (segurança, compliance, desempenho).
   - Consultar Guardião MPC-N para avaliar ajustes operacionais.
3. **Aprovação**
   - CTO (ou delegado) aprova via comentário no issue + evento `change.approved` no MPC-N.
4. **Implementação**
   - Executar mudança em branch dedicado.
   - Rodar suites obrigatórias (`make test`, `make test-security`, `run_*` relevantes).
   - Documentar resultados em DIAGNOSTICS/relatórios apropriados.
5. **Revisão Pós-Implementação**
   - Auditor Interno valida artefatos (commits, logs, docs).
   - Registrar `change.completed` no MPC-N com referência a commit/log.
6. **Encerramento**
   - Atualizar SoA/Inventário se aplicável.
   - Arquivar checklist/issue.

## Critérios de Prioridade
- **Crítico**: impacta segurança/compliance → exige aprovação imediata e execução de todas as suites.
- **Alto**: mudanças em scripts ou documentos regulatórios.
- **Médio/Baixo**: ajustes internos sem impacto nos controles centrais (mesmo assim requer registro).

## Métricas
- Tempo médio entre `change.requested` e `change.completed`.
- Número de rollback por trimestre.
- Cobertura de testes executados por mudança.
