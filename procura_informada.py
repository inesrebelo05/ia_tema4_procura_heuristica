"""
Procura informada em labirintos em grelha: heurística de Manhattan, A*,
procura gulosa e verificação empírica das propriedades da heurística.

UC 04914 · Introdução à Inteligência Artificial · Tema 4
"""
import heapq
from collections import deque
from itertools import count

from procura_nao_informada import _reconstruir


def manhattan(lab, estado):
    """h(s) = |r - r_G| + |c - c_G| (admissível e consistente)."""
    return abs(estado[0] - lab.objetivo[0]) + abs(estado[1] - lab.objetivo[1])


def a_estrela(lab, h=manhattan):
    """A*: fronteira ordenada por f = g + h (desempate por ordem de inserção).

    Guarda o melhor g conhecido de cada estado e só o reabre se encontrar um
    caminho mais barato. O teste de objetivo é feito ao retirar o nó da
    fronteira, o que garante a otimalidade.
    Devolve (ações ou None, nós expandidos).
    """
    s0 = lab.inicio
    contador = count()
    fronteira = [(h(lab, s0), next(contador), 0, s0)]  # (f, desempate, g, estado)
    melhor_g = {s0: 0}
    pai = {s0: None}
    expandidos = 0
    while fronteira:
        f, _, g, s = heapq.heappop(fronteira)
        if g > melhor_g[s]:
            continue  # entrada obsoleta
        if lab.e_objetivo(s):
            return _reconstruir(pai, s), expandidos
        expandidos += 1
        for a in lab.acoes(s):
            t = lab.resultado(s, a)
            g2 = g + lab.custo(s, a, t)
            if t not in melhor_g or g2 < melhor_g[t]:
                melhor_g[t] = g2
                pai[t] = (s, a)
                heapq.heappush(fronteira, (g2 + h(lab, t), next(contador), g2, t))
    return None, expandidos


def gulosa(lab, h=manhattan):
    """Procura gulosa: fronteira ordenada apenas por h(n).

    Usa um conjunto de estados alcançados para evitar ciclos. Não garante a
    solução ótima. Devolve (ações ou None, nós expandidos).
    """
    s0 = lab.inicio
    contador = count()
    fronteira = [(h(lab, s0), next(contador), s0)]
    pai = {s0: None}
    expandidos = 0
    while fronteira:
        _, _, s = heapq.heappop(fronteira)
        if lab.e_objetivo(s):
            return _reconstruir(pai, s), expandidos
        expandidos += 1
        for a in lab.acoes(s):
            t = lab.resultado(s, a)
            if t not in pai:
                pai[t] = (s, a)
                heapq.heappush(fronteira, (h(lab, t), next(contador), t))
    return None, expandidos


def custos_reais_ao_objetivo(lab):
    """Custo real h*(s) de cada estado alcançável até ao objetivo (BFS inversa).

    As ações são reversíveis e o custo é 1, por isso basta uma BFS a partir de G.
    """
    dist = {lab.objetivo: 0}
    fila = deque([lab.objetivo])
    while fila:
        s = fila.popleft()
        for a in lab.acoes(s):
            t = lab.resultado(s, a)
            if t not in dist:
                dist[t] = dist[s] + 1
                fila.append(t)
    return dist


def verifica_heuristica(lab, h=manhattan):
    """Verificação por força bruta de admissibilidade e consistência.

    Admissível : h(s) <= h*(s) para todos os estados que chegam ao objetivo.
    Consistente: h(s) <= c(s, a, s') + h(s') para todas as transições.
    Devolve (admissível, consistente).
    """
    real = custos_reais_ao_objetivo(lab)
    admissivel = all(h(lab, s) <= d for s, d in real.items())
    consistente = True
    for s in real:
        for a in lab.acoes(s):
            t = lab.resultado(s, a)
            if h(lab, s) > lab.custo(s, a, t) + h(lab, t):
                consistente = False
    return admissivel, consistente
