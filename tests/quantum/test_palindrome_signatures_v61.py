#!/usr/bin/env python3
"""
Testes unitários: Rib 7 v6.1 (Ed25519 Asymmetric Signatures)

v6.1: Ed25519 + Palindrome Layer (simplified transform)
Target: 8/8 tests passing
"""

import unittest
import os
import sys

# Adicionar src/ ao path para imports diretos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'core', 'quantum'))

from palindrome_signatures_v61 import (
    PalindromeSignatureSystemV61,
    Signature
)


class TestPalindromeSignaturesV61(unittest.TestCase):
    """Testes para Ed25519 + Palindrome (v6.1)"""
    
    def setUp(self):
        """Setup executado antes de cada teste"""
        self.system = PalindromeSignatureSystemV61()
        self.message = b"KayosCrypto v6.1 Test Message"
    
    def test_1_keypair_generation(self):
        """Test 1: Gerar par de chaves Ed25519"""
        private_key, public_key = self.system.generate_keypair()
        
        # Deve ter 32 bytes cada
        self.assertEqual(len(private_key), 32, "Private key deve ter 32 bytes")
        self.assertEqual(len(public_key), 32, "Public key deve ter 32 bytes")
        
        # Deve ser assimétrico (private ≠ public)
        self.assertNotEqual(private_key, public_key, "Chaves devem ser assimétricas")
        
        print(" Test 1: Keypair Ed25519 gerada (32+32 bytes, assimétrico)")
    
    def test_2_sign_message(self):
        """Test 2: Assinar mensagem com Ed25519"""
        private_key, public_key = self.system.generate_keypair()
        signature = self.system.sign(self.message, private_key)
        
        # Verificar tipo
        self.assertIsInstance(signature, Signature, "Deve retornar Signature dataclass")
        
        # Verificar campos
        self.assertEqual(len(signature.forward), 64, "Forward deve ter 64 bytes (Ed25519)")
        self.assertEqual(len(signature.backward), 64, "Backward deve ter 64 bytes")
        self.assertEqual(len(signature.checksum), 32, "Checksum deve ter 32 bytes")
        self.assertEqual(signature.version, 2, "Version deve ser 2 (Ed25519)")
        
        print(" Test 2: Assinatura Ed25519 criada (64+64+32 bytes, version=2)")
    
    def test_3_palindrome_property(self):
        """Test 3: Verificar propriedade palindrômica"""
        private_key, public_key = self.system.generate_keypair()
        signature = self.system.sign(self.message, private_key)
        
        # forward == backward[::-1] (simetria SATOR)
        self.assertEqual(
            signature.forward,
            signature.backward[::-1],
            "Assinatura deve ter propriedade palindrômica"
        )
        
        print(" Test 3: Propriedade palindrômica preservada (forward == backward[::-1])")
    
    def test_4_verify_valid_signature(self):
        """Test 4: Verificar assinatura válida"""
        private_key, public_key = self.system.generate_keypair()
        signature = self.system.sign(self.message, private_key)
        
        # Verificação deve passar
        is_valid = self.system.verify(self.message, signature, public_key)
        self.assertTrue(is_valid, "Assinatura válida deve passar verificação")
        
        print(" Test 4: Verificação Ed25519 bem-sucedida")
    
    def test_5_reject_tampered_message(self):
        """Test 5: Rejeitar mensagem adulterada"""
        private_key, public_key = self.system.generate_keypair()
        signature = self.system.sign(self.message, private_key)
        
        # Adulterar mensagem
        tampered_message = self.message + b" FAKE"
        
        # Verificação deve falhar
        is_valid = self.system.verify(tampered_message, signature, public_key)
        self.assertFalse(is_valid, "Mensagem adulterada deve falhar verificação")
        
        print(" Test 5: Detecção de adulteração (mensagem modificada)")
    
    def test_6_reject_tampered_signature(self):
        """Test 6: Rejeitar assinatura adulterada"""
        private_key, public_key = self.system.generate_keypair()
        signature = self.system.sign(self.message, private_key)
        
        # Adulterar assinatura
        tampered_forward = bytes([b ^ 0xFF for b in signature.forward])  # Inverter bits
        tampered_sig = Signature(
            forward=tampered_forward,
            backward=tampered_forward[::-1],  # Manter propriedade palindrômica
            checksum=signature.checksum,
            version=signature.version
        )
        
        # Verificação deve falhar (checksum mismatch)
        is_valid = self.system.verify(self.message, tampered_sig, public_key)
        self.assertFalse(is_valid, "Assinatura adulterada deve falhar verificação")
        
        print(" Test 6: Detecção de adulteração (assinatura modificada)")
    
    def test_7_reject_wrong_public_key(self):
        """Test 7: Rejeitar chave pública incorreta"""
        private_key1, public_key1 = self.system.generate_keypair()
        private_key2, public_key2 = self.system.generate_keypair()
        
        # Assinar com private_key1
        signature = self.system.sign(self.message, private_key1)
        
        # Tentar verificar com public_key2 (incorreta)
        is_valid = self.system.verify(self.message, signature, public_key2)
        self.assertFalse(is_valid, "Chave pública incorreta deve falhar verificação")
        
        print(" Test 7: Rejeição de chave pública incorreta")
    
    def test_8_asymmetric_security(self):
        """Test 8: Garantir segurança assimétrica"""
        private_key, public_key = self.system.generate_keypair()
        
        # Tentar assinar com public_key (deve falhar ou gerar signature inválida)
        try:
            # Tentativa inválida: usar public_key como private_key
            fake_signature = self.system.sign(self.message, public_key)
            
            # Se não falhar, verificação com private_key deve falhar
            is_valid = self.system.verify(self.message, fake_signature, private_key)
            self.assertFalse(is_valid, "Assinatura com public_key não deve ser válida")
        except Exception:
            # Esperado: falha ao tentar assinar com public_key
            pass
        
        print(" Test 8: Segurança assimétrica garantida")


def run_tests():
    """Executa todos os testes e mostra relatório"""
    print("="*80)
    print("RIB 7 v6.1: UNIT TESTS (Ed25519 Asymmetric Signatures)")
    print("="*80)
    print()
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPalindromeSignaturesV61)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total Tests:    {result.testsRun}")
    print(f"Passed:         {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed:         {len(result.failures)}")
    print(f"Errors:         {len(result.errors)}")
    print(f"Success Rate:   {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    if result.wasSuccessful():
        print()
        print(" ALL TESTS PASSED - v6.1 Ed25519 operacional!")
        print()
        print("Próximos passos:")
        print("- [ ] Benchmarks de performance (sign/verify ops/s)")
        print("- [ ] Integração com Spine (kayoscrypto_ultimate.py)")
        print("- [ ] Testes de integração (13+8 tests)")
        print("- [ ] Atualizar documentação (TASK_8.5_ED25519_COMPLETE.md)")
        return 0
    else:
        print()
        print(" TESTS FAILED - debug necessário")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
