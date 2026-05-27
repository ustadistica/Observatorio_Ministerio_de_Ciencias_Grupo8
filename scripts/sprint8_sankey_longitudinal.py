"""
Sprint 8 — Sankey longitudinal unico (linea de tiempo de transiciones).

Construye una unica imagen con seis columnas verticales (una por convocatoria
2013-2021) y flujos entre cada par consecutivo. Implementacion manual con
matplotlib + curvas bezier porque Plotly Sankey reordena los nodos pese a
las posiciones manuales y produce layouts inconsistentes para sankeys
multi-paso.

Estructura:
    4 categorías (Junior abajo, Asociado, Senior, Emérito arriba) en cada
    una de las 6 columnas. Total: 24 nodos visibles.
    Los flujos solo conectan pares consecutivos.
    Los Eméritos quedan vitalicios: reciben flujo entrante pero no emiten
    flujo saliente.

Salidas:
    artifacts/sprint8_sankey/sankey_linea_tiempo.png   (estatico)
    evidencias/sankey_linea_tiempo_links.csv          (todos los flujos)

Uso:
    python scripts/sprint8_sankey_longitudinal.py
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, PathPatch
from matplotlib.path import Path
import numpy as np
import pandas as pd

from ingesta import cargar_consolidado
from Transformacion import transformar
from analisis.calidad import filtrar
from analisis.longitudinal import (
    construir_panel, comparar_periodo, matriz_transicion,
)

ARTIFACTS = ROOT / "artifacts" / "sprint8_sankey"
EVIDENCIAS = ROOT / "evidencias"
ARTIFACTS.mkdir(parents=True, exist_ok=True)


COLOR_CAT = {
    "Junior":   "#5b8def",
    "Asociado": "#f4a261",
    "Senior":   "#2a9d8f",
    "Emérito":  "#9b5de5",
}
CATEGORIAS = ["Emérito", "Senior", "Asociado", "Junior"]  # orden visual (arriba → abajo)


def _bezier_band(x0, y0a, y0b, x1, y1a, y1b, color, alpha=0.45):
    """
    Construye un poligono tipo Sankey entre dos columnas: dos curvas
    bezier (la superior y la inferior) cerradas en los extremos.
    """
    cx = (x0 + x1) / 2.0
    verts_top = [
        (x0, y0a),
        (cx, y0a), (cx, y1a),
        (x1, y1a),
    ]
    verts_bot = [
        (x1, y1b),
        (cx, y1b), (cx, y0b),
        (x0, y0b),
    ]
    codes_top = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    codes_bot = [Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    verts = verts_top + verts_bot + [(x0, y0a)]
    codes = codes_top + codes_bot + [Path.CLOSEPOLY]
    path = Path(verts, codes)
    return PathPatch(path, facecolor=color, edgecolor="none", alpha=alpha,
                     linewidth=0)


def calcular_layout(panel: pd.DataFrame, anios: list) -> dict:
    """
    Calcula altura de cada nodo por convocatoria + posiciones (top, bottom)
    en escala 0-1. Devuelve dict con la informacion estructurada.
    """
    # Volumen de cada (categoria, anio): cuántos investigadores hay
    volumenes = {}
    for anio in anios:
        sub = panel[panel["ANO_CONVO_INT"] == anio]
        conteo = sub["categoria"].value_counts().to_dict()
        for cat in CATEGORIAS:
            volumenes[(cat, anio)] = int(conteo.get(cat, 0))

    # Volumen total maximo de cualquier columna (para normalizar)
    max_col = max(sum(volumenes[(c, a)] for c in CATEGORIAS) for a in anios)

    # Altura disponible = 1.0 (en eje Y), gap entre categorías = 0.02
    gap_cat = 0.02
    total_gaps = gap_cat * (len(CATEGORIAS) - 1)
    altura_disp = 1.0 - total_gaps

    # Cada nodo ocupa: altura = (volumen / max_col) * altura_disp,
    # MIN_HEIGHT garantizado para que nodos chicos sean visibles
    MIN_HEIGHT = 0.022  # garantiza visibilidad de los Eméritos (pocos pero importantes)

    nodos = {}  # (cat, anio) -> (y_top, y_bottom, volumen)
    for anio in anios:
        # Alturas escaladas por columna
        alturas_raw = []
        for cat in CATEGORIAS:
            v = volumenes[(cat, anio)]
            h_raw = (v / max_col) * altura_disp if max_col else 0
            alturas_raw.append(max(h_raw, MIN_HEIGHT if v > 0 else 0))
        # Posicionamos de arriba hacia abajo
        y_top = 1.0
        for k, cat in enumerate(CATEGORIAS):
            h = alturas_raw[k]
            y_bottom = y_top - h
            nodos[(cat, anio)] = (y_top, y_bottom, volumenes[(cat, anio)])
            y_top = y_bottom - gap_cat

    return {"nodos": nodos, "volumenes": volumenes, "max_col": max_col}


def construir_flujos(panel: pd.DataFrame, anios: list) -> pd.DataFrame:
    """Devuelve un DataFrame con cada flujo entre pares consecutivos."""
    filas = []
    for a, b in zip(anios, anios[1:]):
        comp = comparar_periodo(panel, a, b)
        conteos, _ = matriz_transicion(comp, incluir_desaparece=False)
        for cat_in in CATEGORIAS:
            if cat_in not in conteos.index:
                continue
            for cat_out in CATEGORIAS:
                if cat_out not in conteos.columns:
                    continue
                v = int(conteos.loc[cat_in, cat_out])
                if v <= 0:
                    continue
                filas.append({
                    "anio_inicial": int(a),
                    "anio_final": int(b),
                    "categoria_inicial": cat_in,
                    "categoria_final": cat_out,
                    "n_investigadores": v,
                })
    return pd.DataFrame(filas)


def dibujar_sankey(panel: pd.DataFrame, anios: list,
                    layout: dict, flujos: pd.DataFrame,
                    out_png: pathlib.Path) -> None:
    fig, ax = plt.subplots(figsize=(16, 7.5))

    # Posiciones X de cada columna
    n_cols = len(anios)
    x_min, x_max = 0.06, 0.94
    x_positions = {anio: x_min + i * (x_max - x_min) / (n_cols - 1)
                   for i, anio in enumerate(anios)}
    node_width = 0.012

    nodos = layout["nodos"]

    # Para cada par consecutivo, dibujar los flujos
    # Importante: dentro de cada nodo origen distribuimos verticalmente cada
    # flujo según el orden de las categorías destino (de arriba abajo) —
    # esto mantiene el orden vertical coherente con la columna destino.
    for a, b in zip(anios, anios[1:]):
        sub_flujos = flujos[(flujos["anio_inicial"] == a) &
                             (flujos["anio_final"] == b)]
        # Posicion "cursor" dentro de cada nodo origen y destino, segun se
        # van consumiendo flujos.
        cursor_origen = {(cat, a): nodos[(cat, a)][0] for cat in CATEGORIAS}
        cursor_destino = {(cat, b): nodos[(cat, b)][0] for cat in CATEGORIAS}

        # Orden: dentro de cada origen, primero los flujos hacia la
        # categoria destino que aparece mas arriba en la columna destino.
        sub_flujos_ord = sub_flujos.copy()
        cat_order = {c: i for i, c in enumerate(CATEGORIAS)}
        sub_flujos_ord["__o_in"] = sub_flujos_ord["categoria_inicial"].map(cat_order)
        sub_flujos_ord["__o_out"] = sub_flujos_ord["categoria_final"].map(cat_order)
        sub_flujos_ord = sub_flujos_ord.sort_values(["__o_in", "__o_out"])

        # Volumen total del nodo origen (para escalar)
        for _, row in sub_flujos_ord.iterrows():
            cat_in = row["categoria_inicial"]
            cat_out = row["categoria_final"]
            v = row["n_investigadores"]

            # Altura del flujo en el nodo origen
            vol_origen = layout["volumenes"][(cat_in, a)]
            top_o, bot_o, _ = nodos[(cat_in, a)]
            alto_total_o = top_o - bot_o
            h_flujo_o = alto_total_o * (v / vol_origen) if vol_origen else 0

            y_top_o = cursor_origen[(cat_in, a)]
            y_bot_o = y_top_o - h_flujo_o
            cursor_origen[(cat_in, a)] = y_bot_o

            # Altura del flujo en el nodo destino
            vol_dest = layout["volumenes"][(cat_out, b)]
            top_d, bot_d, _ = nodos[(cat_out, b)]
            alto_total_d = top_d - bot_d
            h_flujo_d = alto_total_d * (v / vol_dest) if vol_dest else 0

            y_top_d = cursor_destino[(cat_out, b)]
            y_bot_d = y_top_d - h_flujo_d
            cursor_destino[(cat_out, b)] = y_bot_d

            color = COLOR_CAT[cat_in]
            # Ojo a las coordenadas: x0/x1 son los bordes interiores del nodo
            x0 = x_positions[a] + node_width / 2
            x1 = x_positions[b] - node_width / 2
            band = _bezier_band(x0, y_top_o, y_bot_o,
                                 x1, y_top_d, y_bot_d,
                                 color=color, alpha=0.42)
            ax.add_patch(band)

    # Dibujar los nodos (rectangulos) por encima de los flujos
    for cat in CATEGORIAS:
        for anio in anios:
            y_top, y_bot, vol = nodos[(cat, anio)]
            if vol == 0:
                continue
            x = x_positions[anio] - node_width / 2
            rect = Rectangle((x, y_bot), node_width, y_top - y_bot,
                              facecolor=COLOR_CAT[cat], edgecolor="white",
                              linewidth=1.0, zorder=3)
            ax.add_patch(rect)
            # Etiqueta de cantidad al lado del nodo. Para volúmenes pequenos
            # (ej. Emerito ~50-130) usamos fuente menor para que la cifra
            # entre en el espacio sin solaparse.
            font_size_label = 8.5 if vol >= 200 else 7.5
            ax.text(x + node_width + 0.005,
                    (y_top + y_bot) / 2,
                    f"{vol:,}".replace(",", "."),
                    va="center", ha="left",
                    fontsize=font_size_label, color="#0b1320",
                    zorder=4)

    # Etiquetas de categoría — solo en la primera y última columna
    for cat in CATEGORIAS:
        # Columna izquierda
        y_top, y_bot, vol = nodos[(cat, anios[0])]
        if vol > 0:
            ax.text(x_positions[anios[0]] - node_width / 2 - 0.008,
                    (y_top + y_bot) / 2,
                    cat,
                    va="center", ha="right",
                    fontsize=11, fontweight="bold",
                    color=COLOR_CAT[cat], zorder=4)
        # Columna derecha — desplazada más a la derecha para no montarse con los números
        y_top, y_bot, vol = nodos[(cat, anios[-1])]
        if vol > 0:
            ax.text(x_positions[anios[-1]] + node_width / 2 + 0.048,
                    (y_top + y_bot) / 2,
                    cat,
                    va="center", ha="left",
                    fontsize=11, fontweight="bold",
                    color=COLOR_CAT[cat], zorder=4)

    # Etiquetas de año arriba
    for anio in anios:
        ax.text(x_positions[anio], 1.045, str(anio),
                ha="center", va="bottom",
                fontsize=15, fontweight="bold",
                color="#0b1320")

    # Título — subimos la altura para no chocar con la fila de años
    ax.text(0.0, 1.18,
            "Trayectoria de categorías 2013 → 2021",
            ha="left", va="bottom",
            fontsize=16, fontweight="bold", color="#0b1320")
    ax.text(0.0, 1.142,
            "Flujos entre convocatorias consecutivas — cada banda son los investigadores que se mantienen, suben o bajan de categoría",
            ha="left", va="bottom", fontsize=10.5, color="#6b7280")

    ax.set_xlim(-0.04, 1.10)
    ax.set_ylim(-0.06, 1.22)
    ax.set_axis_off()
    fig.subplots_adjust(left=0.04, right=0.96, top=0.94, bottom=0.04)
    fig.savefig(out_png, dpi=140, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


def main() -> None:
    print("[1/4] Cargando panel longitudinal...")
    inv = filtrar(transformar(cargar_consolidado()))
    panel = construir_panel(inv)
    anios = sorted(int(a) for a in panel["ANO_CONVO_INT"].dropna().unique())
    print(f"      Convocatorias: {anios}")

    print("\n[2/4] Calculando layout (alturas y posiciones)...")
    layout = calcular_layout(panel, anios)
    print(f"      Max volumen por columna: {layout['max_col']:,}")
    for anio in anios:
        total = sum(layout["volumenes"][(c, anio)] for c in CATEGORIAS)
        print(f"      {anio}: {total:,} investigadores")

    print("\n[3/4] Construyendo flujos...")
    flujos = construir_flujos(panel, anios)
    print(f"      Flujos totales: {len(flujos):,}")

    print("\n[4/4] Dibujando Sankey...")
    out_png = ARTIFACTS / "sankey_linea_tiempo.png"
    dibujar_sankey(panel, anios, layout, flujos, out_png)
    flujos.to_csv(EVIDENCIAS / "sankey_linea_tiempo_links.csv",
                   index=False, encoding="utf-8")
    print(f"      {out_png}")
    print(f"      {EVIDENCIAS / 'sankey_linea_tiempo_links.csv'}")


if __name__ == "__main__":
    main()
