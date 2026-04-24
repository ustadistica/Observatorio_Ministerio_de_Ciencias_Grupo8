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
|   |-- ingesta/                 # Scripts de extraccion (sodapy)
|   |-- transformacion/          # Limpieza, normalizacion, joins
|   |-- modelo/                  # Modelo estrella / modelado estadistico
|   +-- visualizacion/           # Funciones de graficos reutilizables
|-- notebooks/
|   |-- 01_eda.ipynb
|   |-- 02_analisis.ipynb
|   +-- 03_modelado.ipynb
|-- app/
|   +-- streamlit_app.py         # Dashboard interactivo
|-- datos/
|   |-- raw/                     # Datos crudos (gitignored si pesados)
|   |-- processed/               # Datos limpios
|   +-- catalogo.yaml            # Metadatos de cada dataset
|-- docs/                        # Informes y documentacion
|-- tests/                       # Tests automatizados
|-- artifacts/                   # Artefactos generados (metricas, reportes)
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

# Ejecutar pipeline de ingesta
poetry run python -m src.ingesta.main

# Ejecutar pipeline de transformacion
poetry run python -m src.transformacion.main

# Lanzar dashboard
poetry run streamlit run app/streamlit_app.py
```

## Cronograma -- CRISP-DM

### Sprint 1 (Sem 1-2)

Actualización de datos (verificar convocatoria 2023), automatizar ingesta con sodapy, refactorizar notebooks.

### Sprint 2 (Sem 3-4)

Análisis longitudinal: tracking de investigadores entre convocatorias, matrices de transición de categoría, concentración territorial (HHI).

### Sprint 3 (Sem 5-7)

Network analysis de co-filiación institucional (NetworkX + Pyvis). Dashboard Streamlit con mapa, distribuciones y grafo interactivo.

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
