"""Vagalume — rota mais segura dentro de um orçamento de desvio.

Problema: dado um grafo de ruas (esquinas = nós, trechos = arestas), encontrar o
caminho de MENOR RISCO ACUMULADO de A até B que ande no máximo B metros a mais
que o caminho mais curto. É um caminho mínimo com restrição de recurso,
resolvido por programação dinâmica:

    dp[v][d] = menor risco para chegar ao nó v andando exatamente d passos
    dp[v][d] = min sobre trechos (u -> v) de dp[u][d - passos(u,v)] + risco(u,v)
    resposta = min dp[destino][d], para d <= passos_minimos + orcamento

Só usa a biblioteca padrão do Python.
"""
from __future__ import annotations

import csv
import heapq
import math
import random
from dataclasses import dataclass, field
from pathlib import Path

PASTA_DADOS = Path(__file__).resolve().parent / "dados"

# ---------------------------------------------------------------------------
# Motor de risco
# ---------------------------------------------------------------------------
# Pesos de cada fator na densidade de risco (risco por metro, de 0 a ~1).
# Na versão integrada, os pesos por horário vêm da análise de Data Science.
PESO_BASE = 0.05          # risco mínimo de qualquer rua
PESO_OCORRENCIAS = 0.40   # ocorrências oficiais (SSP-SP), saturam em 10/ano
PESO_ILUMINACAO = 0.30    # (1 - iluminação), pesa mais à noite
PESO_REPORTS = 0.25       # reports da comunidade, saturam em 8
PESO_ACIDENTES = 0.10     # acidentes de trânsito (meta ODS 3.6), saturam em 5
PESO_MOVIMENTO = 0.50     # movimento e comércio aberto REDUZEM o risco
RISCO_MINIMO = 0.02       # garante risco > 0 em todo trecho (ver correção)
LIMIAR_ALTO_RISCO = 0.40  # densidade a partir da qual o trecho é "alto risco"


@dataclass(frozen=True)
class Trecho:
    """Segmento de rua entre duas esquinas (aresta direcionada u -> v)."""

    origem: str
    destino: str
    rua: str
    comprimento_m: float
    ocorrencias: int
    iluminacao: float   # 0 = escuro, 1 = bem iluminado
    movimento: float    # 0 = deserto, 1 = muito movimento à noite
    reports: int
    acidentes: int

    def invertido(self) -> "Trecho":
        return Trecho(self.destino, self.origem, self.rua, self.comprimento_m,
                      self.ocorrencias, self.iluminacao, self.movimento,
                      self.reports, self.acidentes)


@dataclass
class Grafo:
    """Grafo de ruas em lista de adjacência: adj[u] = trechos que saem de u."""

    nos: dict[str, dict]
    adj: dict[str, list[Trecho]] = field(default_factory=dict)

    def trechos(self):
        for lista in self.adj.values():
            yield from lista


def montar_grafo(nos: dict[str, dict], trechos: list[Trecho]) -> Grafo:
    """Cria um grafo não direcionado (cada trecho vale nos dois sentidos)."""
    grafo = Grafo(nos=dict(nos), adj={v: [] for v in nos})
    for t in trechos:
        grafo.adj[t.origem].append(t)
        grafo.adj[t.destino].append(t.invertido())
    return grafo


def carregar_grafo(pasta: Path = PASTA_DADOS) -> Grafo:
    """Lê dados/nos.csv e dados/arestas.csv."""
    with open(pasta / "nos.csv", encoding="utf-8") as f:
        nos = {l["id"]: {"nome": l["nome"], "x": float(l["x_m"]), "y": float(l["y_m"])}
               for l in csv.DictReader(f)}
    with open(pasta / "arestas.csv", encoding="utf-8") as f:
        trechos = [Trecho(l["origem"], l["destino"], l["rua"], float(l["comprimento_m"]),
                          int(l["ocorrencias"]), float(l["iluminacao"]), float(l["movimento"]),
                          int(l["reports"]), int(l["acidentes"]))
                   for l in csv.DictReader(f)]
    return montar_grafo(nos, trechos)


def eh_noite(hora: int) -> bool:
    return hora >= 19 or hora < 6


def fatores_risco(t: Trecho, hora: int) -> dict[str, float]:
    """Contribuição de cada fator para a densidade de risco do trecho (por metro)."""
    noite = eh_noite(hora)
    movimento = t.movimento if noite else max(t.movimento, 0.6)  # de dia a rua tem gente
    positivos = {
        "base": PESO_BASE,
        "ocorrencias": PESO_OCORRENCIAS * min(t.ocorrencias / 10, 1) * (1.0 if noite else 0.8),
        "iluminacao": PESO_ILUMINACAO * (1 - t.iluminacao) * (1.0 if noite else 0.2),
        "reports": PESO_REPORTS * min(t.reports / 8, 1) * (1.0 if noite else 0.5),
        "acidentes": PESO_ACIDENTES * min(t.acidentes / 5, 1),
    }
    positivos["movimento"] = -PESO_MOVIMENTO * movimento * sum(positivos.values())
    return positivos


def densidade_risco(t: Trecho, hora: int) -> float:
    """Risco por metro do trecho no horário (sempre >= RISCO_MINIMO > 0)."""
    return max(RISCO_MINIMO, sum(fatores_risco(t, hora).values()))


def risco_trecho(t: Trecho, hora: int) -> float:
    """Exposição ao risco = comprimento × densidade. É o peso da aresta na DP."""
    return t.comprimento_m * densidade_risco(t, hora)


def passos(t: Trecho, passo_m: int) -> int:
    """Distância discretizada, arredondada para cima e sempre >= 1 passo."""
    return max(1, math.ceil(t.comprimento_m / passo_m))


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------
@dataclass
class Resultado:
    caminho: list[str]
    trechos: list[Trecho]
    risco: float
    passos: int
    passos_minimos: int
    passo_m: int
    hora: int

    @property
    def distancia_m(self) -> float:
        return sum(t.comprimento_m for t in self.trechos)

    @property
    def desvio_m(self) -> int:
        return (self.passos - self.passos_minimos) * self.passo_m

    @property
    def nota_seguranca(self) -> int:
        """Nota de 0 a 100: 100 × (1 − densidade média de risco da rota)."""
        if not self.trechos:
            return 100
        return max(0, min(100, round(100 * (1 - self.risco / self.distancia_m))))

    @property
    def ruas(self) -> list[str]:
        ruas: list[str] = []
        for t in self.trechos:
            if not ruas or ruas[-1] != t.rua:
                ruas.append(t.rua)
        return ruas

    @property
    def metros_alto_risco(self) -> float:
        return sum(t.comprimento_m for t in self.trechos
                   if densidade_risco(t, self.hora) >= LIMIAR_ALTO_RISCO)


# ---------------------------------------------------------------------------
# Pré-processamento: menor distância em passos (Dijkstra)
# ---------------------------------------------------------------------------
def menor_distancia_passos(grafo: Grafo, origem: str, passo_m: int) -> dict[str, int]:
    """Menor número de passos de `origem` até cada nó. Só define o tamanho da tabela."""
    dist = {origem: 0}
    fila = [(0, origem)]
    while fila:
        d, u = heapq.heappop(fila)
        if d > dist[u]:
            continue
        for t in grafo.adj[u]:
            nd = d + passos(t, passo_m)
            if nd < dist.get(t.destino, math.inf):
                dist[t.destino] = nd
                heapq.heappush(fila, (nd, t.destino))
    return dist


def _validar(grafo: Grafo, origem: str, destino: str, orcamento_m: float, passo_m: int):
    for no in (origem, destino):
        if no not in grafo.adj:
            raise ValueError(f"nó inexistente: {no}")
    if orcamento_m < 0:
        raise ValueError("o orçamento de desvio não pode ser negativo")
    if passo_m <= 0:
        raise ValueError("o passo de discretização deve ser positivo")


# ---------------------------------------------------------------------------
# Algoritmo principal: programação dinâmica
# ---------------------------------------------------------------------------
def rota_mais_segura(grafo: Grafo, origem: str, destino: str, orcamento_m: float,
                     hora: int = 23, passo_m: int = 10) -> Resultado | None:
    """Rota de menor risco que anda no máximo `orcamento_m` metros a mais que a mais curta.

    Retorna None se o destino for inalcançável.
    Tempo O(E · D) e memória O(V · D), com D = passos_minimos + orcamento_m / passo_m.
    """
    _validar(grafo, origem, destino, orcamento_m, passo_m)
    if origem == destino:
        return Resultado([origem], [], 0.0, 0, 0, passo_m, hora)

    # 1) Tamanho da tabela: distância mínima + orçamento, em passos.
    passos_minimos = menor_distancia_passos(grafo, origem, passo_m).get(destino)
    if passos_minimos is None:
        return None
    D = passos_minimos + int(orcamento_m // passo_m)

    # 2) Pré-calcula, para cada trecho u -> v: (u, v, passos, risco, trecho).
    indice = {v: i for i, v in enumerate(grafo.adj)}
    arestas = [(indice[t.origem], indice[t.destino], passos(t, passo_m), risco_trecho(t, hora), t)
               for t in grafo.trechos()]

    # 3) Tabela dp[v][d] e ponteiros de pai para reconstruir a rota.
    INF = math.inf
    dp = [[INF] * (D + 1) for _ in indice]
    pai: list[list[tuple[int, Trecho] | None]] = [[None] * (D + 1) for _ in indice]
    dp[indice[origem]][0] = 0.0                         # caso base

    # 4) Preenche em ordem crescente de d. Como todo trecho tem >= 1 passo,
    #    dp[u][d - w] já está pronto quando calculamos dp[v][d] (sem ciclos).
    for d in range(1, D + 1):
        for iu, iv, w, r, t in arestas:
            if w <= d:
                candidato = dp[iu][d - w] + r           # recorrência
                if candidato < dp[iv][d]:
                    dp[iv][d] = candidato
                    pai[iv][d] = (iu, t)

    # 5) Resposta: melhor d dentro do orçamento (empate -> rota mais curta).
    idest = indice[destino]
    melhor_d = min(range(D + 1), key=lambda d: (dp[idest][d], d))

    # 6) Reconstrução do caminho seguindo os pais.
    trechos: list[Trecho] = []
    v, d = idest, melhor_d
    while pai[v][d] is not None:
        iu, t = pai[v][d]
        trechos.append(t)
        d -= passos(t, passo_m)
        v = iu
    trechos.reverse()
    caminho = [origem] + [t.destino for t in trechos]
    return Resultado(caminho, trechos, dp[idest][melhor_d], melhor_d, passos_minimos, passo_m, hora)


# ---------------------------------------------------------------------------
# Força bruta (referência para testes e comparação de eficiência)
# ---------------------------------------------------------------------------
def forca_bruta(grafo: Grafo, origem: str, destino: str, orcamento_m: float,
                hora: int = 23, passo_m: int = 10) -> tuple[float, list[str], int] | None:
    """Testa TODOS os caminhos simples dentro do orçamento. Exponencial.

    Retorna (risco, caminho, caminhos_explorados) ou None.
    """
    _validar(grafo, origem, destino, orcamento_m, passo_m)
    if origem == destino:
        return 0.0, [origem], 1
    passos_minimos = menor_distancia_passos(grafo, origem, passo_m).get(destino)
    if passos_minimos is None:
        return None
    limite = passos_minimos + int(orcamento_m // passo_m)
    melhor: list = [math.inf, None]
    explorados = 0

    def dfs(u: str, gasto: int, risco: float, caminho: list[str], visitados: set[str]):
        nonlocal explorados
        explorados += 1
        if u == destino:
            if risco < melhor[0]:
                melhor[0], melhor[1] = risco, list(caminho)
            return
        for t in grafo.adj[u]:
            w = passos(t, passo_m)
            if t.destino not in visitados and gasto + w <= limite:
                visitados.add(t.destino)
                caminho.append(t.destino)
                dfs(t.destino, gasto + w, risco + risco_trecho(t, hora), caminho, visitados)
                caminho.pop()
                visitados.remove(t.destino)

    dfs(origem, 0, 0.0, [origem], {origem})
    return melhor[0], melhor[1], explorados


# ---------------------------------------------------------------------------
# Explicabilidade
# ---------------------------------------------------------------------------
NOMES_FATORES = {
    "ocorrencias": "ocorrências registradas",
    "iluminacao": "iluminação ruim",
    "reports": "reports recentes da comunidade",
    "acidentes": "acidentes de trânsito",
}


def explicar_rota(r: Resultado, top: int = 3) -> list[str]:
    """Frases simples com os fatores que mais pesaram na nota da rota."""
    if not r.trechos:
        return ["Você já está no destino."]
    total = {f: 0.0 for f in NOMES_FATORES}
    pior = {f: (0.0, None) for f in NOMES_FATORES}
    reducao = 0.0
    for t in r.trechos:
        fat = fatores_risco(t, r.hora)
        reducao += -fat["movimento"] * t.comprimento_m
        for f in NOMES_FATORES:
            contrib = fat[f] * t.comprimento_m
            total[f] += contrib
            if contrib > pior[f][0]:
                pior[f] = (contrib, t)
    soma = sum(total.values()) or 1.0
    frases = []
    for f in sorted(total, key=total.get, reverse=True)[:top]:
        t = pior[f][1]
        if t is None:
            continue
        frases.append(f"{NOMES_FATORES[f].capitalize()}: {100 * total[f] / soma:.0f}% do risco "
                      f"(pior trecho: {t.rua}, {t.comprimento_m:.0f} m)")
    frases.append(f"Movimento e comércios abertos reduziram o risco em "
                  f"{100 * reducao / (soma + PESO_BASE * r.distancia_m):.0f}%")
    return frases


# ---------------------------------------------------------------------------
# Extensão: Ponto Seguro mais próximo (Bellman-Ford, também DP)
# ---------------------------------------------------------------------------
def carregar_pontos_seguros(pasta: Path = PASTA_DADOS) -> list[dict]:
    with open(pasta / "pontos_seguros.csv", encoding="utf-8") as f:
        return [{**l, "abre": int(l["abre"]), "fecha": int(l["fecha"])} for l in csv.DictReader(f)]


def esta_aberto(ponto: dict, hora: int) -> bool:
    abre, fecha = ponto["abre"], ponto["fecha"]
    if abre < fecha:
        return abre <= hora < fecha
    return hora >= abre or hora < fecha    # funciona de madrugada (ex.: 18h às 4h)


def distancias_bellman_ford(grafo: Grafo, origem: str) -> tuple[dict[str, float], dict[str, str]]:
    """dist_k[v] = menor distância usando até k trechos (DP sobre o número de trechos).

    O(V · E). Para quando nenhuma distância melhora.
    """
    dist = {v: math.inf for v in grafo.adj}
    pai: dict[str, str] = {}
    dist[origem] = 0.0
    for _ in range(len(grafo.adj) - 1):
        mudou = False
        for t in grafo.trechos():
            if dist[t.origem] + t.comprimento_m < dist[t.destino]:
                dist[t.destino] = dist[t.origem] + t.comprimento_m
                pai[t.destino] = t.origem
                mudou = True
        if not mudou:
            break
    return dist, pai


def ponto_seguro_mais_proximo(grafo: Grafo, atual: str, hora: int, pontos: list[dict],
                              margem_orgao_m: float = 150) -> list[dict]:
    """Pontos Seguros ABERTOS recomendados, do mais prioritário ao menos.

    Regra do Vagalume: o mais próximo aberto é sempre indicado; um órgão público
    a até `margem_orgao_m` metros a mais aparece junto, na frente.
    Ponto fechado nunca é sugerido.
    """
    dist, pai = distancias_bellman_ford(grafo, atual)
    abertos = [{**p, "distancia_m": dist[p["no"]]} for p in pontos
               if esta_aberto(p, hora) and dist[p["no"]] < math.inf]
    if not abertos:
        return []
    abertos.sort(key=lambda p: p["distancia_m"])
    mais_proximo = abertos[0]
    recomendados = [p for p in abertos if p["tipo"] == "orgao_publico"
                    and p is not mais_proximo
                    and p["distancia_m"] <= mais_proximo["distancia_m"] + margem_orgao_m]
    recomendados.append(mais_proximo)
    for p in recomendados:
        caminho, v = [p["no"]], p["no"]
        while v != atual:
            v = pai[v]
            caminho.append(v)
        p["caminho"] = caminho[::-1]
    return recomendados


# ---------------------------------------------------------------------------
# Gerador de grafos para testes e benchmark
# ---------------------------------------------------------------------------
def gerar_grade(n: int, semente: int = 0, quadra_m: tuple[int, int] = (80, 200)) -> Grafo:
    """Grade n × n de ruas com atributos aleatórios (reprodutível pela semente)."""
    rnd = random.Random(semente)
    nos = {f"{i},{j}": {"nome": f"{i},{j}", "x": j, "y": i} for i in range(n) for j in range(n)}
    trechos = []
    for i in range(n):
        for j in range(n):
            for di, dj in ((0, 1), (1, 0)):
                if i + di < n and j + dj < n:
                    trechos.append(Trecho(
                        f"{i},{j}", f"{i + di},{j + dj}", f"rua {len(trechos)}",
                        rnd.randint(*quadra_m), rnd.randint(0, 10), round(rnd.random(), 2),
                        round(rnd.random(), 2), rnd.randint(0, 8), rnd.randint(0, 5)))
    return montar_grafo(nos, trechos)
