"""
Paquete de ingesta de datos — Observatorio MinCiencias.

Exporta cargar_consolidado() para que los notebooks puedan importarla con:
    from ingesta import cargar_consolidado
"""

import pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
_RAW = ROOT / "datos" / "raw" / "investigadores_consolidado.csv"
_TAREA = ROOT / "datos" / "tarea_join" / "investigadores_consolidado.xlsx"


def cargar_consolidado() -> pd.DataFrame:
    """Carga el dataset consolidado de investigadores (77 237 registros, 30 cols).

    Prioridad: datos/raw/investigadores_consolidado.csv (Socrata)
               datos/tarea_join/investigadores_consolidado.xlsx (Excel local)
    """
    if _RAW.exists():
        print(f"[ingesta] Cargando CSV: {_RAW}")
        df = pd.read_csv(_RAW, low_memory=False)
    elif _TAREA.exists():
        print(f"[ingesta] Cargando XLSX: {_TAREA}")
        df = pd.read_excel(_TAREA)
    else:
        raise FileNotFoundError(
            "Dataset no encontrado. Ejecute: python -m src.ingesta.minciencias"
        )
    df.columns = df.columns.str.upper()
    print(f"[ingesta] {len(df):,} registros | {df.shape[1]} columnas")
    return df
