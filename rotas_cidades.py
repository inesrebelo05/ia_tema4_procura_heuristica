"""
Rotas entre cidades: modelo formal, A*, Dijkstra de referência, validação de
caminhos e verificação da heurística (distância em linha reta).

UC 04914 · Introdução à Inteligência Artificial · Tema 4 (extensão)
"""
import heapq
from itertools import count
from math import asin, cos, radians, sin, sqrt

import pandas as pd

from carregar_dados import FICHEIRO_CIDADES

RAIO_TERRA_KM = 6371.0


def haversine(lat1, lon1, lat2, lon2):
    """Distância em linha reta (km) entre dois pontos, pela fórmula de haversine."""
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = p2 - p1, radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * RAIO_TERRA_KM * asin(sqrt(a))


class Rotas:
    """Modelo formal do problema das rotas (Tabela 6 do relatório).

    Estado    : cidade onde o agente se encontra.
    Ações     : ir para uma cidade vizinha (ligada por estrada).
    Custo     : distância por estrada entre as duas cidades (km, simétrico).
    Objetivo  : cidade de destino.
    Heurística: distância em linha reta (haversine) ao destino.
    """

    def __init__(self, ficheiro=FICHEIRO_CIDADES):
        cidades = pd.read_excel(ficheiro, sheet_name="Cidades")
        trocos = pd.read_excel(ficheiro, sheet_name="Trocos_Estrada")
        self.coords = {r.cidade: (r.latitude, r.longitude) for r in cidades.itertuples()}
        self.cidades = sorted(self.coords)
        self.vizinhos = {c: {} for c in self.cidades}
        self.linha_reta_ficheiro = {}
        for r in trocos.itertuples():
            self.vizinhos[r.cidade_a][r.cidade_b] = r.distancia_estrada_km
            self.vizinhos[r.cidade_b][r.cidade_a] = r.distancia_estrada_km
            self.linha_reta_ficheiro[frozenset((r.cidade_a, r.cidade_b))] = r.distancia_linha_reta_km
        self.n_ligacoes = len(trocos)

    # --- modelo formal -------------------------------------------------
    def acoes(self, cidade):
        """ACTIONS(c): cidades vizinhas, por ordem alfabética (reprodutibilidade)."""
        return sorted(self.vizinhos[cidade])

    def custo(self, u, v):
        return self.vizinhos[u][v]

    def h(self, cidade, destino):
        """Distância em linha reta (km) de `cidade` a `destino`."""
        return haversine(*self.coords[cidade], *self.coords[destino])


def a_estrela(rotas, origem, destino, usar_h=True):
    """A* em grafo, f = g + h, teste de objetivo ao retirar o nó da fronteira.

    Com usar_h=False fica h = 0 (custo uniforme), usado para medir o valor da
    heurística. Devolve (caminho ou None, custo, nós expandidos).
    """
    h = (lambda c: rotas.h(c, destino)) if usar_h else (lambda c: 0.0)
    contador = count()
    fronteira = [(h(origem), next(contador), 0.0, origem)]
    melhor_g = {origem: 0.0}
    pai = {origem: None}
    expandidos = 0
    while fronteira:
        _, _, g, c = heapq.heappop(fronteira)
        if g > melhor_g[c]:
            continue  # entrada obsoleta
        if c == destino:
            caminho = []
            while c is not None:
                caminho.append(c)
                c = pai[c]
            return caminho[::-1], g, expandidos
        expandidos += 1
        for v in rotas.acoes(c):
            g2 = g + rotas.custo(c, v)
            if v not in melhor_g or g2 < melhor_g[v] - 1e-12:
                melhor_g[v] = g2
                pai[v] = c
                heapq.heappush(fronteira, (g2 + h(v), next(contador), g2, v))
    return None, float("inf"), expandidos


def dijkstra(rotas, origem, destino):
    """Dijkstra de referência, implementado SEM reutilizar o código do A*.

    Devolve o custo mínimo (km) de origem a destino (inf se não houver caminho).
    """
    dist = {c: float("inf") for c in rotas.cidades}
    dist[origem] = 0.0
    fila = [(0.0, origem)]
    feito = set()
    while fila:
        d, u = heapq.heappop(fila)
        if u in feito:
            continue
        feito.add(u)
        if u == destino:
            return d
        for v, w in rotas.vizinhos[u].items():
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(fila, (dist[v], v))
    return dist[destino]


def valida_caminho(rotas, caminho, origem, destino):
    """Refaz o caminho ligação a ligação. Devolve (válido, custo em km)."""
    if not caminho or caminho[0] != origem or caminho[-1] != destino:
        return False, None
    custo = 0.0
    for u, v in zip(caminho, caminho[1:]):
        if v not in rotas.vizinhos.get(u, {}):
            return False, None
        custo += rotas.custo(u, v)
    return True, custo


def verifica_heuristica(rotas, tol=1e-9):
    """Verificação por força bruta da heurística de linha reta.

    Admissibilidade: h(c, d) <= custo real de c a d, para todos os pares.
    Consistência   : h(u, d) <= custo(u, v) + h(v, d), para todas as ligações e destinos.
    Devolve (admissível, consistente).
    """
    admissivel = all(
        rotas.h(c, d) <= dijkstra(rotas, c, d) + tol
        for c in rotas.cidades for d in rotas.cidades
    )
    consistente = all(
        rotas.h(u, d) <= rotas.custo(u, v) + rotas.h(v, d) + tol
        for u in rotas.cidades for v in rotas.vizinhos[u] for d in rotas.cidades
    )
    return admissivel, consistente
