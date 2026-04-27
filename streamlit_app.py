# -*- coding: utf-8 -*-
"""
streamlit_app.py

Tablero de control interactivo para el Observatorio de Ciencia, Tecnología e
Innovación — Investigadores Reconocidos Minciencias (Grupo 7).

Ejecución:
    streamlit run streamlit_app.py
"""

import pathlib
import sys

import pandas as pd
import streamlit as st
import plotly.express as px

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from ingesta import cargar_consolidado  # noqa: E402
from Transformacion import transformar  # noqa: E402

# ---------------------------------------------------------------------------
# Configuración de la página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Observatorio Minciencias — Grupo 7",
    page_icon="🔬",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Carga y transformación de datos (cacheado)
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner="Cargando datos…")
def cargar_datos() -> pd.DataFrame:
    df = cargar_consolidado()
    df = transformar(df)
    return df


# ---------------------------------------------------------------------------
# Sidebar — filtros
# ---------------------------------------------------------------------------

def sidebar_filtros(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("🔎 Filtros")

    # Año de convocatoria
    anios = sorted(df["ANO_CONVO_INT"].dropna().unique().tolist())
    anios_sel = st.sidebar.multiselect(
        "Año de convocatoria",
        options=anios,
        default=anios,
    )

    # Género
    generos = sorted(df["NME_GENERO_PR"].dropna().unique().tolist())
    generos_sel = st.sidebar.multiselect(
        "Género",
        options=generos,
        default=generos,
    )

    # Gran área de conocimiento
    areas = sorted(df["NME_GRAN_AREA_PR"].dropna().unique().tolist())
    areas_sel = st.sidebar.multiselect(
        "Gran área de conocimiento",
        options=areas,
        default=areas,
    )

    # Aplicar filtros
    mascara = (
        df["ANO_CONVO_INT"].isin(anios_sel)
        & df["NME_GENERO_PR"].isin(generos_sel)
        & df["NME_GRAN_AREA_PR"].isin(areas_sel)
    )
    return df[mascara]


# ---------------------------------------------------------------------------
# Secciones del tablero
# ---------------------------------------------------------------------------

def seccion_resumen(df: pd.DataFrame) -> None:
    st.header("📊 Resumen general")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de registros", f"{len(df):,}")
    col2.metric(
        "Investigadores únicos",
        f"{df['ID_PERSONA_PR'].nunique():,}" if "ID_PERSONA_PR" in df.columns else "N/A",
    )
    col3.metric(
        "Convocatorias",
        f"{df['ANO_CONVO_INT'].nunique():,}" if "ANO_CONVO_INT" in df.columns else "N/A",
    )


def seccion_evolucion(df: pd.DataFrame) -> None:
    st.header("📈 Evolución por convocatoria")
    if "ANO_CONVO_INT" not in df.columns:
        st.warning("No se pudo determinar el año de convocatoria.")
        return
    conteo = (
        df.groupby("ANO_CONVO_INT")
        .size()
        .reset_index(name="Investigadores")
        .rename(columns={"ANO_CONVO_INT": "Año"})
    )
    fig = px.bar(
        conteo,
        x="Año",
        y="Investigadores",
        text_auto=True,
        title="Número de investigadores reconocidos por convocatoria",
        color="Investigadores",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig, use_container_width=True)


def seccion_genero(df: pd.DataFrame) -> None:
    st.header("👥 Distribución por género")
    if "NME_GENERO_PR" not in df.columns:
        st.warning("Columna de género no disponible.")
        return
    conteo = df["NME_GENERO_PR"].value_counts().reset_index()
    conteo.columns = ["Género", "Cantidad"]
    fig = px.pie(
        conteo,
        names="Género",
        values="Cantidad",
        title="Distribución por género",
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    st.plotly_chart(fig, use_container_width=True)


def seccion_areas(df: pd.DataFrame) -> None:
    st.header("🔬 Distribución por gran área de conocimiento")
    if "NME_GRAN_AREA_PR" not in df.columns:
        st.warning("Columna de área no disponible.")
        return
    conteo = (
        df["NME_GRAN_AREA_PR"]
        .value_counts()
        .reset_index()
    )
    conteo.columns = ["Gran Área", "Cantidad"]
    fig = px.bar(
        conteo,
        x="Cantidad",
        y="Gran Área",
        orientation="h",
        title="Investigadores por gran área OCDE",
        color="Cantidad",
        color_continuous_scale="Teal",
    )
    st.plotly_chart(fig, use_container_width=True)


_COORDENADAS_DEPTO = {
    "AMAZONAS": (-1.44, -71.57),
    "ANTIOQUIA": (7.19, -75.34),
    "ARAUCA": (6.54, -71.00),
    "ARCHIPIÉLAGO DE SAN ANDRÉS, PROVIDENCIA Y SANTA CATALINA": (12.53, -81.72),
    "ATLÁNTICO": (10.69, -74.87),
    "BOGOTÁ, D. C.": (4.71, -74.07),
    "BOLÍVAR": (8.67, -74.03),
    "BOYACÁ": (5.45, -73.36),
    "CALDAS": (5.30, -75.27),
    "CAQUETÁ": (1.61, -75.61),
    "CASANARE": (5.75, -71.57),
    "CAUCA": (2.53, -76.62),
    "CESAR": (9.33, -73.50),
    "CHOCÓ": (5.69, -76.66),
    "CÓRDOBA": (8.39, -75.51),
    "CUNDINAMARCA": (5.03, -74.01),
    "GUAINÍA": (2.58, -68.53),
    "GUAVIARE": (2.57, -72.67),
    "HUILA": (2.53, -75.52),
    "LA GUAJIRA": (11.35, -72.48),
    "MAGDALENA": (10.41, -74.41),
    "META": (3.99, -73.56),
    "NARIÑO": (1.28, -77.35),
    "NORTE DE SANTANDER": (7.94, -72.50),
    "PUTUMAYO": (0.44, -76.64),
    "QUINDÍO": (4.46, -75.67),
    "RISARALDA": (5.31, -75.98),
    "SANTANDER": (6.64, -73.65),
    "SUCRE": (9.30, -75.40),
    "TOLIMA": (4.09, -75.15),
    "VALLE DEL CAUCA": (3.80, -76.51),
    "VAUPÉS": (0.86, -70.81),
    "VICHADA": (4.42, -69.59),
}


def seccion_mapa(df: pd.DataFrame) -> None:
    st.header("Mapa de investigadores por departamento")
    col = "NME_DEPARTAMENTO_RES_PR"
    if col not in df.columns:
        st.warning("Columna de departamento no disponible.")
        return

    conteo = df[col].value_counts().reset_index()
    conteo.columns = ["Departamento", "Investigadores"]
    conteo = conteo[conteo["Departamento"].isin(_COORDENADAS_DEPTO)]
    conteo["lat"] = conteo["Departamento"].map(lambda d: _COORDENADAS_DEPTO[d][0])
    conteo["lon"] = conteo["Departamento"].map(lambda d: _COORDENADAS_DEPTO[d][1])

    fig = px.scatter_mapbox(
        conteo,
        lat="lat",
        lon="lon",
        size="Investigadores",
        color="Investigadores",
        hover_name="Departamento",
        hover_data={"Investigadores": True, "lat": False, "lon": False},
        color_continuous_scale="YlOrRd",
        size_max=60,
        zoom=4.5,
        center={"lat": 4.5, "lon": -74.0},
        mapbox_style="open-street-map",
        title="Investigadores reconocidos por departamento de residencia",
    )
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0}, height=520)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver tabla por departamento"):
        st.dataframe(
            conteo[["Departamento", "Investigadores"]]
            .sort_values("Investigadores", ascending=False)
            .reset_index(drop=True),
            use_container_width=True,
        )


def seccion_departamentos(df: pd.DataFrame) -> None:
    col = "NME_DEPARTAMENTO_RES_PR"
    if col not in df.columns:
        return
    top20 = df[col].value_counts().head(20).reset_index()
    top20.columns = ["Departamento", "Cantidad"]
    fig = px.bar(
        top20,
        x="Cantidad",
        y="Departamento",
        orientation="h",
        title="Top 20 departamentos de residencia",
        color="Cantidad",
        color_continuous_scale="Oranges",
    )
    st.plotly_chart(fig, use_container_width=True)


def seccion_nivel_formacion(df: pd.DataFrame) -> None:
    st.header("🎓 Nivel de formación")
    col = "NME_NIV_FORM_PR"
    if col not in df.columns:
        st.warning("Columna de nivel de formación no disponible.")
        return
    conteo = df[col].value_counts().reset_index()
    conteo.columns = ["Nivel", "Cantidad"]
    fig = px.bar(
        conteo,
        x="Nivel",
        y="Cantidad",
        text_auto=True,
        title="Distribución por nivel de formación",
        color="Cantidad",
        color_continuous_scale="Purples",
    )
    fig.update_xaxes(tickangle=30)
    st.plotly_chart(fig, use_container_width=True)


_CAT_CORTA = {
    "INVESTIGADOR JUNIOR": "Junior",
    "INVESTIGADOR ASOCIADO": "Asociado",
    "INVESTIGADOR SÉNIOR": "Sénior",
    "INVESTIGADOR EMÉRITO": "Emérito",
}


@st.cache_data(show_spinner=False)
def _tabla_instituciones(df_hash: str, df: pd.DataFrame) -> pd.DataFrame:
    """Desagrega inst_filia y construye tabla institución × categoría."""
    cols = ["INST_FILIA", "NME_CLASIFICACION_PR"]
    sub = df[cols].dropna(subset=["INST_FILIA"])
    rows = []
    for _, row in sub.iterrows():
        cat = _CAT_CORTA.get(str(row["NME_CLASIFICACION_PR"]).upper(), str(row["NME_CLASIFICACION_PR"]))
        for inst in str(row["INST_FILIA"]).split("|"):
            inst = inst.strip()
            if inst:
                rows.append({"Institución": inst, "Categoría": cat})
    inst_df = pd.DataFrame(rows)
    pivot = (
        inst_df.groupby(["Institución", "Categoría"])
        .size()
        .unstack(fill_value=0)
    )
    for cat in ["Junior", "Asociado", "Sénior", "Emérito"]:
        if cat not in pivot.columns:
            pivot[cat] = 0
    pivot = pivot[["Junior", "Asociado", "Sénior", "Emérito"]]
    pivot["Total"] = pivot.sum(axis=1)
    return pivot.sort_values("Total", ascending=False).reset_index()


def seccion_instituciones(df: pd.DataFrame) -> None:
    st.header("Instituciones de afiliación")

    tabla = _tabla_instituciones(str(len(df)), df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Instituciones únicas", f"{len(tabla):,}")
    col2.metric("Institución líder", tabla.iloc[0]["Institución"][:40])
    col3.metric("Investigadores (líder)", f"{int(tabla.iloc[0]['Total']):,}")

    top_n = st.slider("Mostrar top N instituciones", min_value=5, max_value=50, value=20, step=5)
    top = tabla.head(top_n)

    fig = px.bar(
        top,
        x="Total",
        y="Institución",
        orientation="h",
        color="Total",
        color_continuous_scale="Blues",
        title=f"Top {top_n} instituciones por total de reconocimientos",
        hover_data={"Junior": True, "Asociado": True, "Sénior": True, "Emérito": True},
    )
    fig.update_layout(yaxis={"autorange": "reversed"}, height=500)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Tabla completa por institución y categoría"):
        buscar = st.text_input("Buscar institución", key="buscar_inst")
        vista = tabla if not buscar else tabla[tabla["Institución"].str.contains(buscar, case=False, na=False)]
        st.dataframe(vista, use_container_width=True, height=400)


def seccion_datos_crudos(df: pd.DataFrame) -> None:
    with st.expander("🗃️ Ver datos (primeras 500 filas)"):
        st.dataframe(df.head(500))


# ---------------------------------------------------------------------------
# App principal
# ---------------------------------------------------------------------------

def main() -> None:
    st.title("🔬 Observatorio de Ciencia, Tecnología e Innovación")
    st.caption(
        "Investigadores Reconocidos por Convocatoria — Minciencias — Grupo 7"
    )

    try:
        df_raw = cargar_datos()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    df = sidebar_filtros(df_raw)

    if df.empty:
        st.warning("No hay registros para los filtros seleccionados.")
        return

    seccion_resumen(df)

    col_izq, col_der = st.columns(2)
    with col_izq:
        seccion_evolucion(df)
    with col_der:
        seccion_genero(df)

    seccion_areas(df)
    seccion_mapa(df)
    seccion_departamentos(df)
    seccion_nivel_formacion(df)
    seccion_instituciones(df)
    seccion_datos_crudos(df)


if __name__ == "__main__":
    main()
