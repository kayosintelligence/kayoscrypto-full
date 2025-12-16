# Controles de Acesso - ISO 27001
# KayosCrypto Access Control Framework
# Versão: 1.0
# Data: 29 de novembro de 2025

## 1. VISÃO GERAL

Este documento define os controles de acesso da KayosCrypto, implementando o princípio do menor privilégio e garantindo que usuários tenham acesso apenas aos recursos necessários para suas funções.

## 2. PRINCÍPIOS DE CONTROLE DE ACESSO

### 2.1 Princípio do Menor Privilégio
Usuários recebem apenas as permissões mínimas necessárias para executar suas tarefas.

### 2.2 Segregação de Funções
Funções conflitantes são separadas para prevenir fraudes e erros.

### 2.3 Controle de Acesso Baseado em Funções (RBAC)
Permissões são atribuídas com base em funções de negócio, não individualmente.

### 2.4 Autenticação Forte
Uso de múltiplos fatores de autenticação para acesso sensível.

## 3. GESTÃO DE ACESSO

### 3.1 Processo de Provisionamento
1. **Solicitação**: Usuário solicita acesso via sistema ITSM
2. **Aprovação**: Gerente aprova baseado na necessidade de negócio
3. **Provisionamento**: Equipe de TI implementa acesso
4. **Confirmação**: Usuário confirma funcionamento

### 3.2 Processo de Desprovisionamento
1. **Trigger**: Saída do funcionário ou mudança de função
2. **Imediata**: Desativação de contas em até 1 hora
3. **Completa**: Remoção total em até 24 horas
4. **Auditoria**: Verificação de remoção completa

### 3.3 Revisão de Acesso
- **Trimestral**: Revisão automática de acessos inativos
- **Semestral**: Revisão gerencial de todos os acessos
- **Imediata**: Após incidentes de segurança

## 4. CONTROLES TÉCNICOS

### 4.1 Autenticação

#### Autenticação Multifator (MFA)
- **Obrigatório para**: Acesso administrativo, sistemas críticos
- **Métodos Aceitos**: App autenticador, YubiKey, SMS
- **Fallback**: Códigos de recuperação seguros

#### Gestão de Senhas
- **Comprimento Mínimo**: 12 caracteres
- **Complexidade**: Maiúscula, minúscula, número, símbolo
- **Histórico**: Últimas 10 senhas não reutilizáveis
- **Expiração**: 90 dias para contas normais, 30 dias para admin

### 4.2 Autorização

#### Matriz de Controle de Acesso

| Função | Sistema | Nível de Acesso | Aprovação |
|--------|---------|-----------------|-----------|
| Desenvolvedor | Repositório Git | Read/Write | Tech Lead |
| Desenvolvedor | Servidores Dev | Admin | DevOps Lead |
| Analista Segurança | SIEM | Read | CISO |
| Analista Segurança | Firewalls | Read/Write | CISO |
| DBA | Bancos de Dados | Admin | CTO |
| Suporte | Sistema Helpdesk | Read/Write | Manager |
| Usuário Final | Aplicação Web | Read | Auto-aprovado |

#### Controle de Acesso a Rede
- **VPN**: Obrigatório para acesso remoto
- **Segmentação**: Redes separadas por função
- **Zero Trust**: Verificação contínua de confiança

### 4.3 Monitoramento
- **Logs de Acesso**: Todos os acessos registrados
- **Alertas**: Tentativas de acesso suspeitas
- **Relatórios**: Acesso por usuário gerados mensalmente

## 5. CONTROLES FÍSICOS

### 5.1 Acesso a Instalações
- **Crachá Eletrônico**: RFID com foto e dados
- **Controle de Portas**: Acesso baseado em horário e função
- **Zonas Seguras**: Servidores em salas dedicadas

### 5.2 Acesso a Equipamentos
- **Lockers**: Equipamentos portáteis trancados
- **Etiquetas**: Marcação de propriedade
- **Inventário**: Controle rigoroso de ativos

## 6. CONTROLES ADMINISTRATIVOS

### 6.1 Políticas
- **Política de Acesso Remoto**: VPN obrigatória
- **Política de Dispositivos**: BYOD proibido para dados sensíveis
- **Política de Visitantes**: Acompanhamento obrigatório

### 6.2 Procedimentos
- **Procedimento de Emergência**: Acesso temporário justificado
- **Procedimento de Exceção**: Aprovação especial documentada
- **Procedimento de Recuperação**: Restauração de acesso perdido

### 6.3 Treinamentos
- **Conscientização**: Uso adequado de credenciais
- **Phishing**: Reconhecimento de tentativas
- **Responsabilidades**: Uso ético de acesso

## 7. GESTÃO DE CONTAS PRIVILEGIADAS

### 7.1 Contas Administrativas
- **Justificativa**: Documentada e aprovada
- **Monitoramento**: Todos os comandos logados
- **Acesso Temporário**: Elevação just-in-time
- **Revisão**: Semestral obrigatória

### 7.2 Contas de Serviço
- **Credenciais**: Armazenadas em cofre digital
- **Rotação**: Automática trimestral
- **Monitoramento**: Alertas em uso suspeito

## 8. GESTÃO DE TERCEIROS

### 8.1 Fornecedores
- **Avaliação**: Due diligence de segurança
- **Contratos**: Cláusulas de segurança específicas
- **Monitoramento**: Acesso revogado ao fim do contrato

### 8.2 Consultores
- **Acesso Temporário**: Limitado ao projeto
- **Supervisão**: Trabalho acompanhado
- **Auditoria**: Logs de acesso revisados

## 9. MONITORAMENTO E AUDITORIA

### 9.1 Métricas de Controle de Acesso
- **Taxa de Sucesso de MFA**: > 99.5%
- **Tentativas de Acesso Falhidas**: Monitoradas
- **Contas Inativas**: Removidas automaticamente
- **Revisões de Acesso**: 100% completadas

### 9.2 Auditorias
- **Interna**: Trimestral
- **Externa**: Anual
- **Surpresa**: Aleatória

### 9.3 Relatórios
- **Semanal**: Tentativas de acesso suspeitas
- **Mensal**: Estatísticas de acesso por departamento
- **Trimestral**: Relatório de conformidade

## 10. PLANO DE CONTINGÊNCIA

### 10.1 Recuperação de Acesso Perdido
1. Verificação de identidade
2. Aprovação gerencial
3. Provisionamento temporário
4. Restauração completa

### 10.2 Comprometimento de Credenciais
1. Detecção automática
2. Bloqueio imediato
3. Investigação forense
4. Notificação aos afetados

## 11. REVISÃO E MELHORIA

Esta estrutura de controle de acesso será revisada:
- Anualmente como parte da auditoria ISO 27001
- Após incidentes de segurança relacionados
- Quando mudanças significativas na organização

## 12. APROVAÇÃO

**Aprovado por**: CISO KayosCrypto
**Data**: 29 de novembro de 2025
**Próxima Revisão**: 29 de novembro de 2026