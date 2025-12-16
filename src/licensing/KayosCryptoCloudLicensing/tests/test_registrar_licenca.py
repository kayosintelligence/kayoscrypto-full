import unittest
from kayosql_release.kayosql_crypto_api import registrar_licenca
from tests.test_verificar_chave import verificar_chave

class TestRegistrarLicenca(unittest.TestCase):
    def test_chave_gerada_valida(self):
        resultado = registrar_licenca()
        self.assertIn("codigo", resultado)
        self.assertIn("chave", resultado)

        chave = resultado["chave"]
        self.assertTrue(verificar_chave(chave), f"Chave inválida: {chave}")

    def test_codigo_gerado_eh_uuid(self):
        import uuid
        resultado = registrar_licenca()
        try:
            uuid_obj = uuid.UUID(resultado["codigo"])
            self.assertEqual(str(uuid_obj), resultado["codigo"])
        except ValueError:
            self.fail(f"Código não é UUID válido: {resultado['codigo']}")

if __name__ == '__main__':
    unittest.main()
