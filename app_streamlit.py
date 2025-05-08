
import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(layout="wide")
st.title("Dashboard Hospital AMA")

# Conexión a la base de datos
conn = sqlite3.connect("hospital_ama.db")

# Crear pestañas
tabs = st.tabs(["📅 Citas", "🩺 Doctores", "🧑 Pacientes", "🧾 Servicios"])

# ---------------- TAB 1: Citas ----------------
with tabs[0]:
    st.header("📅 Citas")
    try:
        df_citas = pd.read_sql_query("SELECT * FROM citas", conn)
        st.dataframe(df_citas)
    except Exception as e:
        st.error("Error cargando la tabla 'citas'. Verifica si existe en la base de datos.")

# ---------------- TAB 2: Doctores ----------------
with tabs[1]:
    st.header("🩺 Doctores")
    try:
        df_doctores = pd.read_sql_query("SELECT * FROM doctores", conn)
        st.dataframe(df_doctores)
    except Exception as e:
        st.error("Error cargando la tabla 'doctores'. Verifica si existe en la base de datos.")

# ---------------- TAB 3: Pacientes ----------------
with tabs[2]:
    st.header("🧑 Pacientes")
    try:
        df_pacientes = pd.read_sql_query("SELECT * FROM pacientes", conn)
        st.dataframe(df_pacientes)
    except Exception as e:
        st.error("Error cargando la tabla 'pacientes'. Verifica si existe en la base de datos.")

# ---------------- TAB 4: Servicios ----------------
with tabs[3]:
    st.header("🧾 Servicios")
    try:
        df_servicios = pd.read_sql_query("SELECT * FROM servicios", conn)
        st.dataframe(df_servicios)
    except Exception as e:
        st.error("Error cargando la tabla 'servicios'. Verifica si existe en la base de datos.")
