# MPC-N Event Code Legend
# Sistema de Monitoramento Preditivo Neural - KayosCrypto v6.0 QUANTUM
# Legenda completa dos códigos de evento para rastreabilidade

## Estrutura dos Eventos
Todos os eventos seguem o formato: `categoria:ação`

## Categorias Principais

### monitoring
Eventos relacionados ao sistema de monitoramento MPC-N
- `monitoring:start` - Início do monitoramento contínuo
- `monitoring:stop` - Parada do monitoramento
- `monitoring:heartbeat` - Pulsação periódica do sistema
- `monitoring:status_check` - Verificação de status do sistema

### alert
Alertas e notificações críticas
- `alert:health_low` - Saúde do sistema abaixo do limite
- `alert:security_violation` - Violação de segurança detectada
- `alert:performance_degradation` - Degradação de performance
- `alert:resource_exhaustion` - Esgotamento de recursos

### crypto
Operações criptográficas
- `crypto:encrypt_start` - Início de operação de criptografia
- `crypto:encrypt_complete` - Criptografia concluída com sucesso
- `crypto:decrypt_start` - Início de operação de descriptografia
- `crypto:decrypt_complete` - Descriptografia concluída com sucesso
- `crypto:key_derivation` - Derivação de chave executada
- `crypto:avalanche_test` - Teste de avalanche realizado

### test
Execução de testes
- `test:suite_start` - Início de suíte de testes
- `test:suite_complete` - Suíte de testes concluída
- `test:security_start` - Início de testes de segurança
- `test:security_complete` - Testes de segurança concluídos
- `test:performance_start` - Início de testes de performance
- `test:performance_complete` - Testes de performance concluídos

### quantum
Operações relacionadas à resistência quântica
- `quantum:resistance_check` - Verificação de resistência quântica
- `quantum:complexity_calculation` - Cálculo de complexidade quântica
- `quantum:simulation_start` - Início de simulação quântica
- `quantum:simulation_complete` - Simulação quântica concluída

### gpu
Operações de aceleração GPU
- `gpu:acceleration_start` - Início de aceleração GPU
- `gpu:acceleration_complete` - Aceleração GPU concluída
- `gpu:memory_check` - Verificação de memória GPU
- `gpu:kernel_execution` - Execução de kernel GPU

### fips
Operações de certificação FIPS
- `fips:certification_start` - Início de processo de certificação
- `fips:certification_complete` - Certificação concluída
- `fips:module_check` - Verificação de módulo FIPS
- `fips:compliance_test` - Teste de conformidade FIPS

### mpcn_guard
Sistema de guarda MPC-N
- `mpcn_guard:check` - Verificação de guarda executada
- `mpcn_guard:alert` - Alerta de guarda acionado
- `mpcn_guard:block` - Operação bloqueada por guarda

### system
Eventos gerais do sistema
- `system:startup` - Inicialização do sistema
- `system:shutdown` - Desligamento do sistema
- `system:config_update` - Atualização de configuração
- `system:dependency_check` - Verificação de dependências

## Detalhes dos Eventos

### Formato dos Detalhes
Cada evento pode incluir detalhes adicionais no campo `details`:
- `timestamp`: Data/hora UTC em ISO format
- `actor`: Componente que gerou o evento
- `action`: Código da ação
- `details`: Dicionário com informações específicas

### Exemplo de Evento
```json
{
  "timestamp": "2025-12-01T18:00:00Z",
  "actor": "crypto_engine",
  "action": "crypto:encrypt_complete",
  "details": {
    "data_size": 1048576,
    "algorithm": "KayosCrypto v6.0",
    "throughput_mbs": 1.85,
    "execution_time": 0.567
  }
}
```

### Interpretação dos Códigos
- **monitoring**: Sistema operacional MPC-N
- **alert**: Condições que requerem atenção
- **crypto**: Operações de criptografia/descriptografia
- **test**: Validação e testes
- **quantum**: Análise de resistência quântica
- **gpu**: Aceleração computacional
- **fips**: Conformidade regulamentar
- **mpcn_guard**: Controle de segurança
- **system**: Operações gerais

### Manutenção da Legenda
Esta legenda deve ser atualizada sempre que novos códigos de evento forem adicionados ao sistema MPC-N. Cada novo código deve ser documentado aqui para manter a rastreabilidade completa.