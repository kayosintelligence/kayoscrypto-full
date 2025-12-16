# Playbook: Execução PractRand 64 TiB (industrial)

Objetivo
- Orquestrar uma campanha PractRand de 64 TiB sobre o stream `sator_6d_master` com auditoria MPC‑N, checkpoints, e resiliência.

Pré-requisitos
- Servidor com armazenamento ≥ 70 TiB disponível (se persistir o stream) ou espaço suficiente para logs (1–5 GiB) se o stream for apenas consumido por `RNG_test`.
- I/O sustentado recomendado: 150 MiB/s (margem para overhead). Observado: 114 MiB/s.
- Python virtualenv com `kayoscrypto` e `kayoscrypto.mpcn` funcionais (.venv).
- `RNG_test` (PractRand) disponível no PATH.
- Acesso ao diretório `artifacts/sator_6d_master/` e permissão de escrita.

Checklist pré-execução
1. Verificar integridade do ambiente: `python -c "import kayoscrypto.mpcn.context"`.
2. Garantir que as salts por etapa serão persistidas em `artifacts/sator_6d_master/staged_run/`.
3. Reservar janela de operação: 8 dias contíguos (inclui margem de recuperação).
4. Criar snapshot/backup do sistema crítico (opcional). 

Comandos úteis (exemplo de execução controlada)
```bash
# iniciar um estágio (exemplo 512GiB):
PYTHONPATH=src .venv/bin/python scripts/run_practrand_staged.sh --start-stage 512G

# verificar watcher (logs locais):
tail -n +1 artifacts/sator_6d_master/staged_run/checkpoints.log -f

# publicar manual heartbeat MPC-N (se guard alertar):
PYTHONPATH=src .venv/bin/python -c "from kayoscrypto.mpcn.context import log_event; log_event(actor='run_practrand_whitened', action='heartbeat', details={'intent':'diagnostics.practrand'})"
```

Checkpoints e monitoramento
- Checkpoint padrão: 512 GiB por checkpoint → 128 checkpoints no total.
- Tempo projetado por checkpoint: ~4 598 s (~1 h 16 m 38 s).
- O `scripts/practrand_checkpoint_watcher.py` gera `artifacts/.../checkpoints.log` e pode emitir `diagnostics.practrand:checkpoint` ao detectar novos checkpoints. Instalar a unit systemd fornecida para execução contínua.

Incidentes e runbook de resposta rápida
1. Se `unusual` ou `FAIL` forem detectados no log do PractRand:
  - Pausar a orquestração: `systemctl stop practrand_runner` (ou matar o PID do runner).
  - Coletar artefatos: copiar o `practrand_*` log, `salt_<SIZE>.hex` e `staged_run_state.json` para `artifacts/incident_<ts>/`.
  - Emitir evento MPC‑N: `diagnostics.practrand:checkpoint` com o contexto do log e o SHA256 do arquivo de log.
  - Rodar regressão `-tf 2` em modo de teste por 64G para verificar reprodutibilidade.

Persistência e assinatura de artefatos
- Ao terminar a campanha, gerar `SHA256SUMS` para `artifacts/sator_6d_master/staged_run/` e assinar com GPG (`gpg --detach-sign SHA256SUMS`).
- Arquivar: `tar -czf artifacts/archive_practrand_sator_6d_<ts>.tar.gz -C artifacts sator_6d_master` e publicar evento `diagnostics.practrand:archived` com os hashes.

Notas operacionais
- Se não for preciso persistir todo o fluxo, mantenha o padrão stream→PractRand (stdin) para reduzir I/O e espaço.
- Validar a política de retentativa do watcher (systemd) e os limites de logrotate para evitar consumo excessivo de disco.

Contatos e aprovações
- Operador: `kbe` (ajustar no unit file se outro usuário).
- Aprovação operacional necessária antes de iniciar a campanha completa (emitir `diagnostics.practrand:estimate_64T` e obter confirmação).

FIM DO PLAYBOOK
