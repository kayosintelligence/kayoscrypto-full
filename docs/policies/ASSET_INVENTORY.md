# Inventário de Ativos de Informação — KayosCrypto SGSI

| Ativo | Tipo | Localização / Referência | Classificação | Observações |
|-------|------|-------------------------|---------------|-------------|
| Código-fonte KayosCrypto | Informação Confidencial | `src/`, `core/`, `cli/`, repositório Git | Confidencial | Inclui algoritmos Spine/Ribs; protegido por controle de versão. |
| Scripts diagnósticos `run_*` | Informação Confidencial | `scripts/diagnostics/`, `tools/` | Confidencial | Executam suites estatísticas; requerem MPC-N. |
| Guardião MPC-N (estado) | Informação Confidencial | `mpcn_state.json` | Confidencial | Registro completo de eventos, base para auditorias. |
| Logs PractRand | Informação Sensível Técnica | `practrand_logs/*.log` | Restrito | Evidenciam qualidade da entropia; associados aos eventos MPC-N. |
| Logs Dieharder/TestU01/ENT/rngtest | Informação Sensível Técnica | `logs/`, `../TESTE_COMPARATIVO/sts-2_1_2/reports/` | Restrito | Incluem p-values e observações; manutenção cronológica. |
| Documentos Diagnósticos | Informação Interna | `docs/diagnostics/*.md` | Interno | Registro narrativo (DIAGNOSTICS, PRE_AUDIT). |
| Segurança / Regulatórios | Informação Confidencial | `docs/fips/SECURITY_POLICY_v0.md`, `docs/cc/THREAT_MODEL_FISHBONE.md`, `docs/policies/SOA_ISO27001_v0.md` | Confidencial | Documentos submetidos a auditoria. |
| Procedimento de incidentes | Informação Interna | `docs/policies/INCIDENT_RESPONSE.md` | Interno | Orienta resposta e pós-incidente. |
| Artefatos PQC | Informação Sensível Técnica | `docs/PQC_VALIDATION_REPORT_2025-11-24.md`, `reports/pqc_benchmark_*.json` | Confidencial | Incluem métricas pós-quânticas. |
| Geração de entropia MatutoRegulatorio | Recurso Técnico | `tools/generate_entropy_stream.py`, `kayos_entropy_stream.bin` | Restrito | Base dos testes raw; deve ser controlado. |
| Pipelines de build/teste | Recurso Operacional | `Makefile`, `check_progress.sh`, `make test-*` | Interno | Garantem repetibilidade. |

## Processo de Manutenção
1. Inventário revisado a cada ciclo de pré-auditoria ou mudança arquitetural.
2. Atualizações devem ser registradas no MPC-N (`actor='pre_audit', action='asset_inventory:update'`).
3. Novos ativos devem indicar classificação (Público, Interno, Restrito, Confidencial) e responsável.
