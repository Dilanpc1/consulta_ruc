import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="🔍 Consulta RUC - SRI", layout="centered")
st.image("logo.png", width=100)
st.title("🔍 Consulta de RUC - SRI")

@st.cache_data(show_spinner=False)
def cargar_datos():
    df = pd.read_excel("RESOLUCION.xlsx", usecols=["RUC", "RAZÓN SOCIAL", "CALIFICACIÓN"], dtype={"RUC": str})
    df.columns = df.columns.str.strip()
    return df

df = cargar_datos()

st.markdown(
    """
    <style>
    div.stButton > button:first-child {
        background-color: #0277bd !important;
        color: white !important;
        border-radius: 8px;
        height: 40px;
        width: 150px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.button("Nueva Consulta"):
    st.session_state["ruc_input"] = ""
    st.session_state["mostrar_password"] = False
    st.session_state["clave_edicion"] = ""
    st.rerun()



ruc_raw = st.text_input("Ingrese el número de RUC:", max_chars=13, key="ruc_input")
ruc_input = ''.join(filter(str.isdigit, ruc_raw))

if ruc_raw != ruc_input and ruc_raw != "":
    st.warning("⚠️ Solo se permiten números. Se eliminaron caracteres no válidos.")

if ruc_input and len(ruc_input) != 13:
    st.error("❌ Ingrese un RUC correcto de 13 dígitos.")

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

        sri_url = "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc"

        # Botón para abrir la página en una nueva pestaña
        if len(ruc_input) == 13 and resultado.empty:
            sri_url = "https://srienlinea.sri.gob.ec/sri-en-linea/SriRucWeb/ConsultaRuc/Consultas/consultaRuc"

            boton_completo = f"""
            <script>
            function copiarYCerrar() {{
                navigator.clipboard.writeText("{ruc_input}").then(() => {{
                    window.open("{sri_url}", "_blank");
                }});
            }}
            </script>

            <button onclick="copiarYCerrar()" style="background-color:#4CAF50;color:white;border:none;padding:10px 15px;border-radius:5px;cursor:pointer;">
                📋 Verificar en el SRI
            </button>
            """

            components.html(boton_completo, height=50)


        if st.button("➕ Ingresar nuevo RUC"):
            st.session_state["mostrar_password"] = True

if st.session_state.get("mostrar_password", False):
    contrasena = st.text_input("🔐 Clave de acceso para editar", type="password", key="clave_edicion")

    if contrasena == "almacen":
        st.success("🔓 Acceso concedido. Ingrese los datos del nuevo RUC:")

        with st.form("formulario_ruc"):
            nuevo_ruc = st.text_input("🔢 RUC:", value=ruc_input, disabled=True)
            nueva_razon = st.text_input("🏢 Razón Social")
            nueva_calificacion = st.selectbox("⭐ Calificación", options=[
                "Es Agente de Retención",
                "Es contribuyente Especial",
                "No es Agente de Retención ni Contribuyente Especial"
            ])

            guardar_nuevo = st.form_submit_button("📩 Guardar nuevo RUC")

            if guardar_nuevo:
                if nuevo_ruc and nueva_razon and nueva_calificacion:
                    if not nuevo_ruc.isdigit():
                        st.error("❌ El RUC solo debe contener números.")
                    elif len(nuevo_ruc) != 13:
                        st.error("❌ El RUC debe tener exactamente 13 dígitos.")
                    elif nuevo_ruc in df["RUC"].values:
                        st.error("❌ Este RUC ya existe en la base de datos.")
                    else:
                        nuevo_df = pd.DataFrame([{
                            "RUC": nuevo_ruc,
                            "RAZÓN SOCIAL": nueva_razon,
                            "CALIFICACIÓN": nueva_calificacion
                        }])

                        df_actualizado = pd.concat([df, nuevo_df], ignore_index=True)

                        try:
                            df_actualizado.to_excel("RESOLUCION.xlsx", index=False)
                            st.success("✅ Nuevo RUC registrado correctamente.")
                            del st.session_state["mostrar_password"]

                            cargar_datos.clear()
                            df = cargar_datos()

                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error al guardar el archivo: {e}")
                else:
                    st.warning("⚠️ Complete todos los campos correctamente.")
    elif contrasena and contrasena != "almacen":
        st.error("❌ Contraseña incorrecta.")

