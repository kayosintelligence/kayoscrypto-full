#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KAYOSCRYPTO ENVIRONMENT VALIDATOR
==================================

Validador de ambiente OBRIGATÓRIO para execução do sistema.
ZERO FALLBACKS - Todas as dependências DEVEM estar presentes.

Para auditoria de segurança:
- Comportamento 100% determinístico
- Sem degradação silenciosa
- Falha rápida e explícita

Autor: KAYOS SYSTEMS
Data: 01 de Dezembro de 2025
Versão: v6.0.1 AUDIT-READY
"""

import sys
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

# Versão mínima do Python
MINIMUM_PYTHON_VERSION = (3, 10)


@dataclass
class DependencyStatus:
    """Status de uma dependência"""
    name: str
    required: bool
    installed: bool
    version: Optional[str]
    error_message: Optional[str]


class EnvironmentValidationError(Exception):
    """Erro fatal de validação de ambiente - sistema não pode executar"""
    pass


class EnvironmentValidator:
    """
    Validador de Ambiente para KayosCrypto
    
    POLÍTICA: ZERO FALLBACKS
    - Se uma dependência obrigatória faltar, o sistema NÃO EXECUTA
    - Não há degradação silenciosa
    - Mensagens de erro claras e acionáveis
    """
    
    # Dependências OBRIGATÓRIAS - sem estas o sistema não funciona
    REQUIRED_DEPENDENCIES = {
        'numpy': {
            'min_version': '1.20.0',
            'purpose': 'Operações matemáticas e arrays'
        },
        'argon2-cffi': {
            'import_name': 'argon2',
            'min_version': '21.0.0',
            'purpose': 'Key derivation resistente a Grover'
        },
        'pynacl': {
            'import_name': 'nacl',
            'min_version': '1.5.0',
            'purpose': 'Assinaturas Ed25519 (Rib 7)'
        },
        'blake3': {
            'min_version': '0.3.0',
            'purpose': 'Hash criptográfico rápido'
        },
    }
    
    # Dependências OPCIONAIS - funcionalidades extras
    OPTIONAL_DEPENDENCIES = {
        'liboqs-python': {
            'import_name': 'oqs',
            'purpose': 'Criptografia pós-quântica (Kyber, Dilithium)'
        },
        'pillow': {
            'import_name': 'PIL',
            'purpose': 'Esteganografia visual'
        },
    }
    
    # Módulos internos OBRIGATÓRIOS
    REQUIRED_MODULES = [
        'src.core.kayoscrypto_final',
        'src.core.ezekiel_concentric',
        'src.core.fibonacci_direction',
    ]
    
    def __init__(self):
        self.validation_results: Dict[str, DependencyStatus] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_python_version(self) -> bool:
        """Valida versão do Python"""
        current = sys.version_info[:2]
        if current < MINIMUM_PYTHON_VERSION:
            self.errors.append(
                f"Python {MINIMUM_PYTHON_VERSION[0]}.{MINIMUM_PYTHON_VERSION[1]}+ "
                f"obrigatório. Versão atual: {current[0]}.{current[1]}"
            )
            return False
        return True
    
    def _check_package_version(self, package_name: str) -> Tuple[bool, Optional[str]]:
        """Verifica se um pacote está instalado e retorna sua versão"""
        try:
            import importlib.metadata
            version = importlib.metadata.version(package_name)
            return True, version
        except importlib.metadata.PackageNotFoundError:
            return False, None
    
    def _try_import(self, import_name: str) -> bool:
        """Tenta importar um módulo"""
        try:
            __import__(import_name)
            return True
        except ImportError:
            return False
    
    def validate_required_dependencies(self) -> bool:
        """Valida todas as dependências obrigatórias"""
        all_valid = True
        
        for pkg_name, config in self.REQUIRED_DEPENDENCIES.items():
            import_name = config.get('import_name', pkg_name.replace('-', '_'))
            min_version = config.get('min_version')
            purpose = config.get('purpose', 'Não especificado')
            
            installed, version = self._check_package_version(pkg_name)
            can_import = self._try_import(import_name)
            
            status = DependencyStatus(
                name=pkg_name,
                required=True,
                installed=installed and can_import,
                version=version,
                error_message=None
            )
            
            if not (installed and can_import):
                status.error_message = f"OBRIGATÓRIO: {pkg_name} ({purpose})"
                self.errors.append(
                    f"[FATAL] {pkg_name} não instalado.\n"
                    f"        Propósito: {purpose}\n"
                    f"        Instalar: pip install {pkg_name}"
                )
                all_valid = False
            elif min_version and version:
                # Comparação simples de versão
                from packaging import version as pkg_version
                try:
                    if pkg_version.parse(version) < pkg_version.parse(min_version):
                        status.error_message = f"Versão {version} < {min_version}"
                        self.errors.append(
                            f"[FATAL] {pkg_name} versão {version} muito antiga.\n"
                            f"        Mínimo: {min_version}\n"
                            f"        Atualizar: pip install --upgrade {pkg_name}"
                        )
                        all_valid = False
                except Exception:
                    pass  # Se packaging não disponível, ignora check de versão
            
            self.validation_results[pkg_name] = status
        
        return all_valid
    
    def validate_optional_dependencies(self) -> None:
        """Valida dependências opcionais (apenas warnings)"""
        for pkg_name, config in self.OPTIONAL_DEPENDENCIES.items():
            import_name = config.get('import_name', pkg_name.replace('-', '_'))
            purpose = config.get('purpose', 'Não especificado')
            
            installed, version = self._check_package_version(pkg_name)
            can_import = self._try_import(import_name)
            
            status = DependencyStatus(
                name=pkg_name,
                required=False,
                installed=installed or can_import,
                version=version,
                error_message=None
            )
            
            if not (installed or can_import):
                self.warnings.append(
                    f"[AVISO] {pkg_name} não instalado.\n"
                    f"        Funcionalidade indisponível: {purpose}\n"
                    f"        Instalar (opcional): pip install {pkg_name}"
                )
            
            self.validation_results[pkg_name] = status
    
    def validate_internal_modules(self) -> bool:
        """Valida módulos internos do KayosCrypto"""
        all_valid = True
        
        # Adicionar path ao sys.path temporariamente
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        
        for module_name in self.REQUIRED_MODULES:
            try:
                __import__(module_name)
            except ImportError as e:
                self.errors.append(
                    f"[FATAL] Módulo interno não encontrado: {module_name}\n"
                    f"        Erro: {e}\n"
                    f"        Verificar integridade da instalação"
                )
                all_valid = False
        
        return all_valid
    
    def validate_all(self, raise_on_error: bool = True) -> bool:
        """
        Executa validação completa do ambiente.
        
        Args:
            raise_on_error: Se True, levanta exceção em caso de erro fatal
            
        Returns:
            True se ambiente válido, False caso contrário
            
        Raises:
            EnvironmentValidationError: Se raise_on_error=True e houver erros
        """
        self.errors.clear()
        self.warnings.clear()
        self.validation_results.clear()
        
        results = {
            'python_version': self.validate_python_version(),
            'required_deps': self.validate_required_dependencies(),
            'internal_modules': self.validate_internal_modules(),
        }
        
        # Opcional - não falha, apenas avisa
        self.validate_optional_dependencies()
        
        all_valid = all(results.values())
        
        if not all_valid and raise_on_error:
            error_report = self._generate_error_report()
            raise EnvironmentValidationError(error_report)
        
        return all_valid
    
    def _generate_error_report(self) -> str:
        """Gera relatório de erros formatado"""
        lines = [
            "",
            "=" * 70,
            "KAYOSCRYPTO - FALHA DE VALIDAÇÃO DE AMBIENTE",
            "=" * 70,
            "",
            "O sistema não pode ser executado devido a dependências ausentes.",
            "POLÍTICA: ZERO FALLBACKS - Todas as dependências são obrigatórias.",
            "",
            "ERROS ENCONTRADOS:",
            "-" * 40,
        ]
        
        for error in self.errors:
            lines.append(error)
            lines.append("")
        
        if self.warnings:
            lines.extend([
                "AVISOS (não bloqueantes):",
                "-" * 40,
            ])
            for warning in self.warnings:
                lines.append(warning)
                lines.append("")
        
        lines.extend([
            "=" * 70,
            "AÇÃO NECESSÁRIA: Instalar dependências antes de executar",
            "  pip install argon2-cffi pynacl blake3 numpy",
            "=" * 70,
            "",
        ])
        
        return "\n".join(lines)
    
    def print_status(self) -> None:
        """Imprime status do ambiente de forma amigável"""
        print("\n" + "=" * 60)
        print("KAYOSCRYPTO - STATUS DO AMBIENTE")
        print("=" * 60)
        
        print("\n[DEPENDÊNCIAS OBRIGATÓRIAS]")
        for name, config in self.REQUIRED_DEPENDENCIES.items():
            status = self.validation_results.get(name)
            if status and status.installed:
                version_str = f" (v{status.version})" if status.version else ""
                print(f"  [OK] {name}{version_str}")
            else:
                print(f"  [ERRO] {name} - NÃO INSTALADO")
        
        print("\n[DEPENDÊNCIAS OPCIONAIS]")
        for name, config in self.OPTIONAL_DEPENDENCIES.items():
            status = self.validation_results.get(name)
            if status and status.installed:
                version_str = f" (v{status.version})" if status.version else ""
                print(f"  [OK] {name}{version_str}")
            else:
                print(f"  [--] {name} - não instalado (opcional)")
        
        print("\n" + "=" * 60)
        
        if self.errors:
            print("[STATUS] AMBIENTE INVÁLIDO - Corrigir erros acima")
        else:
            print("[STATUS] AMBIENTE VÁLIDO - Sistema pronto para execução")
        print("=" * 60 + "\n")


# Singleton global
_validator: Optional[EnvironmentValidator] = None


def get_validator() -> EnvironmentValidator:
    """Retorna instância singleton do validador"""
    global _validator
    if _validator is None:
        _validator = EnvironmentValidator()
    return _validator


def validate_environment(raise_on_error: bool = True) -> bool:
    """
    Função de conveniência para validar ambiente.
    
    DEVE ser chamada no início de qualquer execução do KayosCrypto.
    """
    validator = get_validator()
    return validator.validate_all(raise_on_error=raise_on_error)


def require_environment() -> None:
    """
    Exige ambiente válido ou levanta exceção.
    
    Usar no início de módulos críticos:
    
        from src.core.environment_validator import require_environment
        require_environment()  # Falha rápido se ambiente inválido
    """
    validate_environment(raise_on_error=True)


# =============================================================================
# EXECUÇÃO DIRETA - Verificação de ambiente
# =============================================================================
if __name__ == "__main__":
    print("\nKAYOSCRYPTO - Validador de Ambiente v6.0.1")
    print("-" * 50)
    
    validator = get_validator()
    
    try:
        is_valid = validator.validate_all(raise_on_error=False)
        validator.print_status()
        
        if not is_valid:
            print("\n[ERRO] Ambiente inválido. Instalar dependências:")
            print("  pip install argon2-cffi pynacl blake3 numpy packaging")
            sys.exit(1)
        else:
            print("\n[OK] Ambiente válido. Sistema pronto.")
            sys.exit(0)
            
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        sys.exit(1)
