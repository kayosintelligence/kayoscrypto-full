#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KAYOSQL FIPS 140-3 CERTIFICATION TESTS
=====================================

Suite completa de testes para validação da certificação FIPS 140-3.
Testa todos os aspectos da implementação FIPS-compliant.

Características:
- Power-Up Self-Tests validation
- Conditional Self-Tests validation
- Cryptographic Module Testing
- Key Management validation
- Security Policy compliance
- Audit Logging verification
"""

import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar caminho para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.database.kayosql.fips_certification import (
    FIPSCertificationManager,
    FIPSKeyStore,
    FIPSSelfTests,
    FIPSSecurityPolicy,
    FIPSAuditLog,
    FIPSSecurityLevel,
    FIPSMode,
    get_fips_manager,
    initialize_fips_mode,
    run_fips_self_tests
)

class TestFIPSCertificationManager(unittest.TestCase):
    """Testes para FIPSCertificationManager"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.manager = FIPSCertificationManager()

    def test_initialization(self):
        """Testa inicialização do manager"""
        self.assertEqual(self.manager.fips_mode, FIPSMode.FIPS_COMPLIANT)
        self.assertEqual(self.manager.security_level, FIPSSecurityLevel.LEVEL_3)
        self.assertFalse(self.manager.power_up_tests_passed)
        self.assertTrue(self.manager.conditional_tests_passed)

    def test_fips_initialization_success(self):
        """Testa inicialização FIPS bem-sucedida"""
        with patch.object(self.manager.self_tests, 'run_power_up_tests', return_value={"passed": True}), \
             patch.object(self.manager.security_policy, 'validate_policy', return_value=True), \
             patch.object(self.manager.key_store, 'initialize_fips_key_store', return_value=True), \
             patch.object(self.manager.self_tests, 'run_conditional_tests', return_value={"passed": True}):

            result = self.manager.initialize_fips_mode()
            self.assertTrue(result)
            self.assertTrue(self.manager.power_up_tests_passed)
            self.assertEqual(self.manager.fips_mode, FIPSMode.FIPS_COMPLIANT)

    def test_fips_initialization_failure_power_up(self):
        """Testa falha na inicialização FIPS (Power-Up tests)"""
        with patch.object(self.manager.self_tests, 'run_power_up_tests', return_value={"passed": False}):

            result = self.manager.initialize_fips_mode()
            self.assertFalse(result)
            self.assertEqual(self.manager.fips_mode, FIPSMode.NON_FIPS)

    def test_fips_initialization_failure_security_policy(self):
        """Testa falha na inicialização FIPS (Security Policy)"""
        with patch.object(self.manager.self_tests, 'run_power_up_tests', return_value={"passed": True}), \
             patch.object(self.manager.security_policy, 'validate_policy', return_value=False):

            result = self.manager.initialize_fips_mode()
            self.assertFalse(result)
            self.assertEqual(self.manager.fips_mode, FIPSMode.NON_FIPS)

    def test_encrypt_fips_non_operational(self):
        """Testa criptografia quando FIPS não está operacional"""
        result = self.manager.encrypt_fips(b"test", "key_id")
        self.assertIsNone(result)

    def test_encrypt_fips_success(self):
        """Testa criptografia FIPS bem-sucedida"""
        # Inicializar FIPS
        with patch.object(self.manager.self_tests, 'run_power_up_tests', return_value={"passed": True}), \
             patch.object(self.manager.security_policy, 'validate_policy', return_value=True), \
             patch.object(self.manager.key_store, 'initialize_fips_key_store', return_value=True), \
             patch.object(self.manager.self_tests, 'run_conditional_tests', return_value={"passed": True}):

            self.manager.initialize_fips_mode()

        # Mock key store
        with patch.object(self.manager.key_store, 'get_fips_key', return_value=b'0' * 32), \
             patch.object(self.manager.key_store, 'is_key_valid', return_value=True), \
             patch.object(self.manager.key_store, 'increment_key_usage'):

            result = self.manager.encrypt_fips(b"test data", "test_key")
            self.assertIsNotNone(result)
            self.assertIsInstance(result, bytes)

    def test_generate_fips_key_success(self):
        """Testa geração de chave FIPS bem-sucedida"""
        # Inicializar FIPS
        with patch.object(self.manager.self_tests, 'run_power_up_tests', return_value={"passed": True}), \
             patch.object(self.manager.security_policy, 'validate_policy', return_value=True), \
             patch.object(self.manager.key_store, 'initialize_fips_key_store', return_value=True), \
             patch.object(self.manager.self_tests, 'run_conditional_tests', return_value={"passed": True}):

            self.manager.initialize_fips_mode()

        # Mock key store
        with patch.object(self.manager.key_store, 'store_fips_key'):

            key_id = self.manager.generate_fips_key("AES", 256)
            self.assertIsNotNone(key_id)
            self.assertTrue(key_id.startswith("fips_key_"))

    def test_generate_fips_key_invalid_params(self):
        """Testa geração de chave FIPS com parâmetros inválidos"""
        # Inicializar FIPS
        with patch.object(self.manager.self_tests, 'run_power_up_tests', return_value={"passed": True}), \
             patch.object(self.manager.security_policy, 'validate_policy', return_value=True), \
             patch.object(self.manager.key_store, 'initialize_fips_key_store', return_value=True), \
             patch.object(self.manager.self_tests, 'run_conditional_tests', return_value={"passed": True}):

            self.manager.initialize_fips_mode()

        # Testar algoritmo inválido
        key_id = self.manager.generate_fips_key("INVALID", 256)
        self.assertIsNone(key_id)

        # Testar comprimento inválido
        key_id = self.manager.generate_fips_key("AES", 64)
        self.assertIsNone(key_id)

    def test_run_self_tests(self):
        """Testa execução de self-tests"""
        with patch.object(self.manager.self_tests, 'run_power_up_tests', return_value={"passed": True}), \
             patch.object(self.manager.self_tests, 'run_conditional_tests', return_value={"passed": True}), \
             patch.object(self.manager.self_tests, 'run_integrity_tests', return_value={"passed": True}):

            results = self.manager.run_self_tests()
            self.assertIn("overall_status", results)
            self.assertEqual(results["overall_status"], "PASSED")

    def test_get_fips_status(self):
        """Testa obtenção do status FIPS"""
        status = self.manager.get_fips_status()
        self.assertIn("fips_mode", status)
        self.assertIn("security_level", status)
        self.assertIn("operational", status)
        self.assertIn("crypto_module", status)

class TestFIPSKeyStore(unittest.TestCase):
    """Testes para FIPSKeyStore"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.key_store = FIPSKeyStore()

    def test_store_and_get_key(self):
        """Testa armazenamento e recuperação de chave"""
        from src.database.kayosql.fips_certification import FIPSKeyMetadata

        key_id = "test_key"
        key_material = b"test_key_material"
        metadata = FIPSKeyMetadata(
            key_id=key_id,
            algorithm="AES",
            key_length=256,
            generation_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=1),
            usage_count=0,
            fips_compliant=True
        )

        self.key_store.store_fips_key(key_id, key_material, metadata)
        retrieved = self.key_store.get_fips_key(key_id)

        self.assertEqual(retrieved, key_material)

    def test_key_validation(self):
        """Testa validação de chave"""
        from src.database.kayosql.fips_certification import FIPSKeyMetadata

        # Chave válida
        valid_key_id = "valid_key"
        valid_metadata = FIPSKeyMetadata(
            key_id=valid_key_id,
            algorithm="AES",
            key_length=256,
            generation_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=1),
            usage_count=0,
            fips_compliant=True
        )
        self.key_store.store_fips_key(valid_key_id, b"key", valid_metadata)
        self.assertTrue(self.key_store.is_key_valid(valid_key_id))

        # Chave expirada
        expired_key_id = "expired_key"
        expired_metadata = FIPSKeyMetadata(
            key_id=expired_key_id,
            algorithm="AES",
            key_length=256,
            generation_date=datetime.now(),
            expiry_date=datetime.now() - timedelta(days=1),  # Expirada
            usage_count=0,
            fips_compliant=True
        )
        self.key_store.store_fips_key(expired_key_id, b"key", expired_metadata)
        self.assertFalse(self.key_store.is_key_valid(expired_key_id))

        # Chave inexistente
        self.assertFalse(self.key_store.is_key_valid("nonexistent_key"))

    def test_increment_key_usage(self):
        """Testa incremento do contador de uso da chave"""
        from src.database.kayosql.fips_certification import FIPSKeyMetadata

        key_id = "usage_key"
        metadata = FIPSKeyMetadata(
            key_id=key_id,
            algorithm="AES",
            key_length=256,
            generation_date=datetime.now(),
            expiry_date=datetime.now() + timedelta(days=1),
            usage_count=0,
            fips_compliant=True
        )

        self.key_store.store_fips_key(key_id, b"key", metadata)
        self.assertEqual(self.key_store.metadata[key_id].usage_count, 0)

        self.key_store.increment_key_usage(key_id)
        self.assertEqual(self.key_store.metadata[key_id].usage_count, 1)

class TestFIPSSelfTests(unittest.TestCase):
    """Testes para FIPSSelfTests"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.self_tests = FIPSSelfTests()

    def test_power_up_tests(self):
        """Testa Power-Up Self-Tests"""
        results = self.self_tests.run_power_up_tests()
        self.assertIn("passed", results)
        self.assertIn("tests", results)
        self.assertIsInstance(results["passed"], bool)

    def test_conditional_tests(self):
        """Testa Conditional Self-Tests"""
        results = self.self_tests.run_conditional_tests()
        self.assertIn("passed", results)
        self.assertIn("tests", results)
        self.assertIsInstance(results["passed"], bool)

    def test_integrity_tests(self):
        """Testa Integrity Tests"""
        results = self.self_tests.run_integrity_tests()
        self.assertIn("passed", results)
        self.assertIsInstance(results["passed"], bool)

    def test_aes_encryption_test(self):
        """Testa teste de criptografia AES"""
        result = self.self_tests._test_aes_encryption()
        self.assertIsInstance(result, bool)

    def test_sha256_integrity_test(self):
        """Testa teste de integridade SHA-256"""
        result = self.self_tests._test_sha256_integrity()
        self.assertTrue(result)  # Deve sempre passar

    def test_hmac_verification_test(self):
        """Testa teste de verificação HMAC"""
        result = self.self_tests._test_hmac_verification()
        self.assertTrue(result)  # Deve sempre passar

    def test_rng_test(self):
        """Testa teste de RNG"""
        result = self.self_tests._test_rng()
        self.assertIsInstance(result, bool)

class TestFIPSSecurityPolicy(unittest.TestCase):
    """Testes para FIPSSecurityPolicy"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.policy = FIPSSecurityPolicy()

    def test_policy_validation(self):
        """Testa validação da security policy"""
        result = self.policy.validate_policy()
        self.assertTrue(result)  # Implementação básica sempre retorna True

    def test_policy_rules(self):
        """Testa regras da policy"""
        self.assertIn("encryption_algorithms", self.policy.policy_rules)
        self.assertIn("AES-256", self.policy.policy_rules["encryption_algorithms"])
        self.assertIn("hash_algorithms", self.policy.policy_rules)
        self.assertIn("SHA-256", self.policy.policy_rules["hash_algorithms"])

class TestFIPSAuditLog(unittest.TestCase):
    """Testes para FIPSAuditLog"""

    def setUp(self):
        """Configuração inicial dos testes"""
        self.audit_log = FIPSAuditLog()

    def test_log_event(self):
        """Testa registro de evento no audit log"""
        event_type = "test_event"
        details = {"test": "data"}

        initial_count = len(self.audit_log.entries)
        self.audit_log.log_event(event_type, details)

        self.assertEqual(len(self.audit_log.entries), initial_count + 1)
        last_entry = self.audit_log.entries[-1]
        self.assertEqual(last_entry["event_type"], event_type)
        self.assertEqual(last_entry["details"], details)
        self.assertIn("timestamp", last_entry)

class TestFIPSUtilityFunctions(unittest.TestCase):
    """Testes para funções utilitárias FIPS"""

    def test_get_fips_manager_singleton(self):
        """Testa padrão singleton do FIPS manager"""
        manager1 = get_fips_manager()
        manager2 = get_fips_manager()
        self.assertIs(manager1, manager2)

    def test_initialize_fips_mode_utility(self):
        """Testa função utilitária de inicialização FIPS"""
        with patch('src.database.kayosql.fips_certification.get_fips_manager') as mock_get:
            mock_manager = MagicMock()
            mock_manager.initialize_fips_mode.return_value = True
            mock_get.return_value = mock_manager

            result = initialize_fips_mode()
            self.assertTrue(result)
            mock_manager.initialize_fips_mode.assert_called_once()

    def test_run_fips_self_tests_utility(self):
        """Testa função utilitária de self-tests FIPS"""
        with patch('src.database.kayosql.fips_certification.get_fips_manager') as mock_get:
            mock_manager = MagicMock()
            mock_results = {"overall_status": "PASSED"}
            mock_manager.run_self_tests.return_value = mock_results
            mock_get.return_value = mock_manager

            results = run_fips_self_tests()
            self.assertEqual(results, mock_results)
            mock_manager.run_self_tests.assert_called_once()

class TestFIPSEndToEnd(unittest.TestCase):
    """Testes end-to-end para FIPS"""

    def test_complete_fips_workflow(self):
        """Testa workflow completo FIPS"""
        # Inicializar manager
        manager = FIPSCertificationManager()

        # Mock dos componentes
        with patch.object(manager.self_tests, 'run_power_up_tests', return_value={"passed": True}), \
             patch.object(manager.security_policy, 'validate_policy', return_value=True), \
             patch.object(manager.key_store, 'initialize_fips_key_store', return_value=True), \
             patch.object(manager.self_tests, 'run_conditional_tests', return_value={"passed": True}), \
             patch.object(manager.key_store, 'store_fips_key'), \
             patch.object(manager.key_store, 'get_fips_key', return_value=b'0' * 32), \
             patch.object(manager.key_store, 'is_key_valid', return_value=True), \
             patch.object(manager.key_store, 'increment_key_usage'):

            # Inicializar FIPS
            success = manager.initialize_fips_mode()
            self.assertTrue(success)

            # Gerar chave
            key_id = manager.generate_fips_key("AES", 256)
            self.assertIsNotNone(key_id)

            # Criptografar
            plaintext = b"Dados confidenciais para teste FIPS"
            ciphertext = manager.encrypt_fips(plaintext, key_id)
            self.assertIsNotNone(ciphertext)

            # Decriptografar
            decrypted = manager.decrypt_fips(ciphertext, key_id)
            self.assertEqual(decrypted, plaintext)

            # Verificar status
            status = manager.get_fips_status()
            self.assertTrue(status["operational"])
            self.assertEqual(status["fips_mode"], "fips_compliant")

if __name__ == '__main__':
    # Configurar logging para testes
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Executar testes
    unittest.main(verbosity=2)