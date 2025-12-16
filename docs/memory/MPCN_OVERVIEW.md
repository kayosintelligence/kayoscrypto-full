# MPC-N (Memória Persistente Cognitiva – Neurônios)

## Objetivo
Estabelecer uma “memória viva” obrigatória para qualquer agente de IA que opere no KayosCrypto. A MPC-N funciona como camada zero do pipeline: antes de executar comandos, o agente consulta o contexto, registra intenções e somente então continua. Isso garante alinhamento contínuo com a filosofia KAIOS, evita perda de contexto e cria uma trilha de auditoria.

## Componentes

| Camada | Descrição | Arquivo |
|--------|-----------|---------|
| **Core** | Modelo de dados + carga/salvamento determinístico | `src/kayoscrypto/mpcn/context.py` |
| **Estado** | Instantâneo atual do conhecimento persistido | `mpcn_state.json` |
| **Hooks** | Funções utilitárias para agentes/scripts | `src/kayoscrypto/mpcn/hooks.py` |
| **Guardião** | Verificação automática de instruções e heartbeat | `src/kayoscrypto/mpcn/guard.py`, `tools/mpcn_guard.py` |
| **Checkpoints** | Referências cruzadas para tarefas/documentos | `docs/checkpoints/*.md` |

## Fluxo Operacional
1. **load_context()** – todo entry point chama `mpcn.load_context()` para obter instruções pendentes, tarefas críticas e histórico recente.
2. **apply_behavior()** – o agente adapta seu comportamento ao `context.mode` (ex.: segurança, performance, auditoria).
3. **log_event()** – após cada ação relevante, o agente registra o evento com timestamp, ator e detalhes; o contexto é salvo imediatamente.
4. **snapshot()** – checkpoints (como PractRand/Dieharder) continuam sendo produzidos, mas agora referenciados dentro do MPC-N.

## Tipos de Registro
- **instructions**: blocos de orientações vivas (ex.: “manter GLASSÉ ≥32 GB”).
- **tasks**: TODOs persistentes com status (`pending`, `in_progress`, `done`).
- **history**: lista de eventos (timestamp ISO, ator, ação, payload compacto) para auditoria.
- **tags**: metadados de regime (ex.: `safety`, `performance`, `philosophy`).

## Exemplo de Uso
```python
from kayoscrypto.mpcn import context

ctx = context.load_context()
context.log_event(actor="dieharder_pipeline", action="start", details={
 "script": "run_dieharder_whitened.sh",
 "source": "kayos_entropy_stream.bin",
})
# ... executar tarefa ...
context.log_event(actor="dieharder_pipeline", action="complete", details={
 "status": "passed",
 "log": "logs/dieharder_whitened_20251122_155703.log",
})
```

### Logging automático
Para pipelines que já usam o módulo `logging`, basta acoplar o novo handler MPC-N para replicar cada registro como evento persistente:

```python
import logging
from kayoscrypto.mpcn import attach_mpcn_logging, detach_mpcn_logging

logger = logging.getLogger("diagnostics")
handler = attach_mpcn_logging(actor="diagnostics.pipeline", logger=logger)
try:
 logger.info("Extraindo chunk", extra={"mpcn_details": {"chunk": 12}})
finally:
 detach_mpcn_logging(handler, logger=logger)
```

Cada registro recebe a ação `log:<level>` por padrão (pode ser sobrescrita via `extra={"mpcn_action": "custom"}`) e aceita detalhes adicionais no dicionário `mpcn_details`.

## Guardião MPC-N
- **Objetivo**: impedir que pipelines rodem com neurônios desatualizados ou sem instruções críticas (evita o “mal de Parkinson” citado pelo usuário).
- **API**: `enforce_guardian()` realiza todas as checagens (tempo desde último evento, instruções obrigatórias, heartbeat).
- **CLI**: `tools/mpcn_guard.py` torna obrigatória a verificação em shell scripts.

### Execução rápida
```bash
python tools/mpcn_guard.py --max-inactive-minutes 45 --require GLASSE-32GB \
 --require BATTERY-DIEHARDER --require BATTERY-BIGCRUSH --require LANG-PT-BR
```

### Integração em testes/pipelines
```python
from kayoscrypto.mpcn.guard import enforce_guardian

enforce_guardian(
 actor="pytest_external_diagnostics",
 intent="tests.validation.external",
 required_instruction_ids=["GLASSE-32GB", "BATTERY-DIEHARDER", "BATTERY-BIGCRUSH", "LANG-PT-BR"],
 max_inactive_minutes=60,
)
```

Se o guardião detectar erro, os testes são bloqueados e o log registra `mpcn_guard:check` + detalhes.

## Roadmap
1. **Hooks obrigatórios** – integrar `load_context()` + `log_event()` em todos os scripts críticos (PractRand, Dieharder, BigCrush, CLI).
2. **Validação** – adicionar teste automatizado garantindo que `mpcn_state.json` contenha instruções mínimas antes do pipeline executar.
3. **Visualização** – expor o estado da MPC-N no dashboard KayosCrypto Suite.
4. **Assinatura** – vincular cada checkpoint a um hash MPC-N para rastrear quem/como atualizou.

## Boas Práticas
- Nunca sobrescreva `mpcn_state.json` manualmente; use as funções de contexto para preservar integridade.
- Registre eventos sintéticos somente quando representarem ações reais (evita ruído na auditoria).
- Sempre atualize os campos `last_checkpoint` e `active_tasks` após concluir um marco.

> A MPC-N é o “neurônio espelho” da IA: toda ação fica refletida nela, garantindo memória longa e comportamento coerente mesmo em projetos complexos como o KayosCrypto.
