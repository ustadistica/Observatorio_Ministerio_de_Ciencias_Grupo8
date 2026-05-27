"""
Sprint 7 — Género como lente transversal.

El director pidió eliminar el eje "Personas" y mostrar el comportamiento de
género **integrado** en los demás ejes (Producción, Territorios, Campos OCDE).
Este script materializa esa lectura transversal con tres figuras:

  1. Género × territorio: % de mujeres por departamento de residencia
     (top 15 con más investigadoras reconocidas).
  2. Género × productividad: brecha de productividad por gran área OCDE
     (mismo cálculo del Sprint 5, regenerado con paleta nueva editorial).
  3. Género × campos OCDE: % de mujeres por gran área OCDE en la última
     convocatoria (2021) — barras horizontales con punto de referencia 50 %.

Salidas:
    artifacts/sprint7_genero/fig_genero_territorial.png
    artifacts/sprint7_genero/fig_genero_ocde_2021.png
    evidencias/genero_por_departamento.csv
    evidencias/genero_por_gran_area_2021.csv

Uso:
    python scripts/sprint7_genero_transversal.py
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from ingesta import cargar_consolidado
from Transformacion import transformar
from analisis.calidad import filtrar

ARTIFACTS = ROOT / "artifacts" / "sprint7_genero"
EVIDENCIAS = ROOT / "evidencias"
ARTIFACTS.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


def genero_por_departamento(inv: pd.DataFrame, top_n: int = 15) -> pd.DataFrame:
    sub = inv[inv["NME_GENERO_PR"].isin(["FEMENINO", "MASCULINO"])].copy()
    g = (sub.groupby("NME_DEPARTAMENTO_RES_PR")["NME_GENERO_PR"]
            .value_counts()
            .unstack(fill_value=0)
            .reset_index())
    g["n_total"] = g["FEMENINO"] + g["MASCULINO"]
    g["pct_femenino"] = (g["FEMENINO"] / g["n_total"] * 100).round(1)
    g = g.sort_values("n_total", ascending=False).head(top_n)
    return g


def genero_por_gran_area_2021(inv: pd.DataFrame) -> pd.DataFrame:
    sub = inv[(inv["ANO_CONVO_INT"] == 2021) &
              inv["NME_GENERO_PR"].isin(["FEMENINO", "MASCULINO"]) &
              ~inv["NME_GRAN_AREA_PR"].isin(["NO REGISTRA", "NO REPORTADO"])].copy()
    g = (sub.groupby("NME_GRAN_AREA_PR")["NME_GENERO_PR"]
            .value_counts()
            .unstack(fill_value=0)
            .reset_index())
    g["n_total"] = g["FEMENINO"] + g["MASCULINO"]
    g["pct_femenino"] = (g["FEMENINO"] / g["n_total"] * 100).round(1)
    return g.sort_values("pct_femenino", ascending=True)


def fig_genero_territorial(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 6.5))
    orden = df.sort_values("pct_femenino", ascending=True)
    paleta = ["#b08868" if p < 50 else "#3f7a8a" for p in orden["pct_femenino"]]
    bars = ax.barh(orden["NME_DEPARTAMENTO_RES_PR"], orden["pct_femenino"],
                    color=paleta)
    ax.axvline(50, color="#444", linestyle="--", linewidth=1, alpha=0.6)
    ax.text(50.5, len(orden) - 0.4, "paridad", color="#444", fontsize=9)
    for bar, val, n in zip(bars, orden["pct_femenino"], orden["n_total"]):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}%  (n={int(n):,})",
                va="center", fontsize=8.5, color="#333")
    ax.set_xlim(0, 70)
    ax.set_xlabel("% de mujeres entre los investigadores reconocidos")
    ax.set_ylabel("")
    ax.set_title("Género × territorio: top 15 departamentos por número de investigadores")
    plt.tight_layout()
    fig.savefig(ARTIFACTS / "fig_genero_territorial.png",
                dpi=150, bbox_inches="tight")
    plt.close()


def fig_genero_ocde_2021(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    paleta = ["#b08868" if p < 50 else "#3f7a8a" for p in df["pct_femenino"]]
    bars = ax.barh(df["NME_GRAN_AREA_PR"], df["pct_femenino"], color=paleta)
    ax.axvline(50, color="#444", linestyle="--", linewidth=1, alpha=0.6)
    ax.text(50.5, len(df) - 0.4, "paridad", color="#444", fontsize=9)
    for bar, val, n in zip(bars, df["pct_femenino"], df["n_total"]):
        ax.text(val + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}%  (n={int(n):,})",
                va="center", fontsize=9, color="#333")
    ax.set_xlim(0, 70)
    ax.set_xlabel("% de mujeres entre los investigadores reconocidos (2021)")
    ax.set_ylabel("")
    ax.set_title("Género × gran área OCDE — convocatoria 2021")
    plt.tight_layout()
    fig.savefig(ARTIFACTS / "fig_genero_ocde_2021.png",
                dpi=150, bbox_inches="tight")
    plt.close()


def main() -> None:
    print("[1/3] Cargando datos...")
    inv = filtrar(transformar(cargar_consolidado()))

    print("\n[2/3] Género × territorio (top 15 departamentos)...")
    g_dpto = genero_por_departamento(inv, top_n=15)
    print(g_dpto[["NME_DEPARTAMENTO_RES_PR", "FEMENINO", "MASCULINO",
                  "n_total", "pct_femenino"]].to_string(index=False))

    print("\n[3/3] Género × gran área OCDE (2021)...")
    g_area = genero_por_gran_area_2021(inv)
    print(g_area[["NME_GRAN_AREA_PR", "FEMENINO", "MASCULINO",
                  "n_total", "pct_femenino"]].to_string(index=False))

    fig_genero_territorial(g_dpto)
    fig_genero_ocde_2021(g_area)

    g_dpto.to_csv(EVIDENCIAS / "genero_por_departamento.csv", index=False)
    g_area.to_csv(EVIDENCIAS / "genero_por_gran_area_2021.csv", index=False)

    print(f"\nFiguras: {ARTIFACTS.relative_to(ROOT)}")
    print(f"CSVs:    evidencias/genero_*.csv")


if __name__ == "__main__":
    main()
