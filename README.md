# Tema 4 · Agente Inteligente com Procura Heurística

UC 04914 · Introdução à Inteligência Artificial

Código do relatório: resolução de labirintos (BFS, DFS, A*, gulosa) e rotas entre cidades (A*).

## Estrutura

| Ficheiro | Conteúdo |
| --- | --- |
| `procura_nao_informada.py` | Classe `Labirinto` (modelo formal), BFS, DFS e `valida_solucao` |
| `procura_informada.py` | Heurística de Manhattan, A*, procura gulosa e `verifica_heuristica` |
| `gerar_casos_teste.py` | Gera os 10 casos de teste dos labirintos (semente 2026) |
| `rotas_cidades.py` | Classe `Rotas`, A*, Dijkstra de referência, `valida_caminho`, `verifica_heuristica` |
| `gerar_casos_cidades.py` | Os 10 casos de rotas: executa o A*, valida e desenha o mapa (Figura 5) |
| `reproduzir_resultados.py` | Reproduz as Tabelas 3, 4, 5, 8 e 9 e as verificações |
| `carregar_dados.py` | Leitura da folha Labirintos |
| `dados/` | Ficheiros fornecidos pela UC (`Dados_labirintos.xlsx`, `Tema04_Procura_Heuristica_Instancias.xlsx`) |

## Requisitos

Python 3.9+, `pandas`, `openpyxl` e (opcional, para o mapa) `matplotlib`.

```
pip install pandas openpyxl matplotlib
```

## Como reproduzir

```
python gerar_casos_teste.py        # gera casos_teste_labirintos.xlsx (10 casos)
python gerar_casos_cidades.py      # corre os casos T01-T10 e guarda figura5_rotas.png
python reproduzir_resultados.py    # imprime as Tabelas 3, 4, 5, 8 e 9
```

## Notas

- Os tempos (ms) dependem da máquina; as restantes métricas (nós, custos) são determinísticas.
- Convenções: BFS testa o objetivo ao gerar o nó; DFS, A* e gulosa testam ao retirar da fronteira;
  "nós expandidos" não conta o nó objetivo. Ordem das ações: Cima, Baixo, Esquerda, Direita
  (labirintos) e ordem alfabética (cidades).
