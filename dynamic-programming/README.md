# Vagalume · Dynamic Programming: rota mais segura dentro de um orçamento de desvio (DP `dp[v][d]`, O(E·D))
1. Requisitos: Python 3.10+ e `pip install pandas matplotlib notebook`. Os dados ficam em `dados/` (fontes descritas no notebook).
2. Notebook com cenário, exemplos, testes e benchmark: `jupyter notebook vagalume_rota_segura.ipynb` e depois *Run All*.
3. Só os testes (sem dependências): `python -m unittest -v` nesta pasta.
4. Algoritmo: `rota_dp.py`, função `rota_mais_segura` (DP) e `ponto_seguro_mais_proximo` (Bellman-Ford).
