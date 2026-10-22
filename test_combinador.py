import unittest

from combinador_tons import (
    carregar_catalogo,
    delta_e_2000,
    hex_para_rgb,
    melhores_tons,
    rgb_para_lab,
)


class TestCores(unittest.TestCase):
    def test_hex_com_e_sem_cerquilha(self):
        self.assertEqual(hex_para_rgb("#C68642"), (198, 134, 66))
        self.assertEqual(hex_para_rgb("C68642"), (198, 134, 66))

    def test_hex_curto(self):
        self.assertEqual(hex_para_rgb("#FA0"), (255, 170, 0))

    def test_hex_invalido(self):
        with self.assertRaises(ValueError):
            hex_para_rgb("#ZZZZZZ")
        with self.assertRaises(ValueError):
            hex_para_rgb("#12345")

    def test_branco_e_preto_em_lab(self):
        l, a, b = rgb_para_lab((255, 255, 255))
        self.assertAlmostEqual(l, 100, places=1)
        self.assertAlmostEqual(a, 0, delta=0.1)
        self.assertAlmostEqual(b, 0, delta=0.1)
        self.assertAlmostEqual(rgb_para_lab((0, 0, 0))[0], 0, places=1)


class TestDeltaE(unittest.TestCase):
    """Pares de referencia publicados por Sharma, Wu e Dalal (2005)."""

    def test_par_1(self):
        valor = delta_e_2000((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485))
        self.assertAlmostEqual(valor, 2.0425, places=3)

    def test_par_2(self):
        valor = delta_e_2000((50.0, 3.1571, -77.2803), (50.0, 0.0, -82.7485))
        self.assertAlmostEqual(valor, 2.8615, places=3)

    def test_cores_iguais(self):
        lab = rgb_para_lab((198, 134, 66))
        self.assertEqual(delta_e_2000(lab, lab), 0)


class TestBusca(unittest.TestCase):
    def setUp(self):
        self.catalogo = carregar_catalogo()

    def test_cor_igual_ao_catalogo_vem_em_primeiro(self):
        resultado = melhores_tons(hex_para_rgb("#D2A582"), self.catalogo, 3)
        self.assertEqual(resultado[0]["codigo"], "N40")
        self.assertAlmostEqual(resultado[0]["delta_e"], 0, places=6)

    def test_resultados_ordenados(self):
        resultado = melhores_tons(hex_para_rgb("#C68642"), self.catalogo, 5)
        distancias = [item["delta_e"] for item in resultado]
        self.assertEqual(distancias, sorted(distancias))
        self.assertEqual(len(resultado), 5)


if __name__ == "__main__":
    unittest.main()
