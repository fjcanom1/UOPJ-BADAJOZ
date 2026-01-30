import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="UOPJ BADAJOZ", layout="wide", page_icon="🛡️")

# --- PERSISTENCIA DE DATOS LOCAL ---
DB_FILE = "db_uopj_badajoz.json"

def cargar_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "plana_mayor": {"personal": [], "tareas": []},
        "secciones": {s: {"personal": [], "operaciones": {}} for s in ["PATRIMONIO", "EDOA", "PERSONA", "LABORATORIO", "EDITE", "@RROBA"]},
        "equipos": {e: {"personal": [], "operaciones": {}} for e in ["MONTIJO", "MÉRIDA", "VILLANUEVA", "LLERENA", "ZAFRA"]}
    }

def guardar_db(datos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- SEGURIDAD ---
def login():
    if "auth" not in st.session_state: st.session_state.auth = False
    if st.session_state.auth: return True

    st.title("🛡️ UOPJ BADAJOZ - ACCESO RESTRINGIDO")
    pw = st.text_input("Introduzca Clave de Seguridad", type="password")
    if st.button("Entrar"):
        if pw == "BADAJOZ101640": # Clave local de seguridad
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Clave incorrecta")
    return False

# --- UTILIDADES ---
def exportar_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

# --- MÓDULOS REUTILIZABLES ---
def seccion_personal(datos_unidad, nombre_u):
    st.subheader(f"👥 Personal: {nombre_u}")
    with st.expander("➕ Añadir Nuevo"):
        with st.form(f"f_p_{nombre_u}"):
            c1, c2, c3 = st.columns(3)
            emp = c1.selectbox("Empleo", ["Guardia Civil", "Cabo", "Cabo 1º", "Sargento", "Sargento 1º", "Subteniente", "Teniente", "Capitán"])
            tip = c2.text_input("TIP")
            nom = c3.text_input("Nombre")
            ape = c1.text_input("Apellidos")
            tel = c2.text_input("Teléfono")
            ema = c3.text_input("Email")
            if st.form_submit_button("Guardar"):
                datos_unidad["personal"].append({"EMPLEO":emp, "TIP":tip, "NOMBRE":nom, "APELLIDOS":ape, "TEL":tel, "EMAIL":ema})
                guardar_db(st.session_state.db); st.rerun()
    if datos_unidad["personal"]:
        df = pd.DataFrame(datos_unidad["personal"])
        st.table(df)
        st.download_button("📥 Descargar Excel", data=exportar_excel(df), file_name=f"Personal_{nombre_u}.xlsx")

def seccion_operaciones(datos_unidad, nombre_u):
    st.subheader(f"📁 Operaciones: {nombre_u}")
    with st.expander("✨ Iniciar Nueva Operación"):
        n_op = st.text_input("Nombre de la Operación").upper()
        if st.button("Crear"):
            datos_unidad["operaciones"][n_op] = {"resumen":"", "objetivos":[], "juzgado":{}, "coordinacion":{}, "informes":[]}
            guardar_db(st.session_state.db); st.rerun()
    
    op_list = list(datos_unidad["operaciones"].keys())
    if op_list:
        sel = st.selectbox("Carpeta:", op_list)
        op = datos_unidad["operaciones"][sel]
        t1, t2, t3, t4, t5 = st.tabs(["📄 RESUMEN", "🎯 OBJETIVOS", "⚖️ JUZGADO", "🤝 COORDINACIÓN", "📝 INFORMES"])
        
        with t1:
            op["resumen"] = st.text_area("Datos Operación", value=op["resumen"])
            if st.button("Actualizar"): guardar_db(st.session_state.db)
        
        with t2:
            st.file_uploader("Añadir Fotos Objetivos", type=["jpg", "png"])
            with st.form(f"f_obj_{sel}"):
                c1, c2 = st.columns(2)
                o_n = c1.text_input("Nombre"); o_a = c2.text_input("Apellidos")
                o_d = c1.text_input("DNI"); o_r = c2.text_input("Rol")
                if st.form_submit_button("Añadir Objetivo"):
                    op["objetivos"].append({"NOMBRE":o_n, "APELLIDOS":o_a, "DNI":o_d, "ROL":o_r})
                    guardar_db(st.session_state.db); st.rerun()
            for ob in op["objetivos"]: st.write(f"🔴 {ob['NOMBRE']} {ob['APELLIDOS']} ({ob['DNI']})")

        with t5:
            with st.form(f"f_inf_{sel}"):
                c_h, c_t = st.columns([1, 4])
                hora = c_h.time_input("Hora")
                txt = c_t.text_input("Observación")
                if st.form_submit_button("Añadir"):
                    op["informes"].append({"fecha":datetime.now().strftime("%d/%m/%Y"), "hora":str(hora), "texto":txt})
                    guardar_db(st.session_state.db); st.rerun()
            for i in reversed(op["informes"]): st.write(f"📅 {i['fecha']} | 🕒 {i['hora']} | {i['texto']}")

# --- LÓGICA PRINCIPAL ---
if login():
    if "db" not in st.session_state: st.session_state.db = cargar_db()
    db = st.session_state.db

    st.sidebar.title("🚔 UOPJ BADAJOZ")
    
    # BUSCADOR MAESTRO
    st.sidebar.markdown("---")
    busqueda = st.sidebar.text_input("🔍 Buscador General (TIP/DNI/Nombre)")
    if busqueda:
        st.sidebar.info(f"Buscando: {busqueda}...")
        # Aquí iría la lógica de filtrado del buscador transversal

    menu = st.sidebar.radio("MENÚ", ["1. PLANA MAYOR", "2. SECCIONES", "3. EQUIPOS TERRITORIALES"])

    if menu == "1. PLANA MAYOR":
        t_p, t_o = st.tabs(["PERSONAL", "OBSERVACIONES"])
        with t_p: seccion_personal(db["plana_mayor"], "PLANA MAYOR")
        with t_o:
            st.subheader("Control de Tareas")
            db["plana_mayor"]["tareas"] = st.data_editor(pd.DataFrame(db["plana_mayor"]["tareas"], columns=["TAREAS ENCOMENDADAS", "TAREAS PENDIENTES", "TAREAS FINALIZADAS"]), num_rows="dynamic")
            if st.button("Guardar Tareas"): guardar_db(db)

    elif menu == "2. SECCIONES":
        s_sel = st.sidebar.selectbox("Sección:", list(db["secciones"].keys()))
        t_p, t_o = st.tabs(["PERSONAL", "OPERACIONES"])
        with t_p: seccion_personal(db["secciones"][s_sel], s_sel)
        with t_o: seccion_operaciones(db["secciones"][s_sel], s_sel)

    elif menu == "3. EQUIPOS TERRITORIALES":
        e_sel = st.sidebar.selectbox("Equipo:", list(db["equipos"].keys()))
        t_p, t_o = st.tabs(["PERSONAL", "OPERACIONES"])
        with t_p: seccion_personal(db["equipos"][e_sel], e_sel)
        with t_o: seccion_operaciones(db["equipos"][e_sel], e_sel)
  						


