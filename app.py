import pandas as pd
import re
import streamlit as st


st.set_page_config(
    page_title="FOPEA APP - BOOTCAMP DATA VISUALIZATION 2025",
    layout="wide"
)

# ======================
# CARGA DE DATOS 
# ======================
@st.cache_data
def load_data():
    df = pd.read_csv("data/todos_los_tuits_filtrado.zip")

    # Asegurar tipo fecha
    df["fecha_milei"] = pd.to_datetime(df["fecha_milei"], errors="coerce")

    return df


df = load_data()

st.title("Base de tuits y retuits de Milei (11/12/2023–09/12/2025)")

# ======================
# SIDEBAR – FILTROS
# ======================
st.sidebar.header("🔎 Filtros")

emisor = st.sidebar.multiselect(
    "Emisor",
    options=sorted(df["emisor"].dropna().unique()),
    default=sorted(df["emisor"].dropna().unique())
)

tipo_mensaje = st.sidebar.multiselect(
    "Tipo de mensaje",
    options=sorted(df["tipo_mensaje"].unique()),
    default=list(df["tipo_mensaje"].unique())
)

fecha_min, fecha_max = st.sidebar.date_input(
    "Rango de fechas",
    value=(df["fecha_milei"].min(), df["fecha_milei"].max())
)

fecha_min = pd.to_datetime(fecha_min)
fecha_max = pd.to_datetime(fecha_max)

modo_busqueda = st.sidebar.radio(
    "Modo de búsqueda",
    ["Exacta (palabra completa)", "Por raíz / contiene"],
    help="Exacta busca la palabra completa. Raíz captura variaciones y deformaciones."
)

texto_busqueda = st.sidebar.text_input(
    "Buscar palabras (OR con |)",
    help="Ej: pelotudo|perio|burro"
)

# ======================
# FILTROS BASE
# ======================
df_filt = df[
    (df["emisor"].isin(emisor)) &
    (df["tipo_mensaje"].isin(tipo_mensaje)) &
    (df["fecha_milei"] >= fecha_min) &
    (df["fecha_milei"] <= fecha_max)
].copy()

df_filt = df_filt.dropna(subset=["fecha_milei"])

# Crear mes para gráficos
df_filt["mes"] = df_filt["fecha_milei"].dt.to_period("M").astype(str)

# ======================
# FILTRO POR TEXTO 
# ======================
if texto_busqueda.strip():
    texto = texto_busqueda.lower()

    if modo_busqueda == "Exacta (palabra completa)":
        patron = rf"\b({texto})\b"
    else:
        patron = rf"({texto})"

    df_filt = df_filt[
        df_filt["texto"].str.contains(
            patron, regex=True, na=False
        )
    ]

# ======================
# GRAFICO 1 – TUITS POR MES
# ======================
st.subheader("📝 Cantidad de tuits por mes")

tuits_mes = (
    df_filt[df_filt["tipo_mensaje"] == "T"]
    .groupby("mes")
    .size()
)

st.bar_chart(tuits_mes)

# ======================
# GRAFICO 2 – RETUITS POR MES
# ======================
st.subheader("🔁 Cantidad de retuits por mes")

retuits_mes = (
    df_filt[df_filt["tipo_mensaje"] == "R"]
    .groupby("mes")
    .size()
)

st.bar_chart(retuits_mes)

# ======================
# TABLA FINAL 
# ======================
st.subheader("🧾 Posteos")

st.dataframe(
    df_filt[
        ["emisor", "fecha_milei", "texto", "tipo_mensaje"]
    ],
    use_container_width=True,
    height=500
) 
   
