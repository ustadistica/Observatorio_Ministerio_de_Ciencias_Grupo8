# Observatorio MinCiencias · Paquete de artefactos

Datos limpios y modelos consolidados del **Observatorio de Investigadores Reconocidos de MinCiencias**, construido por Ustadistica (Universidad Santo Tomás) en 2026-I.

Este paquete contiene los artefactos **Silver** (datasets normalizados) y **Gold** (modelo dimensional) que produce el observatorio. Está pensado para que cualquier investigador, docente o estudiante pueda consumir los datos sin tener que ejecutar el pipeline completo del proyecto.

---

## Origen de los datos

**Fuente única: Socrata · `datos.gov.co`**

Los dos datasets primarios provienen exclusivamente de la API pública de Socrata. No se mezclan con snapshots externos, archivos privados ni inyecciones manuales.

| Dataset | Identificador Socrata | URL |
|---|---|---|
| Investigadores reconocidos | `bqtm-4y2h` | [datos.gov.co/resource/bqtm-4y2h.csv](https://www.datos.gov.co/resource/bqtm-4y2h.csv) |
| Producción de grupos de investigación | `33dq-ab5a` | [datos.gov.co/resource/33dq-ab5a.csv](https://www.datos.gov.co/resource/33dq-ab5a.csv) |

Cobertura temporal: **2013 a 2021**, seis convocatorias de clasificación de investigadores (640, 693, 737, 781, 833 y 894).

---

## Contenido del paquete

```
.
├── README.md                            (este archivo)
├── catalogo.yaml                        diccionario de las 30 variables
├── silver/
│   ├── investigadores_consolidado.parquet     (1.2 MB)
│   └── produccion_grupos.parquet              (128 MB)
├── gold/
│   └── observatorio.duckdb                    (229 MB)
└── referencia/
    └── tabla_maestra_ies.csv                  (15 KB)
```

> **Nota.** Si recibes el paquete con otra estructura (todo plano, o con nombres distintos), la lógica de carga es la misma — solo ajusta las rutas en los ejemplos de abajo.

---

## Inventario por archivo

### 1. `silver/investigadores_consolidado.parquet`

**Padrón maestro de investigadores reconocidos.**

| Métrica | Valor |
|---|---|
| Filas (apariciones) | 77.237 |
| Investigadores únicos | 30.086 |
| Columnas | 30 |
| Convocatorias | 640 (2013), 693 (2014), 737 (2015), 781 (2017), 833 (2018), 894 (2021) |
| Llave única | `ID_PERSONA_PR` |
| Tamaño | 1,2 MB (Parquet zstd) · 28 MB en CSV |

Cada fila es la **aparición de un investigador en una convocatoria**. Como un mismo investigador puede aparecer en varias, el conteo de filas (77.237) es mayor que el de personas únicas (30.086).

Variables clave: `ID_PERSONA_PR`, `NME_CONVOCATORIA`, `NME_CLASIFICACION_PR` (Junior/Asociado/Senior/Emérito), `NME_GRAN_AREA_PR` (área OCDE), `NME_GENERO_PR`, `NME_DEPARTAMENTO_RES_PR`, `INST_FILIA` (instituciones de afiliación), `EDAD_ANOS_PR`, `TXT_GRUPO_ETNICO`, `TXT_POBLACION_DISCA`, `ID_VICTIMA_CONFLICTO`.

Variables completas y descripciones → `catalogo.yaml`.

**Tratamientos aplicados:**
- Columnas normalizadas a MAYÚSCULAS.
- Tipos uniformes (`ID_PERSONA_PR` como entero, `EDAD_ANOS_PR` como entero).
- Conservados los valores tal como llegan de Socrata; los outliers de edad (22 apariciones con edad > 100 años, máximo 956) **no se removieron del archivo** — están documentados para que cada usuario decida cómo tratarlos.

---

### 2. `silver/produccion_grupos.parquet`

**Padrón de productos académicos contabilizados a grupos de investigación.**

| Métrica | Valor |
|---|---|
| Filas (productos-autor) | 3.166.629 |
| Autores únicos | 77.401 |
| Columnas | 14 |
| Convocatorias cubiertas | 16 al 21 (2013–2021) |
| Llave de cruce con investigadores | `ID_PERSONA_PD ↔ ID_PERSONA_PR` |
| Tamaño | 128 MB (Parquet zstd) · 1,2 GB en CSV |

Cada fila es **una contribución a un producto** (un producto firmado por tres personas aparece como tres filas). El cruce con el padrón de investigadores se hace por identidad de persona dentro de la misma convocatoria.

**Hallazgo clave:** solo el **63,1%** de los autores únicos están en el padrón de reconocidos. Los otros 48.811 firman productos sin tener perfil ScienTI reconocido por MinCiencias.

---

### 3. `gold/observatorio.duckdb`

**Modelo dimensional consolidado en DuckDB.**

Base de datos analítica con esquema estrella, ~229 MB. Incluye tablas de hechos, dimensiones y vistas materializadas:

| Tabla | Tipo | Contenido |
|---|---|---|
| `fact_reconocimiento` | hecho | Una fila por aparición (77.237) |
| `fact_produccion` | hecho | Una fila por producto-autor (3.166.629) |
| `dim_investigador` | dimensión | 30.086 investigadores únicos |
| `dim_grupo` | dimensión | 7.467 grupos de investigación |
| `dim_producto` | dimensión | Tipologías de productos |
| `dim_convocatoria` | dimensión | 6 convocatorias |
| `vw_investigador_x_produccion` | vista | Cruce listo entre padrón y producción |

Listo para consultas SQL directas.

---

### 4. `referencia/tabla_maestra_ies.csv`

**Tabla maestra de Instituciones de Educación Superior.**

| Métrica | Valor |
|---|---|
| Cadenas de afiliación únicas en el padrón | 2.762 |
| IES canónicas | **211** |
| Cadenas mapeadas | 258 |
| Cobertura del padrón | **91%** |

Entrega lo que el campo `INST_FILIA` no normaliza por sí mismo: consolida `UNAL Bogotá`, `Universidad Nacional sede Bogotá`, `UN`, `UNAL`, etc. en una sola entidad canónica. Lo construyó el observatorio para complementar la información de Socrata; es el **único artefacto del paquete que no viene de la API directamente** (se deriva del campo `INST_FILIA` del mismo dataset Socrata).

Se propone como entregable a MinCiencias para futuras convocatorias.

---

### 5. `catalogo.yaml`

Diccionario de datos. Documenta cada una de las 30 variables del dataset de investigadores y las 14 del dataset de producción: nombre, tipo, descripción, dominio y procedencia.

---

## Cómo consumir el paquete

### Opción A · Python + pandas (lo más común)

```python
import pandas as pd

# Padrón de investigadores
inv = pd.read_parquet("silver/investigadores_consolidado.parquet")
print(f"Investigadores: {inv['ID_PERSONA_PR'].nunique():,} únicos")

# Padrón de producción
prod = pd.read_parquet("silver/produccion_grupos.parquet")
print(f"Productos: {len(prod):,} filas")

# Cruce básico: ¿cuántos productos firma cada categoría?
mezcla = (prod
    .merge(
        inv[["ID_PERSONA_PR", "ID_CONVOCATORIA", "NME_CLASIFICACION_PR"]],
        left_on=["ID_PERSONA_PD", "ID_CONVOCATORIA"],
        right_on=["ID_PERSONA_PR", "ID_CONVOCATORIA"],
        how="left",
    )
)
print(mezcla.groupby("NME_CLASIFICACION_PR").size().sort_values(ascending=False))

# Tabla maestra de IES (para normalizar el campo INST_FILIA)
ies = pd.read_csv("referencia/tabla_maestra_ies.csv")
```

### Opción B · DuckDB (consultas SQL sobre el modelo dimensional)

```python
import duckdb

con = duckdb.connect("gold/observatorio.duckdb", read_only=True)

# Top 10 departamentos
top10 = con.execute("""
    SELECT NME_DEPARTAMENTO_RES_PR AS departamento,
           COUNT(DISTINCT ID_PERSONA_PR) AS investigadores
    FROM fact_reconocimiento
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 10
""").fetchdf()

# Productividad promedio por categoría (Junior / Asociado / Senior)
prod_cat = con.execute("""
    SELECT NME_CLASIFICACION_PR AS categoria,
           AVG(productos) AS productos_promedio
    FROM vw_investigador_x_produccion
    GROUP BY 1
    ORDER BY 2 DESC
""").fetchdf()
```

### Opción C · DuckDB consultando directamente los Parquet (sin convertir)

```python
import duckdb

con = duckdb.connect()

# DuckDB lee Parquet directo, sin importar
res = con.execute("""
    SELECT NME_GRAN_AREA_PR AS area,
           COUNT(*) AS apariciones,
           COUNT(DISTINCT ID_PERSONA_PR) AS personas
    FROM read_parquet('silver/investigadores_consolidado.parquet')
    GROUP BY 1
    ORDER BY 3 DESC
""").fetchdf()
print(res)
```

---

## Para el estudiante recién llegado

Si esta es tu primera vez con estos datos, hay una **demo guiada en notebook** con un análisis básico (carga + top 10 departamentos) construida específicamente para ti. Pídela junto con este paquete: viene en una carpeta llamada `demo/` con su propio `README.md`, notebook, catálogo y datos.

---

## Cuatro ejes del observatorio

Los hallazgos se organizan en cuatro ejes descriptivos. El género no es un eje propio sino una **dimensión transversal** que se aplica en los tres primeros. La calidad de los datos y la cobertura de las variables de diversidad están como cautelas previas (no hallazgos).

1. **Producción.** Qué firman, cobertura del padrón, productividad por categoría, brecha de género en outputs.
2. **Territorios.** Dónde residen, dónde trabajan, flujos investigador → institución, brecha de género por departamento.
3. **Campos OCDE.** Volumen, productividad por área, composición de tipologías, brecha de género por disciplina.
4. **Longitudinal.** Transiciones de categoría (Junior ↔ Asociado ↔ Senior) en seis convocatorias.

---

## Caveats importantes

- **Ventana de observación.** Un producto firmado en 2018 puede aparecer en la convocatoria 2021. Las cifras de producción son *atribución oficial*, no producción anual.
- **Convocatoria 833 (2018).** Aparece fechada con `2019-12-06` (día de publicación de resultados). Si extraes el año de `ANO_CONVO`, vas a obtener 2019, no 2018. Es correcto — es un dato de la fuente.
- **Diversidad solo desde 2021.** Las variables `ID_VICTIMA_CONFLICTO`, `TXT_GRUPO_ETNICO`, `TXT_POBLACION_DISCA` tienen 0% de cobertura entre 2013 y 2019. Solo en 2021 se empiezan a capturar (96,8% de cobertura ese año). **No retropolar.**
- **Eméritos vitalicios.** Los investigadores Eméritos *no reaparecen* en convocatorias siguientes porque el reconocimiento queda vitalicio. No es expulsión, es diseño del sistema. Esto explica el 100% de "desaparición" de la categoría en cualquier análisis longitudinal.
- **Edad atípica.** 22 apariciones tienen `EDAD_ANOS_PR > 100` (máximo: 956). Son errores de digitación de la fuente. Decide si filtras (`df[df["EDAD_ANOS_PR"] <= 100]`) o las dejas; ambas decisiones son defensibles si las documentas.
- **Instituciones sin normalizar.** El campo `INST_FILIA` tiene 2.762 cadenas únicas para ~800 entidades reales. Usa `referencia/tabla_maestra_ies.csv` para consolidarlas y obtener rankings institucionales válidos.

---

## Proyecto completo

Si quieres ver el código que generó estos artefactos, los análisis con los cinco ejes, el dashboard interactivo en Streamlit y la presentación del observatorio:

**[`github.com/ustadistica/Observatorio_Ministerio_de_Ciencias_Grupo8`](https://github.com/ustadistica/Observatorio_Ministerio_de_Ciencias_Grupo8)**

---

## Créditos

**Ustadistica · Universidad Santo Tomás · 2026-I**
Construido como ejercicio de consultoría sobre el Sistema Nacional de Ciencia, Tecnología e Innovación de Colombia (MinCiencias).
