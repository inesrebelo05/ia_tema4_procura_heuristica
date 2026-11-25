"""Leitura das instâncias fornecidas (folha Labirintos)."""
import os

import pandas as pd

PASTA = os.path.dirname(os.path.abspath(__file__))
FICHEIRO_LABIRINTOS = os.path.join(PASTA, "dados", "Dados_labirintos.xlsx")
FICHEIRO_CIDADES = os.path.join(PASTA, "dados", "Tema04_Procura_Heuristica_Instancias.xlsx")


def carregar_labirintos(caminho=FICHEIRO_LABIRINTOS):
    """DataFrame com as 210 instâncias da folha Labirintos."""
    return pd.read_excel(caminho, sheet_name="Labirintos")
