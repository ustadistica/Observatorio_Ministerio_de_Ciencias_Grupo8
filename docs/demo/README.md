# Demo · Observatorio MinCiencias

Carpeta autocontenida para que estudiantes nuevos exploren los datos del **Observatorio de Investigadores Reconocidos de MinCiencias** (Ustadistica 2026-I) sin necesidad de instalar el proyecto completo.

---

## Qué hay en esta carpeta

```
demo/
├── 01_introduccion.ipynb       Notebook didáctico (5-10 minutos)
├── README.md                   Este archivo
├── catalogo.yaml               Diccionario de datos (30 variables documentadas)
└── datos/
    └── investigadores_consolidado.csv     (se descarga aparte, ver abajo)
```

Cuando recibas la carpeta, esos cuatro elementos deberían estar todos juntos. Si te faltan archivos, pídelos a quien te entregó el demo.

---

## Cómo usarlo

### 1. Requisitos

Python 3.10 o superior, y tres librerías:

```bash
pip install pandas matplotlib pyyaml jupyter
```

### 2. Si te falta el archivo de datos

`datos/investigadores_consolidado.csv` se descarga desde la **API pública de Socrata** (datos.gov.co). Identificador del dataset: `bqtm-4y2h`. URL directa:

> https://www.datos.gov.co/resource/bqtm-4y2h.csv?$limit=100000

Guárdalo en una subcarpeta `datos/` al lado del notebook. Pesa ~30 MB.

### 3. Abre el notebook

```bash
jupyter notebook 01_introduccion.ipynb
```

O directamente en VS Code: abre el `.ipynb` y selecciona un kernel Python.

### 4. Corre todas las celdas (`Cell → Run All`)

El notebook está pensado para ejecutarse de principio a fin. Cada celda tiene una explicación corta arriba.

---

## Qué vas a ver

El notebook te guía por tres pasos:

1. **Cargar el dataset** desde la subcarpeta `datos/`. Verás que tiene 77.237 filas (apariciones) y 30.086 investigadores únicos.

2. **Conocer las columnas clave** del padrón: identificador de persona, convocatoria, categoría (Junior/Asociado/Senior/Emérito), área OCDE, género, departamento de residencia, etc. El catálogo completo está en `catalogo.yaml`.

3. **Tu primer gráfico**: top 10 departamentos por cantidad de investigadores reconocidos. Verás cómo Bogotá y Antioquia concentran cerca del 48% del padrón nacional.

---

## Sobre el dataset

| Convocatoria | Año | Apariciones |
|---|---|---|
| 640 | 2013 | 8.016 |
| 693 | 2014 | 8.280 |
| 737 | 2015 | 10.050 |
| 781 | 2017 | 13.001 |
| 833 | 2018 | 16.796 |
| 894 | 2021 | 21.094 |
| **Total** | **2013–2021** | **77.237 / 30.086 únicos** |

**Fuente única:** API de Socrata (`datos.gov.co`). Identificador `bqtm-4y2h`. Todos los análisis del observatorio se construyen sobre este mismo CSV.

Cada fila es una *aparición* de un investigador en una convocatoria. Un investigador reconocido en cuatro convocatorias aparece como cuatro filas distintas (que se pueden unir por `ID_PERSONA_PR`).

---

## Ideas para tu propio análisis

El notebook deja varias preguntas abiertas para que tomes el dataset y vayas más lejos:

- ¿Cómo cambió el porcentaje de mujeres en Ingeniería entre 2013 y 2021?
- ¿Cuál es la categoría (Junior / Asociado / Senior) con mayor crecimiento?
- ¿Qué departamentos tienen menor edad promedio de sus investigadores?
- ¿Hay correlación entre tamaño del departamento y área OCDE dominante?
- ¿Cuántos investigadores fueron clasificados por primera vez en 2021?

El dataset tiene 30 columnas. El catálogo (`catalogo.yaml`) documenta cada una.

---

## Si quieres ver el proyecto completo

El observatorio completo (4 ejes de análisis con género como lente transversal, cruce con 3,16 M productos académicos, tabla maestra de 211 IES, dashboard interactivo en Streamlit, sankeys de transición de categoría, análisis territorial institucional, modelo dimensional en DuckDB) está en:

**[`github.com/ustadistica/Observatorio_Ministerio_de_Ciencias_Grupo8`](https://github.com/ustadistica/Observatorio_Ministerio_de_Ciencias_Grupo8)**

Ahí encontrarás los scripts por sprint, los hallazgos críticos, la presentación HTML y el manual técnico.
