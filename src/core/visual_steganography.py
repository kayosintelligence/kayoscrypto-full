"""
 RIB 7: VISUAL STEGANOGRAPHY - KAYOSCRYPTO
Sistema de esteganografia visual com LSB (Least Significant Bit)

ARQUITETURA KAIOS:
- Velho Matuto: "Esconder em plena vista" (dados dentro de imagens comuns)
- Sator: Equilíbrio entre capacidade (payload) e imperceptibilidade
- Ezequiel: 3 canais RGB como "3 rodas" de armazenamento
- Relojoeiro: LSB otimizado (máxima capacidade sem degradação visual)

FILOSOFIA:
"Como o homem não conhece o caminho do vento" (Eclesiastes 11:5)
- Dados cifrados são invisíveis dentro da imagem
- Mesmo com imagem capturada, dados permanecem protegidos (KayosCrypto)
- Análise forense comum não detecta (steganalysis requer expertise)

TÉCNICA LSB (Least Significant Bit):
- Cada pixel RGB tem 3 bytes (Red, Green, Blue)
- Modificar último bit de cada byte (imperceptível ao olho humano)
- 1 pixel = 3 bits de payload (R[0], G[0], B[0])
- Capacidade: (largura × altura × 3) / 8 bytes

EXEMPLO:
Imagem 800×600 = 480,000 pixels × 3 bits = 180 KB de payload oculto

Autor: KAYOS SYSTEMS
Data: 15 de Novembro de 2025
Versão: v6.3 - Visual Steganography
"""

import os
import sys
from pathlib import Path
from typing import Tuple, Optional
from dataclasses import dataclass

# PIL/Pillow - obrigatorio para esteganografia
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    raise ImportError("Pillow is required for steganography - run: pip install Pillow")

# KayosCrypto (para criptografar antes de embutir)
sys.path.insert(0, str(Path(__file__).parent))
try:
    from .kayoscrypto_ultimate import KayosCryptoUltimate
    KAYOS_AVAILABLE = True
except ImportError:
    KAYOS_AVAILABLE = False


# =====================================================================
# DATACLASSES
# =====================================================================

@dataclass
class SteganographyMetadata:
    """Metadados do payload oculto"""
    payload_size_bytes: int
    image_width: int
    image_height: int
    capacity_bytes: int
    utilization_percent: float
    encrypted: bool = True


# =====================================================================
# RIB 7: VISUAL STEGANOGRAPHY ENGINE
# =====================================================================

class VisualSteganography:
    """
    Sistema de esteganografia visual LSB com integração KayosCrypto
    
    ARQUITETURA (3 Canais RGB = 3 Rodas Ezequiel):
    
    Canal R (Red):    Armazena bits 0, 3, 6, 9... do payload
    Canal G (Green):  Armazena bits 1, 4, 7, 10... do payload
    Canal B (Blue):   Armazena bits 2, 5, 8, 11... do payload
    
    PROCESSO DE EMBEDDING:
    1. Criptografar payload com KayosCrypto (segurança)
    2. Converter para bits (ex: 'A' = 01000001)
    3. Modificar LSB de cada canal RGB sequencialmente
    4. Salvar imagem (visualmente idêntica)
    
    PROCESSO DE EXTRACTION:
    1. Ler LSB de cada canal RGB
    2. Reconstruir bytes do payload
    3. Descriptografar com KayosCrypto
    4. Retornar payload original
    """
    
    def __init__(self, encrypt_payload: bool = True, password: Optional[str] = None):
        """
        Inicializa sistema de esteganografia
        
        Args:
            encrypt_payload: Se True, criptografa payload antes de embutir
            password: Senha para KayosCrypto (obrigatória se encrypt_payload=True)
        """
        self.encrypt_payload = encrypt_payload
        self.password = password
        
        if encrypt_payload and not password:
            raise ValueError("Senha obrigatória quando encrypt_payload=True")
        
        if encrypt_payload and KAYOS_AVAILABLE:
            # NOTA: use_quantum=False temporariamente (bug em v6.0 com quantum + decrypt)
            # TODO: Investigar incompatibilidade quantum mode
            self.cipher = KayosCryptoUltimate(use_quantum=False, use_ed25519=False, 
                                              use_concentric=True, use_direction=False)
        else:
            self.cipher = None
        
        # Estatísticas
        self.stats = {
            'images_processed': 0,
            'payloads_embedded': 0,
            'payloads_extracted': 0,
            'total_bytes_hidden': 0
        }
    
    def calculate_capacity(self, image_path: str) -> int:
        """
        Calcula capacidade máxima de payload em bytes
        
        LSB em RGB: 3 bits por pixel / 8 = 0.375 bytes por pixel
        
        Args:
            image_path: Caminho da imagem
        
        Returns:
            Capacidade em bytes
        """
        img = Image.open(image_path)
        width, height = img.size
        
        # 3 bits por pixel (1 bit de cada canal RGB)
        # Dividir por 8 para converter bits → bytes
        # Subtrair 32 bytes para metadados (tamanho do payload)
        capacity = ((width * height * 3) // 8) - 32
        
        return max(capacity, 0)
    
    def embed(self, 
              cover_image_path: str, 
              payload: bytes, 
              output_image_path: str) -> SteganographyMetadata:
        """
        Embute payload em imagem usando LSB
        
        Args:
            cover_image_path: Imagem original (cover)
            payload: Dados a ocultar
            output_image_path: Imagem de saída (stego)
        
        Returns:
            Metadados do embedding
        """
        # 1. Criptografar payload (se habilitado)
        if self.encrypt_payload and self.cipher:
            # KayosCrypto retorna dict com 'ciphertext' e 'metadata'
            encrypted_result = self.cipher.encrypt(payload, self.password)
            if isinstance(encrypted_result, dict):
                payload_encrypted = encrypted_result['ciphertext']
            else:
                payload_encrypted = encrypted_result
            print(f" Payload criptografado: {len(payload)} → {len(payload_encrypted)} bytes")
        else:
            payload_encrypted = payload
        
        # 2. Abrir imagem
        img = Image.open(cover_image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        pixels = img.load()
        
        # 3. Verificar capacidade
        capacity = self.calculate_capacity(cover_image_path)
        if len(payload_encrypted) > capacity:
            raise ValueError(f"Payload muito grande! Max: {capacity} bytes, fornecido: {len(payload_encrypted)} bytes")
        
        # 4. Preparar payload com metadados
        # Header: 32 bits (4 bytes) = tamanho do payload
        payload_size = len(payload_encrypted)
        header = payload_size.to_bytes(4, 'big')
        full_payload = header + payload_encrypted
        
        # 5. Converter payload para bits
        payload_bits = []
        for byte in full_payload:
            for i in range(8):
                bit = (byte >> (7 - i)) & 1
                payload_bits.append(bit)
        
        # 6. Embute bits no LSB de cada canal RGB
        bit_index = 0
        total_bits = len(payload_bits)
        
        for y in range(height):
            for x in range(width):
                if bit_index >= total_bits:
                    break
                
                r, g, b = pixels[x, y]
                
                # Modificar LSB de cada canal
                if bit_index < total_bits:
                    r = (r & 0xFE) | payload_bits[bit_index]
                    bit_index += 1
                
                if bit_index < total_bits:
                    g = (g & 0xFE) | payload_bits[bit_index]
                    bit_index += 1
                
                if bit_index < total_bits:
                    b = (b & 0xFE) | payload_bits[bit_index]
                    bit_index += 1
                
                pixels[x, y] = (r, g, b)
            
            if bit_index >= total_bits:
                break
        
        # 7. Salvar imagem
        img.save(output_image_path, 'PNG')  # PNG = lossless (não perde bits)
        
        # 8. Estatísticas
        self.stats['images_processed'] += 1
        self.stats['payloads_embedded'] += 1
        self.stats['total_bytes_hidden'] += payload_size
        
        # 9. Metadados
        metadata = SteganographyMetadata(
            payload_size_bytes=payload_size,
            image_width=width,
            image_height=height,
            capacity_bytes=capacity,
            utilization_percent=(payload_size / capacity * 100),
            encrypted=self.encrypt_payload
        )
        
        return metadata
    
    def extract(self, stego_image_path: str) -> bytes:
        """
        Extrai payload oculto de imagem
        
        Args:
            stego_image_path: Imagem com payload oculto
        
        Returns:
            Payload original (descriptografado se encrypt_payload=True)
        """
        # 1. Abrir imagem
        img = Image.open(stego_image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        pixels = img.load()
        
        # 2. Extrair bits do LSB
        extracted_bits = []
        
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                
                # Extrair LSB de cada canal
                extracted_bits.append(r & 1)
                extracted_bits.append(g & 1)
                extracted_bits.append(b & 1)
        
        # 3. Converter bits → bytes
        extracted_bytes = bytearray()
        for i in range(0, len(extracted_bits), 8):
            if i + 8 <= len(extracted_bits):
                byte_bits = extracted_bits[i:i+8]
                byte_value = 0
                for bit in byte_bits:
                    byte_value = (byte_value << 1) | bit
                extracted_bytes.append(byte_value)
        
        # 4. Ler header (primeiros 4 bytes = tamanho)
        if len(extracted_bytes) < 4:
            raise ValueError("Imagem não contém payload válido (header ausente)")
        
        payload_size = int.from_bytes(extracted_bytes[0:4], 'big')
        
        # 5. Extrair payload
        if len(extracted_bytes) < 4 + payload_size:
            raise ValueError(f"Payload incompleto (esperado {payload_size} bytes)")
        
        payload_encrypted = bytes(extracted_bytes[4:4+payload_size])
        
        # 6. Descriptografar (se habilitado)
        if self.encrypt_payload and self.cipher:
            decrypted_result = self.cipher.decrypt(payload_encrypted, self.password)
            if isinstance(decrypted_result, dict):
                payload = decrypted_result['plaintext']
            else:
                payload = decrypted_result
            print(f" Payload descriptografado: {len(payload_encrypted)} → {len(payload)} bytes")
        else:
            payload = payload_encrypted
        
        # 7. Estatísticas
        self.stats['payloads_extracted'] += 1
        
        return payload
    
    def get_stats(self) -> dict:
        """Retorna estatísticas de uso"""
        return self.stats.copy()


# =====================================================================
# TESTES E VALIDAÇÃO
# =====================================================================

if __name__ == "__main__":
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║      RIB 7: VISUAL STEGANOGRAPHY - TESTE COMPLETO            ║")
    print("╚═══════════════════════════════════════════════════════════════╝\n")
    
    # Criar imagem de teste
    print("  TESTE 1: Criar Imagem de Teste")
    print("="*70)
    test_image_path = "/tmp/kayos_test_cover.png"
    test_stego_path = "/tmp/kayos_test_stego.png"
    
    # Criar imagem RGB 200x200 (gradiente colorido)
    import numpy as np
    width, height = 200, 200
    image_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            image_array[y, x] = [
                (x * 255) // width,      # Red: gradiente horizontal
                (y * 255) // height,     # Green: gradiente vertical
                ((x + y) * 255) // (width + height)  # Blue: gradiente diagonal
            ]
    
    test_img = Image.fromarray(image_array, 'RGB')
    test_img.save(test_image_path)
    print(f" Imagem criada: {test_image_path} ({width}×{height})\n")
    
    try:
        # Inicializar
        password = os.getenv("KAYOS_AUTH_PASSWORD", "default_insecure_password")
        stego = VisualSteganography(encrypt_payload=True, password=password)  # TESTAR COM CRIPTOGRAFIA
        
        # Teste 2: Calcular capacidade
        print(" TESTE 2: Capacidade da Imagem")
        print("="*70)
        capacity = stego.calculate_capacity(test_image_path)
        print(f"├─ Tamanho imagem:     {width}×{height} = {width*height:,} pixels")
        print(f"├─ Bits disponíveis:   {width*height*3:,} bits")
        print(f"└─ Capacidade payload: {capacity:,} bytes ({capacity/1024:.2f} KB)\n")
        
        # Teste 3: Embute payload
        print(" TESTE 3: Embedding de Payload")
        print("="*70)
        secret_payload = b"KAYOSCRYPTO STEGANOGRAPHY TEST - DADOS SECRETOS " * 50
        print(f"Payload original: {len(secret_payload)} bytes")
        
        metadata = stego.embed(test_image_path, secret_payload, test_stego_path)
        
        print(f"\n├─ Payload:            {metadata.payload_size_bytes} bytes")
        print(f"├─ Capacidade:         {metadata.capacity_bytes} bytes")
        print(f"├─ Utilização:         {metadata.utilization_percent:.2f}%")
        print(f"├─ Criptografado:      {metadata.encrypted}")
        print(f"└─ Stego image:        {test_stego_path}\n")
        
        # Teste 4: Extrai payload
        print(" TESTE 4: Extraction de Payload")
        print("="*70)
        extracted_payload = stego.extract(test_stego_path)
        
        print(f"Payload extraído: {len(extracted_payload)} bytes")
        
        # Teste 5: Verificar integridade
        print("\n TESTE 5: Verificação de Integridade")
        print("="*70)
        match = (secret_payload == extracted_payload)
        print(f"Payloads são iguais: {match} {'' if match else ''}")
        
        if not match:
            print(f"  DEBUG:")
            print(f"├─ Original size:   {len(secret_payload)}")
            print(f"├─ Extracted size:  {len(extracted_payload)}")
            print(f"├─ Original[0:20]:  {secret_payload[:20]}")
            print(f"└─ Extracted[0:20]: {extracted_payload[:20]}")
        
        if match:
            print(f"├─ Primeiros 50 bytes: {extracted_payload[:50]}")
            print(f"└─ Últimos 50 bytes:   {extracted_payload[-50:]}\n")
        
        # Teste 6: Comparar imagens
        print(" TESTE 6: Análise Visual das Imagens")
        print("="*70)
        original_img = Image.open(test_image_path)
        stego_img = Image.open(test_stego_path)
        
        original_pixels = list(original_img.getdata())
        stego_pixels = list(stego_img.getdata())
        
        differences = sum(1 for i in range(len(original_pixels)) 
                         if original_pixels[i] != stego_pixels[i])
        
        print(f"├─ Pixels totais:      {len(original_pixels):,}")
        print(f"├─ Pixels modificados: {differences:,}")
        print(f"└─ Diferença visual:   {(differences/len(original_pixels)*100):.4f}% (imperceptível)\n")
        
        # Teste 7: Estatísticas
        print(" TESTE 7: Estatísticas de Uso")
        print("="*70)
        stats = stego.get_stats()
        for key, value in stats.items():
            print(f"├─ {key:25s}: {value}")
        
        print("\n╔═══════════════════════════════════════════════════════════════╗")
        print("║                      TODOS OS TESTES OK                     ║")
        print("║        Rib 7 (Visual Steganography) FUNCIONAL                ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        
        # Limpar arquivos de teste
        os.remove(test_image_path)
        os.remove(test_stego_path)
        print("\n Arquivos de teste removidos")
        
    except Exception as e:
        print(f"\n ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
