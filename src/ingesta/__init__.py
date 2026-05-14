"""
Paquete de ingesta de datos — Observatorio MinCiencias.

Toda la informacion del proyecto proviene de Socrata (datos.gov.co):
- Investigadores reconocidos: dataset bqtm-4y2h
- Produccion de grupos:        dataset 33dq-ab5a

Exporta cargar_consolidado() y cargar_produccion() para que los notebooks
y scripts puedan importarlas con:
    from ingesta import cargar_consolidado, cargar_produccion
"""

import pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[2]
_RAW = ROOT / "datos" / "raw" / "investigadores_consolidado.csv"
_PROD = ROOT / "datos" / "raw" / "produccion_grupos.csv"


def cargar_consolidado() -> pd.DataFrame:
    """Carga el dataset consolidado de investigadores (77.237 registros, 30 cols).

    Fuente: datos/raw/investigadores_consolidado.csv, descargado desde Socrata
    (bqtm-4y2h). Si no existe localmente, ejecutar primero:

        python -m src.ingesta.minciencias
    """
    if not _RAW.exists():
        raise FileNotFoundError(
            "Dataset no encontrado en datos/raw/investigadores_consolidado.csv. "
            "Ejecute: python -m src.ingesta.minciencias"
        )
    print(f"[ingesta] Cargando CSV: {_RAW}")
    df = pd.read_csv(_RAW, low_memory=False)
    df.columns = df.columns.str.upper()
    print(f"[ingesta] {len(df):,} registros | {df.shape[1]} columnas")
    return df


def cargar_produccion() -> pd.DataFrame:
    """Carga el dataset de Produccion de Grupos de Investigacion (Socrata 33dq-ab5a).

    ~3.2M filas. Llave para cruzar con investigadores: ID_PERSONA_PD <-> ID_PERSONA_PR.
    """
    if not _PROD.exists():
        raise FileNotFoundError(
            "Dataset de produccion no encontrado en datos/raw/produccion_grupos.csv. "
            "Ejecute: python -m src.ingesta.produccion"
        )
    print(f"[ingesta] Cargando CSV produccion: {_PROD}")
    df = pd.read_csv(_PROD, low_memory=False)
    df.columns = df.columns.str.upper()
    print(f"[ingesta] {len(df):,} filas | {df.shape[1]} columnas")
    return df
