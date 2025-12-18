import pandas as pd
import re
import streamlit as st
import unicodedata

st.set_page_config(
    page_title="FOPEA APP - DJV 2025",
    layout="wide"
)

# ======================
# CARGA DE DATOS 
# ======================
@st.cache_data
def load_data():
    df = pd.read_csv("data/todos_los_tuits_filtrado.zip")

    # # Asegurar tipo fecha
    df["fecha_milei"] = pd.to_datetime(df["fecha_milei"], errors="coerce", utc=True)

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
    value=(df["fecha_milei"].min().date(), df["fecha_milei"].max().date())
)
fecha_min = pd.Timestamp(fecha_min).tz_localize("UTC")
fecha_max = pd.Timestamp(fecha_max).tz_localize("UTC")

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

import unicodedata
import re

# ======================
# FILTRO POR TEXTO 
# ======================
def quitar_urls(texto):
    return re.sub(r'https?://\S+', '', texto)

def normalizar(texto):
    texto = quitar_urls(texto)  # eliminar enlaces
    texto = str(texto).lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    return texto

if texto_busqueda.strip():
    texto_norm = normalizar(texto_busqueda)

    # Normalizar columna de texto (sin URLs)
    df_filt["texto_norm"] = df_filt["texto"].apply(normalizar)

   
    if modo_busqueda == "Exacta (palabra completa)":
        palabras = texto_norm.split("|")
        patron = r"\b(" + "|".join(re.escape(p) for p in palabras) + r")\b"
    else:  # Por raíz / contiene
        patron = rf"{re.escape(texto_norm)}"

    df_filt = df_filt[df_filt["texto_norm"].str.contains(patron, regex=True, na=False)]



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
import io

# ======================
# BOTÓN PARA EXPORTAR CSV
# ======================
import io

st.subheader("💾 Exportar Archivo")

# Crear copia del DataFrame sin la columna 'texto_norm'
df_export = df_filt.drop(columns=["texto_norm"], errors="ignore")

excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df_export.to_excel(writer, index=False, sheet_name="Tuits_filtrados")
excel_buffer.seek(0)

st.download_button(
    label="Descargar Excel",
    data=excel_buffer,
    file_name="tuits_filtrados.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)



