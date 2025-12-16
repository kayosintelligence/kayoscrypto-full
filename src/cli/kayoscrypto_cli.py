#!/usr/bin/env python3
"""
 KAYOSCRYPTO CLI - SISTEMA DE CRIPTOGRAFIA DE ARQUIVOS/PASTAS
Interface de linha de comando para criptografia Ezequiel

Autor: KAYOS SYSTEMS
Data: 12 de outubro de 2025
Versão: 2.0.0
"""

import sys
import os
from pathlib import Path
import argparse
import json
import getpass
from datetime import datetime, timezone
import hashlib
import base64
from typing import List, Optional

# Garantir que raiz do repositório e pasta src estejam no sys.path antes de outros imports
REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

try:
    from src.quantum import get_quantum_hook
    from src.quantum.resistance_manager import QuantumResistanceManager
    from src.quantum.entropy_pool import GeometricEntropyPool
    from src.core.quantum.entropy_pool import (
        build_entropy_snapshot,
        persist_entropy_snapshot,
    )
    from src.core.quantum.certification_tracker import CertificationTracker
    QUANTUM_ASSURANCE_AVAILABLE = True
    CERTIFICATION_TRACKER_AVAILABLE = True
except ImportError:
    try:
        from quantum import get_quantum_hook  # type: ignore
        from quantum.resistance_manager import QuantumResistanceManager  # type: ignore
        from quantum.entropy_pool import GeometricEntropyPool  # type: ignore
        from src.core.quantum.entropy_pool import (  # type: ignore
            build_entropy_snapshot,
            persist_entropy_snapshot,
        )
        from src.core.quantum.certification_tracker import CertificationTracker  # type: ignore
        QUANTUM_ASSURANCE_AVAILABLE = True
        CERTIFICATION_TRACKER_AVAILABLE = True
    except ImportError:
        QUANTUM_ASSURANCE_AVAILABLE = False
        CERTIFICATION_TRACKER_AVAILABLE = False
        CertificationTracker = None  # type: ignore
        build_entropy_snapshot = None  # type: ignore
        persist_entropy_snapshot = None  # type: ignore

# Adicionar paths
sys.path.insert(0, str(Path(__file__).parent / "src/enterprise3d/KayosCryptoEnterprise3D/src/cube"))
sys.path.insert(0, str(Path(__file__).parent / "src/licensing/KayosCryptoCloudLicensing"))
sys.path.insert(0, str(Path(__file__).parent / "src/suite/KayosCryptoSuite/core"))
sys.path.insert(0, str(Path(__file__).parent))  # Para fibonacci_permutation.py

try:
    from src.core.kayoscrypto_final import KayosCryptoFinal
    KAYOSCRYPTO_FINAL_AVAILABLE = True
except ImportError as e:
    KAYOSCRYPTO_FINAL_AVAILABLE = False
    print(f"  KayosCrypto Final não disponível: {e}")
    raise

# Importar KayosCryptoUltimate (v6.0 QUANTUM + v6.1 Ed25519)
try:
    from src.core.kayoscrypto_ultimate import KayosCryptoUltimate
    KAYOSCRYPTO_ULTIMATE_AVAILABLE = True
except ImportError as e:
    KAYOSCRYPTO_ULTIMATE_AVAILABLE = False
    print(f"  KayosCrypto Ultimate (v6.0) não disponível: {e}")
    raise

# Manter compatibilidade com versões antigas
try:
    from ezekiel_wheel_engine import EzekielWheelEngine, EzekielWheel, PHI, FIBONACCI_SEQUENCE
    from fibonacci_permutation import FibonacciPermutation
    EZEKIEL_AVAILABLE = True
except ImportError as e:
    EZEKIEL_AVAILABLE = False


# =====================================================================
# KAYOSCRYPTO FILE ENCRYPTOR
# =====================================================================

class KayosCryptoFileEncryptor:
    """
    Sistema de criptografia de arquivos/pastas usando Ezekiel Engine
    """
    
    def __init__(self):
        """Inicializa o encryptor"""
        # Prioridade: KayosCryptoFinal (nova versão)
        if KAYOSCRYPTO_FINAL_AVAILABLE:
            self.crypto_engine = KayosCryptoFinal()
            self.engine_type = "kayoscrypto_final"
            print(" KayosCrypto Final Engine carregado!")
        elif EZEKIEL_AVAILABLE:
            self.ezekiel_engine = EzekielWheelEngine(dimension=5)
            self.crypto_engine = None
            self.engine_type = "fibonacci_permutation"
            print("  Usando Fibonacci Permutation (versão antiga)")
        else:
            self.ezekiel_engine = None
            self.crypto_engine = None
            self.engine_type = "xor_fallback"
            print("  Usando XOR fallback (básico)")
        
        self.version = "3.0.0"  # Atualizado para v3.0.0
    
    def generate_key_from_password(self, password: str, salt: bytes = None) -> tuple:
        """
        Gera chave criptográfica a partir de senha
        
        Args:
            password: Senha do usuário
            salt: Salt (se None, gera novo)
        
        Returns:
            (key, salt) - Chave de 32 bytes e salt usado
        """
        if salt is None:
            salt = os.urandom(32)
        
        # Derivar chave usando PBKDF2 com SHA3-512
        key = hashlib.pbkdf2_hmac(
            'sha3_512',
            password.encode('utf-8'),
            salt,
            iterations=100000,
            dklen=32
        )
        
        return key, salt
    
    def encrypt_file(
        self,
        input_path: str,
        password: str,
        output_path: str = None,
        fibonacci_level: int = 8,
        quantum_mode: str = 'off',
        quantum_assurance: bool = False,
        quantum_hooks: Optional[List[str]] = None,
    ) -> dict:
        """
        Criptografa um arquivo
        
        Args:
            input_path: Caminho do arquivo original
            password: Senha para criptografia
            output_path: Caminho do arquivo criptografado (se None, adiciona .kayos)
            fibonacci_level: Nível Fibonacci (1-13)
            quantum_mode: Controle do modo Quantum Ultimate (off/compatible/enhanced)
            quantum_assurance: Habilita relatório de métricas pós-quantum
            quantum_hooks: Lista opcional de hooks Quantum Assurance a ativar
        
        Returns:
            Dicionário com informações da criptografia
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")
        
        if not input_path.is_file():
            raise ValueError(f"Não é um arquivo: {input_path}")
        
        # Output path
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + '.kayos')
        else:
            output_path = Path(output_path)
        
        # Ler arquivo
        print(f" Lendo arquivo: {input_path.name} ({input_path.stat().st_size} bytes)")
        with open(input_path, 'rb') as f:
            plaintext = f.read()
        
        # Gerar chave
        print(f" Gerando chave a partir da senha...")
        key, salt = self.generate_key_from_password(password)

        normalized_quantum_mode = (quantum_mode or 'off').lower()
        use_quantum = normalized_quantum_mode in ('compatible', 'enhanced')
        selected_hooks = [hook.strip() for hook in (quantum_hooks or []) if hook.strip()]
        use_assurance = quantum_assurance or bool(selected_hooks)
        if use_assurance and not QUANTUM_ASSURANCE_AVAILABLE:
            raise RuntimeError("Módulos de Quantum Assurance não disponíveis no ambiente atual")
        quantum_metadata = None

        if use_quantum and not KAYOSCRYPTO_ULTIMATE_AVAILABLE:
            raise RuntimeError("KayosCrypto Ultimate não disponível para modo quantum")

        # Criptografar
        assurance_payload = None
        manager = None
        pool = None
        tracker = None

        if use_assurance:
            manager = QuantumResistanceManager() if QUANTUM_ASSURANCE_AVAILABLE else None
            pool = GeometricEntropyPool() if QUANTUM_ASSURANCE_AVAILABLE else None
            tracker = CertificationTracker() if CERTIFICATION_TRACKER_AVAILABLE else None

        if use_quantum:
            print(" Criptografando com kayoscrypto_ultimate (modo quantum)...")
            entropy_mode = normalized_quantum_mode if normalized_quantum_mode in ('compatible', 'enhanced') else 'compatible'
            level = min(fibonacci_level, 5)
            try:
                quantum_cipher = KayosCryptoUltimate(
                    use_quantum=True,
                    quantum_entropy_mode=entropy_mode,
                    use_quantum_assurance=use_assurance,
                )
            except TypeError:
                quantum_cipher = KayosCryptoUltimate(
                    use_quantum=True,
                    quantum_entropy_mode=entropy_mode
                )
            encrypted_payload = quantum_cipher.encrypt(plaintext, password, level=level)
            encrypted, quantum_metadata = quantum_cipher.prepare_encryption_package(
                encrypted_payload,
                salt_encoding='hex'
            )
            engine_type = 'kayoscrypto_ultimate'

        elif KAYOSCRYPTO_FINAL_AVAILABLE and self.crypto_engine:
            print(f" Criptografando com {self.engine_type}...")
            level = min(fibonacci_level, 5)
            encrypted = self.crypto_engine.encrypt(plaintext, password, level=level)
            engine_type = self.engine_type

        elif EZEKIEL_AVAILABLE and self.ezekiel_engine:
            # NOVA ABORDAGEM: Permutação + Substituição + Difusão
            # (100% reversível, COM difusão bit-a-bit)
            
            # 1. Fibonacci spiral permutation
            encrypted = FibonacciPermutation.fibonacci_spiral_permutation(
                plaintext, 
                level=fibonacci_level,
                seed=key,
                reverse=False
            )
            
            # 1.5. Byte substitution (S-box para difusão)
            encrypted = FibonacciPermutation.byte_substitution(encrypted, key, reverse=False)
            
            # 2. Golden Ratio permutation
            encrypted = FibonacciPermutation.golden_ratio_permutation(
                encrypted,
                seed=key,
                reverse=False
            )
            
            # 2.5. Byte substitution (S-box novamente)
            encrypted = FibonacciPermutation.byte_substitution(encrypted, key + b"_layer2", reverse=False)
            
            # 3. Difusão criptográfica XOR (100% reversível)
            encrypted = FibonacciPermutation.xor_diffusion(
                encrypted,
                key=key,
                rounds=fibonacci_level
            )
            engine_type = "fibonacci_permutation"
            
        else:
            # Fallback: XOR com chave derivada
            encrypted = bytearray()
            key_expanded = (key * ((len(plaintext) // len(key)) + 1))[:len(plaintext)]
            for i, byte in enumerate(plaintext):
                encrypted.append(byte ^ key_expanded[i])
            encrypted = bytes(encrypted)
            engine_type = "xor_fallback"

        entropy_snapshot = None
        if use_assurance and manager and pool:
            snapshot = {
                "plaintext_bytes": plaintext,
                "ciphertext_bytes": encrypted,
                "key_bytes": key,
            }
            report = manager.assess_vulnerability(snapshot)
            report_payload = manager.build_report(report)
            suggestions = manager.recommend_improvements(report)
            entropy_key = pool.generate_quantum_safe_key(32, report.metrics)
            if build_entropy_snapshot:
                try:
                    entropy_snapshot = build_entropy_snapshot(
                        entropy_key,
                        context={
                            "source": "cli",
                            "mode": "file",
                            "engine_type": engine_type,
                            "hooks": selected_hooks,
                            "metrics": report.metrics,
                        },
                    )
                    if persist_entropy_snapshot:
                        persisted_path = persist_entropy_snapshot(entropy_snapshot)
                        if persisted_path:
                            entropy_snapshot['persisted_to'] = persisted_path
                except Exception as exc:  # pragma: no cover - telemetria best-effort
                    entropy_snapshot = {"error": str(exc)}
            hook_results = {}
            if selected_hooks:
                base_state = {
                    "phase": "encrypt",
                    "quantum_snapshot": dict(snapshot),
                    "ciphertext": encrypted,
                }
                for hook_name in selected_hooks:
                    hook = get_quantum_hook(hook_name)
                    if hook is None:
                        hook_results[hook_name] = {"error": "hook_not_found"}
                        continue
                    state = dict(base_state)
                    try:
                        hook.update(state)
                        hook_results[hook_name] = {
                            key: value
                            for key, value in state.items()
                            if key not in {"ciphertext", "quantum_snapshot", "phase"}
                        }
                    except Exception as exc:  # pragma: no cover - defensive guard
                        hook_results[hook_name] = {"error": str(exc)}
            assurance_payload = {
                "report": report_payload,
                "suggestions": suggestions,
                "metrics": report.metrics,
                "hooks": selected_hooks,
                "entropy_key": entropy_key.hex(),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            if entropy_snapshot:
                assurance_payload["entropy_snapshot"] = entropy_snapshot
            if hook_results:
                assurance_payload["hook_results"] = hook_results
            if tracker:
                metrics_payload = getattr(report, "metrics", None) or getattr(report, "raw_metrics", {})
                scorecard_payload = None
                if hasattr(report, "scorecard"):
                    scorecard_obj = getattr(report, "scorecard")
                    if scorecard_obj is not None:
                        if hasattr(scorecard_obj, "to_dict"):
                            scorecard_payload = scorecard_obj.to_dict()
                        elif isinstance(scorecard_obj, dict):
                            scorecard_payload = scorecard_obj
                findings_payload = list(getattr(report, "findings", [])) if hasattr(report, "findings") else None
                certification_snapshot = tracker.update_from_assurance(
                    metrics_payload,
                    hooks=hook_results or None,
                    context={
                        "source": "cli",
                        "input_path": str(input_path),
                        "engine_type": engine_type,
                        "quantum_mode": normalized_quantum_mode,
                        "entropy_snapshot": entropy_snapshot.get('persisted_to') if isinstance(entropy_snapshot, dict) else None,
                    },
                    suggestions=suggestions,
                    scorecard=scorecard_payload,
                    findings=findings_payload,
                )
                assurance_payload["certification"] = certification_snapshot
        
        # Criar metadata
        metadata = {
            'version': self.version,
            'engine_type': engine_type,
            'original_filename': input_path.name,
            'original_size': len(plaintext),
            'encrypted_size': len(encrypted),
            'fibonacci_level': fibonacci_level,
            'salt': base64.b64encode(salt).decode(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'ezekiel_engine': EZEKIEL_AVAILABLE,
            'crypto_method': engine_type,
            'angles': None
        }

        if use_quantum:
            metadata['quantum'] = {
                'mode': normalized_quantum_mode,
                'salt_encoding': 'hex',
                'quantum_salt': quantum_metadata.get('quantum_salt') if quantum_metadata else None
            }

        if assurance_payload:
            metadata['quantum_assurance'] = assurance_payload
        
        # Salvar arquivo criptografado
        print(f" Salvando arquivo criptografado: {output_path.name}")
        
        with open(output_path, 'wb') as f:
            # Header: KAYOS + versão (10 bytes)
            header = b'KAYOS' + self.version.encode('ascii').ljust(5)[:5]
            f.write(header)
            
            # Metadata length (4 bytes)
            metadata_json = json.dumps(metadata).encode('utf-8')
            f.write(len(metadata_json).to_bytes(4, 'big'))
            
            # Metadata
            f.write(metadata_json)
            
            # Encrypted data
            f.write(encrypted)
        
        print(f" Arquivo criptografado com sucesso!")
        print(f"   Original: {len(plaintext)} bytes")
        print(f"   Criptografado: {len(encrypted)} bytes")
        print(f"   Output: {output_path}")
        
        return {
            'input_path': str(input_path),
            'output_path': str(output_path),
            'original_size': len(plaintext),
            'encrypted_size': len(encrypted),
            'fibonacci_level': fibonacci_level,
            'metadata': metadata,
            'quantum_assurance': assurance_payload,
        }
    
    def decrypt_file(self, input_path: str, password: str, output_path: str = None) -> dict:
        """
        Descriptografa um arquivo
        
        Args:
            input_path: Caminho do arquivo criptografado (.kayos)
            password: Senha para descriptografia
            output_path: Caminho do arquivo descriptografado (se None, usa metadata)
        
        Returns:
            Dicionário com informações da descriptografia
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")
        
        # Ler arquivo criptografado
        print(f" Lendo arquivo criptografado: {input_path.name}")
        
        with open(input_path, 'rb') as f:
            # Ler header
            header = f.read(10)
            if not header.startswith(b'KAYOS'):
                raise ValueError("Arquivo inválido - não é um arquivo KayosCrypto")
            
            version = header[5:10].decode('ascii').strip()
            print(f"   Versão: {version}")
            
            # Ler metadata length
            metadata_len = int.from_bytes(f.read(4), 'big')
            
            # Ler metadata
            metadata_json = f.read(metadata_len)
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            print(f"   Arquivo original: {metadata['original_filename']}")
            print(f"   Fibonacci Level: {metadata['fibonacci_level']}")
            
            # Ler dados criptografados
            encrypted = f.read()
        
        # Recuperar salt
        salt = base64.b64decode(metadata['salt'])
        
        # Gerar chave
        print(f" Gerando chave a partir da senha...")
        key, _ = self.generate_key_from_password(password, salt)
        
        # Descriptografar
        print(f" Descriptografando com {metadata.get('engine_type', 'unknown')}...")
        
        engine_type = metadata.get('engine_type', self.engine_type)
        quantum_info = metadata.get('quantum') if metadata.get('quantum') else None

        if engine_type == 'kayoscrypto_ultimate' and KAYOSCRYPTO_ULTIMATE_AVAILABLE:
            level = min(metadata['fibonacci_level'], 5)
            entropy_mode = (quantum_info.get('mode') if quantum_info else 'compatible') or 'compatible'
            cipher = KayosCryptoUltimate(
                use_quantum=True,
                quantum_entropy_mode=entropy_mode if entropy_mode in ('compatible', 'enhanced') else 'compatible'
            )
            decrypt_metadata = None
            if quantum_info and quantum_info.get('quantum_salt'):
                decrypt_metadata = {'quantum_salt': quantum_info['quantum_salt']}
            if entropy_mode == 'enhanced' and decrypt_metadata is None:
                raise ValueError("Metadata quantum_salt ausente para descriptografia enhanced")
            decrypted = cipher.decrypt(encrypted, password, level=level, metadata=decrypt_metadata)

        elif engine_type == 'kayoscrypto_final' and KAYOSCRYPTO_FINAL_AVAILABLE:
            # ═══════════════════════════════════════════════════════════
            # NOVA VERSÃO: KayosCryptoFinal
            # ═══════════════════════════════════════════════════════════
            level = min(metadata['fibonacci_level'], 5)
            decrypted = self.crypto_engine.decrypt(encrypted, password, level=level)
            
        elif metadata.get('ezekiel_engine', False) and EZEKIEL_AVAILABLE and self.ezekiel_engine:
            # NOVA ABORDAGEM: Reverter em ORDEM INVERSA
            # (Permutação + Substituição + Difusão)
            
            # 3. Reverter difusão XOR
            decrypted = FibonacciPermutation.xor_diffusion_reverse(
                encrypted,
                key=key,
                rounds=metadata['fibonacci_level']
            )
            
            # 2.5. Reverter byte substitution layer 2
            decrypted = FibonacciPermutation.byte_substitution(decrypted, key + b"_layer2", reverse=True)
            
            # 2. Reverter Golden Ratio permutation
            decrypted = FibonacciPermutation.golden_ratio_permutation(
                decrypted,
                seed=key,
                reverse=True
            )
            
            # 1.5. Reverter byte substitution layer 1
            decrypted = FibonacciPermutation.byte_substitution(decrypted, key, reverse=True)
            
            # 1. Reverter Fibonacci spiral permutation
            decrypted = FibonacciPermutation.fibonacci_spiral_permutation(
                decrypted, 
                level=metadata['fibonacci_level'],
                seed=key,
                reverse=True  # REVERTER!
            )
            
        else:
            # Fallback: XOR com chave derivada (auto-reversível)
            decrypted = bytearray()
            key_expanded = (key * ((len(encrypted) // len(key)) + 1))[:len(encrypted)]
            for i, byte in enumerate(encrypted):
                decrypted.append(byte ^ key_expanded[i])
            decrypted = bytes(decrypted)
        
        # Output path
        if output_path is None:
            output_path = Path(metadata['original_filename'])
        else:
            output_path = Path(output_path)
        
        # Salvar arquivo descriptografado
        print(f" Salvando arquivo descriptografado: {output_path.name}")
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        
        print(f" Arquivo descriptografado com sucesso!")
        print(f"   Criptografado: {len(encrypted)} bytes")
        print(f"   Descriptografado: {len(decrypted)} bytes")
        print(f"   Output: {output_path}")
        
        return {
            'input_path': str(input_path),
            'output_path': str(output_path),
            'encrypted_size': len(encrypted),
            'decrypted_size': len(decrypted),
            'metadata': metadata
        }
    
    def encrypt_folder(
        self,
        folder_path: str,
        password: str,
        output_path: str = None,
        fibonacci_level: int = 8,
        quantum_mode: str = 'off',
        quantum_assurance: bool = False,
        quantum_hooks: Optional[List[str]] = None,
    ) -> dict:
        """
        Criptografa uma pasta inteira
        
        Args:
            folder_path: Caminho da pasta
            password: Senha para criptografia
            output_path: Caminho do arquivo .kayos (se None, usa nome da pasta)
            fibonacci_level: Nível Fibonacci (1-13)
            quantum_mode: Controle do modo Quantum Ultimate (off/compatible/enhanced)
            quantum_assurance: Habilita relatório de métricas pós-quantum
            quantum_hooks: Lista opcional de hooks Quantum Assurance a ativar
        
        Returns:
            Dicionário com informações da criptografia
        """
        folder_path = Path(folder_path)
        
        if not folder_path.exists():
            raise FileNotFoundError(f"Pasta não encontrada: {folder_path}")
        
        if not folder_path.is_dir():
            raise ValueError(f"Não é uma pasta: {folder_path}")

        normalized_quantum_mode = (quantum_mode or 'off').lower()
        use_quantum = normalized_quantum_mode in ('compatible', 'enhanced')
        selected_hooks = [hook.strip() for hook in (quantum_hooks or []) if hook.strip()]
        use_assurance = quantum_assurance or bool(selected_hooks)

        if use_assurance and not QUANTUM_ASSURANCE_AVAILABLE:
            raise RuntimeError("Módulos de Quantum Assurance não disponíveis no ambiente atual")

        assurance_payload = None
        manager = QuantumResistanceManager() if use_assurance and QUANTUM_ASSURANCE_AVAILABLE else None
        pool = GeometricEntropyPool() if use_assurance and QUANTUM_ASSURANCE_AVAILABLE else None
        tracker = CertificationTracker() if use_assurance and CERTIFICATION_TRACKER_AVAILABLE else None

        if use_quantum and not KAYOSCRYPTO_ULTIMATE_AVAILABLE:
            raise RuntimeError("KayosCrypto Ultimate não disponível para modo quantum em pastas")

        print(f" Preparando para criptografar pasta: {folder_path.name}")
        
        # Coletar todos os arquivos
        files = []
        for root, dirs, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = Path(root) / filename
                relative_path = file_path.relative_to(folder_path)
                files.append(relative_path)
        
        print(f"   Encontrados {len(files)} arquivos")
        
        # Criar estrutura de dados
        folder_data = {
            'folder_name': folder_path.name,
            'files': {},
            'total_size': 0
        }

        file_manifest = {}
        
        # Ler todos os arquivos
        for i, relative_path in enumerate(files, 1):
            file_path = folder_path / relative_path
            print(f"   [{i}/{len(files)}] Lendo: {relative_path}")
            
            with open(file_path, 'rb') as f:
                content = f.read()
            
            folder_data['files'][str(relative_path)] = base64.b64encode(content).decode()
            folder_data['total_size'] += len(content)

            file_manifest[str(relative_path)] = {
                'size': len(content),
                'sha256': hashlib.sha256(content).hexdigest()
            }
        
        # Serializar
        folder_json = json.dumps(folder_data, indent=2).encode('utf-8')
        
        print(f"\n Criptografando {len(files)} arquivos ({folder_data['total_size']} bytes)...")
        
        # Gerar chave/salt (necessário para compatibilidade de metadata)
        key, salt = self.generate_key_from_password(password)

        encrypted = b''
        angles = None
        engine_type = 'xor_fallback'
        quantum_info = None

        if use_quantum:
            print(" Criptografando com KayosCrypto Ultimate (modo quantum)...")
            entropy_mode = normalized_quantum_mode if normalized_quantum_mode in ('compatible', 'enhanced') else 'compatible'
            level = min(fibonacci_level, 5)
            quantum_cipher = KayosCryptoUltimate(
                use_quantum=True,
                quantum_entropy_mode=entropy_mode
            )
            encrypted_payload = quantum_cipher.encrypt(folder_json, password, level=level)
            encrypted, quantum_metadata = quantum_cipher.prepare_encryption_package(
                encrypted_payload,
                salt_encoding='hex'
            )

            if entropy_mode == 'enhanced' and not (quantum_metadata and quantum_metadata.get('quantum_salt')):
                raise ValueError("Modo enhanced requer quantum_salt no metadata do pacote")

            package_checksum = hashlib.sha256(encrypted).hexdigest()
            quantum_info = {
                'mode': entropy_mode,
                'salt_encoding': 'hex',
                'quantum_salt': quantum_metadata.get('quantum_salt') if quantum_metadata else None,
                'entropy_mode': entropy_mode,
                'package_checksum': package_checksum,
                'files': file_manifest
            }
            engine_type = 'kayoscrypto_ultimate'
        elif EZEKIEL_AVAILABLE and self.ezekiel_engine:
            encrypted = self.ezekiel_engine.fibonacci_spiral_rotation(folder_json, level=fibonacci_level)

            angle_x = (int.from_bytes(key[0:4], 'big') % 360)
            angle_y = (int.from_bytes(key[4:8], 'big') % 360)
            angle_z = (int.from_bytes(key[8:12], 'big') % 360)

            wheel = EzekielWheel(
                angle_x=angle_x * 3.14159 / 180,
                angle_y=angle_y * 3.14159 / 180,
                angle_z=angle_z * 3.14159 / 180
            )
            encrypted = self.ezekiel_engine.apply_ezekiel_wheel(encrypted, wheel)

            encrypted = self.ezekiel_engine.cryptographic_diffusion(encrypted, rounds=fibonacci_level)

            angles = {
                'x': angle_x,
                'y': angle_y,
                'z': angle_z
            }
            engine_type = 'ezekiel_folder'
        else:
            encrypted = bytearray()
            key_expanded = (key * ((len(folder_json) // len(key)) + 1))[:len(folder_json)]
            for i, byte in enumerate(folder_json):
                encrypted.append(byte ^ key_expanded[i])
            encrypted = bytes(encrypted)
            engine_type = 'xor_fallback'

        entropy_snapshot = None
        if use_assurance and manager and pool:
            snapshot = {
                "plaintext_bytes": folder_json,
                "ciphertext_bytes": encrypted,
                "key_bytes": key,
            }
            report = manager.assess_vulnerability(snapshot)
            report_payload = manager.build_report(report)
            suggestions = manager.recommend_improvements(report)
            entropy_key = pool.generate_quantum_safe_key(32, report.metrics)
            if build_entropy_snapshot:
                try:
                    entropy_snapshot = build_entropy_snapshot(
                        entropy_key,
                        context={
                            "source": "cli",
                            "mode": "folder",
                            "engine_type": engine_type,
                            "hooks": selected_hooks,
                            "metrics": report.metrics,
                        },
                    )
                    if persist_entropy_snapshot:
                        persisted_path = persist_entropy_snapshot(entropy_snapshot)
                        if persisted_path:
                            entropy_snapshot['persisted_to'] = persisted_path
                except Exception as exc:  # pragma: no cover - telemetria best-effort
                    entropy_snapshot = {"error": str(exc)}
            hook_results = {}
            if selected_hooks:
                base_state = {
                    "phase": "encrypt",
                    "quantum_snapshot": dict(snapshot),
                    "ciphertext": encrypted,
                }
                for hook_name in selected_hooks:
                    hook = get_quantum_hook(hook_name)
                    if hook is None:
                        hook_results[hook_name] = {"error": "hook_not_found"}
                        continue
                    state = dict(base_state)
                    try:
                        hook.update(state)
                        hook_results[hook_name] = {
                            key: value
                            for key, value in state.items()
                            if key not in {"ciphertext", "quantum_snapshot", "phase"}
                        }
                    except Exception as exc:  # pragma: no cover - defensive guard
                        hook_results[hook_name] = {"error": str(exc)}
            assurance_payload = {
                "report": report_payload,
                "suggestions": suggestions,
                "metrics": report.metrics,
                "hooks": selected_hooks,
                "entropy_key": entropy_key.hex(),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
            if entropy_snapshot:
                assurance_payload["entropy_snapshot"] = entropy_snapshot
            if hook_results:
                assurance_payload["hook_results"] = hook_results
            if tracker:
                metrics_payload = getattr(report, "metrics", None) or getattr(report, "raw_metrics", {})
                scorecard_payload = None
                if hasattr(report, "scorecard"):
                    scorecard_obj = getattr(report, "scorecard")
                    if scorecard_obj is not None:
                        if hasattr(scorecard_obj, "to_dict"):
                            scorecard_payload = scorecard_obj.to_dict()
                        elif isinstance(scorecard_obj, dict):
                            scorecard_payload = scorecard_obj
                findings_payload = list(getattr(report, "findings", [])) if hasattr(report, "findings") else None
                certification_snapshot = tracker.update_from_assurance(
                    metrics_payload,
                    hooks=hook_results or None,
                    context={
                        "source": "cli",
                        "folder_path": str(folder_path),
                        "quantum_mode": normalized_quantum_mode,
                        "engine_type": engine_type,
                        "entropy_snapshot": entropy_snapshot.get('persisted_to') if isinstance(entropy_snapshot, dict) else None,
                    },
                    suggestions=suggestions,
                    scorecard=scorecard_payload,
                    findings=findings_payload,
                )
                assurance_payload["certification"] = certification_snapshot
        
        # Metadata
        metadata = {
            'version': self.version,
            'type': 'folder',
            'engine_type': engine_type,
            'folder_name': folder_path.name,
            'file_count': len(files),
            'total_size': folder_data['total_size'],
            'encrypted_size': len(encrypted),
            'fibonacci_level': fibonacci_level,
            'salt': base64.b64encode(salt).decode(),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'ezekiel_engine': engine_type == 'ezekiel_folder',
            'angles': angles
        }

        if quantum_info:
            metadata['quantum'] = quantum_info

        if assurance_payload:
            metadata['quantum_assurance'] = assurance_payload
        
        # Output path
        if output_path is None:
            output_path = Path(f"{folder_path.name}.kayos")
        else:
            output_path = Path(output_path)
        
        # Salvar
        print(f" Salvando pasta criptografada: {output_path.name}")
        
        with open(output_path, 'wb') as f:
            # Header
            header = b'KAYOS' + self.version.encode('ascii').ljust(5)[:5]
            f.write(header)
            
            # Metadata
            metadata_json = json.dumps(metadata).encode('utf-8')
            f.write(len(metadata_json).to_bytes(4, 'big'))
            f.write(metadata_json)
            
            # Encrypted data
            f.write(encrypted)
        
        print(f" Pasta criptografada com sucesso!")
        print(f"   {len(files)} arquivos ({folder_data['total_size']} bytes)")
        print(f"   Criptografado: {len(encrypted)} bytes")
        print(f"   Output: {output_path}")
        
        return {
            'input_path': str(folder_path),
            'output_path': str(output_path),
            'file_count': len(files),
            'total_size': folder_data['total_size'],
            'encrypted_size': len(encrypted),
            'metadata': metadata,
            'quantum_assurance': assurance_payload,
        }
    
    def decrypt_folder(self, input_path: str, password: str, output_path: str = None) -> dict:
        """
        Descriptografa uma pasta
        
        Args:
            input_path: Caminho do arquivo .kayos
            password: Senha para descriptografia
            output_path: Caminho da pasta de saída (se None, usa metadata)
        
        Returns:
            Dicionário com informações da descriptografia
        """
        input_path = Path(input_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")
        
        print(f" Lendo arquivo criptografado: {input_path.name}")
        
        # Ler arquivo
        with open(input_path, 'rb') as f:
            # Header
            header = f.read(10)
            if not header.startswith(b'KAYOS'):
                raise ValueError("Arquivo inválido")
            
            # Metadata
            metadata_len = int.from_bytes(f.read(4), 'big')
            metadata_json = f.read(metadata_len)
            metadata = json.loads(metadata_json.decode('utf-8'))
            
            if metadata.get('type') != 'folder':
                raise ValueError("Não é uma pasta criptografada")
            
            print(f"   Pasta: {metadata['folder_name']}")
            print(f"   Arquivos: {metadata['file_count']}")
            
            # Dados criptografados
            encrypted = f.read()
        
        engine_type = metadata.get('engine_type', 'ezekiel_folder')
        quantum_info = metadata.get('quantum') if metadata.get('quantum') else None

        if quantum_info and quantum_info.get('package_checksum'):
            expected_checksum = quantum_info['package_checksum']
            actual_checksum = hashlib.sha256(encrypted).hexdigest()
            if actual_checksum != expected_checksum:
                raise ValueError("Checksum do pacote quantum inválido - arquivo corrompido")

        print(f" Descriptografando ({engine_type})...")

        if engine_type == 'kayoscrypto_ultimate' and KAYOSCRYPTO_ULTIMATE_AVAILABLE:
            entropy_mode = (quantum_info.get('mode') if quantum_info else 'compatible') or 'compatible'
            level = min(metadata.get('fibonacci_level', 3), 5)
            cipher = KayosCryptoUltimate(
                use_quantum=True,
                quantum_entropy_mode=entropy_mode if entropy_mode in ('compatible', 'enhanced') else 'compatible'
            )

            decrypt_metadata = None
            if quantum_info and quantum_info.get('quantum_salt'):
                decrypt_metadata = {'quantum_salt': quantum_info['quantum_salt']}

            if entropy_mode == 'enhanced' and not (decrypt_metadata and decrypt_metadata.get('quantum_salt')):
                raise ValueError("Metadata quantum_salt ausente para descriptografia enhanced")

            decrypted = cipher.decrypt(encrypted, password, level=level, metadata=decrypt_metadata)
        else:
            salt = base64.b64decode(metadata['salt'])
            key, _ = self.generate_key_from_password(password, salt)

            if metadata.get('ezekiel_engine', False) and EZEKIEL_AVAILABLE and self.ezekiel_engine:
                decrypted = self.ezekiel_engine.cryptographic_diffusion(
                    encrypted,
                    rounds=metadata['fibonacci_level']
                )

                angles = metadata.get('angles', {})
                wheel = EzekielWheel(
                    angle_x=-angles.get('x', 0) * 3.14159 / 180,
                    angle_y=-angles.get('y', 0) * 3.14159 / 180,
                    angle_z=-angles.get('z', 0) * 3.14159 / 180
                )
                decrypted = self.ezekiel_engine.apply_ezekiel_wheel(decrypted, wheel)

                decrypted = self.ezekiel_engine.fibonacci_spiral_rotation(
                    decrypted,
                    level=metadata['fibonacci_level']
                )
            else:
                decrypted = bytearray()
                key_expanded = (key * ((len(encrypted) // len(key)) + 1))[:len(encrypted)]
                for i, byte in enumerate(encrypted):
                    decrypted.append(byte ^ key_expanded[i])
                decrypted = bytes(decrypted)

        # Deserializar e validar conteúdo
        folder_data = json.loads(decrypted.decode('utf-8'))

        decoded_files = {}
        file_manifest = quantum_info.get('files') if quantum_info else None

        for relative_path, content_b64 in folder_data['files'].items():
            content = base64.b64decode(content_b64)

            if file_manifest and relative_path in file_manifest:
                expected = file_manifest[relative_path]
                if expected.get('size') is not None and expected['size'] != len(content):
                    raise ValueError(f"Tamanho divergente para {relative_path}")
                if expected.get('sha256'):
                    digest = hashlib.sha256(content).hexdigest()
                    if digest != expected['sha256']:
                        raise ValueError(f"Checksum divergente para {relative_path}")

            decoded_files[relative_path] = content

        recalculated_total = sum(len(content) for content in decoded_files.values())
        if folder_data.get('total_size') and recalculated_total != folder_data['total_size']:
            raise ValueError("Total de bytes não confere com metadata (possível corrupção)")
        
        # Output path
        if output_path is None:
            output_path = Path(folder_data['folder_name'])
        else:
            output_path = Path(output_path)
        
        # Criar pasta
        output_path.mkdir(parents=True, exist_ok=True)
        print(f" Criando pasta: {output_path.name}")
        
        # Restaurar arquivos
        for i, (relative_path, content) in enumerate(decoded_files.items(), 1):
            file_path = output_path / relative_path
            print(f"   [{i}/{len(folder_data['files'])}] Restaurando: {relative_path}")
            
            # Criar diretórios
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Decodificar e salvar
            with open(file_path, 'wb') as f:
                f.write(content)
        
        print(f" Pasta descriptografada com sucesso!")
        print(f"   {len(folder_data['files'])} arquivos restaurados")
        print(f"   Output: {output_path}")
        
        return {
            'input_path': str(input_path),
            'output_path': str(output_path),
            'file_count': len(folder_data['files']),
            'total_size': folder_data['total_size'],
            'metadata': metadata
        }
    
    def save_key_file(self, password: str, output_path: str, metadata: dict = None) -> str:
        """
        Salva arquivo de chave para backup
        
        Args:
            password: Senha original
            output_path: Caminho do arquivo .key
            metadata: Metadata opcional
        
        Returns:
            Caminho do arquivo salvo
        """
        output_path = Path(output_path)
        
        # Gerar hash da senha
        password_hash = hashlib.sha3_256(password.encode()).hexdigest()
        
        key_data = {
            'version': self.version,
            'password_hash': password_hash,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metadata': metadata or {}
        }
        
        with open(output_path, 'w') as f:
            json.dump(key_data, f, indent=2)
        
        print(f" Arquivo de chave salvo: {output_path}")
        print(f"     IMPORTANTE: Guarde este arquivo em local seguro!")
        print(f"     A senha original ainda é necessária para descriptografar!")
        
        return str(output_path)


# =====================================================================
# CLI INTERFACE
# =====================================================================

def main():
    """Interface CLI principal"""
    
    parser = argparse.ArgumentParser(
        description=' KayosCrypto CLI - Sistema de Criptografia de Arquivos/Pastas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Criptografar arquivo
  %(prog)s encrypt documento.pdf
  
  # Criptografar pasta
  %(prog)s encrypt minha_pasta/ -o backup.kayos
  
  # Descriptografar
  %(prog)s decrypt arquivo.kayos
  
  # Salvar chave de backup
  %(prog)s encrypt arquivo.txt --save-key chave.key
  
  # Nível Fibonacci personalizado
  %(prog)s encrypt arquivo.txt -l 13
  
  # Assinatura digital HMAC (v6.0.3, simétrica)
  %(prog)s encrypt arquivo.txt --signature-type hmac
  
  # Assinatura digital Ed25519 (v6.1, assimétrica TRUE)
  %(prog)s encrypt arquivo.txt --signature-type ed25519 --save-keypair keypair.json

Desenvolvido por: KAYOS SYSTEMS
Versão: 2.0.0 (QUANTUM v6.1 - Ed25519)
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando')
    
    # Comando: encrypt
    encrypt_parser = subparsers.add_parser('encrypt', help='Criptografar arquivo ou pasta')
    encrypt_parser.add_argument('input', help='Arquivo ou pasta para criptografar')
    encrypt_parser.add_argument('-o', '--output', help='Arquivo de saída (.kayos)')
    encrypt_parser.add_argument('-l', '--level', type=int, default=8, choices=range(1, 14),
                               help='Nível Fibonacci (1-13, padrão: 8)')
    encrypt_parser.add_argument('--quantum-mode', choices=['off', 'compatible', 'enhanced'], default='off',
                                help='Ativa KayosCrypto Ultimate com modo quantum (compatible ou enhanced)')
    encrypt_parser.add_argument('--quantum-assurance', action='store_true',
                                help='Habilita coleta de métricas Quantum Assurance durante a criptografia')
    encrypt_parser.add_argument('--quantum-hook', dest='quantum_hooks', action='append', default=None,
                                help='Registrar hook Quantum Assurance específico (pode ser usado múltiplas vezes)')
    encrypt_parser.add_argument('--save-key', help='Salvar arquivo de chave (.key)')
    encrypt_parser.add_argument('--signature-type', choices=['hmac', 'ed25519'], default=None,
                               help='Tipo de assinatura digital: hmac (v6.0.3, simétrica) ou ed25519 (v6.1, assimétrica TRUE)')
    encrypt_parser.add_argument('--save-keypair', help='Salvar par de chaves de assinatura (.json)')
    
    # Comando: decrypt
    decrypt_parser = subparsers.add_parser('decrypt', help='Descriptografar arquivo ou pasta')
    decrypt_parser.add_argument('input', help='Arquivo .kayos para descriptografar')
    decrypt_parser.add_argument('-o', '--output', help='Arquivo/pasta de saída')
    
    # Comando: info
    info_parser = subparsers.add_parser('info', help='Informações sobre arquivo .kayos')
    info_parser.add_argument('input', help='Arquivo .kayos')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Banner
    print("=" * 80)
    print(" KAYOSCRYPTO CLI - SISTEMA DE CRIPTOGRAFIA")
    print("=" * 80)
    print(f"Versão: 2.0.0")
    print(f"Ezekiel Engine: {' Disponível' if EZEKIEL_AVAILABLE else ' Indisponível (usando fallback)'}")
    print("=" * 80)
    print()
    
    encryptor = KayosCryptoFileEncryptor()
    
    try:
        if args.command == 'encrypt':
            # Solicitar senha
            password = getpass.getpass(" Digite a senha para criptografia: ")
            password_confirm = getpass.getpass(" Confirme a senha: ")
            
            if password != password_confirm:
                print(" Senhas não coincidem!")
                return 1
            
            quantum_mode = getattr(args, 'quantum_mode', 'off') or 'off'

            # Verificar se é arquivo ou pasta
            input_path = Path(args.input)
            
            if input_path.is_file():
                result = encryptor.encrypt_file(
                    args.input,
                    password,
                    args.output,
                    args.level,
                    quantum_mode=quantum_mode,
                    quantum_assurance=getattr(args, 'quantum_assurance', False),
                    quantum_hooks=getattr(args, 'quantum_hooks', None),
                )
            elif input_path.is_dir():
                result = encryptor.encrypt_folder(
                    args.input,
                    password,
                    args.output,
                    args.level,
                    quantum_mode=quantum_mode,
                    quantum_assurance=getattr(args, 'quantum_assurance', False),
                    quantum_hooks=getattr(args, 'quantum_hooks', None),
                )
            else:
                print(f" Arquivo ou pasta não encontrado: {args.input}")
                return 1
            
            # Salvar chave se solicitado
            if args.save_key:
                encryptor.save_key_file(password, args.save_key, result['metadata'])
            
            # Assinar arquivo criptografado (novo em v6.0 QUANTUM)
            if args.signature_type:  # ← CORRIGIDO: era args.sign
                if not KAYOSCRYPTO_ULTIMATE_AVAILABLE:
                    print("  Assinatura não disponível (KayosCrypto Ultimate v6.0 não instalado)")
                else:
                    print(f"\n  Assinando arquivo com {args.signature_type.upper()}...")
                    
                    # Inicializar sistema de assinatura
                    use_ed25519 = (args.signature_type == 'ed25519')
                    try:
                        cipher = KayosCryptoUltimate(use_quantum=True, use_ed25519=use_ed25519)
                    except TypeError as exc:
                        if 'permutation_strategy' in str(exc):
                            raise ImportError(
                                "KayosCryptoFinal desatualizado detectado durante assinatura. "
                                "Garanta que PYTHONPATH aponte para a raiz do repositório (pasta que contém src)."
                            ) from exc
                        raise
                    
                    # Gerar par de chaves
                    private_key, public_key = cipher.generate_keypair()
                    
                    # Ler ciphertext
                    output_file = args.output if args.output else (str(input_path) + '.kayos')
                    with open(output_file, 'rb') as f:
                        ciphertext = f.read()
                    
                    # Assinar
                    signature = cipher.sign_message(ciphertext, private_key)
                    
                    # Salvar assinatura no arquivo .kayos.sig (JSON, não binário!)
                    sig_file = output_file + '.sig'
                    sig_data = {
                        'version': signature.version,
                        'type': args.signature_type,
                        'forward': base64.b64encode(signature.forward).decode('ascii'),
                        'backward': base64.b64encode(signature.backward).decode('ascii'),
                        'checksum': base64.b64encode(signature.checksum).decode('ascii'),
                        'public_key': base64.b64encode(public_key).decode('ascii'),
                        'timestamp': datetime.now().isoformat()
                    }
                    with open(sig_file, 'w') as f:
                        json.dump(sig_data, f, indent=2)
                    
                    print(f" Assinatura salva: {sig_file}")
                    print(f"   Tipo: {args.signature_type} (version {signature.version})")
                    
                    # Salvar keypair se solicitado
                    if args.save_keypair:
                        keypair_data = {
                            'private_key': base64.b64encode(private_key).decode('ascii'),
                            'public_key': base64.b64encode(public_key).decode('ascii'),
                            'type': args.signature_type,
                            'created': datetime.now().isoformat()
                        }
                        with open(args.save_keypair, 'w') as f:
                            json.dump(keypair_data, f, indent=2)
                        print(f" Par de chaves salvo: {args.save_keypair}")
                        if use_ed25519:
                            print(f"     GUARDE O ARQUIVO COM SEGURANÇA (contém private_key assimétrico!)")
        
        elif args.command == 'decrypt':
            # Verificação de assinatura digital (antes da descriptografia)
            sig_file = args.input + '.sig'
            if os.path.exists(sig_file) and KAYOSCRYPTO_ULTIMATE_AVAILABLE:
                print("\n Verificando assinatura digital...")
                
                try:
                    # Carregar assinatura
                    with open(sig_file, 'r') as f:
                        sig_data = json.load(f)
                    
                    # Reconstruir Signature object
                    from src.core.quantum.palindrome_signatures import Signature
                    signature = Signature(
                        forward=base64.b64decode(sig_data['forward']),
                        backward=base64.b64decode(sig_data['backward']),
                        checksum=base64.b64decode(sig_data['checksum']),
                        version=sig_data['version']
                    )
                    public_key = base64.b64decode(sig_data['public_key'])
                    
                    # Inicializar cipher (v6.0.3 HMAC ou v6.1 Ed25519)
                    use_ed25519 = (sig_data['type'] == 'ed25519')
                    cipher = KayosCryptoUltimate(
                        use_quantum=True,
                        use_ed25519=use_ed25519
                    )
                    
                    # Ler ciphertext completo
                    with open(args.input, 'rb') as f:
                        ciphertext = f.read()
                    
                    # Verificar assinatura
                    is_valid = cipher.verify_signature(ciphertext, signature, public_key)
                    
                    # Exibir resultado
                    if is_valid:
                        print(f" Assinatura válida!")
                        print(f"   Tipo: {sig_data['type']} (version {sig_data['version']})")
                        print(f"   Data: {sig_data.get('timestamp', 'N/A')}")
                    else:
                        print(f" ASSINATURA INVÁLIDA!")
                        print(f"     AVISO: Arquivo pode ter sido adulterado!")
                        
                        # Perguntar se deseja continuar
                        response = input("\n Continuar descriptografia mesmo assim? (s/N): ")
                        if response.lower() != 's':
                            print(" Operação cancelada por segurança.")
                            return 1
                
                except Exception as e:
                    print(f"  Erro ao verificar assinatura: {e}")
                    print("Continuando descriptografia sem verificação...\n")
            
            # Solicitar senha
            password = getpass.getpass(" Digite a senha para descriptografia: ")
            
            # Verificar tipo de arquivo
            with open(args.input, 'rb') as f:
                f.seek(10)  # Pular header
                metadata_len = int.from_bytes(f.read(4), 'big')
                metadata_json = f.read(metadata_len)
                metadata = json.loads(metadata_json.decode('utf-8'))
            
            if metadata.get('type') == 'folder':
                result = encryptor.decrypt_folder(args.input, password, args.output)
            else:
                result = encryptor.decrypt_file(args.input, password, args.output)
        
        elif args.command == 'info':
            # Ler metadata
            with open(args.input, 'rb') as f:
                header = f.read(10)
                if not header.startswith(b'KAYOS'):
                    print(" Arquivo inválido")
                    return 1
                
                version = header[5:10].decode('ascii').strip()
                metadata_len = int.from_bytes(f.read(4), 'big')
                metadata_json = f.read(metadata_len)
                metadata = json.loads(metadata_json.decode('utf-8'))
            
            # Exibir informações
            print(" INFORMAÇÕES DO ARQUIVO")
            print("-" * 80)
            print(f"Versão: {version}")
            print(f"Tipo: {metadata.get('type', 'file')}")
            
            if metadata.get('type') == 'folder':
                print(f"Pasta: {metadata['folder_name']}")
                print(f"Arquivos: {metadata['file_count']}")
                print(f"Tamanho total: {metadata['total_size']:,} bytes")
            else:
                print(f"Arquivo: {metadata['original_filename']}")
                print(f"Tamanho original: {metadata['original_size']:,} bytes")
            
            print(f"Tamanho criptografado: {metadata['encrypted_size']:,} bytes")
            print(f"Fibonacci Level: {metadata['fibonacci_level']}")
            print(f"Motor: {metadata.get('engine_type', 'desconhecido')}")
            print(f"Ezekiel Engine: {'Sim' if metadata.get('ezekiel_engine') else 'Não'}")
            print(f"Timestamp: {metadata['timestamp']}")

            qa_metadata = metadata.get('quantum_assurance')
            if qa_metadata:
                report = qa_metadata.get('report', {})
                overall = report.get('overall', 'desconhecido').upper()
                metrics = report.get('metrics', {})
                print("\nQuantum Assurance:")
                print(f"  Overall: {overall}")
                if metrics:
                    avalanche = metrics.get('avalanche')
                    entropy_val = metrics.get('entropy')
                    log_sensitivity = metrics.get('log_sensitivity')
                    key_bits = metrics.get('key_bits')
                    if avalanche is not None:
                        print(f"  Avalanche: {avalanche:.3f}")
                    if entropy_val is not None:
                        print(f"  Entropy: {entropy_val:.3f}")
                    if log_sensitivity is not None:
                        print(f"  Log Sensitivity: {log_sensitivity:.3f}")
                    if key_bits is not None:
                        print(f"  Key Bits: {key_bits:.0f}")
                suggestions = qa_metadata.get('suggestions') or []
                if suggestions:
                    print("  Sugestões:")
                    for item in suggestions:
                        print(f"    - {item}")
                hooks_list = qa_metadata.get('hooks') or []
                if hooks_list:
                    print(f"  Hooks: {', '.join(hooks_list)}")
                entropy_key = qa_metadata.get('entropy_key')
                if entropy_key:
                    print(f"  Entropy Key: {entropy_key[:16]}…")

            if metadata.get('quantum'):
                q = metadata['quantum']
                print("\nQuantum Suite:")
                print(f"  Modo: {q.get('mode', 'off')}")
                salt_present = 'Sim' if q.get('quantum_salt') else 'Não'
                print(f"  quantum_salt registrado: {salt_present}")
                if q.get('quantum_salt'):
                    print(f"  Encoding: {q.get('salt_encoding', 'hex')}")
                if q.get('package_checksum'):
                    print(f"  package_checksum: {q['package_checksum']}")
                if q.get('files'):
                    print(f"  Arquivos monitorados: {len(q['files'])}")
            
            if metadata.get('angles'):
                print(f"\nÂngulos Ezequiel:")
                print(f"  X: {metadata['angles']['x']}°")
                print(f"  Y: {metadata['angles']['y']}°")
                print(f"  Z: {metadata['angles']['z']}°")
    
    except Exception as e:
        print(f"\n ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print()
    print("=" * 80)
    print(" Operação concluída com sucesso!")
    print("=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
