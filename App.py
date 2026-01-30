import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import io

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="UOPJ BADAJOZ", layout="wide", page_icon="🛡️")

# --- CONTRASEÑA ---
# La clave es: BADAJOZ101640
def check_password():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if st.session_state.auth:
        return True

    st.title("🛡️ UOPJ BADAJOZ - ACCESO")
    pw = st.text_input("Clave de Seguridad", type="password")
    if st.button("Acceder"):
        # Intenta leer de Secrets, si no, usa la fija
        password_correcta = st.secrets.get("pass_uopj", "BADAJOZ101640")
        if pw == password_correcta:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("❌ Clave incorrecta")
    return False

# --- GESTIÓN DE BASE DE DATOS ---
DB_FILE = "database_pj_badajoz.json"

def inicializar_db():
    return {
        "plana_mayor": {"personal": [], "tareas": []},
        "secciones": {s: {"personal": [], "operaciones": {}} for s in ["PATRIMONIO", "EDOA", "PERSONA", "LABORATORIO", "EDITE", "@RROBA"]},
        "equipos": {e: {"personal": [], "operaciones": {}} for e in ["MONTIJO", "MÉRIDA", "VILLANUEVA", "LLERENA", "ZAFRA"]}
    }

def cargar_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                return json.loads(content) if content else inicializar_db()
        except:
            return inicializar_db()
    return inicializar_db()

def guardar_db(datos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

# --- INICIO DE LA APP ---
if check_password():
    if "db" not in st.session_state:
        st.session_state.db = cargar_db()
    
    db = st.session_state.db

    # BARRA LATERAL
    st.sidebar.title("🚔 MENÚ UOPJ")
    
    # BUSCADOR
    st.sidebar.subheader("🔍 Buscador")
    busqueda = st.sidebar.text_input("Nombre o DNI")
    
    menu = st.sidebar.radio("IR A:", ["PLANA MAYOR", "SECCIONES", "EQUIPOS TERRITORIALES"])

    # --- 1. PLANA MAYOR ---
    if menu == "PLANA MAYOR":
        st.header("🏢 PLANA MAYOR")
        t_pers, t_obs = st.tabs(["👥 PERSONAL", "📝 OBSERVACIONES"])
        
        with t_pers:
            st.subheader("Listado de Personal")
            with st.expander("➕ Añadir Miembro"):
                with st.form("form_plana"):
                    c1, c2 = st.columns(2)
                    emp = c1.selectbox("Empleo", ["GC", "Cabo", "Cabo1", "Sgto", "Sgto1", "Subteniente", "Tte", "Capitan"])
                    tip = c2.text_input("TIP")
                    nom = c1.text_input("Nombre")
                    ape = c2.text_input("Apellidos")
                    if st.form_submit_button("Registrar"):
                        db["plana_mayor"]["personal"].append({"EMPLEO": emp, "TIP": tip, "NOMBRE": nom, "APELLIDOS": ape})
                        guardar_db(db); st.rerun()
            if db["plana_mayor"]["personal"]:
                st.table(pd.DataFrame(db["plana_mayor"]["personal"]))

        with t_obs:
            st.subheader("Gestión de Tareas")
            df_tareas = pd.DataFrame(db["plana_mayor"]["tareas"], columns=["ENCOMENDADAS", "PENDIENTES", "FINALIZADAS"])
            editado = st.data_editor(df_tareas, num_rows="dynamic")
            if st.button("Guardar Tareas"):
                db["plana_mayor"]["tareas"] = editado.to_dict('records')
                guardar_db(db); st.success("Guardado")

    # --- 2. SECCIONES ---
    elif menu == "SECCIONES":
        sec_sel = st.sidebar.selectbox("Seleccione Sección:", list(db["secciones"].keys()))
        st.header(f"🔍 SECCIÓN: {sec_sel}")
        t_pers, t_ops = st.tabs(["👥 PERSONAL", "📁 OPERACIONES"])
        
        with t_pers:
            # Reutiliza lógica de añadir personal (simplificado)
            st.write(f"Personal de {sec_sel}")
            if db["secciones"][sec_sel]["personal"]:
                st.table(pd.DataFrame(db["secciones"][sec_sel]["personal"]))

        with t_ops:
            with st.expander("✨ Nueva Operación"):
                n_op = st.text_input("Nombre Op").upper()
                if st.button("Crear"):
                    db["secciones"][sec_sel]["operaciones"][n_op] = {"resumen": "", "objetivos": [], "informes": []}
                    guardar_db(db); st.rerun()
            
            op_list = list(db["secciones"][sec_sel]["operaciones"].keys())
            if op_list:
                sel = st.selectbox("Abrir Op:", op_list)
                st.info(f"Carpeta: {sel}")

    # --- 3. EQUIPOS TERRITORIALES ---
    elif menu == "EQUIPOS TERRITORIALES":
        eq_sel = st.sidebar.selectbox("Seleccione Equipo:", list(db["equipos"].keys()))
        st.header(f"🚔 EQUIPO: {eq_sel}")
        # Lógica idéntica a secciones...
  						


