# Matriz RACI — SGSI KayosCrypto (Pré-Auditoria)

| Atividade / Controle | Responsável (R) | Aprovador (A) | Consultado (C) | Informado (I) |
|----------------------|-----------------|---------------|----------------|----------------|
| Execução de suites diagnósticas (PractRand, TestU01, Dieharder, ENT, rngtest) | Operador Técnico | Guardião MPC-N | Auditor Interno | Diretoria Técnica |
| Atualização de documentos críticos (`DIAGNOSTICS`, Security Policy, Threat Model, SoA) | Operador Técnico | Auditor Interno | Guardião MPC-N | Diretoria Técnica |
| Manutenção do guardião MPC-N (scripts, limites de inatividade) | Guardião MPC-N | CTO | Operador Técnico | Auditor Interno |
| Aprovação de releases KayosCrypto | CTO | CEO | Auditor Interno | Guardião MPC-N, Operador |
| Resposta a incidentes (INCIDENT_RESPONSE) | Operador Técnico | Auditor Interno | Guardião MPC-N | Diretoria Técnica |
| Gestão de mudanças (Change Management) | Operador Técnico | Auditor Interno | Guardião MPC-N, CTO | Diretoria Técnica |
| Inventário e classificação de ativos | Auditor Interno | CTO | Operador Técnico | Diretoria Técnica |
| Revisão periódica de compliance (SoA, PRE_AUDIT) | Auditor Interno | CTO | Guardião MPC-N | Diretoria Técnica |

Notas:
- Operador Técnico: equipe que executa os scripts `run_*` e mantém o repositório.
- Guardião MPC-N: responsável pelo monitoramento automático e integridade dos eventos.
- Auditor Interno: função que revisa docs, confirma execuções e prepara material para auditorias externas.
- CTO/CEO/Diretoria Técnica: patrocinadores executivos do processo.
