"""Convierte los datasets crudos descargados de Socrata a formato Parquet
para subir al SharePoint institucional como artefactos Silver.

Uso:
    python scripts/exportar_parquet.py            # ambos datasets
    python scripts/exportar_parquet.py --investigadores
    python scripts/exportar_parquet.py --produccion

Entradas (descargadas previamente desde Socrata):
    datos/raw/investigadores_consolidado.csv   (bqtm-4y2h) — usar src.ingesta.minciencias
    datos/raw/produccion_grupos.csv            (33dq-ab5a) — usar src.ingesta.produccion

Salidas:
    datos/processed/investigadores_consolidado.parquet  (~5-8 MB)
    datos/processed/produccion_grupos.parquet           (~80-150 MB)

Estos son los archivos Silver del observatorio: limpios, normalizados (columnas en
MAYUSCULAS, tipos uniformes) y listos para ser consumidos por estudiantes nuevos.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from time import perf_counter

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "datos" / "raw"
OUT = ROOT / "datos" / "processed"


def _format_bytes(num: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


def exportar_investigadores() -> Path:
    src_csv = RAW / "investigadores_consolidado.csv"

    if not src_csv.exists():
        raise FileNotFoundError(
            f"No se encontro {src_csv.relative_to(ROOT)}. "
            "Ejecuta primero: python -m src.ingesta.minciencias"
        )

    print(f"[investigadores] Leyendo CSV de Socrata: {src_csv.relative_to(ROOT)}")
    df = pd.read_csv(src_csv, low_memory=False)
    df.columns = df.columns.str.upper()
    print(f"[investigadores] Shape: {df.shape[0]:,} x {df.shape[1]}")

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "investigadores_consolidado.parquet"
    t0 = perf_counter()
    df.to_parquet(out, compression="zstd", index=False)
    dt = perf_counter() - t0
    size = out.stat().st_size
    print(f"[investigadores] OK -> {out.relative_to(ROOT)} ({_format_bytes(size)}, {dt:.1f}s)")
    return out


def exportar_produccion() -> Path:
    src = RAW / "produccion_grupos.csv"
    if not src.exists():
        raise FileNotFoundError(
            f"No se encontro {src.relative_to(ROOT)}. Ejecuta primero "
            "`python -m src.ingesta.produccion` para descargarlo desde Socrata."
        )

    raw_size = src.stat().st_size
    print(f"[produccion] Leyendo CSV de Socrata: {src.relative_to(ROOT)} ({_format_bytes(raw_size)})")
    t0 = perf_counter()
    df = pd.read_csv(src, low_memory=False)
    print(f"[produccion] CSV leído en {perf_counter() - t0:.1f}s")

    df.columns = df.columns.str.upper()
    print(f"[produccion] Shape: {df.shape[0]:,} × {df.shape[1]}")

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "produccion_grupos.parquet"
    t0 = perf_counter()
    df.to_parquet(out, compression="zstd", index=False)
    dt = perf_counter() - t0
    size = out.stat().st_size
    ratio = raw_size / size if size else 0
    print(
        f"[produccion] OK -> {out.relative_to(ROOT)} "
        f"({_format_bytes(size)}, compresión {ratio:.1f}×, {dt:.1f}s)"
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--investigadores", action="store_true", help="Solo investigadores")
    parser.add_argument("--produccion", action="store_true", help="Solo producción de grupos")
    args = parser.parse_args()

    do_inv = args.investigadores or not args.produccion
    do_prod = args.produccion or not args.investigadores

    if do_inv:
        exportar_investigadores()
    if do_prod:
        exportar_produccion()
    return 0


if __name__ == "__main__":
    sys.exit(main())
