"""
Genera docs/manual.ipynb — manual reproducible del Observatorio.

El notebook está organizado por los cuatro ejes del análisis (Producción,
Territorios, Campos OCDE, Longitudinal), con la sección de cautelas previas
(calidad y diversidad invisible) al inicio. El género no aparece como eje
propio sino como dimensión transversal integrada en cada eje.

Uso:
    python scripts/generar_manual.py
"""

import pathlib
import sys

import nbformat as nbf

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

cells = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text))


# =====================================================================
# Portada
# =====================================================================
md("""# Manual reproducible — Observatorio MinCiencias

> Universidad Santo Tomás · Ustadistica · 2026-I

Este manual reproduce, en código y con texto explicativo, los hallazgos del
observatorio sobre el sistema de reconocimiento de investigadores de
MinCiencias. No reemplaza el informe final; lo precede.

**Lectura por cuatro ejes.** A partir de las cautelas metodológicas iniciales,
el manual se organiza en cuatro bloques temáticos:

1. **Producción** — autoría no reconocida, productividad por categoría, brecha de género en outputs.
2. **Territorios** — concentración, ratio per cápita, flujos investigador → institución, brecha de género territorial.
3. **Campos OCDE** — volumen, productividad por área, composición de tipologías, brecha de género por disciplina.
4. **Análisis longitudinal** — matrices de transición, Sankeys, Eméritos vitalicios.

El **género no es un eje aparte** sino una dimensión que atraviesa los tres primeros.

**Cómo usarlo.** Ejecute las celdas en orden. Cada sección produce figuras en
`artifacts/` y tablas en `evidencias/`. Las funciones reutilizables viven en
`src/analisis/`; los scripts orquestadores en `scripts/`.

**Insumos.** Antes de ejecutar este manual hay que haber descargado los
datasets de Socrata:

```bash
python -m src.ingesta.minciencias    # 77.237 filas
python -m src.ingesta.produccion     # 3.166.629 filas (~1.2 GB)
```
""")

# =====================================================================
# 1. Setup
# =====================================================================
md("""## 1. Setup y carga de datos

Carga los dos datasets de Socrata, aplica la transformación común y deja
listos los DataFrames `inv` (padrón de investigadores) y `prod` (producción
de grupos). Todas las celdas posteriores asumen estos dos objetos en memoria.
""")

code("""# Setup de paths e imports
import pathlib
import sys

ROOT = pathlib.Path.cwd()
if (ROOT / "src").exists():
    sys.path.insert(0, str(ROOT / "src"))
elif (ROOT.parent / "src").exists():
    ROOT = ROOT.parent
    sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
pd.set_option("display.max_columns", 100)
pd.set_option("display.width", 160)
print(f"ROOT = {ROOT}")
""")

code("""# Carga de los dos datasets desde Socrata (CSVs en datos/raw/)
from ingesta import cargar_consolidado, cargar_produccion
from Transformacion import transformar
from analisis.produccion import normalizar_produccion

inv = transformar(cargar_consolidado())
print(f"Padron de investigadores: {inv.shape}")

prod = normalizar_produccion(cargar_produccion())
print(f"Produccion de grupos:     {prod.shape}")
""")


# =====================================================================
# 2. Cautelas previas — calidad + diversidad invisible
# =====================================================================
md("""## 2. Cautelas previas

### 2.1 Atípicos de edad

El padrón contiene **22 apariciones con edad superior a 100 años** (máximo: 956).
Decisión metodológica: eliminación, con cada caso auditable en
`evidencias/calidad_atipicos_edad.csv`. Justificación: 22 sobre 77.237 (0,03 %);
el sesgo introducido es despreciable.
""")

code("""from analisis.calidad import (
    detectar_atipicos_edad, resumen_tratamiento, filtrar
)

atipicos = detectar_atipicos_edad(inv)
print(f"Atipicos detectados: {len(atipicos)}")
atipicos.head(10)
""")

code("""inv_clean = filtrar(inv)
print(f"Antes:    {len(inv):,} registros")
print(f"Despues:  {len(inv_clean):,} registros (drop = {len(inv) - len(inv_clean)})")
""")

md("""### 2.2 Diversidad invisible

Las variables `ID_VICTIMA_CONFLICTO`, `TXT_GRUPO_ETNICO` y `TXT_POBLACION_DISCA`
sólo se capturan desde 2021. Las cinco convocatorias anteriores (2013-2019)
tienen 0 % de cobertura. **No se retropola**: la condición de víctima del
conflicto no es estática.

La comparación 2021 vs DANE-CNPV 2018 / RUV 2021 muestra subrepresentación de
indígenas (7,9× menos que su peso poblacional), afros (3×), víctimas del
conflicto (8,6×) y personas con discapacidad (8×).
""")

code("""from analisis.diversidad import cobertura_por_convocatoria, comparar_dane

cob = cobertura_por_convocatoria(inv_clean)
cob[["ANO_CONVO_INT", "n_total",
     "ID_VICTIMA_CONFLICTO_pct_cobertura",
     "TXT_GRUPO_ETNICO_pct_cobertura",
     "TXT_POBLACION_DISCA_pct_cobertura"]]
""")

code("""inv_2021 = inv_clean[inv_clean["ANO_CONVO_INT"] == 2021]
comp = comparar_dane(inv_2021)
comp
""")

md("""### 2.3 Tabla maestra de instituciones

El campo `inst_filia` registra **2.762 cadenas únicas** que corresponden a
~800 IES reales. El observatorio construyó una primera tabla maestra
(211 IES canónicas) que cubre el 91 % del padrón.
""")

code("""maestra = pd.read_csv(ROOT / "evidencias/tabla_maestra_ies.csv")
mapping = pd.read_csv(ROOT / "evidencias/mapping_inst_filia_to_ies.csv")

cob = (mapping.loc[mapping["estado"] == "asignado", "n_apariciones"].sum()
       / mapping["n_apariciones"].sum() * 100)
print(f"IES canonicas: {len(maestra)}")
print(f"Cobertura del padron: {cob:.1f}%")
maestra.head(15)
""")


# =====================================================================
# 3. Eje 1 — Producción
# =====================================================================
md("""## 3. Eje 1 — Producción

Cobertura del padrón, productividad por categoría y brecha de género en outputs.
""")

md("""### 3.1 Autoría no reconocida

De los 77.401 autores únicos en `33dq-ab5a`, sólo 28.590 están en el padrón de
reconocidos. **Los 48.811 restantes (36,9 %) firman productos sin perfil
ScienTI reconocido.** La proporción crece con el tiempo: del 23 % en 2013 al
28 % en 2021.
""")

code("""from analisis.produccion import (
    cobertura_reconocidos, cobertura_autores_unicos,
    productividad_por_categoria, brecha_productividad_genero,
    reconocidos_sin_produccion
)

cov = cobertura_autores_unicos(prod, inv_clean)
for k, v in cov.items():
    print(f"  {k}: {v:,}" if isinstance(v, int) else f"  {k}: {v}")
""")

md("""### 3.2 Productividad por categoría

Junior 30 productos → Asociado 65 → **Senior 121** → Emérito 34. El sistema
premia productividad de manera ordenada. Los Eméritos producen menos que los
Asociados, no porque el sistema los exija menos sino porque el reconocimiento
queda **vitalicio**: una vez reconocidos no se postulan otra vez, así que la
métrica oficial pierde de vista su producción posterior.
""")

code("""prod_cat = productividad_por_categoria(prod, inv_clean)
prod_cat.head(20)
""")

md("""### 3.3 Brecha de género en productividad

En cinco de las seis grandes áreas las mujeres registran menos productos en
promedio. Única excepción: Humanidades. Mayores brechas: Ciencias Médicas
(--2,95 productos) e Ingeniería (--2,59).
""")

code("""brecha = brecha_productividad_genero(prod, inv_clean)
brecha = brecha[~brecha["NME_GRAN_AREA_PR"].isin(["NO REGISTRA", "NO REPORTADO"])]
brecha
""")

md("""### 3.4 Reconocidos sin producción

El porcentaje de reconocidos sin ningún producto registrado en su ventana de
convocatoria pasa del 15,4 % (2013) al 5,5 % (2021). Interpretación más razonable:
la captura del campo mejoró, no necesariamente que produzcan más.
""")

code("""sin_prod = reconocidos_sin_produccion(prod, inv_clean)
sin_prod
""")


# =====================================================================
# 4. Eje 2 — Territorios
# =====================================================================
md("""## 4. Eje 2 — Territorios

Concentración, ratio per cápita, flujos investigador → institución y
participación femenina por departamento. Para el director este es el eje
más relevante.
""")

md("""### 4.1 Concentración residencial

Bogotá D.C. (32 %) + Antioquia (16 %) = 51 % del padrón. El restante se
distribuye entre los otros 30 departamentos. 22 departamentos no llegan a
500 investigadores reconocidos.
""")

code("""top_dpto = (inv_clean["NME_DEPARTAMENTO_RES_PR"].value_counts()
            .head(15).reset_index())
top_dpto.columns = ["departamento", "n_investigadores"]
top_dpto["pct"] = (top_dpto["n_investigadores"] / len(inv_clean) * 100).round(1)
top_dpto
""")

md("""### 4.2 Flujos residencia → departamento de la institución

Con la tabla maestra de IES se puede cruzar el departamento donde vive el
investigador con el departamento donde está su institución. Resultados clave:

- Bogotá retiene 92 % de sus investigadores y absorbe ~1.000 de otros departamentos.
- Antioquia → Bogotá: 242 investigadores. Valle del Cauca → Bogotá: 236.
- Cundinamarca tiene 67 % de retención local (el resto se va a Bogotá).
- Chocó retiene 92 % pese a tener apenas 49 reconocidos.
- El único investigador de Vichada trabaja en Bogotá.
""")

code("""import subprocess
subprocess.run(["python3", "scripts/sprint6_geografia_institucional.py"],
               cwd=ROOT, check=True)
""")

code("""resumen = pd.read_csv(ROOT / "evidencias/geografia_resumen_por_dpto_residencia.csv")
resumen.head(15)
""")

md("""**Sankey territorial residencia → institución** (interactivo).
""")

code("""import subprocess
subprocess.run(["python3", "scripts/sprint6_sankey_territorial.py"], cwd=ROOT, check=True)
""")

code("""from IPython.display import IFrame
IFrame("../artifacts/sprint6_sankey/sankey_territorial.html", width=950, height=620)
""")

md("""### 4.3 Brecha de género por territorio

**Ningún departamento alcanza la paridad de género.** Máximo: Boyacá (42 %),
Bolívar (42 %) y Cundinamarca (41 %). Mínimo: Risaralda (30 %), Caldas (35 %).
""")

code("""import subprocess
subprocess.run(["python3", "scripts/sprint7_genero_transversal.py"],
               cwd=ROOT, check=True)
""")

code("""genero_dpto = pd.read_csv(ROOT / "evidencias/genero_por_departamento.csv")
genero_dpto[["NME_DEPARTAMENTO_RES_PR", "FEMENINO", "MASCULINO",
             "n_total", "pct_femenino"]]
""")


# =====================================================================
# 5. Eje 3 — Campos OCDE
# =====================================================================
md("""## 5. Eje 3 — Campos OCDE

Volumen, productividad por investigador y composición por género dentro de
cada disciplina.
""")

md("""### 5.1 Volumen y productividad por área

Ciencias Sociales gana en volumen total (585 mil productos). Pero
**Ingeniería gana en productividad por investigador** (67 productos por
investigador, contra 48 de Humanidades).
""")

code("""import subprocess
subprocess.run(["python3", "scripts/sprint6_ocde_composicion.py"], cwd=ROOT, check=True)
""")

code("""prod_area = pd.read_csv(ROOT / "evidencias/ocde_productividad_por_area.csv")
prod_area
""")

md("""### 5.2 Composición de tipologías por área

Tres categorías concentran ~73 % de la producción: Formación de RR.HH. (33 %),
Apropiación social (30 %), Nuevo conocimiento Tipo A (10 %). El mix varía
por disciplina.
""")

code("""composicion = pd.read_csv(ROOT / "evidencias/ocde_composicion_por_area.csv")
pivot = composicion.pivot_table(
    index="NME_GRAN_AREA_PR",
    columns="NME_TIPO_MEDICION_PD",
    values="pct", fill_value=0).round(1)
pivot
""")

md("""### 5.3 Brecha de género por disciplina

En la convocatoria 2021 sólo Ciencias Médicas (50,9 %) supera la paridad.
Ingeniería registra el mínimo (26,5 %).
""")

code("""genero_area = pd.read_csv(ROOT / "evidencias/genero_por_gran_area_2021.csv")
genero_area
""")


# =====================================================================
# 6. Eje 4 — Análisis longitudinal
# =====================================================================
md("""## 6. Eje 4 — Análisis longitudinal

Cómo cambian las categorías de los investigadores entre convocatorias. Patrón
clave: la mayoría se mantiene, pero los descensos desde Asociado a Junior son
significativos y los Eméritos no reaparecen (porque quedan vitalicios).
""")

md("""### 6.1 Matrices de transición
""")

code("""from analisis.longitudinal import (
    construir_panel, matrices_todos_periodos
)

panel = construir_panel(inv_clean)
anios = sorted(panel["ANO_CONVO_INT"].dropna().unique())
print(f"Convocatorias en el panel: {anios}")

matrices = matrices_todos_periodos(panel, incluir_desaparece=True)
for periodo, m in matrices.items():
    print(f"\\n{periodo}")
    print(m["conteos"])
""")

md("""### 6.2 Sankeys de transición de categoría

Cinco diagramas, uno por par consecutivo. Permiten ver flujos de promoción,
descenso y desaparición.
""")

code("""import subprocess
subprocess.run(["python3", "scripts/sprint6_sankey_categoria.py"], cwd=ROOT, check=True)
""")

code("""from IPython.display import IFrame
IFrame("../artifacts/sprint6_sankey/sankey_2019_2021.html", width=900, height=550)
""")

md("""### 6.3 Eméritos vitalicios

**Caveat importante.** En las matrices, los Eméritos aparecen al 100 % en la
columna "Desaparece" en cada par consecutivo. La lectura correcta no es que
sean expulsados del sistema: **el reconocimiento Emérito queda vitalicio y no
requiere re-postulación.** No reaparecen porque no lo necesitan.
""")


# =====================================================================
# 7. Cierre
# =====================================================================
md("""## 7. Cierre — recomendaciones de política pública

Los hallazgos se agrupan en cuatro líneas operativas para MinCiencias.

### A. Calidad y gobernanza del dato
- Validación previa a la publicación: edad ≤ 100, fecha de convocatoria distinta de la de publicación.
- Adopción de la tabla maestra de instituciones que aquí se propone.
- Campo obligatorio de departamento de la institución.

### B. Equidad y diversidad
- Captura obligatoria de etnia, discapacidad y conflicto desde el formulario inicial — no sólo desde 2021.
- Comparar representación contra población con educación superior, no contra población total.
- Programas focalizados en regiones con baja retención local (Cundinamarca, Risaralda, departamentos amazónicos).
- Indicadores de paridad de género por departamento como métrica oficial — ningún departamento alcanza paridad hoy.

### C. Apertura y trazabilidad
- Captura sistemática de doble afiliación en todas las convocatorias.
- Apertura del padrón completo de ScienTI.
- Apertura del dataset de proyectos evaluados.

### D. Métricas alineadas con la realidad
- Productividad ajustada por categoría, área OCDE y género.
- Reporte de flujos investigador–institución (residencia vs.\\ institución).
- Calendario predecible de convocatorias.

---

**Cierre.** Este observatorio queda como herramienta abierta. Código, datos
de evidencia, tabla maestra de instituciones, manual reproducible, dashboard
interactivo y presentación HTML están publicados en
`github.com/ustadistica/Observatorio_Ministerio_de_Ciencias_Grupo8`.
""")


# =====================================================================
# Guardar
# =====================================================================
def main() -> None:
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.11"},
        "title": "Manual reproducible — Observatorio MinCiencias",
    }
    salida = DOCS / "manual.ipynb"
    with open(salida, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    print(f"Notebook generado: {salida}")
    print(f"Celdas totales: {len(cells)}")
    print(f"  Markdown: {sum(1 for c in cells if c['cell_type'] == 'markdown')}")
    print(f"  Codigo:   {sum(1 for c in cells if c['cell_type'] == 'code')}")


if __name__ == "__main__":
    main()
