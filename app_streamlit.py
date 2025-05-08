
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Dashboard Hospital AMA")

# Conexión a la base de datos
conn = sqlite3.connect("hospital_ama.db")

tabs = st.tabs(["📅 Citas", "🩺 Doctores", "🧑 Pacientes", "🧾 Servicios"])

# ---------------- TAB 1: Citas ----------------
with tabs[0]:
    st.header("📅 Citas")
    mostrar_datos = st.checkbox("Mostrar datos de apoyo (Citas)")

    try:
        df_estado = pd.read_sql_query("SELECT estado, COUNT(*) as cantidad FROM citas GROUP BY estado", conn)
        df_dia = pd.read_sql_query("SELECT STRFTIME('%Y-%m-%d', fecha) as dia, COUNT(*) as cantidad FROM citas GROUP BY dia ORDER BY dia", conn)
        df_top_doc = pd.read_sql_query("SELECT d.nombre AS doctor, COUNT(*) AS cantidad FROM citas c JOIN doctores d ON c.doctor_id = d.id GROUP BY d.nombre ORDER BY cantidad DESC LIMIT 5", conn)
        df_hora = pd.read_sql_query("SELECT STRFTIME('%H', hora) as hora, COUNT(*) as cantidad FROM citas GROUP BY hora ORDER BY hora", conn)
        df_hora['hora'] = df_hora['hora'].astype(int)

        if mostrar_datos:
            st.subheader("Datos de citas por estado")
            st.dataframe(df_estado)

        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        axs[0, 0].pie(df_estado['cantidad'], labels=df_estado['estado'], autopct='%1.1f%%')
        axs[0, 0].set_title("Distribución por Estado")

        axs[0, 1].plot(df_dia['dia'], df_dia['cantidad'], marker='o')
        axs[0, 1].set_title("Citas por Día")
        axs[0, 1].tick_params(axis='x', rotation=45)

        axs[1, 0].bar(df_top_doc['doctor'], df_top_doc['cantidad'], color='skyblue')
        axs[1, 0].set_title("Top 5 Doctores")
        axs[1, 0].tick_params(axis='x', rotation=30)

        axs[1, 1].barh(df_hora['hora'], df_hora['cantidad'], color='lightgreen')
        axs[1, 1].set_title("Citas por Hora")
        axs[1, 1].set_xlabel("Cantidad")
        axs[1, 1].set_ylabel("Hora")

        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error("Error en gráficos de citas.")
        st.exception(e)

# ---------------- TAB 2: Doctores ----------------
with tabs[1]:
    st.header("🩺 Doctores")
    mostrar_datos = st.checkbox("Mostrar datos de apoyo (Doctores)")

    try:
        df_citas_doc = pd.read_sql_query("SELECT d.nombre, COUNT(c.id) AS total_citas FROM doctores d LEFT JOIN citas c ON c.doctor_id = d.id GROUP BY d.nombre", conn)
        df_especialidad = pd.read_sql_query("SELECT especialidad, COUNT(*) as cantidad FROM doctores GROUP BY especialidad", conn)

        if mostrar_datos:
            st.subheader("Datos de citas por doctor")
            st.dataframe(df_citas_doc)

        fig, axs = plt.subplots(1, 2, figsize=(14, 5))
        axs[0].bar(df_citas_doc['nombre'], df_citas_doc['total_citas'], color='orange')
        axs[0].set_title("Citas por Doctor")
        axs[0].tick_params(axis='x', rotation=45)

        axs[1].pie(df_especialidad['cantidad'], labels=df_especialidad['especialidad'], autopct='%1.1f%%')
        axs[1].set_title("Distribución por Especialidad")

        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error("Error en gráficos de doctores.")
        st.exception(e)

# ---------------- TAB 3: Pacientes ----------------
with tabs[2]:
    st.header("🧑 Pacientes")
    mostrar_datos = st.checkbox("Mostrar datos de apoyo (Pacientes)")

    try:
        df_edad = pd.read_sql_query("SELECT STRFTIME('%Y', fecha_nacimiento) as anio, COUNT(*) as cantidad FROM pacientes GROUP BY anio ORDER BY anio", conn)
        df_citas_pac = pd.read_sql_query("SELECT p.nombre, COUNT(c.id) AS total_citas FROM pacientes p LEFT JOIN citas c ON c.paciente_id = p.id GROUP BY p.nombre ORDER BY total_citas DESC LIMIT 5", conn)

        if mostrar_datos:
            st.subheader("Datos de distribución de pacientes")
            st.dataframe(df_edad)

        fig, axs = plt.subplots(1, 2, figsize=(14, 5))
        axs[0].plot(df_edad['anio'], df_edad['cantidad'], marker='o')
        axs[0].set_title("Distribución por Año de Nacimiento")
        axs[0].tick_params(axis='x', rotation=45)

        axs[1].bar(df_citas_pac['nombre'], df_citas_pac['total_citas'], color='purple')
        axs[1].set_title("Top 5 Pacientes con Más Citas")
        axs[1].tick_params(axis='x', rotation=30)

        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error("Error en gráficos de pacientes.")
        st.exception(e)

# ---------------- TAB 4: Servicios ----------------
with tabs[3]:
    st.header("🧾 Servicios")
    mostrar_datos = st.checkbox("Mostrar datos de apoyo (Servicios)")

    try:
        df_tipo = pd.read_sql_query("SELECT tipo, COUNT(*) as cantidad FROM servicios GROUP BY tipo", conn)
        df_costo = pd.read_sql_query("SELECT nombre, costo FROM servicios ORDER BY costo DESC LIMIT 10", conn)

        if mostrar_datos:
            st.subheader("Datos de tipos de servicios")
            st.dataframe(df_tipo)

        fig, axs = plt.subplots(1, 2, figsize=(14, 5))
        axs[0].pie(df_tipo['cantidad'], labels=df_tipo['tipo'], autopct='%1.1f%%')
        axs[0].set_title("Tipos de Servicios")

        axs[1].barh(df_costo['nombre'], df_costo['costo'], color='teal')
        axs[1].set_title("Top 10 Servicios por Costo")
        axs[1].set_xlabel("Costo")

        plt.tight_layout()
        st.pyplot(fig)
    except Exception as e:
        st.error("Error en gráficos de servicios.")
        st.exception(e)
