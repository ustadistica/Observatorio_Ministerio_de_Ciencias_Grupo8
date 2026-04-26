"""
Paquete de análisis — Observatorio MinCiencias.
"""
from .territorial import hhi, hhi_por_convocatoria, top_territorios, tabla_cuotas
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
    "hhi",
    "hhi_por_convocatoria",
    "top_territorios",
    "tabla_cuotas",
    "construir_panel",
    "comparar_periodo",
    "resumen_tracking",
    "tracking_por_categoria",
    "tracking_todos_periodos",
    "tasa_retencion_por_periodo",
    "matriz_transicion",
    "matrices_todos_periodos",
]
