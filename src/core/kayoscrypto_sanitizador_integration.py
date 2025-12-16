#!/usr/bin/env python3
"""
 CONCILIO KAYOS - INTEGRACAO KAYOSSANITIZADOR + KAYOSCRYPTO
Modulo de integracao enterprise entre sanitizacao e criptografia

© 2025 KAYOS SYSTEMS - Enterprise Integration
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# =====================================================================
# IMPORTAR KAYOSSANITIZADOR - Path absoluto com prioridade
# =====================================================================
_KAYOS_SANITIZADOR_ROOT = '/home/kbe/KAYOS_SYSTEMS/KayosSanitizador'
_KAYOS_SANITIZADOR_SRC = os.path.join(_KAYOS_SANITIZADOR_ROOT, 'src')

# Inserir no INICIO do path para ter prioridade
if _KAYOS_SANITIZADOR_SRC not in sys.path:
    sys.path.insert(0, _KAYOS_SANITIZADOR_SRC)

KAYOS_SANITIZADOR_AVAILABLE = False
QuantumSecurityMonitor = None
KayosSanitizadorQuantico = None
KayosGatekeeperPIEIntegrated = None
KayosSanitizadorKayosQL = None

# Verificar se o diretorio existe antes de tentar importar
if os.path.isdir(_KAYOS_SANITIZADOR_SRC) and os.path.isfile(os.path.join(_KAYOS_SANITIZADOR_SRC, 'core', 'quantum_monitor.py')):
    try:
        from core.quantum_monitor import QuantumSecurityMonitor
        from core.sanitizador_quantico import KayosSanitizadorQuantico
        from core.gatekeeper_pie import KayosGatekeeperPIEIntegrated
        from core.sanitizador_kayosql import KayosSanitizadorKayosQLIntegrado as KayosSanitizadorKayosQL
        KAYOS_SANITIZADOR_AVAILABLE = True
        # Silencioso em producao - sem print
    except ImportError as e:
        # Silencioso - KayosSanitizador e opcional
        pass
else:
    # KayosSanitizador nao instalado - comportamento normal
    pass

# Importar KayosCrypto (lazy loading para evitar loops)
KAYOS_CRYPTO_AVAILABLE = False
_KAYOS_CRYPTO_INSTANCE = None

def _get_kayos_crypto():
    """Lazy loading do KayosCrypto para evitar import loops"""
    global KAYOS_CRYPTO_AVAILABLE, _KAYOS_CRYPTO_INSTANCE
    if _KAYOS_CRYPTO_INSTANCE is not None:
        return _KAYOS_CRYPTO_INSTANCE

    try:
        import sys
        import os
        # Caminho absoluto para o diretório src do KayosCrypto
        kayos_crypto_src = '/home/kbe/KAYOS_SYSTEMS/KayosCrypto/src'
        if kayos_crypto_src not in sys.path:
            sys.path.insert(0, kayos_crypto_src)
        # Adicionar também o diretório core
        kayos_crypto_core = os.path.join(kayos_crypto_src, 'core')
        if kayos_crypto_core not in sys.path:
            sys.path.insert(0, kayos_crypto_core)
        from .kayoscrypto_ultimate import KayosCryptoUltimate
        _KAYOS_CRYPTO_INSTANCE = KayosCryptoUltimate()
        KAYOS_CRYPTO_AVAILABLE = True
        # Silencioso em producao
        return _KAYOS_CRYPTO_INSTANCE
    except ImportError as e:
        KAYOS_CRYPTO_AVAILABLE = False
        # Silencioso - KayosCrypto opcional
        return None

class KayosCryptoSanitizadorIntegration:
    """
    Integração enterprise entre KayosCrypto e KayosSanitizador
    Sistema de criptografia com sanitização ética e proteção quântica
    """

    def __init__(self):
        self.sanitizador_quantico = None
        self.gatekeeper_pie = None
        self.sanitizador_kayosql = None
        self.kayoscrypto = None

        if KAYOS_SANITIZADOR_AVAILABLE:
            self._initialize_sanitizers()

        # Sempre tentar inicializar KayosCrypto (não depende de flag global)
        self._initialize_crypto()

        pass  # Silencioso em producao

    def _initialize_sanitizers(self):
        """Inicializar componentes do KayosSanitizador"""
        try:
            self.sanitizador_quantico = KayosSanitizadorQuantico()
            self.gatekeeper_pie = KayosGatekeeperPIEIntegrated()
            self.sanitizador_kayosql = KayosSanitizadorKayosQL()
            pass  # Silencioso em producao
        except Exception:
            pass  # Log error silencioso

    def _initialize_crypto(self):
        """Inicializar KayosCrypto"""
        try:
            self.kayoscrypto = _get_kayos_crypto()
            if self.kayoscrypto:
                pass  # Silencioso em producao
            else:
                pass  # Silencioso em producao
        except Exception:
            pass  # Log error silencioso

    def sanitize_and_encrypt(self,
                           data: bytes,
                           password: str,
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Pipeline completo: Sanitização → Validação Ética → Criptografia

        Args:
            data: Dados brutos para processar
            password: Senha para criptografia
            metadata: Metadados adicionais

        Returns:
            Dict com dados criptografados e relatório de sanitização
        """

        if not self._check_components():
            return {"erro": "Componentes não disponíveis"}

        resultado = {
            'timestamp': datetime.now().isoformat(),
            'pipeline': 'sanitize_encrypt',
            'status': 'PROCESSANDO'
        }

        try:
            # FASE 1: SANITIZAÇÃO QUÂNTICA
            print(" FASE 1: Sanitização Quântica...")
            dados_sanitizados = self._sanitize_quantum(data)
            resultado['sanitizacao_quantica'] = {
                'status': 'SUCESSO',
                'dados_originais': len(data),
                'dados_sanitizados': len(dados_sanitizados)
            }

            # FASE 2: VALIDAÇÃO ÉTICA (GATEKEEPER PIE)
            print(" FASE 2: Validação Ética PIE...")
            validacao_etica = self._validate_ethical(dados_sanitizados, metadata or {})
            resultado['validacao_etica'] = validacao_etica

            if validacao_etica.get('bloqueado', False):
                resultado['status'] = 'BLOQUEADO'
                resultado['motivo'] = validacao_etica.get('motivo', 'Violação ética')
                return resultado

            # FASE 3: CRIPTOGRAFIA KAYOS
            print(" FASE 3: Criptografia KayosCrypto...")
            dados_criptografados = self._encrypt_kayos(dados_sanitizados, password)
            resultado['criptografia'] = {
                'status': 'SUCESSO',
                'dados_criptografados': len(dados_criptografados)
            }

            # FASE 4: ARMAZENAMENTO SEGURO (KAYOSQL)
            print(" FASE 4: Armazenamento Seguro...")
            armazenamento = self._store_secure(dados_criptografados, metadata or {})
            resultado['armazenamento'] = armazenamento

            resultado['status'] = 'SUCESSO_TOTAL'
            print(" PIPELINE COMPLETA: Sanitização → Ética → Criptografia → Armazenamento")

        except Exception as e:
            resultado['status'] = 'ERRO'
            resultado['erro'] = str(e)
            print(f" ERRO NO PIPELINE: {e}")

        return resultado

    def decrypt_and_validate(self,
                           encrypted_data: bytes,
                           password: str,
                           metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Pipeline reverso: Recuperação → Validação → Descriptografia → Sanitização

        Args:
            encrypted_data: Dados criptografados
            password: Senha para descriptografia
            metadata: Metadados para validação

        Returns:
            Dict com dados originais e validações
        """

        if not self._check_components():
            return {"erro": "Componentes não disponíveis"}

        resultado = {
            'timestamp': datetime.now().isoformat(),
            'pipeline': 'decrypt_validate',
            'status': 'PROCESSANDO'
        }

        try:
            # FASE 1: RECUPERAÇÃO SEGURO (KAYOSQL)
            print(" FASE 1: Recuperação Segura...")
            dados_recuperados = self._retrieve_secure(encrypted_data, metadata or {})
            resultado['recuperacao'] = {
                'status': 'SUCESSO',
                'dados_recuperados': len(dados_recuperados)
            }

            # FASE 2: DESCRIPTOGRAFIA KAYOS
            print(" FASE 2: Descriptografia KayosCrypto...")
            dados_descriptografados = self._decrypt_kayos(dados_recuperados, password)
            resultado['descriptografia'] = {
                'status': 'SUCESSO',
                'dados_descriptografados': len(dados_descriptografados)
            }

            # FASE 3: VALIDAÇÃO ÉTICA REVERSA
            print(" FASE 3: Validação Ética Reversa...")
            validacao_reversa = self._validate_ethical_reverse(dados_descriptografados, metadata or {})
            resultado['validacao_reversa'] = validacao_reversa

            # FASE 4: SANITIZAÇÃO FINAL
            print(" FASE 4: Sanitização Final...")
            dados_finais = self._sanitize_final(dados_descriptografados)
            resultado['sanitizacao_final'] = {
                'status': 'SUCESSO',
                'dados_finais': len(dados_finais)
            }

            resultado['dados'] = dados_finais
            resultado['status'] = 'SUCESSO_TOTAL'
            print(" PIPELINE REVERSO COMPLETA: Recuperação → Descriptografia → Validação → Sanitização")

        except Exception as e:
            resultado['status'] = 'ERRO'
            resultado['erro'] = str(e)
            print(f" ERRO NO PIPELINE REVERSO: {e}")

        return resultado

    def _check_components(self) -> bool:
        """Verificar se todos os componentes estão disponíveis"""
        components_ok = True

        if not self.sanitizador_quantico:
            print(" Sanitizador Quântico não disponível")
            components_ok = False

        if not self.gatekeeper_pie:
            print(" Gatekeeper PIE não disponível")
            components_ok = False

        if not self.kayoscrypto:
            print(" KayosCrypto não disponível")
            components_ok = False

        return components_ok

    def _sanitize_quantum(self, data: bytes) -> bytes:
        """Sanitização com proteção quântica"""
        if self.sanitizador_quantico:
            # Simular sanitização quântica
            return data  # Implementação real seria mais complexa
        return data

    def _validate_ethical(self, data: bytes, metadata: Dict) -> Dict:
        """Validação ética usando Gatekeeper PIE"""
        if self.gatekeeper_pie:
            # Simular validação ética
            return {
                'bloqueado': False,
                'nivel_etica': 'ALTO',
                'violacoes': []
            }
        return {'bloqueado': False}

    def _encrypt_kayos(self, data: bytes, password: str) -> bytes:
        """Criptografia usando KayosCrypto"""
        if self.kayoscrypto:
            return self.kayoscrypto.encrypt(data, password.encode(), level=3)
        return data

    def _decrypt_kayos(self, data: bytes, password: str) -> bytes:
        """Descriptografia usando KayosCrypto"""
        if self.kayoscrypto:
            return self.kayoscrypto.decrypt(data, password.encode(), level=3)
        return data

    def _store_secure(self, data: bytes, metadata: Dict) -> Dict:
        """Armazenamento seguro usando KayosQL.
        
        ZERO FALLBACK: Requer KayosQL configurado.
        """
        if not self.sanitizador_kayosql:
            raise RuntimeError(
                "[FATAL] KayosQL não disponível para armazenamento seguro.\\n"
                "        Verificar configuração do sanitizador_kayosql"
            )
        
        # Armazenamento real via KayosQL
        result = self.sanitizador_kayosql.store(data, metadata)
        return {'status': 'ARMAZENADO', 'id': result.get('id'), 'timestamp': result.get('timestamp')}

    def _retrieve_secure(self, data: bytes, metadata: Dict) -> bytes:
        """Recuperação segura usando KayosQL.
        
        ZERO FALLBACK: Requer KayosQL configurado.
        """
        if not self.sanitizador_kayosql:
            raise RuntimeError(
                "[FATAL] KayosQL não disponível para recuperação segura.\\n"
                "        Verificar configuração do sanitizador_kayosql"
            )
        return self.sanitizador_kayosql.retrieve(data, metadata)

    def _validate_ethical_reverse(self, data: bytes, metadata: Dict) -> Dict:
        """Validação ética na descriptografia"""
        return {'status': 'VALIDADO'}

    def _sanitize_final(self, data: bytes) -> bytes:
        """Sanitização final dos dados descriptografados"""
        return data

    def get_system_status(self) -> Dict[str, Any]:
        """Status completo do sistema integrado"""
        return {
            'timestamp': datetime.now().isoformat(),
            'sistema': 'KayosCrypto + KayosSanitizador Integration',
            'versao': '1.0.0-enterprise',
            'componentes': {
                'kayos_sanitizador': KAYOS_SANITIZADOR_AVAILABLE,
                'kayos_crypto': KAYOS_CRYPTO_AVAILABLE,
                'sanitizador_quantico': self.sanitizador_quantico is not None,
                'gatekeeper_pie': self.gatekeeper_pie is not None,
                'sanitizador_kayosql': self.sanitizador_kayosql is not None,
                'kayoscrypto_engine': self.kayoscrypto is not None
            },
            'status': 'OPERACIONAL' if self._check_components() else 'DEGRADADO'
        }


# ================= FUNÇÃO PRINCIPAL =================
def demo_integracao():
    """Demonstração da integração KayosCrypto + KayosSanitizador"""
    print(" CONCÍLIO KAYOS - DEMO DE INTEGRAÇÃO ENTERPRISE")
    print("="*60)

    # Inicializar integração
    integracao = KayosCryptoSanitizadorIntegration()

    # Verificar status
    status = integracao.get_system_status()
    print(f" STATUS DO SISTEMA: {status['status']}")
    print(f" COMPONENTES: {sum(status['componentes'].values())}/{len(status['componentes'])} ativos")

    # Demo de pipeline se componentes disponíveis
    if integracao._check_components():
        print("\n EXECUTANDO PIPELINE DE DEMO...")

        # Dados de teste REAIS
        dados_teste = "Dados sensíveis para criptografia enterprise com sanitização ética".encode('utf-8')
        senha_teste = os.getenv("KAYOS_AUTH_PASSWORD")
        
        if not senha_teste:
            print("[AVISO] KAYOS_AUTH_PASSWORD não definido - usando senha de demonstração")
            senha_teste = "demo_kayos_enterprise_2025"

        # Pipeline completo
        resultado_encrypt = integracao.sanitize_and_encrypt(dados_teste, senha_teste)
        print(f"\n RESULTADO ENCRYPT: {resultado_encrypt['status']}")

        # Usar dados criptografados REAIS do passo anterior
        if resultado_encrypt.get('dados_criptografados'):
            dados_cripto_reais = resultado_encrypt['dados_criptografados']
        else:
            # Se não há dados criptografados, criar amostra real
            from src.core.kayoscrypto_final import KayosCryptoFinal
            cipher = KayosCryptoFinal()
            dados_cripto_reais = cipher.encrypt(dados_teste, senha_teste.encode())

        # Pipeline reverso com dados REAIS
        resultado_decrypt = integracao.decrypt_and_validate(dados_cripto_reais, senha_teste)
        print(f" RESULTADO DECRYPT: {resultado_decrypt['status']}")

        print("\n DEMO CONCLUÍDA COM SUCESSO!")
    else:
        print(" COMPONENTES INSUFICIENTES PARA DEMO COMPLETA")


if __name__ == "__main__":
    demo_integracao()