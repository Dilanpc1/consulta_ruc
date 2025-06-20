import streamlit as st
import pandas as pd

st.set_page_config(page_title="🔍 Consulta RUC - SRI", layout="centered")
st.image("logo.png", width=100)
st.title("🔍 Consulta de RUC - SRI")

@st.cache_data(show_spinner=False)
def cargar_datos():
    df = pd.read_excel("RESOLUCION.xlsx", usecols=["RUC", "RAZÓN SOCIAL", "CALIFICACIÓN"], dtype={"RUC": str})
    df.columns = df.columns.str.strip()
    return df

with st.spinner("Cargando base de datos..."):
    df = cargar_datos()

# Entrada de RUC
ruc_raw = st.text_input("Ingrese el número de RUC:", max_chars=13)

# Filtrar solo números
ruc_input = ''.join(filter(str.isdigit, ruc_raw))

# Aviso si hay caracteres no válidos
if ruc_raw != ruc_input:
    st.warning("⚠️ Solo se permiten números. Se eliminaron caracteres no válidos.")

# Validación de longitud
if ruc_input and len(ruc_input) != 13:
    st.error("❌ Ingrese un RUC correcto de 13 dígitos.")

# Búsqueda solo si es exactamente 13 dígitos
if len(ruc_input) == 13:
    resultado = df[df["RUC"] == ruc_input]

    if not resultado.empty:
        st.success("✅ RUC encontrado")
        st.write("**Razón Social:**", resultado.iloc[0]["RAZÓN SOCIAL"])
        st.write("**Calificación(es):**")
        st.dataframe(resultado[["CALIFICACIÓN"]].drop_duplicates().reset_index(drop=True))
    else:
        st.error("❌ RUC no encontrado en la base de datos")
        st.warning("⚠️ Revisar SRI.")
