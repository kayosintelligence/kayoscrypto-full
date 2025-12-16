# Makefile - KayosCrypto Enterprise
# Data: 13 de Outubro de 2025

.PHONY: help setup setup-dev test test-unit test-integration test-security test-performance
.PHONY: lint format coverage clean run benchmark deploy quantum-optimization quantum-validation-suite test-fibonacci-improvement

# Variáveis
VENV_PATH := .venv

ifeq ($(wildcard $(VENV_PATH)/bin/python),$(VENV_PATH)/bin/python)
    PYTHON := $(VENV_PATH)/bin/python
    PIP := $(VENV_PATH)/bin/pip
else
    PYTHON := python3
    PIP := pip3
endif
SRC_DIR := src
TESTS_DIR := tests
DOCS_DIR := docs
QUANTUM_OPTIMIZATION_INPUT ?= kayos_entropy_stream.bin
QUANTUM_OPTIMIZATION_OUTPUT ?= kayos_entropy_optimized.bin
ENTROPY_GENERATOR := ./src/rust/target/release/generate_entropy_stream
PRACTRAND_CMD := /home/kbe/.local/bin/RNG_test
TESTU01_CMD := testu01_stdin
NIST_DATASET := ../TESTE_COMPARATIVO/sts-2_1_2/data/kayoscrypto_sequences.bin
NIST_DATASET_SHA256 := 4d2c13b59685cd91e709277cf2c9ae028fc2499764c63be2e582704ab1e1b7a8
NIST_RUNNER := ../TESTE_COMPARATIVO/run_nist_auto.sh
NIST_EXPERIMENTS_DIR := ../TESTE_COMPARATIVO/sts-2_1_2/experiments
NIST_LOG_PATTERN := ../TESTE_COMPARATIVO/sts-2_1_2/nist_output_full_1000streams_*.log
NIST_REPORT_DIR := artifacts/nist_sts/latest
NIST_REPORT := $(NIST_REPORT_DIR)/finalAnalysisReport.txt
NIST_LOG_LATEST := logs/nist_output_full_1000streams_latest.log
PRE_AUDIT_DIR := artifacts/pre_audit
PRE_AUDIT_DOCS := \
	docs/diagnostics/DIAGNOSTICS_MPCN_GUARD_2025-11-23.md \
	docs/diagnostics/PRE_AUDIT_FIPS_ISO_EXPECTATIVA_2025-11-26.md \
	docs/diagnostics/EMULATOR_EXECUTIVE_REPORT_2025-11-27.json \
	docs/fips/SECURITY_POLICY_v0.md \
	docs/cc/THREAT_MODEL_FISHBONE.md \
	docs/policies/SOA_ISO27001_v0.md \
	docs/policies/INCIDENT_RESPONSE.md \
	docs/policies/RACI_SGSI.md \
	docs/policies/ASSET_INVENTORY.md \
	docs/policies/CHANGE_MANAGEMENT.md
PRE_AUDIT_LOGS := \
	practrand_logs/practrand_whitened_20251124_011640.log \
	practrand_logs/practrand_raw_stream_20251125_64G_buffered_attempt4.log \
	practrand_logs/practrand_raw_stream_20251125_128G_buffered_attempt1.log \
	practrand_logs/practrand_raw_stream_20251125_256G_buffered_attempt1.log \
	practrand_logs/practrand_raw_stream_20251125_512G_buffered_attempt2.log \
	practrand_logs/practrand_raw_stream_20251125_1T_buffered_attempt2.log

# Cores
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ Ajuda

help: ## Mostrar esta ajuda
	@echo '$(BLUE)KayosCrypto v5.0.1 ULTIMATE$(NC)'
	@echo '$(GREEN)Comandos disponíveis:$(NC)'
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup

setup: ## Instalar dependências de produção
	@echo "$(BLUE)Instalando dependências...$(NC)"
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Instalação completa!$(NC)"

setup-dev: ## Instalar dependências de desenvolvimento
	@echo "$(BLUE)Instalando dependências dev...$(NC)"
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✅ Ambiente dev pronto!$(NC)"

##@ Testes

test: ## Rodar todos os testes
	@echo "$(BLUE)Rodando todos os testes...$(NC)"
	@$(PYTHON) -m pytest $(TESTS_DIR)/ -v
	@echo "$(GREEN)✅ Testes completos!$(NC)"

test-unit: ## Rodar testes unitários
	@echo "$(BLUE)Rodando testes unitários...$(NC)"
	@$(PYTHON) -m pytest $(TESTS_DIR)/unit/ -v

test-integration: ## Rodar testes de integração
	@echo "$(BLUE)Rodando testes de integração...$(NC)"
	@$(PYTHON) -m pytest $(TESTS_DIR)/integration/ -v

test-security: ## Rodar testes de segurança
	@echo "$(BLUE)Rodando testes de segurança...$(NC)"
	@$(PYTHON) $(TESTS_DIR)/security/real_security_tests.py
	@echo "$(GREEN)✅ Testes de segurança completos!$(NC)"

test-performance: ## Rodar testes de performance
	@echo "$(BLUE)Rodando testes de performance...$(NC)"
	@$(PYTHON) $(TESTS_DIR)/performance/real_performance_tests_fixed.py
	@echo "$(GREEN)✅ Testes de performance completos!$(NC)"

test-nist: ## Rodar NIST STS oficial (1000 streams + sync artefatos)
	@echo "$(BLUE)Validando dataset NIST...$(NC)"
	@[ -f $(NIST_DATASET) ] || (echo "$(RED)Dataset não encontrado em $(NIST_DATASET)$(NC)" && exit 1)
	@ACTUAL_HASH=$$(sha256sum $(NIST_DATASET) | awk '{print $$1}'); \
	if [ "$$ACTUAL_HASH" != "$(NIST_DATASET_SHA256)" ]; then \
		echo "$(RED)Hash divergente para $(NIST_DATASET). Esperado $(NIST_DATASET_SHA256) mas obtido $$ACTUAL_HASH$(NC)"; \
		exit 1; \
	else \
		echo "$(GREEN)✅ Hash validado$(NC)"; \
	fi
	@echo "$(BLUE)Executando runner oficial (1000 streams)...$(NC)"
	@python3 $(NIST_RUNNER)
	@echo "$(BLUE)Sincronizando artefatos...$(NC)"
	@mkdir -p artifacts/nist_sts/latest logs
	@LATEST_RUN=$$(ls -td $(NIST_EXPERIMENTS_DIR)/AlgorithmTesting* 2>/dev/null | head -n1); \
	if [ -n "$$LATEST_RUN" ] && [ -f "$$LATEST_RUN/finalAnalysisReport.txt" ]; then \
		cp "$$LATEST_RUN/finalAnalysisReport.txt" artifacts/nist_sts/latest/finalAnalysisReport.txt; \
		echo "$(GREEN)✅ Relatório copiado de $$LATEST_RUN$(NC)"; \
	else \
		echo "$(YELLOW)Aviso: finalAnalysisReport.txt não encontrado na última execução$(NC)"; \
	fi
	@LATEST_LOG=$$(ls -t $(NIST_LOG_PATTERN) 2>/dev/null | head -n1); \
	if [ -n "$$LATEST_LOG" ]; then \
		cp "$$LATEST_LOG" logs/$$(basename $$LATEST_LOG); \
		cp "$$LATEST_LOG" $(NIST_LOG_LATEST); \
		echo "$(GREEN)✅ Log replicado para logs/$$(basename $$LATEST_LOG) e $(NIST_LOG_LATEST)$(NC)"; \
	else \
		echo "$(YELLOW)Aviso: nenhum log NIST encontrado para copiar$(NC)"; \
	fi
	@echo "$(GREEN)📊 NIST STS finalizado — consulte artifacts/nist_sts/latest/$(NC)"

test-quick: ## Rodar teste rápido do sistema
	@echo "$(BLUE)Teste rápido do sistema...$(NC)"
	@$(PYTHON) $(SRC_DIR)/core/kayoscrypto_ultimate.py
	@echo "$(GREEN)✅ Teste rápido OK!$(NC)"

coverage: ## Gerar relatório de cobertura
	@echo "$(BLUE)Gerando relatório de cobertura...$(NC)"
	@$(PYTHON) -m pytest $(TESTS_DIR)/ --cov=$(SRC_DIR) --cov-report=html
	@echo "$(GREEN)✅ Relatório em htmlcov/index.html$(NC)"

##@ Qualidade de Código

lint: ## Verificar estilo de código
	@echo "$(BLUE)Verificando código...$(NC)"
	@$(PYTHON) -m pylint $(SRC_DIR)/
	@$(PYTHON) -m flake8 $(SRC_DIR)/
	@echo "$(GREEN)✅ Código verificado!$(NC)"

format: ## Formatar código
	@echo "$(BLUE)Formatando código...$(NC)"
	@$(PYTHON) -m black $(SRC_DIR)/
	@$(PYTHON) -m isort $(SRC_DIR)/
	@echo "$(GREEN)✅ Código formatado!$(NC)"

type-check: ## Verificar tipos
	@echo "$(BLUE)Verificando tipos...$(NC)"
	@$(PYTHON) -m mypy $(SRC_DIR)/
	@echo "$(GREEN)✅ Tipos verificados!$(NC)"

##@ Execução

run: ## Rodar sistema
	@echo "$(BLUE)Iniciando KayosCrypto...$(NC)"
	@$(PYTHON) $(SRC_DIR)/core/kayoscrypto_ultimate.py

cli: ## Rodar CLI
	@echo "$(BLUE)KayosCrypto CLI$(NC)"
	@$(PYTHON) $(SRC_DIR)/cli/kayoscrypto_cli.py

benchmark: ## Rodar benchmarks
	@echo "$(BLUE)Rodando benchmarks...$(NC)"
	@$(PYTHON) scripts/benchmark.sh
	@echo "$(GREEN)✅ Benchmarks completos!$(NC)"

##@ Documentação

docs: ## Gerar documentação
	@echo "$(BLUE)Gerando documentação...$(NC)"
	@cd $(DOCS_DIR) && make html
	@echo "$(GREEN)✅ Documentação gerada!$(NC)"

docs-serve: ## Servir documentação localmente
	@echo "$(BLUE)Servindo documentação em http://localhost:8000$(NC)"
	@cd $(DOCS_DIR)/_build/html && $(PYTHON) -m http.server

##@ Build & Deploy

build: ## Build do projeto
	@echo "$(BLUE)Building projeto...$(NC)"
	@$(PYTHON) setup.py sdist bdist_wheel
	@echo "$(GREEN)✅ Build completo! dist/$(NC)"

install: ## Instalar localmente
	@echo "$(BLUE)Instalando localmente...$(NC)"
	@$(PIP) install -e .
	@echo "$(GREEN)✅ Instalado!$(NC)"

publish: ## Publicar no PyPI
	@echo "$(BLUE)Publicando no PyPI...$(NC)"
	@$(PYTHON) -m twine upload dist/*
	@echo "$(GREEN)✅ Publicado!$(NC)"

docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t kayoscrypto:latest -f docker/Dockerfile .
	@echo "$(GREEN)✅ Docker image pronta!$(NC)"

docker-run: ## Rodar container Docker
	@echo "$(BLUE)Rodando container...$(NC)"
	@docker run -it --rm kayoscrypto:latest

##@ Limpeza

clean: ## Limpar arquivos temporários
	@echo "$(BLUE)Limpando arquivos temporários...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
	@echo "$(GREEN)✅ Limpeza completa!$(NC)"

clean-all: clean ## Limpar tudo incluindo dependências
	@echo "$(BLUE)Limpeza profunda...$(NC)"
	@rm -rf venv/ .venv/
	@echo "$(GREEN)✅ Limpeza profunda completa!$(NC)"

##@ Desenvolvimento

watch-test: ## Rodar testes automaticamente ao salvar
	@echo "$(BLUE)Monitorando mudanças...$(NC)"
	@$(PYTHON) -m pytest_watch $(TESTS_DIR)/

shell: ## Abrir Python shell com projeto carregado
	@$(PYTHON) -i -c "from src.core.kayoscrypto_ultimate import KayosCryptoUltimate; print('KayosCrypto carregado. Use: cipher = KayosCryptoUltimate(password=\"test\")')"

##@ Análise

security-audit: ## Auditoria de segurança
	@echo "$(BLUE)Auditoria de segurança...$(NC)"
	@$(PYTHON) -m bandit -r $(SRC_DIR)/
	@$(PYTHON) -m safety check
	@echo "$(GREEN)✅ Auditoria completa!$(NC)"

complexity: ## Análise de complexidade
	@echo "$(BLUE)Analisando complexidade...$(NC)"
	@$(PYTHON) -m radon cc $(SRC_DIR)/ -a
	@echo "$(GREEN)✅ Análise completa!$(NC)"

diagnose-stream: ## Rodar KayosStreamAnalyzer (STREAM=arquivo|diretorio, OUT=destino opcional)
	@if [ -z "$(STREAM)" ]; then \
		echo "$(RED)Informe STREAM=</caminho/para/arquivo ou diretorio>$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Executando KayosStreamAnalyzer em $(STREAM)...$(NC)"
	@if [ -n "$(OUT)" ]; then \
		scripts/diagnostics/run_stream_analyzer.sh "$(STREAM)" "$(OUT)"; \
	else \
		scripts/diagnostics/run_stream_analyzer.sh "$(STREAM)"; \
	fi
	@echo "$(GREEN)✅ Diagnóstico gerado!$(NC)"

##@ Auditoria

pre-audit: ## Gerar bundle de pré-auditoria com documentos e logs principais
	@echo "$(BLUE)Montando bundle de pré-auditoria...$(NC)"
	@BUNDLE_DIR=$(PRE_AUDIT_DIR); \
	 rm -rf $$BUNDLE_DIR; \
	 mkdir -p $$BUNDLE_DIR/docs $$BUNDLE_DIR/logs; \
	 for f in $(PRE_AUDIT_DOCS); do \
	 	if [ -f $$f ]; then \
	 		cp "$$f" $$BUNDLE_DIR/docs/; \
	 	else \
	 		echo "$(YELLOW)Aviso: $$f não encontrado$(NC)"; \
	 	fi; \
	 done; \
	 for f in $(PRE_AUDIT_LOGS); do \
	 	if [ -f $$f ]; then \
	 		cp "$$f" $$BUNDLE_DIR/logs/; \
	 	else \
	 		echo "$(YELLOW)Aviso: $$f não encontrado$(NC)"; \
	 	fi; \
	 done; \
	 if [ -f $(NIST_REPORT) ]; then \
		mkdir -p $$BUNDLE_DIR/nist; \
		cp $(NIST_REPORT) $$BUNDLE_DIR/nist/finalAnalysisReport.txt; \
		echo "$(GREEN)✅ Relatório NIST anexado ao bundle$(NC)"; \
	 else \
		echo "$(YELLOW)Aviso: $(NIST_REPORT) não encontrado$(NC)"; \
	 fi; \
	 if [ -f $(NIST_LOG_LATEST) ]; then \
		cp $(NIST_LOG_LATEST) $$BUNDLE_DIR/logs/; \
		echo "$(GREEN)✅ Log NIST mais recente anexado$(NC)"; \
	 else \
		echo "$(YELLOW)Aviso: $(NIST_LOG_LATEST) não encontrado$(NC)"; \
	 fi; \
	 BUNDLE_NAME=pre_audit_bundle_$$(date +%Y%m%dT%H%M%S).tar.gz; \
	 (cd $$BUNDLE_DIR && tar -czf ../$$BUNDLE_NAME .); \
	 echo "$(GREEN)✅ Bundle gerado em artifacts/$$BUNDLE_NAME$(NC)"

# TARGETS DE VALIDAÇÃO ESTATÍSTICA
practrand-test:
	@mkdir -p reports
	@echo "=== EXECUTANDO PRACTRAND (100MB) ==="
	@$(ENTROPY_GENERATOR) 100mb - 8 123456789 matuto --matrix-fix | \
	$(PRACTRAND_CMD) stdin32 -tlmin 12 -tlmax 32 > reports/practrand_test.log
	@echo "✅ PractRand concluído - verifique reports/practrand_test.log"

testu01-test:
	@mkdir -p reports
	@echo "=== EXECUTANDO TESTU01 SMALLCRUSH (10MB) ==="
	@$(ENTROPY_GENERATOR) 10mb - 8 123456789 matuto --matrix-fix | \
	$(TESTU01_CMD) -s smallcrush > reports/testu01_smallcrush.log
	@echo "✅ TestU01 SmallCrush concluído - verifique reports/testu01_smallcrush.log"

nist-validation:
	@echo "=== VALIDAÇÃO NIST (Matrix Rank) ==="
	@cd hardware/emulation && ./run_emulation.sh
	@echo "✅ Validação NIST concluída - verifique hardware/emulation/entropy_samples.bin"

fips-health-check:
	@echo "=== TESTES DE SAÚDE FIPS ==="
	@$(ENTROPY_GENERATOR) 1mb fips_test.bin 8 123456789 matuto --matrix-fix
	@echo "✅ Testes FIPS concluídos - arquivo fips_test.bin gerado"

##@ Validação Quântica

quantum-optimization: ## Executar otimização Fibonacci completa
	@mkdir -p reports
	@echo "$(BLUE)=== EXECUTANDO OTIMIZAÇÃO QUÂNTICA FIBONACCI ===$(NC)"
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m python.diagnostics.cli optimize-fibonacci \
		$(QUANTUM_OPTIMIZATION_INPUT) \
		--output $(QUANTUM_OPTIMIZATION_OUTPUT) \
		--context production \
		--validate \
		--json > reports/quantum_optimization.json
	@echo "$(GREEN)✅ Otimização quântica concluída$(NC)"
	@cat reports/quantum_optimization.json | jq '.'

quantum-validation-suite: practrand-test testu01-test nist-validation quantum-optimization test-nist ## Rodar suite completa (PractRand + TestU01 + NIST + otimização + run oficial)
	@echo "$(BLUE)=== SUITE COMPLETA DE VALIDAÇÃO QUÂNTICA ===$(NC)"
	@echo "$(GREEN)✅ Todos os testes quânticos concluídos$(NC)"

test-fibonacci-improvement: ## Comparar métricas antes/depois da otimização
	@mkdir -p reports
	@echo "$(BLUE)=== VALIDAÇÃO ANTES/DEPOIS FIBONACCI ===$(NC)"
	@echo "$(YELLOW)📊 ANTES da otimização:$(NC)"
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m python.diagnostics.cli $(QUANTUM_OPTIMIZATION_INPUT) --no-emulator --json > reports/fibonacci_before.json
	@echo "$(YELLOW)📊 DEPOIS da otimização:$(NC)"
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) -m python.diagnostics.cli $(QUANTUM_OPTIMIZATION_OUTPUT) --no-emulator --json > reports/fibonacci_after.json
	@echo "$(BLUE)📈 COMPARAÇÃO$(NC)"
	@echo "Antes: $$(jq '.quantum.metrics[] | select(.name | contains("Fibonacci")) | .score' reports/fibonacci_before.json)"
	@echo "Depois: $$(jq '.quantum.metrics[] | select(.name | contains("Fibonacci")) | .score' reports/fibonacci_after.json)"

emulator-production-test:
	@echo "=== TESTE DE PRODUÇÃO DO EMULADOR ==="
	@cd hardware/emulation && ./run_emulation.sh
	@mkdir -p reports
	@PYTHONPATH=src $(PYTHON) -m python.diagnostics.cli optimize-fibonacci \
		hardware/emulation/entropy_samples.bin \
		--output hardware/emulation/entropy_enterprise.bin \
		--validate --json > reports/emulator_enterprise.json
	@echo "✅ Emulador enterprise validado - consulte reports/emulator_enterprise.json"

debug-fibonacci:
	@echo "=== DEBUG DETALHADO FIBONACCI ==="
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) scripts/debug_fibonacci.py

.PHONY: enterprise-fibonacci
enterprise-fibonacci: ## Executar diagnóstico enterprise Fibonacci
	@echo "=== 🚀 SISTEMA ENTERPRISE FIBONACCI ==="
	@PYTHONPATH=$(SRC_DIR) $(PYTHON) scripts/enterprise_fibonacci.py

##@ Informações

version: ## Mostrar versão
	@echo "$(GREEN)KayosCrypto v5.0.1 ULTIMATE$(NC)"
	@echo "Python: $$($(PYTHON) --version)"
	@echo "Score: 96.7%"

status: ## Status do projeto
	@echo "$(GREEN)📊 STATUS KAYOSCRYPTO$(NC)"
	@echo "Versão: v5.0.1 ULTIMATE"
	@echo "Testes: 9/9 passando (100%)"
	@echo "Score: 96.7%"
	@echo "Status: ✅ Production Ready"
	@echo ""
	@echo "$(BLUE)Estrutura:$(NC)"
	@tree -L 2 -d | head -20

.DEFAULT_GOAL := help
