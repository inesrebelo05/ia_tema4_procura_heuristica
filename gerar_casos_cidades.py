"""
Casos de teste das rotas entre cidades (T01 a T10): executa o A* (e o custo
uniforme, h = 0), valida com o Dijkstra independente e produz o mapa (Figura 5).

Uso:  python gerar_casos_cidades.py
"""
import os
import time
from statistics import median

import pandas as pd

from rotas_cidades import Rotas, a_estrela, dijkstra, valida_caminho

PASTA = os.path.dirname(os.path.abspath(__file__))

# (id, origem, destino, descrição)
CASOS = [
    ("T01", "Porto", "Porto", "Trivial: origem igual ao destino"),
    ("T02", "Braga", "Guimarães", "Cidades ligadas diretamente (1 troço)"),
    ("T03", "Porto", "Viseu", "Litoral norte para o interior (2 troços)"),
    ("T04", "Viseu", "Coimbra", "Cidades próximas sem ligação direta (desvio pelo litoral)"),
    ("T05", "Peniche", "Elvas", "Caminho ótimo com mais troços do que o mínimo possível"),
    ("T06", "Porto", "Lisboa", "Eixo do litoral, norte-sul"),
    ("T07", "Mértola", "Vila Nova de Foz Côa", "Interior, sul para norte"),
    ("T08", "Chaves", "Beja", "Interior norte para o Alentejo"),
    ("T09", "Viana do Castelo", "Tavira", "Litoral norte para o Algarve oriental"),
    ("T10", "Bragança", "Lagos", "Maior custo do grafo (extremos)"),
]


def dificuldade(n_trocos):
    """Como no ficheiro de dados: fácil até 3 troços, média 4 a 6, difícil 7 ou mais."""
    if n_trocos == 0:
        return "trivial"
    return "fácil" if n_trocos <= 3 else "média" if n_trocos <= 6 else "difícil"


def tempo_ms(f, repeticoes=200):
    """Mediana de `repeticoes` execuções, em milissegundos."""
    t = []
    for _ in range(repeticoes):
        t0 = time.perf_counter()
        f()
        t.append((time.perf_counter() - t0) * 1000)
    return median(t)


def executar_casos(rotas):
    linhas = []
    for id_caso, o, d, descricao in CASOS:
        caminho, custo, nos = a_estrela(rotas, o, d)
        _, _, nos0 = a_estrela(rotas, o, d, usar_h=False)
        valido, custo_validado = valida_caminho(rotas, caminho, o, d)
        otimo = abs(custo - dijkstra(rotas, o, d)) < 1e-6
        linhas.append({
            "caso": id_caso, "origem": o, "destino": d, "descricao": descricao,
            "dificuldade": dificuldade(len(caminho) - 1),
            "trocos": len(caminho) - 1, "custo_km": round(custo, 1),
            "h0_km": round(rotas.h(o, d), 1), "nos_A*": nos, "nos_h0": nos0,
            "poupanca_%": int(100 * (1 - nos / nos0) + 0.5) if nos0 else None,
            "valido": valido and otimo,
            "tempo_ms": round(tempo_ms(lambda: a_estrela(rotas, o, d)), 3),
            "caminho": " → ".join(caminho),
        })
    return pd.DataFrame(linhas)


def desenhar_mapa(rotas, df, ficheiro):
    """Figura 5: rota ótima de cada caso (T02 a T10) sobre o grafo de estradas."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    casos = df[df["trocos"] > 0]
    fig, eixos = plt.subplots(3, 3, figsize=(13, 15))
    for ax, (_, caso) in zip(eixos.ravel(), casos.iterrows()):
        for u in rotas.cidades:  # estradas a cinzento
            for v in rotas.vizinhos[u]:
                if u < v:
                    (la1, lo1), (la2, lo2) = rotas.coords[u], rotas.coords[v]
                    ax.plot([lo1, lo2], [la1, la2], color="#cccccc", lw=0.8, zorder=1)
        nomes = caso["caminho"].split(" → ")
        ax.plot([rotas.coords[c][1] for c in nomes], [rotas.coords[c][0] for c in nomes],
                color="#d62728", lw=2.2, zorder=2)
        for c in rotas.cidades:
            ax.scatter(rotas.coords[c][1], rotas.coords[c][0], s=8, color="#888888", zorder=3)
        for c, cor in ((caso["origem"], "#2ca02c"), (caso["destino"], "#1f77b4")):
            ax.scatter(rotas.coords[c][1], rotas.coords[c][0], s=70, color=cor, zorder=4)
            ax.annotate(c, (rotas.coords[c][1], rotas.coords[c][0]), fontsize=8,
                        xytext=(4, 4), textcoords="offset points")
        ax.set_title(f'{caso["caso"]}: {caso["custo_km"]} km, {caso["trocos"]} troços', fontsize=10)
        ax.set_aspect(1.3)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(ficheiro, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    rotas = Rotas()
    df = executar_casos(rotas)
    print(df.drop(columns=["caminho", "descricao"]).to_string(index=False))
    print(f"\nTotal de nós: A* = {df['nos_A*'].sum()}, h = 0: {df['nos_h0'].sum()}")
    df.to_excel(os.path.join(PASTA, "resultados_casos_cidades.xlsx"), index=False)
    try:
        desenhar_mapa(rotas, df, os.path.join(PASTA, "figura5_rotas.png"))
        print("Mapa guardado em figura5_rotas.png")
    except ImportError:
        print("matplotlib não instalado: mapa não gerado.")
