# High-Risk Guardrails – KayosCrypto Quantum Suite

## Objetivo
Estabelecer controles operacionais e métricas verificáveis para operar o KayosCrypto em ambientes de alto risco (99.5% maturidade alvo), garantindo consistência com a filosofia KAIOS e a Arquitetura Fishbone.

## Guardrails Operacionais
- **Reversibilidade absoluta**: toda alteração de pipeline deve manter 100% de reversibilidade; validar com `make test` antes de promover builds.
- **Avalanche mínimo**: manter pontuação >47% (baseline atual 47.80%). Qualquer regressão <45% deve bloquear deploy até correção.
- **Quantum readiness**: resistências individuais das fases devem permanecer ≥0.85; acionar análise imediata se qualquer fase ficar <0.80.
- **Entropy floor**: entropia por byte ≥95% (7.6 bits/byte) para chaves geradas via GeometricEntropyPool; snapshots abaixo desse piso são marcados como falha crítica.
- **Key size enforcement**: chaves simétricas ≥256 bits; CLI/API bloquearão operações abaixo desse limite em modo quantum.
- **Rotina de auditoria**: executar `python tools/generate_quantum_dashboard.py` e `python tools/generate_certification_gap_report.py` semanalmente; anexar saídas à pasta `reports/` para rastreabilidade.

## Telemetria Oficial
1. **Coleta automática** (API/CLI): cada criptografia quantum grava snapshot de entropia em `reports/quantum/entropy_pool/entropy_snapshot_*.json`.
2. **Dashboard unificado**: `python tools/generate_quantum_dashboard.py` consolida entropia, resistência e certificações em:
   - `reports/quantum/dashboard_summary.json`
   - `reports/quantum/dashboard_summary.md`
3. **Integração com certificações**: `CertificationTracker` registra atualizações em `reports/certifications/cert_snapshot_*.json`; guardamos referência do snapshot de entropia associado ao evento.
4. **Evidências versionadas**: manter os arquivos `reports/` sob controle de versão em releases candidatos à certificação.

## Evidências de Certificação
- **Gap report atualizado**: `python tools/generate_certification_gap_report.py` gera `gap_report_latest.(json|md)` com prontidão, gaps e ações priorizadas.
- **Roadmap consolidado**: `CertificationTracker.generate_roadmap()` é armazenado em cada snapshot; revisar antes de reuniões com auditores.
- **Métricas alvo**:
  - FIPS 140-3: prontidão ≥65% + plano de self-tests aprovado.
  - ISO 27001: ISMS ≥70% implementado + auditoria interna concluída.
  - NIST PQC: resistência quântica ≥0.95 + whitepaper técnico pronto.
  - Common Criteria: documentação ST/PP ≥60% + orçamento comprometido.

## Processo de Resposta
1. **Detecção**: dashboards sinalizam queda em métricas (ver guardrails).
2. **Classificação**:
   - Se reversibilidade/entropia < limiar → incidente crítico; suspender operações.
   - Se readiness certificação < baseline → incidente maior; agendar revisão semanal.
3. **Correção**: abrir tarefa Fishbone (Rib correspondente) e atualizar `docs/checkpoints/` com evidências.
4. **Verificação**: rerodar suíte completa + geração de dashboards; anexar resultados no MR.
5. **Comunicação**: registrar decisão no documento de operações (`docs/operations/`) e informar stakeholders em até 24h.

## Fluxo de Homologação
- **Diário**: `make test`, `python tools/generate_quantum_dashboard.py`, revisão dos diffs gerados.
- **Semanal**: execução de `gap_report`, atualização do roadmap, checkpoint no diretório `docs/checkpoints/`.
- **Mensal**: auditoria cruzada (segurança + engenharia) com revisão de snapshots, validação manual dos guardrails e atualização do plano de certificações.

## Próximos Passos
1. Automatizar execução dos scripts em pipeline CI (cron semanal) com upload dos artefatos.
2. Integrar dashboards ao painel KayosCryptoSuite para visualização executiva.
3. Preparar dossiê de evidências consolidado para submissão FIPS/ISO (anexando relatórios de gap + snapshots recentes).
