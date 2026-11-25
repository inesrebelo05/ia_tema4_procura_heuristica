"""
Reproduz as tabelas do relatório:
  Tabela 3   - desempenho nas 210 instâncias fornecidas
  Tabela 4/5 - 10 casos de teste dos labirintos
  Tabela 8   - A* nos 10 casos de rotas
  Tabela 9   - A* em todos os pares de cidades
  e as verificações (heurísticas, validação, Dijkstra).

Uso:  python reproduzir_resultados.py
"""
import time
from collections import defaultdict
from statistics import mean, median

from carregar_dados import carregar_labirintos
from gerar_casos_cidades import CASOS, dificuldade
from gerar_casos_teste import carregar_casos
from procura_informada import a_estrela, gulosa, verifica_heuristica
from procura_nao_informada import Labirinto, bfs, dfs, valida_solucao
import rotas_cidades as rc

ALGORITMOS = [("BFS", bfs), ("DFS", dfs), ("A*", a_estrela), ("Gulosa", gulosa)]


def avaliar(lab, otimo, repeticoes=1):
    """Corre os 4 algoritmos num labirinto. Devolve {nome: métricas}."""
    saida = {}
    for nome, f in ALGORITMOS:
        tempos = []
        for _ in range(repeticoes):
            t0 = time.perf_counter()
            acoes, nos = f(lab)
            tempos.append((time.perf_counter() - t0) * 1000)
        valida, custo = valida_solucao(lab, acoes)
        saida[nome] = dict(valida=valida, otimo=valida and custo == otimo, nos=nos,
                           custo=custo, razao=(custo / otimo if valida and otimo else None),
                           tempo=median(tempos))
    return saida


def resumo(linhas, tabela_por_alg):
    for nome, _ in ALGORITMOS:
        m = [l[nome] for l in linhas]
        tabela_por_alg[nome] = m


def tabela3():
    df = carregar_labirintos()
    todos = []
    for r in df.itertuples():
        lab = Labirinto(r.grelha, r.id_labirinto)
        todos.append(avaliar(lab, r.comprimento_caminho_otimo))
    print("\n=== Tabela 3 · 210 instâncias fornecidas ===")
    print(f"{'Algoritmo':8} {'Válidas':>8} {'Ótimas':>8} {'Nós (média)':>12} {'Tempo (ms)':>11} {'Sobrecusto':>11}")
    for nome, _ in ALGORITMOS:
        m = [t[nome] for t in todos]
        print(f"{nome:8} {sum(x['valida'] for x in m):>5}/{len(m)} {sum(x['otimo'] for x in m):>5}/{len(m)}"
              f" {mean(x['nos'] for x in m):>12.1f} {mean(x['tempo'] for x in m):>11.2f}"
              f" {mean(x['razao'] for x in m):>10.2f}x")
    # heurística de Manhattan: admissível e consistente nas 210?
    ok = [verifica_heuristica(Labirinto(r.grelha)) for r in df.itertuples()]
    print("Manhattan admissível/consistente em todas:", all(a for a, _ in ok), all(c for _, c in ok))
    h_menor = sum(1 for r in df.itertuples() if r.distancia_manhattan_SG < r.comprimento_caminho_otimo)
    print("Instâncias com h(s0) < ótimo:", h_menor)


def tabelas45():
    casos = carregar_casos()
    linhas = []
    print("\n=== Tabela 4 · nós expandidos nos 10 casos (custo entre parênteses se não ótimo) ===")
    print(f"{'Caso':5} {'Ótimo':>6} " + " ".join(f"{n:>10}" for n, _ in ALGORITMOS))
    for r in casos.itertuples():
        lab = Labirinto(r.grelha, r.id_labirinto)
        m = avaliar(lab, r.comprimento_caminho_otimo, repeticoes=200)
        linhas.append(m)
        cel = [f"{m[n]['nos']}" + ("" if m[n]["otimo"] else f" ({m[n]['custo']})") for n, _ in ALGORITMOS]
        print(f"{r.id_labirinto:5} {r.comprimento_caminho_otimo:>6} " + " ".join(f"{c:>10}" for c in cel))
    print("\n=== Tabela 5 · resumo nos 10 casos ===")
    print(f"{'Algoritmo':8} {'Válidas':>8} {'Ótimas':>8} {'Nós':>6} {'Tempo (ms)':>11} {'Sobrec. médio':>14} {'máx.':>6}")
    for nome, _ in ALGORITMOS:
        m = [t[nome] for t in linhas]
        print(f"{nome:8} {sum(x['valida'] for x in m):>5}/10 {sum(x['otimo'] for x in m):>5}/10"
              f" {sum(x['nos'] for x in m):>6} {mean(x['tempo'] for x in m):>11.2f}"
              f" {mean(x['razao'] for x in m):>13.2f}x {max(x['razao'] for x in m):>5.2f}x")


def tabelas89():
    rotas = rc.Rotas()
    print("\n=== Verificação da heurística de linha reta (50x50 pares; todas as ligações e destinos) ===")
    print("admissível, consistente:", rc.verifica_heuristica(rotas))

    print("\n=== Tabela 8 · A* nos 10 casos de rotas ===")
    print(f"{'Caso':5} {'Troços':>6} {'Custo':>7} {'h(s0)':>7} {'A*':>4} {'h=0':>4} {'Poup.':>6}")
    tot_a = tot_u = 0
    for id_caso, o, d, _ in CASOS:
        caminho, custo, n = rc.a_estrela(rotas, o, d)
        _, _, n0 = rc.a_estrela(rotas, o, d, usar_h=False)
        assert rc.valida_caminho(rotas, caminho, o, d)[0] and abs(custo - rc.dijkstra(rotas, o, d)) < 1e-6
        tot_a, tot_u = tot_a + n, tot_u + n0
        poup = f"{int(100 * (1 - n / n0) + 0.5)}%" if n0 else "–"
        print(f"{id_caso:5} {len(caminho) - 1:>6} {custo:>7.1f} {rotas.h(o, d):>7.1f} {n:>4} {n0:>4} {poup:>6}")
    print(f"Total: A* = {tot_a}, h = 0: {tot_u} (poupança {100 * (1 - tot_a / tot_u):.0f}%)")

    print("\n=== Tabela 9 · todos os pares de cidades ===")
    acc = defaultdict(lambda: [0, 0, 0])
    corretos = 0
    for o in rotas.cidades:
        for d in rotas.cidades:
            if o == d:
                continue
            caminho, custo, n = rc.a_estrela(rotas, o, d)
            _, _, n0 = rc.a_estrela(rotas, o, d, usar_h=False)
            corretos += rc.valida_caminho(rotas, caminho, o, d)[0] and abs(custo - rc.dijkstra(rotas, o, d)) < 1e-6
            classe = dificuldade(len(caminho) - 1)
            for k in (classe, "total"):
                acc[k][0] += 1
                acc[k][1] += n
                acc[k][2] += n0
    print(f"Caminhos válidos e ótimos (= Dijkstra): {corretos}/2450")
    for k, nome in (("fácil", "Fácil (1 a 3 troços)"), ("média", "Média (4 a 6)"),
                    ("difícil", "Difícil (7 ou mais)"), ("total", "Total")):
        p, a, u = acc[k]
        print(f"{nome:22} pares={p:>5}  A*={a / p:>5.1f}  h=0={u / p:>5.1f}  poupança={100 * (1 - a / u):.1f}%")


if __name__ == "__main__":
    tabela3()
    tabelas45()
    tabelas89()
