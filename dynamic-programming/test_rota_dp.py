"""Testes do algoritmo de rota segura. Rodar com: python -m unittest -v"""
import random
import unittest

from rota_dp import (Trecho, carregar_grafo, carregar_pontos_seguros, esta_aberto, forca_bruta,
                     gerar_grade, montar_grafo, ponto_seguro_mais_proximo, risco_trecho,
                     rota_mais_segura)


class TestBordas(unittest.TestCase):
    def setUp(self):
        self.g = carregar_grafo()

    def test_orcamento_zero_retorna_rota_mais_curta(self):
        r = rota_mais_segura(self.g, "B1", "B5", 0)
        self.assertEqual(r.distancia_m, 800)
        self.assertEqual(r.desvio_m, 0)

    def test_destino_inalcancavel(self):
        nos = {"A": {}, "B": {}, "ILHA": {}}
        g = montar_grafo(nos, [Trecho("A", "B", "rua", 100, 1, 0.5, 0.5, 1, 0)])
        self.assertIsNone(rota_mais_segura(g, "A", "ILHA", 500))
        self.assertIsNone(forca_bruta(g, "A", "ILHA", 500))

    def test_origem_igual_destino(self):
        r = rota_mais_segura(self.g, "P3", "P3", 300)
        self.assertEqual(r.caminho, ["P3"])
        self.assertEqual(r.risco, 0)
        self.assertEqual(r.nota_seguranca, 100)

    def test_entradas_invalidas(self):
        with self.assertRaises(ValueError):
            rota_mais_segura(self.g, "B1", "XX", 100)
        with self.assertRaises(ValueError):
            rota_mais_segura(self.g, "B1", "B5", -1)


class TestCenarioPaulista(unittest.TestCase):
    """Os exemplos de demonstração: a rota muda conforme o orçamento e o horário."""

    def setUp(self):
        self.g = carregar_grafo()

    def test_rota_muda_com_orcamento_a_noite(self):
        r0 = rota_mais_segura(self.g, "B1", "B5", 0, hora=23)
        r200 = rota_mais_segura(self.g, "B1", "B5", 200, hora=23)
        r500 = rota_mais_segura(self.g, "B1", "B5", 500, hora=23)
        self.assertEqual(r0.ruas, ["R. Cincinato Braga"])
        self.assertIn("R. São Carlos do Pinhal", r200.ruas)
        self.assertIn("Av. Paulista", r500.ruas)
        self.assertGreater(r0.risco, r200.risco)
        self.assertGreater(r200.risco, r500.risco)

    def test_horario_muda_a_rota(self):
        noite = rota_mais_segura(self.g, "B1", "B5", 500, hora=23)
        dia = rota_mais_segura(self.g, "B1", "B5", 500, hora=15)
        self.assertNotEqual(noite.caminho, dia.caminho)

    def test_rota_segura_evita_trechos_de_alto_risco(self):
        rapida = rota_mais_segura(self.g, "B1", "B5", 0, hora=23)
        segura = rota_mais_segura(self.g, "B1", "B5", 500, hora=23)
        self.assertGreater(rapida.metros_alto_risco, segura.metros_alto_risco)


class TestCorrecao(unittest.TestCase):
    """A DP deve dar o mesmo risco que testar todos os caminhos."""

    def test_dp_igual_forca_bruta_em_grafos_aleatorios(self):
        rnd = random.Random(42)
        for semente in range(30):
            g = gerar_grade(rnd.choice([3, 4]), semente)
            nos = list(g.adj)
            o, d = rnd.sample(nos, 2)
            orcamento = rnd.choice([0, 50, 150, 300])
            hora = rnd.choice([3, 12, 22])
            dp = rota_mais_segura(g, o, d, orcamento, hora=hora)
            fb = forca_bruta(g, o, d, orcamento, hora=hora)
            self.assertAlmostEqual(dp.risco, fb[0], places=6, msg=f"semente {semente}")

    def test_risco_nunca_aumenta_com_mais_orcamento(self):
        g = gerar_grade(5, semente=7)
        riscos = [rota_mais_segura(g, "0,0", "4,4", b).risco for b in range(0, 601, 50)]
        for antes, depois in zip(riscos, riscos[1:]):
            self.assertLessEqual(depois, antes + 1e-9)

    def test_rota_respeita_orcamento_e_e_valida(self):
        g = gerar_grade(5, semente=3)
        for b in (0, 100, 400):
            r = rota_mais_segura(g, "0,0", "4,4", b)
            self.assertLessEqual(r.passos, r.passos_minimos + b // r.passo_m)
            self.assertEqual(r.caminho[0], "0,0")
            self.assertEqual(r.caminho[-1], "4,4")
            for t, (u, v) in zip(r.trechos, zip(r.caminho, r.caminho[1:])):
                self.assertEqual((t.origem, t.destino), (u, v))
            self.assertAlmostEqual(r.risco, sum(risco_trecho(t, r.hora) for t in r.trechos))


class TestPontoSeguro(unittest.TestCase):
    def setUp(self):
        self.g = carregar_grafo()
        self.pontos = carregar_pontos_seguros()

    def test_nunca_sugere_ponto_fechado(self):
        for hora in range(24):
            for p in ponto_seguro_mais_proximo(self.g, "B3", hora, self.pontos):
                self.assertTrue(esta_aberto(p, hora))

    def test_horario_de_madrugada(self):
        lanchonete = next(p for p in self.pontos if p["id"] == "PS10")  # 18h às 4h
        self.assertTrue(esta_aberto(lanchonete, 2))
        self.assertFalse(esta_aberto(lanchonete, 10))

    def test_orgao_publico_proximo_aparece_primeiro(self):
        recomendados = ponto_seguro_mais_proximo(self.g, "C1", 23, self.pontos)
        self.assertEqual(recomendados[0]["tipo"], "orgao_publico")
        self.assertEqual(len(recomendados), 2)


if __name__ == "__main__":
    unittest.main()
