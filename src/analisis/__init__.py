"""
Paquete de análisis — Observatorio MinCiencias.
"""
from .longitudinal import (
    construir_panel,
    comparar_periodo,
    resumen_tracking,
    tracking_por_categoria,
    tracking_todos_periodos,
    tasa_retencion_por_periodo,
    matriz_transicion,
    matrices_todos_periodos,
)

__all__ = [
    "construir_panel",
    "comparar_periodo",
    "resumen_tracking",
    "tracking_por_categoria",
    "tracking_todos_periodos",
    "tasa_retencion_por_periodo",
    "matriz_transicion",
    "matrices_todos_periodos",
]
