# Procedimento de Resposta a Incidentes — KayosCrypto / MPC-N

## 1. Objetivo
Fornecer um fluxo operacional para lidar com incidentes que afetem o módulo KayosCryptoUltimate, suas campanhas estatísticas ou o guardião MPC-N, garantindo rastreabilidade completa e retorno rápido ao estado seguro.

## 2. Escopo
- Execuções de suites (PractRand, Dieharder, TestU01, ENT, rngtest, PQC).
- Documentação e artefatos de pré-auditoria (Security Policy, Threat Model, SoA).
- Infraestrutura de geração de entropia (MatutoRegulatorio) e pipelines `run_*`.

## 3. Papéis
| Papel | Responsabilidades |
|-------|-------------------|
| Operador | Detectar incidentes, acionar MPC-N, executar passos de contenção e coleta de logs. |
| Guardião (MPC-N) | Registrar automaticamente eventos `error/failed`, monitorar inatividade, gerar alertas. |
| Auditor Interno | Revisar incidentes, validar correções, atualizar documentação (DIAGNOSTICS, PRE_AUDIT). |

## 4. Fluxo de Resposta
1. **Detecção**: qualquer falha (ex.: queda de energia, Ctrl+C involuntário, alerta PractRand) deve ser registrada via `log_event(actor=..., action='diagnostics.*:error', details={...})` imediatamente.
2. **Classificação**:
   - *Operacional*: interrupção não maliciosa (energia, pipeline). → Reexecutar após verificar integridade.
   - *Segurança*: suspeita de manipulação, vazamento ou comportamento estatístico persistente. → Escalar para auditor.
3. **Contenção**:
   - Pausar novas execuções.
   - Salvar logs (`practrand_logs/...`, `terminal_output`) e estado do gerador.
   - Atualizar MPC-N com `action='heartbeat'` indicando “incident in progress”.
4. **Erradicação/Correção**:
   - Documentar causa raiz (`docs/diagnostics/...` ou issue tracker interno).
   - Implementar fix (ex.: ajustar scripts, substituir arquivo corrompido, revisar chave).
5. **Recuperação**:
   - Reexecutar a suíte afetada com novo log.
   - Validar que as estatísticas retornaram ao baseline (ex.: 0 anomalias em `practrand_whitened`).
6. **Pós-Incidente**:
   - Atualizar `INCIDENT_RESPONSE.md` se o processo mudou.
   - Referenciar o incidente no SoA (controles A.14.1/14.3) e no PRE_AUDIT.

## 5. Comunicação
- **Interna**: via MPC-N + registro em `docs/diagnostics/...`.
- **Externa**: somente após revisão do auditor; preparar resumo com: descrição, impacto, ações corretivas, logs associados.

## 6. Integrações Futuras
- Automatizar criação de tickets quando `log_event(... status='failed')` ocorrer >2 vezes.
- Assinar criptograficamente os logs de incidente para fornecer prova de integridade.
- Integrar com monitoramento em tempo real (ex.: Slack, PagerDuty) para alertas imediatos.
