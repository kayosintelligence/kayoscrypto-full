#!/usr/bin/env python3
"""
 Teste Unitário para o Hipercubo Sator 4D - VERSÃO CORRIGIDA.
Valida a arquitetura, as rotações e a derivação da chave de singularidade 5D.
"""
import unittest
import sys
import os
import logging

# Adicionar o diretório 'src' ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# CORREÇÃO 1: Importar HypercubeCell diretamente
from crypto.sator_hypercube_4d import SatorHypercube4D, RotationPlane, HypercubeCell
from crypto.real_oqs_engine_fixed import RealQuantumClassicalExchange

logging.basicConfig(level=logging.INFO)

class TestSatorHypercube4D(unittest.TestCase):

 def setUp(self):
 """Configura o ambiente para cada teste."""
 self.hypercube = SatorHypercube4D()
 self.key_exchange_engine = RealQuantumClassicalExchange()
 self.key_material = self.key_exchange_engine.perform_key_exchange()

 def test_01_initialization(self):
 """Testa se o Hipercubo é inicializado com as 8 células corretamente."""
 print("\n--- Teste 1: Inicialização do Hipercubo ---")
 self.assertEqual(len(self.hypercube.cells), 8)
 # CORREÇÃO: Usar a classe importada 'HypercubeCell'
 self.assertIn("Kyber1024", self.hypercube.cells[HypercubeCell.QUANTUM]['anverso'])
 self.assertIn("Falcon-1024", self.hypercube.cells[HypercubeCell.SIGNATURE]['anverso'])
 print(" Inicialização com 8 células validada.")

 def test_02_planar_rotation(self):
 """Testa se uma rotação planar altera o estado do Hipercubo."""
 print("\n--- Teste 2: Rotação Planar ---")
 initial_state = self.hypercube.get_current_state()
 self.hypercube.rotate_hypercube(RotationPlane.XY)
 rotated_state = self.hypercube.get_current_state()
 
 self.assertNotEqual(initial_state, rotated_state, "O estado do cubo não mudou após a rotação.")
 
 # CORREÇÃO 2: Verificar a célula correta após a rotação (Quantum -> Classical -> Symmetric -> Hash -> Quantum)
 # O valor original de 'symmetric' deve estar agora em 'classical'
 self.assertEqual(rotated_state['classical']['anverso'], initial_state['symmetric']['anverso'])
 print(" Rotação XY alterou o estado do hipercubo como esperado.")

 def test_03_fibonacci_rotation(self):
 """Testa a Rotação Espiral de Fibonacci."""
 print("\n--- Teste 3: Rotação Espiral de Fibonacci ---")
 initial_state = self.hypercube.get_current_state()
 self.hypercube.perform_fibonacci_spiral_rotation(level=5)
 final_state = self.hypercube.get_current_state()
 
 self.assertNotEqual(initial_state, final_state, "A rotação Fibonacci não alterou o estado do cubo.")
 print(" Rotação Espiral Nível 5 concluída e estado alterado.")
 
 def test_04_5d_singularity_key_derivation(self):
 """Testa a geração da Chave de Singularidade 5D."""
 print("\n--- Teste 4: Geração da Chave de Singularidade 5D ---")
 key1 = self.hypercube.get_5d_singularity_key(self.key_material)
 
 self.assertIsInstance(key1, bytes)
 self.assertEqual(len(key1), 64)
 
 import time
 time.sleep(0.01)
 key2 = self.hypercube.get_5d_singularity_key(self.key_material)
 self.assertNotEqual(key1, key2, "Duas chaves geradas em momentos diferentes são idênticas, o salt temporal falhou.")
 print(" Geração de Chave 5D validada: tamanho correto e unicidade temporal.")

if __name__ == '__main__':
 unittest.main()
