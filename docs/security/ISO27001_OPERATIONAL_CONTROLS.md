# Controles Operacionais - ISO 27001
# KayosCrypto Operational Security Controls
# Versão: 1.0
# Data: 29 de novembro de 2025

## 1. VISÃO GERAL

Este documento define os controles operacionais da KayosCrypto para garantir a segurança contínua das operações de TI, incluindo gestão de mudanças, capacidade, proteção contra malware e continuidade de operações.

## 2. GESTÃO DE MUDANÇAS

### 2.1 Processo de Gestão de Mudanças
1. **Registro**: Solicitação documentada via sistema ITSM
2. **Avaliação**: Impacto técnico e de segurança analisado
3. **Aprovação**: Comitê de mudanças aprova baseado em risco
4. **Implementação**: Em janela de manutenção ou rollback plan
5. **Validação**: Testes pós-implementação
6. **Fechamento**: Documentação e lições aprendidas

### 2.2 Classificação de Mudanças
- **Padrão**: Mudanças rotineiras pré-aprovadas
- **Normal**: Mudanças significativas com avaliação completa
- **Emergencial**: Mudanças críticas sem aprovação prévia

### 2.3 Comitê de Gestão de Mudanças
- **Composição**: Representantes de TI, Segurança, Negócio
- **Frequência**: Semanal para mudanças normais
- **Poder de Decisão**: Aprovação até nível de risco médio

## 3. GESTÃO DE CAPACIDADE

### 3.1 Monitoramento de Capacidade
- **CPU**: Alerta em > 80% utilização média
- **Memória**: Monitoramento contínuo de vazamentos
- **Disco**: Alerta em < 20% espaço livre
- **Rede**: Monitoramento de latência e throughput

### 3.2 Planejamento de Capacidade
- **Curto Prazo**: Próximos 3 meses baseado em tendências
- **Médio Prazo**: Próximos 12 meses baseado em roadmap
- **Longo Prazo**: Estratégia de arquitetura

### 3.3 Auto-scaling
- **Horizontal**: Adição automática de instâncias
- **Vertical**: Upgrade automático de recursos
- **Limites**: Máximos definidos para controle de custos

## 4. PROTEÇÃO CONTRA MALWARE

### 4.1 Endpoint Protection
- **Antivírus**: Atualizado automaticamente
- **Anti-malware**: Proteção em tempo real
- **Endpoint Detection**: Comportamental avançado
- **Response**: Isolamento automático de ameaças

### 4.2 Proteção de Email
- **Anti-spam**: Filtragem baseada em IA
- **Anti-phishing**: Detecção de URLs maliciosas
- **Sandboxing**: Análise de anexos suspeitos
- **DLP**: Prevenção de vazamento de dados

### 4.3 Proteção de Web
- **Web Gateway**: Filtragem de conteúdo
- **SSL Inspection**: Análise de tráfego criptografado
- **Zero-day Protection**: Comportamental

### 4.4 Resposta a Malware
1. **Detecção**: Alertas automáticos
2. **Isolamento**: Segmentação imediata
3. **Análise**: Investigação forense
4. **Remediação**: Limpeza e recuperação
5. **Prevenção**: Atualização de assinaturas

## 5. GESTÃO DE BACKUP E RECUPERAÇÃO

### 5.1 Estratégia 3-2-1
- **3 Cópias**: Dados originais + 2 backups
- **2 Mídias Diferentes**: Disco + nuvem
- **1 Off-site**: Localização geográfica separada

### 5.2 Tipos de Backup
- **Completo**: Semanal, retenção 1 ano
- **Incremental**: Diariamente, retenção 30 dias
- **Transacional**: A cada 15 minutos para dados críticos

### 5.3 Testes de Recuperação
- **Mensal**: Restauração de arquivos individuais
- **Trimestral**: Recuperação completa de sistemas
- **Anual**: Simulação de desastre completo

### 5.4 Recovery Time Objectives (RTO)
- **Dados Críticos**: 4 horas
- **Sistemas Essenciais**: 8 horas
- **Sistemas Suporte**: 24 horas

### 5.5 Recovery Point Objectives (RPO)
- **Dados Financeiros**: 15 minutos
- **Dados Operacionais**: 1 hora
- **Dados Arquivados**: 24 horas

## 6. GESTÃO DE LOGS E MONITORAMENTO

### 6.1 Coleta de Logs
- **Sistemas**: Todos os servidores e aplicações
- **Rede**: Firewalls, switches, load balancers
- **Segurança**: Autenticações, acessos, mudanças
- **Aplicações**: Eventos de negócio e erro

### 6.2 Centralização
- **SIEM**: Agregação e correlação de logs
- **Armazenamento**: Retenção de 1 ano para logs operacionais
- **Backup**: Logs críticos retidos por 7 anos

### 6.3 Análise e Alertas
- **Tempo Real**: Alertas para eventos críticos
- **Diária**: Revisão de logs de segurança
- **Semanal**: Relatórios de tendências
- **Mensal**: Análise de conformidade

### 6.4 Correlação de Eventos
- **Regras de Correlação**: Padrões de ataque identificados
- **Machine Learning**: Detecção de anomalias
- **Threat Hunting**: Investigação proativa

## 7. GESTÃO DE VULNERABILIDADES

### 7.1 Scanning Contínuo
- **Vulnerabilidades**: Semanal em todos os sistemas
- **Configurações**: Verificação diária de conformidade
- **Código**: Análise estática em CI/CD

### 7.2 Priorização
- **CVSS Score**: Classificação por severidade
- **Exploitabilidade**: Disponibilidade de exploits
- **Impacto no Negócio**: Efeito nas operações

### 7.3 Remediação
- **Críticas**: 24 horas para correção
- **Altas**: 7 dias para correção
- **Médias**: 30 dias para correção
- **Baixas**: No próximo ciclo de manutenção

## 8. GESTÃO DE TERCEIROS

### 8.1 Avaliação de Fornecedores
- **Segurança**: Questionário de segurança obrigatório
- **Conformidade**: Verificação de certificações
- **Referências**: Contato com clientes existentes

### 8.2 Contratos
- **Cláusulas de Segurança**: Requisitos específicos
- **Direito de Auditoria**: Acesso para verificação
- **Responsabilidades**: Definição clara de obrigações

### 8.3 Monitoramento
- **Performance**: Métricas de SLA de segurança
- **Incidentes**: Notificação obrigatória
- **Auditorias**: Anuais ou quando necessário

## 9. CONTINUIDADE OPERACIONAL

### 9.1 Plano de Continuidade
- **Análise de Impacto**: Identificação de processos críticos
- **Estratégias**: Alternativas para continuidade
- **Planos de Recuperação**: Procedimentos detalhados

### 9.2 Testes de Continuidade
- **Simulação**: Exercícios de mesa trimestrais
- **Testes Funcionais**: Semestral
- **Testes Completos**: Anual

### 9.3 Comunicação
- **Interna**: Equipes notificadas automaticamente
- **Externa**: Clientes informados conforme necessário
- **Stakeholders**: Atualizações regulares durante incidentes

## 10. MÉTRICAS E RELATÓRIOS

### 10.1 KPIs Operacionais
- **Disponibilidade**: > 99.9% para sistemas críticos
- **Tempo Médio de Resolução**: < 4 horas para incidentes
- **Taxa de Detecção**: > 95% de ameaças
- **Tempo de Backup**: < 2 horas para dados críticos

### 10.2 Relatórios
- **Diário**: Status operacional e alertas
- **Semanal**: Métricas de segurança e performance
- **Mensal**: Relatório executivo de operações
- **Trimestral**: Análise de tendências e melhorias

## 11. REVISÃO E MELHORIA

Os controles operacionais serão revisados:
- Após incidentes operacionais significativos
- Com base em resultados de auditorias
- Quando mudanças na arquitetura ou processos
- Anualmente como parte da certificação ISO 27001

## 12. APROVAÇÃO

**Aprovado por**: CTO KayosCrypto
**Data**: 29 de novembro de 2025
**Próxima Revisão**: 29 de novembro de 2026