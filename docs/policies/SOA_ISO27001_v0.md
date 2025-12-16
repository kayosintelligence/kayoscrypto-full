# Statement of Applicability (ISO/IEC 27001:2022) — versão 0.2 (Audit Ready)

## 1. Escopo e Contexto
- **Organização:** KayosCrypto (Arquitetura Fishbone / MPC-N Guard).
- **Escopo do SGSI:** desenvolvimento, testes, distribuição e suporte do KayosCryptoUltimate (Spine + Ribs) incluindo pipelines de validação estatística (PractRand/TestU01) e automação de auditoria MPC-N.
- **Exclusões:** infraestrutura física dos clientes e datacenters de terceiros (controlados pelo cliente final). Esses itens são sinalizados como *Não Aplicável* no Anexo A.

## 2. Metodologia de Avaliação
- Todos os 93 controles do Anexo A (2022) foram avaliados segundo três estados: **I** (Implementado), **P** (Planejado em roadmap com owner e prazo) e **NA** (Não Aplicável ao escopo). 
- Cada controle tem justificativa, evidência rastreável e, quando aplicável, próxima ação com responsável.
- As evidências mencionadas estão publicadas em `docs/policies/`, `docs/diagnostics/`, `docs/business/` ou registradas via MPC-N (`mpcn_state.json`).

## 3. Resumo por Domínio

| Domínio (ISO 27001:2022) | Qtde de controles | I | P | NA |
|--------------------------|-------------------|---|---|----|
| A.5 Organizational | 37 | 18 | 17 | 2 |
| A.6 People | 8 | 3 | 5 | 0 |
| A.7 Physical | 14 | 2 | 4 | 8 |
| A.8 Technological | 34 | 15 | 17 | 2 |

Legenda: **I** = controles operacionais com evidência; **P** = plano registrado; **NA** = fora do escopo (devidamente justificado).

---

## 4. Matriz Detalhada (por domínio)

### A.5 Organizational Controls (37)

| Controle | Status | Implementação / Evidência | Próxima ação |
|----------|--------|---------------------------|---------------|
| A.5.1 Policies for Information Security | I | `docs/fips/SECURITY_POLICY_v0.md` + `EVOLUTION_COMPLETE_SUMMARY.md` publicados e controlados por git/MPC-N. | Atualizar para versão 1.0 após revisão jurídica (jan/26). |
| A.5.2 Roles and Responsibilities | P | Responsáveis descritos informalmente; rascunho `docs/policies/RACI_SGSI.md`. | Oficializar RACI com aprovação da direção (dez/25). |
| A.5.3 Segregation of Duties | P | Fluxos de desenvolvimento/teste definidos, mas sem matriz formal. | Documentar matriz de segregação na `CHANGE_MANAGEMENT.md`. |
| A.5.4 Management Responsibilities | I | Accountability do CTO registrada via MPC-N e reuniões semanais (`docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md`). | Registrar atas trimestrais (Q1/26). |
| A.5.5 Contact with Authorities | P | Canal com ANPD/NIST ainda não formalizado. | Criar procedimento em `INCIDENT_RESPONSE.md` (jan/26). |
| A.5.6 Contact with Special Interest Groups | P | Participação ad-hoc em fóruns PQC. | Registrar afiliações em `docs/business/ALLIANCES.md`. |
| A.5.7 Threat Intelligence | P | Monitoramento manual de CVE/PQC. | Implementar feed semanal documentado (`THREAT_INTELLIGENCE.md`). |
| A.5.8 Security in Project Management | I | Fishbone/Spine com gates definidos (`PLANO_EVOLUCAO_EZEKIEL.md`). | Adicionar checklist ISO ao template de projetos. |
| A.5.9 Inventory of Assets | P | Inventário parcial (`docs/policies/ASSET_INVENTORY.md`). | Expandir com classificação/confidencialidade (jan/26). |
| A.5.10 Acceptable Use | P | Política em elaboração (`ACCEPTABLE_USE.md`). | Publicar e coletar aceite dos operadores. |
| A.5.11 Return of Assets | NA | Não há cessão de ativos físicos no escopo. | Revisar quando houver funcionários CLT. |
| A.5.12 Classification of Information | P | Tags “Public/Restricted/Internal” esboçadas. | Formalizar matriz e instruções de rotulagem. |
| A.5.13 Labelling of Information | P | Git usa labels básicos. | Documentar padrão em `docs/policies/LABELLING.md`. |
| A.5.14 Information Transfer | I | Bundler (`bundle_due_diligence.py`) + MPC-N logging cobrem envios. | Adicionar checklist de criptografia no README Due Diligence. |
| A.5.15 Access Control Policy | I | Definida em SECURITY_POLICY + enforcement via `.venv` segregado. | Revisar para incluir RBAC do MPC-N. |
| A.5.16 Identity Management | P | Gestão de contas Git/Drive manual. | Implementar inventário de identidades e revisões trimestrais. |
| A.5.17 Authentication Information | I | Senhas derivadas via SHA-256 (Key derivation pattern) e secrets via `KAYOS_SIGN_PASSWORD`. | Adicionar política de troca periódica. |
| A.5.18 Access Rights | P | Revisões ad-hoc. | Processo formal documentado em `ACCESS_REVIEW.md`. |
| A.5.19 Supplier Relationships | P | Hoje sem fornecedores críticos. | Criar checklist para futuros contratos. |
| A.5.20 Supplier Agreements | NA | Não existem acordos em vigor. | Atualizar quando houver. |
| A.5.21 ICT Supply Chain | P | Dependências open-source listadas em `requirements*.txt`. | Adicionar avaliação de risco por componente. |
| A.5.22 Supplier Monitoring | P | Sem fornecedores. | Alinhar com 5.19 quando aplicável. |
| A.5.23 Cloud Services | P | Uso limitado (Google Drive). | Escrever política mínima de uso de nuvem (dez/25). |
| A.5.24 Incident Management Planning | I | `docs/policies/INCIDENT_RESPONSE.md` define fases e owners. | Exercício anual (mar/26). |
| A.5.25 Event Assessment | P | Triagem hoje manual via MPC-N. | Criar playbook com critérios objetivos. |
| A.5.26 Incident Response | I | Procedimentos no `INCIDENT_RESPONSE.md` + MPC-N para execução. | Registrar lições aprendidas pós-ocorrência. |
| A.5.27 Learning from Incidents | P | Apenas registro textual. | Adicionar seção lessons learned por evento. |
| A.5.28 Collection of Evidence | P | Logs preservados porém sem cadeia de custódia formal. | Publicar `EVIDENCE_HANDLING.md`. |
| A.5.29 Information Security During Disruption | I | PractRand + bundler contam com redundância e scripts de retomada. | Acrescentar cenários de desastre no plano de continuidade. |
| A.5.30 ICT Readiness for BC | P | Não há RTO/RPO definidos. | Criar BIA simplificada (fev/26). |
| A.5.31 Legal and Regulatory Requirements | P | Rastreados informalmente. | Checklist jurídico trimestral. |
| A.5.32 Intellectual Property Rights | I | Direitos definidos em `SEGURANCA_EXPOSICAO.md`, repositório privado. | Validar com jurídico externo. |
| A.5.33 Protection of Records | I | Documentos versionados via Git/MPC-N (immutability). | Definir tempo de retenção formal (12 meses mínimo). |
| A.5.34 Privacy & PII Protection | P | Sem PII processada, mas necessário statement. | Emitir declaração “No PII Processed” assinada. |
| A.5.35 Independent Review of ISMS | P | Ainda não auditado. | Planejar auditor interno Q2/26. |
| A.5.36 Compliance with Policies | I | MPC-N audita entradas vs policies. | Automatizar checagem com CI. |
| A.5.37 Documented Operating Procedures | I | `README_DUE_DILIGENCE.md`, `Makefile pre-audit`, `bundle_due_diligence.py`. | Revisar semestralmente. |

### A.6 People Controls (8)

| Controle | Status | Implementação / Evidência | Próxima ação |
|----------|--------|---------------------------|---------------|
| A.6.1 Screening | P | Background checks previstos para novas contratações (não executados). | Criar checklist com parceiro de compliance. |
| A.6.2 Terms of Employment | P | Sem contrato padrão. | Produzir NDA + cláusulas de segurança (jan/26). |
| A.6.3 Awareness & Training | I | Sessões Fishbone/KAIOS registradas, README e docs internos. | Formalizar trilha anual. |
| A.6.4 Disciplinary Process | P | Não documentado. | Incluir no manual do colaborador. |
| A.6.5 Responsibilities After Termination | P | Necessária política de revogação de acesso. | Integrar com A.5.18. |
| A.6.6 NDAs | I | NDAs padrão aplicados a consultores (arquivados). | Atualizar para refletir PQC roadmap. |
| A.6.7 Remote Working | P | Trabalho 100% remoto sem política. | Publicar `REMOTE_WORK_POLICY.md`. |
| A.6.8 User Event Reporting | I | MPC-N permite reporte e classificação de eventos pelos operadores. | Treinar novos membros no fluxo. |

### A.7 Physical Controls (14)

| Controle | Status | Implementação / Evidência | Próxima ação |
|----------|--------|---------------------------|---------------|
| A.7.1 Physical Security Perimeter | NA | Operações executadas em ambientes dos operadores; responsabilidade do provedor local. | Avaliar quando houver data center próprio. |
| A.7.2 Physical Entry Controls | NA | Mesma justificativa de 7.1. | — |
| A.7.3 Securing Offices/Facilities | NA | Não aplicável ao software standalone. | — |
| A.7.4 Physical Security Monitoring | NA | Fora do escopo atual. | — |
| A.7.5 Protection Against Phys./Env. Threats | P | Dependente do provedor; precisamos checklist. | Exigir evidências dos provedores quando onboarding. |
| A.7.6 Working in Secure Areas | NA | Sem áreas dedicadas. | — |
| A.7.7 Clear Desk/Clear Screen | P | Recomendações informais. | Incluir em `ACCEPTABLE_USE.md`. |
| A.7.8 Equipment Siting/Protection | P | Equipamentos de desenvolvimento pessoais. | Checklists de hardening endpoint (jan/26). |
| A.7.9 Off-premises Assets | P | Laptops pessoais com criptografia, sem política formal. | Documentar requisitos mínimos. |
| A.7.10 Storage Media | P | Uso mínimo de mídia removível. | Criar política de proibição/controle. |
| A.7.11 Supporting Utilities | NA | Sem infraestrutura própria. | — |
| A.7.12 Cabling Security | NA | Não aplicável no escopo software. | — |
| A.7.13 Equipment Maintenance | P | Atualizações feitas pelo operador. | Registrar cronograma de manutenção. |
| A.7.14 Secure Disposal/Reuse | P | Dados apagados manualmente. | Formalizar procedimento de limpeza segura. |

### A.8 Technological Controls (34)

| Controle | Status | Implementação / Evidência | Próxima ação |
|----------|--------|---------------------------|---------------|
| A.8.1 User Endpoint Devices | P | Hardening básico documentado em `README.md`. | Criar baseline de SO + verificações. |
| A.8.2 Privileged Access Rights | P | Apenas poucos operadores com sudo. | Implementar registros aprovados via MPC-N. |
| A.8.3 Information Access Restriction | I | Repositórios privados + RBAC Git/GDrive. | Revisão trimestral automática. |
| A.8.4 Access to Source Code | I | Controle via Git + reviews obrigatórios. | Adicionar auditoria de push force. |
| A.8.5 Secure Authentication | I | `KayosCryptoUltimate` usa derivação SHA-256 e `KAYOS_SIGN_PASSWORD`. | Implementar MFA para canais externos. |
| A.8.6 Capacity Management | P | Métricas básicas; sem limites formais. | Script para monitorar throughput + storage. |
| A.8.7 Malware Protection | I | Estações com AV padrão + isolamento virtualenv. | Documentar ferramenta usada. |
| A.8.8 Technical Vulnerability Management | P | Rodos PQC/crypto; faltam SAST/DAST. | Integrar `bandit`/`pip-audit` no CI. |
| A.8.9 Configuration Management | P | `Makefile`, `requirements`, mas sem CMDB. | Criar `CONFIG_BASELINE.md`. |
| A.8.10 Information Deletion | P | Deleção manual. | Procedimento seguro + scripts shred. |
| A.8.11 Data Masking | NA | Não tratamos dados sensíveis/PII. | Reavaliar se onboarding de clientes exigir. |
| A.8.12 Data Leakage Prevention | P | Uso consciente, sem ferramenta. | Avaliar DLP em Drive/Git. |
| A.8.13 Backup | I | Repositório Git + bundles replicados em `artifacts/` e Drive. | Documentar política de retenção (mín. 12 meses). |
| A.8.14 Redundancy | P | Sem replicação automática. | Script de cópia incremental dos artefatos. |
| A.8.15 Logging | I | `mpcn_state.json` (append-only) + logs PractRand com timestamps UTC. | Converter para backend imutável (S3/WORM). |
| A.8.16 Monitoring Activities | I | Heartbeats MPC-N + dashboards `healthy_runs_analysis.py`. | Acrescentar alertas automatizados. |
| A.8.17 Clock Synchronization | P | Sistemas dependem de NTP do host. | Registrar requisito e checagem mensal. |
| A.8.18 Privileged Utility Programs | P | Uso controlado porém sem whitelist. | Documentar ferramentas autorizadas. |
| A.8.19 Installation of Software | P | Sem processo formal; dependências aprovadas manualmente. | Adicionar fluxo de aprovação/interlock. |
| A.8.20 Network Security | P | Ambiente local; sem segmentação formal. | Definir requisitos mínimos de firewall/VPN. |
| A.8.21 Security of Network Services | P | Dependemos do ISP/local. | Checklist de avaliação para serviços externos. |
| A.8.22 Segregation of Networks | P | Não implementado (apenas rede doméstica). | Definir padrão (ex.: VLAN dedicada). |
| A.8.23 Web Filtering | P | Não aplicado. | Adotar política de bloqueio básico via gateway. |
| A.8.24 Use of Cryptography | I | Documentado em `SECURITY_POLICY_v0` e nos módulos `core/`. | Adicionar registro de chaves e owners. |
| A.8.25 Secure Development Life Cycle | I | Fishbone + pipeline de testes (PractRand, TestU01, security suites). | Criar checklist SDLC anexado ao PR template. |
| A.8.26 Application Security Requirements | I | Definidos nos documentos das Ribs + `docs/technical/ARCHITECTURE`. | Formalizar requisito antes de novos módulos. |
| A.8.27 Secure Architecture and Engineering | I | KayosCryptoUltimate + Ribs descritos em docs técnicos. | Revisão anual de arquitetura. |
| A.8.28 Secure Coding | I | Revisões manuais + dependências lint/test. | Integrar scans automáticos (bandit). |
| A.8.29 Security Testing in Dev/Acceptance | I | Suites `tests/security/real_security_tests.py` e `tests/performance/`. | Acrescentar testes DAST. |
| A.8.30 Outsourced Development | P | Não há fornecedores hoje; requisito pronto. | Criar checklist contratual. |
| A.8.31 Separation Dev/Test/Prod | P | Estruturas lógicas (folders). | Automatizar pipelines separados (CI/CD). |
| A.8.32 Change Management | P | Processo informal via Git. | Completar `CHANGE_MANAGEMENT.md` com fluxo de aprovação. |
| A.8.33 Test Data | I | Usa dados sintéticos (PractRand). | Documentar garantia de não uso de PII. |
| A.8.34 Technical Compliance Review | P | Sem auditorias de configuração. | Agendar revisão semestral. |

---

## 5. Plano de Ação Consolidado
1. **RACI + Gestão de Acesso (A.5.2, A.5.18, A.6.5):** finalizar `RACI_SGSI.md`, publicar `ACCESS_REVIEW.md` e executar primeira revisão até 31/jan/2026.
2. **Inventário e Classificação (A.5.9–A.5.13):** atualizar `ASSET_INVENTORY.md` com categoria, dono, criticidade e link para controles de classificação (prazo 15/jan/2026).
3. **Policies de Uso/Endpoint/Remote (A.5.10, A.6.7, A.7.x, A.8.1):** criar pacote “Uso Aceitável + Remote Work + Endpoint Baseline”.
4. **Gestão de Mudanças e Vulnerabilidades (A.5.32, A.8.8, A.8.32):** completar `CHANGE_MANAGEMENT.md`, integrar `bandit` + `pip-audit` no CI e registrar aprovações no MPC-N (fev/2026).
5. **Incidentes e Evidências (A.5.24–A.5.28):** rodar simulado, coletar lições aprendidas e publicar `EVIDENCE_HANDLING.md`.
6. **BCP e Continuidade (A.5.29–A.5.30):** elaborar BIA simplificada e definir RTO/RPO para módulos críticos (mar/2026).
7. **Controles Físicos & Fornecedores (A.7, A.5.19–A.5.22):** montar checklist para operadores e futuros contratos.

## 6. Referências Cruzadas
- `docs/policies/INCIDENT_RESPONSE.md`
- `docs/policies/RACI_SGSI.md`
- `docs/policies/ASSET_INVENTORY.md`
- `docs/policies/CHANGE_MANAGEMENT.md`
- `docs/business/EXECUTIVE_SUMMARY_A16Z.md`
- `bundle_due_diligence.py` e `README_DUE_DILIGENCE.md`
- `mpcn_state.json` (registro append-only)

> Esta versão substitui a tabela simplificada anterior e serve como base audit-ready. Atualizações serão registradas via MPC-N e versão 0.3 incluirá métricas de maturidade por controle.
