# Observatorio MinCiencias — Investigadores Reconocidos

> **Ustadistica** -- Consultoria e Investigacion . Universidad Santo Tomas . 2026-I

Observatorio de investigadores reconocidos por MinCiencias. Análisis longitudinal de convocatorias 2017, 2019, 2021 (y 2023 si disponible).

## Fuentes de Datos

MinCiencias / datos.gov.co — Investigadores reconocidos por convocatoria. El dataset consolidado (`datos/tarea_join/investigadores_consolidado.xlsx`) integra **6 convocatorias históricas**:

| Convocatoria | Año | Registros |
|---|---|---|
| 640 | 2013 | 8.016 |
| 693 | 2014 | 8.280 |
| 737 | 2015 | 10.050 |
| 781 | 2017 | 13.001 |
| 833 | 2018 | 16.796 |
| 894 | 2021 | 21.094 |
| **Total** | **2013–2021** | **77.237 registros / 30.086 investigadores únicos** |

Consultar [`datos/catalogo.yaml`](datos/catalogo.yaml) para los identificadores Socrata y metadatos de cada dataset.

## Preguntas de Investigacion

- ¿Cuál es la tasa de retención de investigadores reconocidos entre convocatorias sucesivas?
- ¿Qué instituciones concentran la mayor producción de investigadores Senior y Emérito?
- ¿Existe segregación territorial en el reconocimiento de investigadores por fuera de las tres principales ciudades?
- ¿La representación de mujeres investigadoras ha mejorado significativamente entre 2017 y 2021 en áreas STEM?

## Estructura del Proyecto

```
Observatorio_Ministerio_de_Ciencias_Grupo7/
|-- README.md                    # Este archivo
|-- CONTRIBUTING.md              # Guia de contribucion y Git Flow
|-- pyproject.toml               # Poetry (dependencias + metadata)
|-- Dockerfile                   # Contenedor reproducible
|-- .github/
|   +-- workflows/
|       +-- etl_update.yml       # GitHub Actions para ingesta periodica
|-- src/
|   |-- ingesta/                 # Paquete de carga (cargar_consolidado + sodapy)
|   |-- analisis/                # Logica reutilizable: longitudinal, territorial, genero
|   |-- modelo/                  # Modelo estrella DuckDB (dimensional.py)
|   +-- Transformacion.py        # Pipeline limpieza + normalizacion
|-- scripts/                     # Orquestacion por sprint (genera figuras + CSVs)
|   |-- sprint2_panel_longitudinal.py
|   |-- sprint2_matrices_transicion.py
|   |-- sprint2_territorial.py
|   |-- sprint2_genero_ocde.py
|   +-- sprint2_duckdb.py
|-- notebooks/
|   +-- 01_eda.ipynb             # Unico notebook activo (EDA exploratorio)
|-- streamlit_app.py             # Dashboard interactivo (Sprint 3)
|-- datos/
|   |-- raw/                     # Datos crudos (gitignored)
|   |-- processed/               # observatorio.duckdb (gitignored)
|   +-- catalogo.yaml            # Metadatos de cada dataset
|-- artifacts/                   # Figuras PNG generadas por sprint
|-- evidencias/                  # CSVs exportados por los scripts
|-- docs/                        # Informes y documentacion
|-- tests/                       # Tests automatizados
+-- models/                      # Modelos serializados
```

## Instalacion

```bash
# Clonar el repositorio
git clone https://github.com/ustadistica/Observatorio_Ministerio_de_Ciencias_Grupo7.git
cd Observatorio_Ministerio_de_Ciencias_Grupo7

# Instalar dependencias con Poetry
pip install poetry
poetry install

# Descargar dataset consolidado desde Socrata
poetry run python -m src.ingesta.minciencias

# Ejecutar scripts de Sprint 2 (genera figuras en artifacts/ y CSVs en evidencias/)
poetry run python scripts/sprint2_panel_longitudinal.py
poetry run python scripts/sprint2_matrices_transicion.py
poetry run python scripts/sprint2_territorial.py
poetry run python scripts/sprint2_genero_ocde.py
poetry run python scripts/sprint2_duckdb.py

# Lanzar dashboard
poetry run streamlit run streamlit_app.py
```

## Cronograma -- CRISP-DM

### Sprint 1 (Sem 1-2)

Actualización de datos (verificar convocatoria 2023), automatizar ingesta con sodapy, refactorizar notebooks.

### Sprint 2 (Sem 3-4) — COMPLETADO ✅

| Issue | Título | Estado |
|---|---|---|
| #11 | Panel longitudinal de investigadores | ✅ Completado |
| #12 | Matrices de transición de categoría | ✅ Completado |
| #13 | Análisis de concentración territorial (HHI) | ✅ Completado |
| #14 | Modelo dimensional en DuckDB | ✅ Completado |
| #22 | Análisis de género por área OCDE | ✅ Completado |

### Sprint 3 (Sem 5-7)

Network analysis de co-filiación institucional (NetworkX + Pyvis). Dashboard Streamlit con mapa, distribuciones y grafo interactivo.

| Issue | Título | Estado |
|---|---|---|
| #15 | Network analysis de co-filiación | ✅ Completado |
| #16 | Visualización de grafo interactivo | ✅ Completado |
| #17 | Dashboard: mapa de investigadores | ⏳ Pendiente |
| #18 | Dashboard: tabla de instituciones | ⏳ Pendiente |
| #19 | Deploy dashboard en Streamlit Cloud | ⏳ Pendiente |

### Sprint 4 (Sem 8)

Análisis de variables de conflicto, etnia y discapacidad. Comparación con proporciones poblacionales DANE 2018.


## Equipo

| Rol | GitHub |
|-----|--------|
| Pipeline + deploy | [@Victor-Diaz-Usta](https://github.com/Victor-Diaz-Usta) |

**Director / Revisor PRs:** [@Izainea](https://github.com/Izainea)

## Metodologia

- **Framework analitico:** CRISP-DM
- **Gestion de proyecto:** Sprints de 2 semanas con Kanban (GitHub Projects)
- **Control de versiones:** Git Flow (`main` / `develop` / `feature/*`)
- **Estandar operativo:** Big 4 (governance formal, auditoria cruzada, mejora continua)

Consultar [CONTRIBUTING.md](CONTRIBUTING.md) para la guia completa de contribucion.

## Stack Tecnologico

| Capa | Herramientas |
|------|-------------|
| Ingesta | sodapy, pandas, requests |
| Almacen | DuckDB (modelo estrella) |
| Analisis | pandas, scikit-learn, statsmodels |
| Visualizacion | matplotlib, seaborn, plotly, folium |
| Dashboard | Streamlit |
| Reproducibilidad | Poetry, Docker, GitHub Actions |
| Testing | pytest, pandera |

---

> *"Si no esta en el README, el proyecto no existe."* -- Ustadistica 2026-I
