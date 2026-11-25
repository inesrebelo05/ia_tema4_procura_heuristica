"""
Procura não informada em labirintos em grelha: modelo formal, BFS, DFS e
validação independente de soluções.

UC 04914 · Introdução à Inteligência Artificial · Tema 4
"""
from collections import deque

# Ações: nome -> (dr, dc). A ordem é a ordem de exploração.
ACOES = {
    "Cima": (-1, 0),
    "Baixo": (1, 0),
    "Esquerda": (0, -1),
    "Direita": (0, 1),
}


class Labirinto:
    """Modelo formal do problema (Tabela 2 do relatório).

    Estado    : s = (r, c), posição do agente (o labirinto é constante).
    Ações     : Cima, Baixo, Esquerda, Direita (só se não houver parede).
    Transição : RESULT((r, c), a) = (r + dr, c + dc).
    Custo     : c(s, a, s') = 1.
    Objetivo  : s == posição de G.
    """

    def __init__(self, grelha, id_labirinto=""):
        """`grelha` é o texto da folha Labirintos, com linhas separadas por '|'."""
        self.id = id_labirinto
        self.linhas = grelha.split("|")
        self.R = len(self.linhas)
        self.C = len(self.linhas[0])
        self.inicio = self.objetivo = None
        for r, linha in enumerate(self.linhas):
            for c, ch in enumerate(linha):
                if ch == "S":
                    self.inicio = (r, c)
                elif ch == "G":
                    self.objetivo = (r, c)
        if self.inicio is None or self.objetivo is None:
            raise ValueError(f"Labirinto {id_labirinto}: falta S ou G")

    # --- modelo formal -------------------------------------------------
    def livre(self, r, c):
        return 0 <= r < self.R and 0 <= c < self.C and self.linhas[r][c] != "#"

    def acoes(self, estado):
        """ACTIONS(s): ações aplicáveis (não entram em parede)."""
        r, c = estado
        return [a for a, (dr, dc) in ACOES.items() if self.livre(r + dr, c + dc)]

    def resultado(self, estado, acao):
        """RESULT(s, a): modelo de transição determinístico."""
        dr, dc = ACOES[acao]
        return (estado[0] + dr, estado[1] + dc)

    def custo(self, estado, acao, novo_estado):
        """c(s, a, s') = 1."""
        return 1

    def e_objetivo(self, estado):
        """GOAL-TEST(s)."""
        return estado == self.objetivo

    # --- utilitários ---------------------------------------------------
    def alcancaveis(self):
        """Número de estados alcançáveis a partir do estado inicial."""
        vistos = {self.inicio}
        fila = deque([self.inicio])
        while fila:
            s = fila.popleft()
            for a in self.acoes(s):
                t = self.resultado(s, a)
                if t not in vistos:
                    vistos.add(t)
                    fila.append(t)
        return len(vistos)

    def __str__(self):
        return "\n".join(self.linhas)


def _reconstruir(pai, estado):
    """Devolve a lista de ações do estado inicial até `estado`."""
    acoes = []
    while pai[estado] is not None:
        estado, acao = pai[estado]
        acoes.append(acao)
    acoes.reverse()
    return acoes


def bfs(lab):
    """Procura em largura (fila FIFO, procura em grafo).

    O teste de objetivo é feito quando o nó é GERADO (com custo unitário
    preserva a otimalidade e poupa uma expansão).
    Devolve (ações ou None, nós expandidos).
    """
    s0 = lab.inicio
    if lab.e_objetivo(s0):
        return [], 0
    pai = {s0: None}  # estado -> (estado anterior, ação); também é o conjunto "alcançados"
    fila = deque([s0])
    expandidos = 0
    while fila:
        s = fila.popleft()
        expandidos += 1
        for a in lab.acoes(s):
            t = lab.resultado(s, a)
            if t not in pai:
                pai[t] = (s, a)
                if lab.e_objetivo(t):
                    return _reconstruir(pai, t), expandidos
                fila.append(t)
    return None, expandidos


def dfs(lab):
    """Procura em profundidade (pilha LIFO, procura em grafo).

    Os estados são marcados como visitados ao serem EXPANDIDOS e o teste de
    objetivo é feito ao retirar o nó da pilha. A ordem de exploração das ações
    é Cima, Baixo, Esquerda, Direita.
    Devolve (ações ou None, nós expandidos).
    """
    s0 = lab.inicio
    pilha = [(s0, None)]  # (estado, (estado anterior, ação))
    pai = {}
    visitados = set()
    expandidos = 0
    while pilha:
        s, origem = pilha.pop()
        if s in visitados:
            continue
        visitados.add(s)
        pai[s] = origem
        if lab.e_objetivo(s):
            return _reconstruir(pai, s), expandidos
        expandidos += 1
        # inverte-se para que a primeira ação (Cima) fique no topo da pilha
        for a in reversed(lab.acoes(s)):
            t = lab.resultado(s, a)
            if t not in visitados:
                pilha.append((t, (s, a)))
    return None, expandidos


def valida_solucao(lab, acoes):
    """Validador INDEPENDENTE dos algoritmos.

    Refaz a sequência de ações a partir de s0, verifica que cada ação é
    aplicável (o agente nunca entra em parede) e que o último estado é o
    objetivo. Devolve (válida, custo).
    """
    if acoes is None:
        return False, None
    estado = lab.inicio
    custo = 0
    for a in acoes:
        if a not in ACOES or a not in lab.acoes(estado):
            return False, None
        novo = lab.resultado(estado, a)
        custo += lab.custo(estado, a, novo)
        estado = novo
    return lab.e_objetivo(estado), custo
