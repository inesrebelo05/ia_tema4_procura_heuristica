"""
Geração dos 10 casos de teste de labirintos (C01 a C10), semente base 2026.

  C01, C03, C05 : construídos à mão (situações específicas)
  C06           : escolhido por pesquisa de sementes (labirinto onde a gulosa
                  mais se afasta do ótimo)
  restantes     : aleatórios, com random.Random(2026 + n.º do caso) e a
                  densidade de paredes indicada. Se o labirinto não tiver
                  solução (verificado por BFS), gera-se outro com o mesmo
                  gerador de números aleatórios.

Escreve casos_teste_labirintos.xlsx, no mesmo formato da folha Labirintos.

Uso:  python gerar_casos_teste.py
"""
import os
import random

import pandas as pd

from procura_informada import gulosa
from procura_nao_informada import Labirinto, bfs

SEMENTE = 2026
PASTA = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(PASTA, "casos_teste_labirintos.xlsx")


def para_texto(g):
    return "|".join("".join(linha) for linha in g)


def grelha_vazia(n):
    """Moldura de paredes com interior livre."""
    g = [["#"] * n for _ in range(n)]
    for r in range(1, n - 1):
        for c in range(1, n - 1):
            g[r][c] = "."
    return g


def aleatorio(n, densidade, rng):
    """Interior com paredes aleatórias; S em (1,1) e G em (n-2,n-2)."""
    g = [["#"] * n for _ in range(n)]
    for r in range(1, n - 1):
        for c in range(1, n - 1):
            g[r][c] = "#" if rng.random() < densidade else "."
    g[1][1], g[n - 2][n - 2] = "S", "G"
    return para_texto(g)


def aleatorio_com_solucao(n, densidade, semente):
    """Gera labirintos com a mesma semente até existir solução (BFS)."""
    rng = random.Random(semente)
    while True:
        texto = aleatorio(n, densidade, rng)
        if bfs(Labirinto(texto))[0] is not None:
            return texto


def c01():
    """8x8 sem paredes interiores: h exata."""
    g = grelha_vazia(8)
    g[1][1], g[6][6] = "S", "G"
    return para_texto(g)


def c03():
    """11x11 em serpentina: um único caminho, longo (48 passos)."""
    g = grelha_vazia(11)
    ligacao = {2: 9, 4: 1, 6: 9, 8: 1}  # coluna da passagem em cada linha-parede
    for r, col in ligacao.items():
        for c in range(1, 10):
            if c != col:
                g[r][c] = "#"
    g[1][1], g[9][9] = "S", "G"
    return para_texto(g)


def c05():
    """13x13 com duas salas separadas por uma parede, com porta junto ao fundo.

    S e G não estão nos cantos: confirma que o modelo aceita qualquer posição.
    """
    g = grelha_vazia(13)
    for r in range(1, 12):
        if r != 10:  # porta em (10, 6)
            g[r][6] = "#"
    g[2][1], g[2][11] = "S", "G"
    return para_texto(g)


def c06(n=15, densidade=0.25, n_sementes=2000):
    """Pesquisa de sementes: maximiza custo(gulosa) / custo(ótimo)."""
    melhor, melhor_razao = None, 0.0
    for semente in range(n_sementes):
        texto = aleatorio_com_solucao(n, densidade, semente)
        lab = Labirinto(texto)
        otimo = len(bfs(lab)[0])
        gulosa_acoes, _ = gulosa(lab)
        razao = len(gulosa_acoes) / otimo
        if razao > melhor_razao:
            melhor, melhor_razao = texto, razao
    return melhor


# (id, descrição, tamanho, densidade, função geradora)
def casos():
    return [
        ("C01", "Sem paredes interiores (h exata)", 8, 0.0, c01()),
        ("C02", "Aleatório, densidade 0,20", 10, 0.20, aleatorio_com_solucao(10, 0.20, SEMENTE + 2)),
        ("C03", "Serpentina: caminho único e longo", 11, None, c03()),
        ("C04", "Aleatório, densidade 0,30", 12, 0.30, aleatorio_com_solucao(12, 0.30, SEMENTE + 4)),
        ("C05", "Duas salas, porta junto ao fundo", 13, None, c05()),
        ("C06", "Selecionado: a gulosa afasta-se do ótimo", 15, 0.25, c06()),
        ("C07", "Aleatório, densidade 0,25", 18, 0.25, aleatorio_com_solucao(18, 0.25, SEMENTE + 7)),
        ("C08", "Muito aberto, densidade 0,10 (empates)", 22, 0.10, aleatorio_com_solucao(22, 0.10, SEMENTE + 8)),
        ("C09", "Aleatório, densidade 0,30", 26, 0.30, aleatorio_com_solucao(26, 0.30, SEMENTE + 9)),
        ("C10", "Aleatório, densidade 0,28", 30, 0.28, aleatorio_com_solucao(30, 0.28, SEMENTE + 10)),
    ]


def para_dataframe(lista):
    linhas = []
    for id_caso, descricao, n, dens, texto in lista:
        lab = Labirinto(texto)
        otimo = len(bfs(lab)[0])
        h0 = abs(lab.inicio[0] - lab.objetivo[0]) + abs(lab.inicio[1] - lab.objetivo[1])
        linhas.append({
            "id_labirinto": id_caso,
            "descricao": descricao,
            "linhas": lab.R,
            "colunas": lab.C,
            "densidade_paredes": dens,
            "inicio": f"({lab.inicio[0]},{lab.inicio[1]})",
            "objetivo": f"({lab.objetivo[0]},{lab.objetivo[1]})",
            "grelha": texto,
            "comprimento_caminho_otimo": otimo,
            "distancia_manhattan_SG": h0,
            "celulas_alcancaveis": lab.alcancaveis(),
        })
    return pd.DataFrame(linhas)


def carregar_casos(caminho=SAIDA):
    """Lê os casos já gerados (gera-os primeiro se o ficheiro não existir)."""
    if not os.path.exists(caminho):
        gerar()
    return pd.read_excel(caminho)


def gerar():
    df = para_dataframe(casos())
    df.to_excel(SAIDA, index=False)
    return df


if __name__ == "__main__":
    df = gerar()
    print(df.drop(columns="grelha").to_string(index=False))
    print(f"\nEscrito em {SAIDA}")
