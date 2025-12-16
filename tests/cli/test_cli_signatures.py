#!/usr/bin/env python3
"""
 TESTES DE INTEGRAÇÃO DO CLI - ASSINATURAS DIGITAIS
Valida workflow completo: encrypt + sign → decrypt + verify

Autor: KAYOS SYSTEMS
Data: Janeiro 2025
Versão: 1.0.0 (Phase 3.7 - Task 3)
"""

import pytest
import subprocess
import os
import json
import tempfile
from pathlib import Path
import sys

# Paths
CLI_PATH = Path(__file__).parent.parent.parent / "src" / "cli" / "kayoscrypto_cli.py"


class TestCLISignatures:
    """Testes de integração para assinaturas digitais no CLI"""
    
    @pytest.fixture
    def temp_dir(self):
        """Diretório temporário para testes"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def sample_file(self, temp_dir):
        """Arquivo de teste"""
        file_path = temp_dir / "test.txt"
        file_path.write_text("KayosCrypto Phase 3.7 - Ed25519 Integration Test\n" * 100)
        return file_path
    
    def run_cli(self, args, input_data=None):
        """Executa CLI usando o Python do virtualenv sempre que possível."""
        repo_root = Path(__file__).resolve().parents[2]
        venv_python = repo_root / '.venv' / 'bin' / 'python'
        python_exec = venv_python if venv_python.exists() else Path(sys.executable)
        cmd = [str(python_exec), str(CLI_PATH)] + args
        env = os.environ.copy()
        repo_root_str = str(repo_root)
        existing_path = env.get('PYTHONPATH')
        env['PYTHONPATH'] = f"{repo_root_str}:{existing_path}" if existing_path else repo_root_str
        result = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            env=env,
        )
        return result
    
    def test_hmac_signature_workflow(self, temp_dir, sample_file):
        """
        Teste 1: Workflow completo com HMAC (v6.0.3)
        
        Passos:
        1. Encrypt + Sign (HMAC)
        2. Verificar .sig criado
        3. Decrypt + Verify
        4. Validar plaintext == original
        """
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        encrypted_file = temp_dir / "test.txt.kayos"
        sig_file = temp_dir / "test.txt.kayos.sig"
        decrypted_file = temp_dir / "test_decrypted.txt"
        
        # 1. Encrypt + Sign HMAC
        result = self.run_cli([
            "encrypt",
            str(sample_file),
            "-o", str(encrypted_file),
            "--signature-type", "hmac"
        ], input_data=f"{password}\n")
        
        assert result.returncode == 0, f"Encrypt failed: {result.stderr}"
        assert encrypted_file.exists(), "Encrypted file not created"
        assert sig_file.exists(), "Signature file not created"
        
        # 2. Verificar .sig (HMAC)
        with open(sig_file, 'r') as f:
            sig_data = json.load(f)
        
        assert sig_data['version'] == 1, "Version should be 1 (HMAC)"
        assert sig_data['type'] == 'hmac', "Type should be hmac"
        assert 'forward' in sig_data
        assert 'backward' in sig_data
        assert 'checksum' in sig_data
        assert 'public_key' in sig_data
        assert 'timestamp' in sig_data
        
        # 3. Decrypt + Verify
        result = self.run_cli([
            "decrypt",
            str(encrypted_file),
            "-o", str(decrypted_file)
        ], input_data=f"{password}\n")
        
        assert result.returncode == 0, f"Decrypt failed: {result.stderr}"
        assert " Assinatura válida!" in result.stdout, "Signature verification should pass"
        assert decrypted_file.exists(), "Decrypted file not created"
        
        # 4. Validar plaintext
        original = sample_file.read_text()
        decrypted = decrypted_file.read_text()
        assert decrypted == original, "Decrypted content mismatch"
    
    def test_ed25519_signature_workflow(self, temp_dir, sample_file):
        """
        Teste 2: Workflow completo com Ed25519 (v6.1)
        
        Passos:
        1. Encrypt + Sign (Ed25519) + Save Keypair
        2. Verificar .sig e keypair criados
        3. Decrypt + Verify (TRUE asymmetric)
        4. Validar plaintext == original
        """
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        encrypted_file = temp_dir / "test.txt.kayos"
        sig_file = temp_dir / "test.txt.kayos.sig"
        keypair_file = temp_dir / "keypair.json"
        decrypted_file = temp_dir / "test_decrypted.txt"
        
        # 1. Encrypt + Sign Ed25519
        result = self.run_cli([
            "encrypt",
            str(sample_file),
            "-o", str(encrypted_file),
            "--signature-type", "ed25519",
            "--save-keypair", str(keypair_file)
        ], input_data=f"{password}\n")
        
        assert result.returncode == 0, f"Encrypt failed: {result.stderr}"
        assert encrypted_file.exists(), "Encrypted file not created"
        assert sig_file.exists(), "Signature file not created"
        assert keypair_file.exists(), "Keypair file not created"
        
        # 2. Verificar .sig (Ed25519)
        with open(sig_file, 'r') as f:
            sig_data = json.load(f)
        
        assert sig_data['version'] == 2, "Version should be 2 (Ed25519)"
        assert sig_data['type'] == 'ed25519', "Type should be ed25519"
        assert 'forward' in sig_data
        assert 'backward' in sig_data
        assert 'checksum' in sig_data
        assert 'public_key' in sig_data
        assert 'timestamp' in sig_data
        
        # Verificar keypair (assimétrico)
        with open(keypair_file, 'r') as f:
            keypair = json.load(f)
        
        assert 'private_key' in keypair
        assert 'public_key' in keypair
        assert keypair['private_key'] != keypair['public_key'], "Keys should be different (asymmetric)"
        
        # 3. Decrypt + Verify
        result = self.run_cli([
            "decrypt",
            str(encrypted_file),
            "-o", str(decrypted_file)
        ], input_data=f"{password}\n")
        
        assert result.returncode == 0, f"Decrypt failed: {result.stderr}"
        assert " Assinatura válida!" in result.stdout, "Signature verification should pass"
        assert "(version 2)" in result.stdout, "Should show version 2 (Ed25519)"
        assert decrypted_file.exists(), "Decrypted file not created"
        
        # 4. Validar plaintext
        original = sample_file.read_text()
        decrypted = decrypted_file.read_text()
        assert decrypted == original, "Decrypted content mismatch"
    
    def test_tampered_signature_detection(self, temp_dir, sample_file):
        """
        Teste 3: Detectar adulteração de assinatura
        
        Passos:
        1. Encrypt + Sign
        2. Modificar ciphertext (adulterar)
        3. Decrypt + Verify → deve falhar
        """
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        encrypted_file = temp_dir / "test.txt.kayos"
        sig_file = temp_dir / "test.txt.kayos.sig"
        
        # 1. Encrypt + Sign
        result = self.run_cli([
            "encrypt",
            str(sample_file),
            "-o", str(encrypted_file),
            "--signature-type", "ed25519"
        ], input_data=f"{password}\n")
        
        assert result.returncode == 0, f"Encrypt failed: {result.stderr}"
        
        # 2. Adulterar ciphertext (modificar 1 byte no meio)
        with open(encrypted_file, 'rb') as f:
            ciphertext = bytearray(f.read())
        
        # Modificar byte no meio (offset 500)
        if len(ciphertext) > 500:
            ciphertext[500] ^= 0xFF  # Flip all bits
        
        with open(encrypted_file, 'wb') as f:
            f.write(ciphertext)
        
        # 3. Decrypt + Verify → deve detectar adulteração
        result = self.run_cli([
            "decrypt",
            str(encrypted_file),
            "-o", str(temp_dir / "test_decrypted.txt")
        ], input_data=f"N\n")  # Responder 'N' ao prompt de continuar
        
        assert " ASSINATURA INVÁLIDA!" in result.stdout, "Should detect tampered signature"
        assert "Arquivo pode ter sido adulterado" in result.stdout
        assert result.returncode == 1, "Should abort on invalid signature"
    
    def test_missing_signature_graceful(self, temp_dir, sample_file):
        """
        Teste 4: Decrypt sem .sig deve funcionar normalmente
        
        Passos:
        1. Encrypt SEM assinatura
        2. Decrypt → deve funcionar (sem verificação)
        """
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        encrypted_file = temp_dir / "test.txt.kayos"
        decrypted_file = temp_dir / "test_decrypted.txt"
        
        # 1. Encrypt SEM assinatura (não passar --signature-type)
        result = self.run_cli([
            "encrypt",
            str(sample_file),
            "-o", str(encrypted_file)
        ], input_data=f"{password}\n")
        
        assert result.returncode == 0, f"Encrypt failed: {result.stderr}"
        assert encrypted_file.exists()
        assert not (temp_dir / "test.txt.kayos.sig").exists(), ".sig should NOT be created"
        
        # 2. Decrypt (sem .sig)
        result = self.run_cli([
            "decrypt",
            str(encrypted_file),
            "-o", str(decrypted_file)
        ], input_data=f"{password}\n")
        
        assert result.returncode == 0, f"Decrypt failed: {result.stderr}"
        assert " Verificando assinatura" not in result.stdout, "Should skip signature verification"
        assert decrypted_file.exists()
        
        # Validar plaintext
        original = sample_file.read_text()
        decrypted = decrypted_file.read_text()
        assert decrypted == original


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
