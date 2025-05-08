
import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Dashboard Hospital AMA")

# Conexión a la base de datos
conn = sqlite3.connect("hospital_ama.db")

# --- Tabs principales ---
tabs = st.tabs(["📅 Citas", "🩺 Doctores", "🧑 Pacientes", "🧾 Servicios"])

# ---------------- TAB 1: Citas ----------------
with tabs[0]:
    st.header("Análisis de Citas")

    # Filtros interactivos
    estados = pd.read_sql_query("SELECT DISTINCT estado FROM citas", conn)['estado'].tolist()
    doctores = pd.read_sql_query("SELECT nombre FROM doctores", conn)['nombre'].tolist()

    col1, col2, col3 = st.columns(3)
    estado_sel = col1.selectbox("Filtrar por estado", ["Todos"] + estados)
    doctor_sel = col2.selectbox("Filtrar por doctor", ["Todos"] + doctores)
    fecha_sel = col3.date_input("Filtrar por fecha")

    # Construcción dinámica de consulta con filtros
    condiciones = []
    if estado_sel != "Todos":
        condiciones.append(f"c.estado = '{estado_sel}'")
    if doctor_sel != "Todos":
        condiciones.append(f"d.nombre = '{doctor_sel}'")
    if fecha_sel:
        condiciones.append(f"DATE(c.fecha) = '{fecha_sel}'")

    filtro_sql = " AND ".join(condiciones)
    if filtro_sql:
        filtro_sql = "WHERE " + filtro_sql

    # 1. Citas por estado
    query_estado = f'''
    SELECT c.estado, COUNT(*) as cantidad
    FROM citas c
    JOIN doctores d ON c.doctor_id = d.id
    {filtro_sql}
    GROUP BY c.estado
    '''
    df_estado = pd.read_sql_query(query_estado, conn)

    # 2. Citas por día
    query_dia = f'''
    SELECT DATE(c.fecha) as dia, COUNT(*) as cantidad
    FROM citas c
    JOIN doctores d ON c.doctor_id = d.id
    {filtro_sql}
    GROUP BY dia ORDER BY dia
    '''
    df_dia = pd.read_sql_query(query_dia, conn)

    # 3. Top 5 doctores
    query_top_doctores = f'''
    SELECT d.nombre as doctor, COUNT(*) as cantidad
    FROM citas c
    JOIN doctores d ON c.doctor_id = d.id
    {filtro_sql}
    GROUP BY d.nombre
    ORDER BY cantidad DESC
    LIMIT 5
    '''
    df_top_doctores = pd.read_sql_query(query_top_doctores, conn)

    # 4. Citas por hora
    query_hora = f'''
    SELECT STRFTIME('%H', c.hora) as hora, COUNT(*) as cantidad
    FROM citas c
    JOIN doctores d ON c.doctor_id = d.id
    {filtro_sql}
    GROUP BY hora ORDER BY hora
    '''
    df_hora = pd.read_sql_query(query_hora, conn)
    df_hora['hora'] = df_hora['hora'].astype(int)

    # --- Subplots ---
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))

    if not df_estado.empty:
        axs[0, 0].pie(df_estado['cantidad'], labels=df_estado['estado'], autopct='%1.1f%%', startangle=90)
        axs[0, 0].set_title("Distribución por Estado")
    else:
        axs[0, 0].text(0.5, 0.5, 'Sin datos', ha='center', va='center')
        axs[0, 0].axis('off')

    if not df_dia.empty:
        axs[0, 1].plot(df_dia['dia'], df_dia['cantidad'], marker='o')
        axs[0, 1].set_title("Citas por Día")
        axs[0, 1].tick_params(axis='x', rotation=45)
    else:
        axs[0, 1].text(0.5, 0.5, 'Sin datos', ha='center', va='center')
        axs[0, 1].axis('off')

    if not df_top_doctores.empty:
        axs[1, 0].bar(df_top_doctores['doctor'], df_top_doctores['cantidad'], color='skyblue')
        axs[1, 0].set_title("Top 5 Doctores")
        axs[1, 0].tick_params(axis='x', rotation=30)
    else:
        axs[1, 0].text(0.5, 0.5, 'Sin datos', ha='center', va='center')
        axs[1, 0].axis('off')

    if not df_hora.empty:
        axs[1, 1].barh(df_hora['hora'], df_hora['cantidad'], color='lightgreen')
        axs[1, 1].set_title("Citas por Hora")
        axs[1, 1].set_xlabel("Cantidad")
        axs[1, 1].set_ylabel("Hora")
    else:
        axs[1, 1].text(0.5, 0.5, 'Sin datos', ha='center', va='center')
        axs[1, 1].axis('off')

    plt.tight_layout()
    st.pyplot(fig)

    # Exportar a CSV o Excel
    st.subheader("Exportar citas filtradas")
    query_export = f'''
    SELECT c.id, c.fecha, c.hora, c.estado, p.nombre AS paciente, d.nombre AS doctor
    FROM citas c
    JOIN doctores d ON c.doctor_id = d.id
    JOIN pacientes p ON c.paciente_id = p.id
    {filtro_sql if filtro_sql else ""}
    ORDER BY c.fecha ASC
    '''
    df_export = pd.read_sql_query(query_export, conn)

    if not df_export.empty:
        csv = df_export.to_csv(index=False).encode('utf-8')
        excel = df_export.to_excel(index=False, engine='openpyxl')
        st.download_button("📥 Descargar CSV", data=csv, file_name="citas_filtradas.csv", mime="text/csv")
        st.download_button("📥 Descargar Excel", data=excel, file_name="citas_filtradas.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.info("No hay datos disponibles para exportar con los filtros seleccionados.")

# ---------------- TAB 2: Doctores ----------------
with tabs[1]:
    st.header("Listado de Doctores")
    st.dataframe(pd.read_sql_query("SELECT * FROM doctores", conn))

    st.subheader("Cantidad de citas por doctor")
    query_doctores_citas = '''
    SELECT d.nombre as doctor, COUNT(c.id) as total_citas
    FROM doctores d
    LEFT JOIN citas c ON c.doctor_id = d.id
    GROUP BY d.nombre
    ORDER BY total_citas DESC
    '''
    df_doc_citas = pd.read_sql_query(query_doctores_citas, conn)
    st.bar_chart(df_doc_citas.set_index('doctor'))

# ---------------- TAB 3: Pacientes ----------------
with tabs[2]:
    st.header("Pacientes Registrados")
    st.dataframe(pd.read_sql_query("SELECT * FROM pacientes", conn))

    st.subheader("Pacientes sin citas")
    query_pacientes_sin_citas = '''
    SELECT p.*
    FROM pacientes p
    LEFT JOIN citas c ON c.paciente_id = p.id
    WHERE c.id IS NULL
    '''
    df_sin_citas = pd.read_sql_query(query_pacientes_sin_citas, conn)
    st.write(f"Total sin citas: {len(df_sin_citas)}")
    st.dataframe(df_sin_citas)

# ---------------- TAB 4: Servicios ----------------
with tabs[3]:
    st.header("Servicios Médicos")
    df_servicios = pd.read_sql_query("SELECT * FROM servicios", conn)
    st.dataframe(df_servicios)

    if 'tipo' in df_servicios.columns:
        st.subheader("Distribución de tipos de servicios")
        conteo_tipos = df_servicios['tipo'].value_counts()
        st.bar_chart(conteo_tipos)
