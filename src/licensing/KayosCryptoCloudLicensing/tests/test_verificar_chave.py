import unittest
from kayosql_release.kayosql_crypto_api import verificar_chave

class TestVerificarChave(unittest.TestCase):

    def test_valida_chave_correta(self):
        chave = "A1B2C3D4E"
        self.assertTrue(verificar_chave(chave))

    def test_nao_string(self):
        chave = 123456789
        self.assertFalse(verificar_chave(chave))

    def test_menos_de_9_caracteres(self):
        chave = "A1B2C3D"
        self.assertFalse(verificar_chave(chave))

    def test_mais_de_9_caracteres(self):
        chave = "A1B2C3D4E5"
        self.assertFalse(verificar_chave(chave))

    def test_caracteres_nao_alfanumericos(self):
        chave = "A1B2C3D$%"
        self.assertFalse(verificar_chave(chave))

    def test_string_vazia(self):
        chave = ""
        self.assertFalse(verificar_chave(chave))

    def test_caracteres_acentuados(self):
        chave = "çãé123456"
        self.assertFalse(verificar_chave(chave))

if __name__ == '__main__':
    unittest.main()
