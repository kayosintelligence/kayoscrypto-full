# Pré-Auditoria FIPS 140-3 / ISO 19790 — Expectativa 26/11/2025

## Objetivo
Estabelecer o plano de pré-auditoria para os frameworks FIPS 140-3/ISO 19790 (módulos criptográficos), Common Criteria (EAL2+/EAL4) e ISO 27001 (controles organizacionais), usando as evidências já coletadas nas campanhas PractRand, TestU01, Dieharder, ENT e MPC-N. O documento descreve como iremos organizar o material, quais evidências cobrem cada requisito e onde ainda existem lacunas antes de submeter o projeto a uma auditoria formal.

## Escopo Regulatório
| Framework | Foco no KayosCrypto | Componentes no escopo |
|-----------|---------------------|------------------------|
| FIPS 140-3 / ISO 19790 | Validação de módulo criptográfico (software). | Spine KayosCryptoUltimate + Ribs (Fibonacci Direction, Ezekiel Concentric, Core) + pipeline de testes estatísticos controlados pelo MPC-N. |
| Common Criteria (prov. EAL4) | Confiança no ciclo de desenvolvimento e mitigação de ameaças. | Código-fonte, processos MPC-N, documentação Fishbone, relatórios de testes externos. |
| ISO 27001 | Controles de segurança da informação e rastreabilidade operacional. | Guardião MPC-N, logs de auditoria, scripts `run_*`, políticas de resposta a incidentes descritas nos relatórios. |

## Estratégia Geral
1. **Coleção de Evidências** – Consolidar os logs de diagnóstico (PractRand raw/whitened, TestU01, Dieharder, ENT, rngtest, PQC stack) em um inventário único, todos com apontamento MPC-N.
2. **Mapeamento por requisito** – Relacionar cada requisito dos frameworks com evidências existentes (ex.: FIPS SP 800-90B para fontes de entropia → `practrand_raw_stream_*`, requisitos ISO 19790 5.1/5.2 → `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md`).
3. **Análise de lacunas** – Destacar controles não cobertos ou parcialmente cobertos (ex.: FIPS exige documentação formal de mitigação de tamper, Common Criteria requer modelagem de ameaça detalhada, ISO 27001 pede SoA).
4. **Planos de ação** – Definir tarefas imediatas (curto prazo) para endereçar lacunas antes do engajamento com laboratórios (ex.: escrever Security Policy FIPS, criar checklist SoA ISO 27001, expandir logs PQC com assinaturas Dilithium 5, etc.).
5. **Compromissos MPC-N** – Registrar cada passo relevante no guardião para garantir cadeia de custódia e comprovar disciplina operacional durante a pré-auditoria.

Esta estratégia serve como guia para os próximos dois subtópicos (mapeamento e gaps).

## Mapa de Evidências

### FIPS 140-3 / ISO 19790
| Requisito | Evidências KayosCrypto |
|-----------|------------------------|
| Qualidade da fonte de entropia (SP 800-90B §3-4) | `practrand_logs/practrand_raw_stream_20251125_{64G,128G,256G,512G,1T}_buffered_attempt*.log` + eventos `diagnostics.practrand_raw:*` no `mpcn_state.json`, mostrando testes core até 1 TB sem whitening e anomalias catalogadas. |
| Integridade e controle operacional (ISO 19790 §5.1/5.2) | `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md` descreve guardião MPC-N, traps e heartbeats; `mpcn_state.json` demonstra rastreabilidade completa com timestamps e resultados. |
| Auto-testes e monitoração contínua (FIPS §7) | `tests/security/real_security_tests.py`, `make test-security`, e logs `practrand_logs/practrand_whitened_*` (1.5 TB) para monitoramento contínuo; eventos `diagnostics.practrand:*` registram cada rodada. |
| Segurança algorítmica e sensibilidade a chaves | `reports/key_sensitivity_20251124T103534Z.json` (1000 amostras p/ 512/1024/2048 bits) + `docs/PQC_VALIDATION_REPORT_2025-11-24.md` cobrindo resistência Grover/Shor. |
| Gestão de configuração e documentação | `docs/technical/ARCHITECTURE.md`, `docs/checkpoints/TASK_10.4_STATISTICAL_BATTERY_PROGRESS_2025-11-22.md`, mais commits MPC-N (actions `diagnostics_report`, `pqc_summary`). |

### Common Criteria (EAL alvo)
| Requisito | Evidências KayosCrypto |
|-----------|------------------------|
| ALC_CMC / ALC_CMS (controle de configuração) | Guardião MPC-N (`mpcn_state.json`) + scripts `tools/mpcn_guard.py`; garante linha do tempo assinada. |
| ADV_FSP / ADV_TDS (descrição funcional e de design) | `docs/technical/ARCHITECTURE.md`, `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md`, `docs/diagnostics/PRE_AUDIT_FIPS_ISO_EXPECTATIVA_2025-11-26.md` (este documento) descrevendo interfaces e fluxo Fishbone. |
| ATE_FUN / ATE_COV (testes funcionais) | Logs PractRand, Dieharder, TestU01, ENT, rngtest e `practrand_logs/pqc_practrand_*` com referências a scripts `run_*`. |
| AVA_VAN (análise de vulnerabilidade) | `docs/PQC_VALIDATION_REPORT_2025-11-24.md` cobre ameaças pós-quânticas; `reports/pqc_benchmark_full_20251124T110127Z.json` mostra resultados de KEM/Assinatura; ainda precisamos complementar com avaliação formal clássica. |

### ISO 27001 (controles selecionados)
| Controle (Anexo A) | Evidências KayosCrypto |
|--------------------|------------------------|
| A.5.1 Governança | `docs/INDEX.md`, `EVOLUTION_COMPLETE_SUMMARY.md`, manutenção do guardião MPC-N para accountability. |
| A.8.16 Registro de eventos | `mpcn_state.json` com todos os `log_event`, incluindo heartbeat, erro, conclusão e atualização de documentação. |
| A.14.2 Segurança em desenvolvimento | `docs/technical/ARCHITECTURE.md`, `docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md` (processos de teste automatizados, traps `set -euo pipefail`). |
| A.16.1 Resposta a incidentes | Eventos MPC-N que capturam quedas de energia, Ctrl+C involuntário, correções subsequentes; `run_practrand_raw_stream` registra motivo e ação corretiva. |
| A.18.2 Auditoria e evidências | Este documento + logs consolidados, permitindo trilha completa para auditorias externas. |

## Lacunas e Próximos Passos
- **FIPS 140-3 / ISO 19790**
	- Elaborar Security Policy formal (Seções 3/4) descrevendo modos aprovados (whitening ON/off) e operações do guardião. Arquivo alvo: `docs/fips/SECURITY_POLICY_v0.md` (a criar).
	- Documentar mitigação de tamper físico/software (mesmo que “not applicable”) e dependências de plataforma.
	- Consolidar relatório SP 800-90B completo com estatísticas (hoje temos PractRand raw; precisamos adicionar testes IID e `non-IID` com scripts dedicados).

- **Common Criteria**
	- Criar modelo de ameaças (TOE, TOE environment, atacantes) alinhado ao Fishbone → sugestão: `docs/cc/THREAT_MODEL_FISHBONE.md`.
	- Preparar documentação ADV_FSP/ADV_TDS detalhando APIs (KayosCryptoUltimate, Ribs) com diagramas formais.
	- Adicionar análise AVA_VAN clássica (buffer overflow, timing, fault injection) além do foco PQC.

- **ISO 27001**
	- Produzir Statement of Applicability (SoA) mapeando quais controles do Anexo A são aplicáveis e justificativas.
	- Formalizar procedimento de resposta a incidentes (workflow MPC-N + acionamento humano) em `docs/policies/INCIDENT_RESPONSE.md`.
	- Registrar Risk Assessment/Risk Treatment (por exemplo, tabela com probabilidade/impacto para quedas de energia, fault injection, indisponibilidade do guardião).

- **Ações Operacionais Imediatas**
	1. Agendar heartbeat MPC-N de pré-auditoria (`actor='pre_audit'`, intent `diagnostics.pre_audit`).
	2. Criar pastas `docs/fips`, `docs/cc`, `docs/policies` para receber os artefatos acima e garantir versionamento.
	3. Integrar scripts `run_*` com checklist automatizada (ex.: `make pre-audit`) para repetir rapidamente as evidências antes de cada marco.
	4. `make pre-audit` agora copia automaticamente `artifacts/nist_sts/latest/finalAnalysisReport.txt` + `logs/nist_output_full_1000streams_latest.log`, garantindo que o bundle contenha a execução oficial do NIST STS (1000 streams, 27/11/2025).
	5. Montar pacote zipado com logs chave (`practrand_logs`, `reports/*.json`, `docs/diagnostics/*.md`) para compartilhar com o laboratório quando necessário.