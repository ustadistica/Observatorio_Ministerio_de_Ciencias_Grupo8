"""
analisis/redes.py

Network analysis de co-filiacion institucional — Issue #15.

Un investigador con dos instituciones en inst_filia crea un enlace entre ambas.
Nodo = institucion; arista = investigadores compartidos (peso = conteo).
"""

import pandas as pd
import networkx as nx


def construir_pares(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extrae pares (inst_a, inst_b) de investigadores con doble afiliacion.

    Retorna columnas: [ID_PERSONA_PR, ANO_CONVO_INT, inst_a, inst_b]
    """
    multi = df[df["INST_FILIA"].str.contains("|", na=False, regex=False)].copy()
    multi[["inst_a", "inst_b"]] = (
        multi["INST_FILIA"]
        .str.split("|", n=1, expand=True)
        .apply(lambda s: s.str.strip())
    )
    multi["inst_a"] = multi["inst_a"].str.upper().str.strip()
    multi["inst_b"] = multi["inst_b"].str.upper().str.strip()
    # Normalizar orden para que (A,B) == (B,A)
    multi[["inst_a", "inst_b"]] = pd.DataFrame(
        [sorted([a, b]) for a, b in zip(multi["inst_a"], multi["inst_b"])],
        index=multi.index,
    )
    return multi[["ID_PERSONA_PR", "ANO_CONVO_INT", "inst_a", "inst_b"]].reset_index(drop=True)


def construir_grafo(pares: pd.DataFrame, anio: int = None) -> nx.Graph:
    """
    Construye grafo de co-filiacion a partir de los pares.

    Si anio != None filtra por convocatoria. Peso de arista = n investigadores compartidos.
    """
    if anio is not None:
        pares = pares[pares["ANO_CONVO_INT"] == anio]

    G = nx.Graph()
    for (a, b), grp in pares.groupby(["inst_a", "inst_b"]):
        peso = len(grp)
        if G.has_edge(a, b):
            G[a][b]["weight"] += peso
        else:
            G.add_edge(a, b, weight=peso)
    return G


def metricas_grafo(G: nx.Graph) -> dict:
    """Metricas globales del grafo."""
    if len(G) == 0:
        return {}
    componentes = list(nx.connected_components(G))
    grado = dict(G.degree(weight="weight"))
    return {
        "n_nodos": G.number_of_nodes(),
        "n_aristas": G.number_of_edges(),
        "densidad": round(nx.density(G), 6),
        "n_componentes": len(componentes),
        "tam_componente_mayor": max(len(c) for c in componentes),
        "grado_promedio": round(sum(grado.values()) / len(grado), 2),
        "grado_max": max(grado.values()),
        "nodo_mayor_grado": max(grado, key=grado.get),
    }


def tabla_nodos(G: nx.Graph) -> pd.DataFrame:
    """
    DataFrame de nodos con grado, grado ponderado y betweenness.
    """
    if len(G) == 0:
        return pd.DataFrame()
    grado = dict(G.degree())
    grado_w = dict(G.degree(weight="weight"))
    between = nx.betweenness_centrality(G, weight="weight", normalized=True)
    df = pd.DataFrame({
        "institucion": list(grado.keys()),
        "grado": [grado[n] for n in grado],
        "grado_ponderado": [grado_w[n] for n in grado],
        "betweenness": [round(between[n], 6) for n in grado],
    })
    return df.sort_values("grado_ponderado", ascending=False).reset_index(drop=True)


def tabla_aristas(G: nx.Graph) -> pd.DataFrame:
    """DataFrame de aristas con peso."""
    rows = [{"inst_a": u, "inst_b": v, "peso": d["weight"]} for u, v, d in G.edges(data=True)]
    return pd.DataFrame(rows).sort_values("peso", ascending=False).reset_index(drop=True)


def metricas_por_convocatoria(pares: pd.DataFrame) -> pd.DataFrame:
    """Metricas globales del grafo para cada convocatoria."""
    rows = []
    for anio in sorted(pares["ANO_CONVO_INT"].unique()):
        G = construir_grafo(pares, anio=anio)
        m = metricas_grafo(G)
        m["anio"] = anio
        rows.append(m)
    return pd.DataFrame(rows)[["anio", "n_nodos", "n_aristas", "densidad",
                                "n_componentes", "tam_componente_mayor",
                                "grado_promedio", "grado_max", "nodo_mayor_grado"]]
