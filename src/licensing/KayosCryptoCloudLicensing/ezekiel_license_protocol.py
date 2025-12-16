"""
 EZEKIEL LICENSE PROTOCOL - KAYOSCRYPTO CLOUD LICENSING
Sistema de Licenciamento com Roda de Ezequiel

Evolução do sistema de licenças com:
- Rotações multi-dimensionais para validação
- Fibonacci spiral para geração de tokens
- Golden Ratio para distribuição de permissões
- Centro TENET fixo para âncora de licenças

Autor: KAYOS SYSTEMS
Data: 12 de outubro de 2025
Versão: 2.0.0 - Ezekiel Integration
"""

import hashlib
import secrets
import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import base64

# Importar Ezekiel Wheel Engine
try:
    import sys
    from pathlib import Path
    ezekiel_path = Path(__file__).parent.parent.parent / "enterprise3d/KayosCryptoEnterprise3D/src/cube"
    sys.path.insert(0, str(ezekiel_path))
    from ezekiel_wheel_engine import EzekielWheelEngine, EzekielWheel, PHI, FIBONACCI_SEQUENCE
    EZEKIEL_AVAILABLE = True
except ImportError:
    EZEKIEL_AVAILABLE = False
    PHI = 1.618034
    FIBONACCI_SEQUENCE = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]


# =====================================================================
# CONSTANTES
# =====================================================================

LICENSE_TYPES = {
    'FREE': {'level': 1, 'features': ['basic'], 'rotation_level': 1},
    'BASIC': {'level': 2, 'features': ['basic', 'encryption'], 'rotation_level': 3},
    'PROFESSIONAL': {'level': 3, 'features': ['basic', 'encryption', 'quantum'], 'rotation_level': 5},
    'ENTERPRISE': {'level': 4, 'features': ['basic', 'encryption', 'quantum', 'hypercube'], 'rotation_level': 8},
    'ULTIMATE': {'level': 5, 'features': ['basic', 'encryption', 'quantum', 'hypercube', 'ezekiel'], 'rotation_level': 13}
}


# =====================================================================
# DATACLASSES
# =====================================================================

@dataclass
class EzekielLicense:
    """Licença baseada em Roda de Ezequiel"""
    license_id: str
    license_type: str
    user_id: str
    organization_id: Optional[str]
    
    # Configuração Ezequiel
    wheel_x: float  # Rotação no eixo X
    wheel_y: float  # Rotação no eixo Y
    wheel_z: float  # Rotação no eixo Z
    fibonacci_level: int  # Nível da espiral Fibonacci
    
    # Metadados
    issued_at: str
    expires_at: str
    features: List[str]
    max_devices: int
    
    # Segurança
    signature: str
    tenet_anchor: str  # Hash do centro TENET [2,2,2]
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_token(self) -> str:
        """Converte licença para token JWT-like"""
        data = self.to_dict()
        json_str = json.dumps(data, sort_keys=True)
        encoded = base64.urlsafe_b64encode(json_str.encode()).decode()
        return f"ezk_{encoded}"
    
    @staticmethod
    def from_token(token: str) -> 'EzekielLicense':
        """Decodifica token para licença"""
        if not token.startswith('ezk_'):
            raise ValueError("Token inválido")
        
        encoded = token[4:]
        json_str = base64.urlsafe_b64decode(encoded).decode()
        data = json.loads(json_str)
        return EzekielLicense(**data)


# =====================================================================
# LICENSE MANAGER
# =====================================================================

class EzekielLicenseManager:
    """
    Gerenciador de Licenças com Roda de Ezequiel
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Inicializa gerenciador
        
        Args:
            master_key: Chave mestra para assinatura (se None, gera nova)
        """
        self.master_key = master_key or secrets.token_bytes(32)
        
        # Inicializar Ezekiel Engine se disponível
        if EZEKIEL_AVAILABLE:
            self.ezekiel_engine = EzekielWheelEngine(dimension=5)
        else:
            self.ezekiel_engine = None
        
        # Centro TENET como âncora de licenças
        self.tenet_anchor = self._generate_tenet_anchor()
    
    def _generate_tenet_anchor(self) -> str:
        """Gera âncora TENET [2,2,2] para licenças"""
        tenet_data = b"TENET_CENTER_[2,2,2]_KAYOSCRYPTO"
        h = hashlib.sha3_256()
        h.update(tenet_data)
        h.update(self.master_key)
        return h.hexdigest()[:32]
    
    def create_license(self, 
                      user_id: str,
                      license_type: str = 'BASIC',
                      organization_id: Optional[str] = None,
                      validity_days: int = 365) -> EzekielLicense:
        """
        Cria nova licença com Roda de Ezequiel
        
        Args:
            user_id: ID do usuário
            license_type: Tipo da licença (FREE, BASIC, PROFESSIONAL, ENTERPRISE, ULTIMATE)
            organization_id: ID da organização (opcional)
            validity_days: Dias de validade
        
        Returns:
            Licença Ezequiel criada
        """
        if license_type not in LICENSE_TYPES:
            raise ValueError(f"Tipo de licença inválido: {license_type}")
        
        config = LICENSE_TYPES[license_type]
        
        # Gerar ID único
        license_id = f"LIC-EZK-{uuid.uuid4().hex[:16].upper()}"
        
        # Calcular ângulos de rotação baseados em Golden Ratio
        base_angle = 360 / PHI  # ~222.5°
        wheel_x = (base_angle * config['level']) % 360
        wheel_y = (base_angle * config['level'] * PHI) % 360
        wheel_z = (base_angle * config['level'] / PHI) % 360
        
        # Nível Fibonacci baseado no tipo
        fibonacci_level = config['rotation_level']
        
        # Datas
        issued_at = datetime.now(timezone.utc)
        expires_at = issued_at + timedelta(days=validity_days)
        
        # Max devices baseado em Fibonacci
        max_devices = FIBONACCI_SEQUENCE[min(config['level'], len(FIBONACCI_SEQUENCE)-1)]
        
        # Criar licença (sem assinatura ainda)
        license_obj = EzekielLicense(
            license_id=license_id,
            license_type=license_type,
            user_id=user_id,
            organization_id=organization_id,
            wheel_x=wheel_x,
            wheel_y=wheel_y,
            wheel_z=wheel_z,
            fibonacci_level=fibonacci_level,
            issued_at=issued_at.isoformat(),
            expires_at=expires_at.isoformat(),
            features=config['features'],
            max_devices=max_devices,
            signature="",  # Será preenchido
            tenet_anchor=self.tenet_anchor
        )
        
        # Assinar licença
        license_obj.signature = self._sign_license(license_obj)
        
        return license_obj
    
    def _sign_license(self, license_obj: EzekielLicense) -> str:
        """
        Assina licença usando Ezekiel Wheel
        
        Args:
            license_obj: Licença a assinar
        
        Returns:
            Assinatura hexadecimal
        """
        # Dados a assinar (sem signature e tenet_anchor)
        data = {
            'license_id': license_obj.license_id,
            'license_type': license_obj.license_type,
            'user_id': license_obj.user_id,
            'organization_id': license_obj.organization_id,
            'wheel_x': license_obj.wheel_x,
            'wheel_y': license_obj.wheel_y,
            'wheel_z': license_obj.wheel_z,
            'fibonacci_level': license_obj.fibonacci_level,
            'issued_at': license_obj.issued_at,
            'expires_at': license_obj.expires_at,
            'features': license_obj.features,
            'max_devices': license_obj.max_devices
        }
        
        json_str = json.dumps(data, sort_keys=True)
        
        # Se Ezekiel disponível, usar difusão criptográfica
        if EZEKIEL_AVAILABLE and self.ezekiel_engine:
            # Difusão com Ezekiel
            diffused = self.ezekiel_engine.cryptographic_diffusion(
                json_str.encode(),
                rounds=license_obj.fibonacci_level
            )
            # Hash final
            h = hashlib.sha3_512()
            h.update(diffused)
            h.update(self.master_key)
            signature = h.hexdigest()
        else:
            # Fallback: HMAC simples
            h = hashlib.sha3_512()
            h.update(json_str.encode())
            h.update(self.master_key)
            signature = h.hexdigest()
        
        return signature[:64]  # 256-bit signature
    
    def verify_license(self, license_obj: EzekielLicense) -> Dict:
        """
        Verifica validade da licença
        
        Args:
            license_obj: Licença a verificar
        
        Returns:
            Dicionário com resultado da verificação
        """
        # Verificar assinatura
        expected_signature = self._sign_license(license_obj)
        signature_valid = (expected_signature == license_obj.signature)
        
        # Verificar TENET anchor
        tenet_valid = (license_obj.tenet_anchor == self.tenet_anchor)
        
        # Verificar expiração
        expires_at = datetime.fromisoformat(license_obj.expires_at)
        now_utc = datetime.now(timezone.utc)
        expired = now_utc > expires_at
        
        # Verificar rotações Ezequiel (validação geométrica)
        wheel_valid = self._verify_ezekiel_wheel(
            license_obj.wheel_x,
            license_obj.wheel_y,
            license_obj.wheel_z,
            license_obj.fibonacci_level
        )
        
        # Resultado
        valid = signature_valid and tenet_valid and not expired and wheel_valid
        
        return {
            'valid': valid,
            'signature_valid': signature_valid,
            'tenet_valid': tenet_valid,
            'expired': expired,
            'wheel_valid': wheel_valid,
            'license_id': license_obj.license_id,
            'license_type': license_obj.license_type,
            'features': license_obj.features,
            'expires_at': license_obj.expires_at,
            'days_remaining': (expires_at - now_utc).days if not expired else 0
        }
    
    def _verify_ezekiel_wheel(self, wheel_x: float, wheel_y: float, wheel_z: float, fib_level: int) -> bool:
        """
        Verifica se as rotações Ezequiel são válidas geometricamente
        
        Args:
            wheel_x, wheel_y, wheel_z: Ângulos das rodas
            fib_level: Nível Fibonacci
        
        Returns:
            True se válido
        """
        # Verificar se ângulos estão no range [0, 360)
        if not (0 <= wheel_x < 360 and 0 <= wheel_y < 360 and 0 <= wheel_z < 360):
            return False
        
        # Verificar se nível Fibonacci é válido
        if not (1 <= fib_level <= len(FIBONACCI_SEQUENCE)):
            return False
        
        # Verificar proporção Golden Ratio entre ângulos
        # wheel_y deve ser ~φ vezes wheel_x (dentro de tolerância)
        ratio_xy = wheel_y / wheel_x if wheel_x != 0 else 0
        ratio_xz = wheel_x / wheel_z if wheel_z != 0 else 0
        
        # Tolerância de 10% para PHI
        phi_tolerance = 0.1
        valid_ratio = (
            abs(ratio_xy - PHI) / PHI < phi_tolerance or
            abs(ratio_xz - PHI) / PHI < phi_tolerance
        )
        
        return valid_ratio
    
    def rotate_license(self, license_obj: EzekielLicense, angle_x: float = 0, angle_y: float = 0, angle_z: float = 0) -> EzekielLicense:
        """
        Rotaciona licença (gera nova versão com rotações adicionais)
        Útil para renovação ou upgrade
        
        Args:
            license_obj: Licença original
            angle_x, angle_y, angle_z: Ângulos de rotação adicionais
        
        Returns:
            Nova licença rotacionada
        """
        new_wheel_x = (license_obj.wheel_x + angle_x) % 360
        new_wheel_y = (license_obj.wheel_y + angle_y) % 360
        new_wheel_z = (license_obj.wheel_z + angle_z) % 360
        
        # Criar nova licença com rotações atualizadas
        new_license = EzekielLicense(
            license_id=license_obj.license_id + "-R",  # Sufixo de rotação
            license_type=license_obj.license_type,
            user_id=license_obj.user_id,
            organization_id=license_obj.organization_id,
            wheel_x=new_wheel_x,
            wheel_y=new_wheel_y,
            wheel_z=new_wheel_z,
            fibonacci_level=license_obj.fibonacci_level,
            issued_at=datetime.now(timezone.utc).isoformat(),
            expires_at=license_obj.expires_at,
            features=license_obj.features,
            max_devices=license_obj.max_devices,
            signature="",
            tenet_anchor=self.tenet_anchor
        )
        
        # Assinar nova licença
        new_license.signature = self._sign_license(new_license)
        
        return new_license
    
    def upgrade_license(self, license_obj: EzekielLicense, new_type: str) -> EzekielLicense:
        """
        Faz upgrade da licença para tipo superior
        
        Args:
            license_obj: Licença original
            new_type: Novo tipo (deve ser superior ao atual)
        
        Returns:
            Nova licença com upgrade
        """
        if new_type not in LICENSE_TYPES:
            raise ValueError(f"Tipo inválido: {new_type}")
        
        current_level = LICENSE_TYPES[license_obj.license_type]['level']
        new_level = LICENSE_TYPES[new_type]['level']
        
        if new_level <= current_level:
            raise ValueError(f"Novo tipo deve ser superior ao atual")
        
        # Criar nova licença com tipo superior
        return self.create_license(
            user_id=license_obj.user_id,
            license_type=new_type,
            organization_id=license_obj.organization_id,
            validity_days=365
        )
    
    def get_license_status(self, license_obj: EzekielLicense) -> Dict:
        """
        Obtém status detalhado da licença com métricas Ezequiel
        
        Args:
            license_obj: Licença a analisar
        
        Returns:
            Status completo
        """
        verification = self.verify_license(license_obj)
        
        # Calcular "força" da licença baseada em Fibonacci
        strength_score = FIBONACCI_SEQUENCE[min(license_obj.fibonacci_level, len(FIBONACCI_SEQUENCE)-1)]
        
        # Calcular rotação total (magnitude do vetor [x, y, z])
        import math
        total_rotation = math.sqrt(
            license_obj.wheel_x**2 + 
            license_obj.wheel_y**2 + 
            license_obj.wheel_z**2
        )
        
        return {
            **verification,
            'fibonacci_level': license_obj.fibonacci_level,
            'strength_score': strength_score,
            'wheel_config': {
                'x': license_obj.wheel_x,
                'y': license_obj.wheel_y,
                'z': license_obj.wheel_z,
                'total_rotation': total_rotation
            },
            'tenet_anchor': license_obj.tenet_anchor,
            'max_devices': license_obj.max_devices,
            'ezekiel_engine_available': EZEKIEL_AVAILABLE
        }


# =====================================================================
# EXEMPLO DE USO
# =====================================================================

if __name__ == "__main__":
    print("=" * 80)
    print(" EZEKIEL LICENSE PROTOCOL - DEMONSTRAÇÃO")
    print("=" * 80)
    
    # Criar gerenciador
    manager = EzekielLicenseManager()
    
    print(f"\n Gerenciador criado")
    print(f"   TENET Anchor: {manager.tenet_anchor}")
    print(f"   Ezekiel Engine: {' Disponível' if EZEKIEL_AVAILABLE else ' Indisponível'}")
    
    # Criar licença ENTERPRISE
    print("\n Criando licença ENTERPRISE...")
    license_ent = manager.create_license(
        user_id="user@kayos.com",
        license_type="ENTERPRISE",
        organization_id="ORG-KAYOS-001",
        validity_days=365
    )
    
    print(f" Licença criada:")
    print(f"   ID: {license_ent.license_id}")
    print(f"   Tipo: {license_ent.license_type}")
    print(f"   Roda X: {license_ent.wheel_x:.2f}°")
    print(f"   Roda Y: {license_ent.wheel_y:.2f}°")
    print(f"   Roda Z: {license_ent.wheel_z:.2f}°")
    print(f"   Fibonacci Level: {license_ent.fibonacci_level}")
    print(f"   Max Devices: {license_ent.max_devices}")
    print(f"   Features: {', '.join(license_ent.features)}")
    
    # Verificar licença
    print("\n Verificando licença...")
    status = manager.get_license_status(license_ent)
    print(f" Status da licença:")
    print(f"   Válida: {status['valid']}")
    print(f"   Assinatura: {status['signature_valid']}")
    print(f"   TENET: {status['tenet_valid']}")
    print(f"   Roda Válida: {status['wheel_valid']}")
    print(f"   Dias restantes: {status['days_remaining']}")
    print(f"   Strength Score: {status['strength_score']}")
    print(f"   Rotação Total: {status['wheel_config']['total_rotation']:.2f}°")
    
    # Converter para token
    print("\n Gerando token...")
    token = license_ent.to_token()
    print(f"Token: {token[:50]}...")
    print(f"Tamanho: {len(token)} caracteres")
    
    # Decodificar token
    print("\n Decodificando token...")
    decoded = EzekielLicense.from_token(token)
    print(f" Token decodificado:")
    print(f"   ID: {decoded.license_id}")
    print(f"   Tipo: {decoded.license_type}")
    
    print("\n" + "=" * 80)
    print(" Demonstração completa!")
    print("=" * 80)
