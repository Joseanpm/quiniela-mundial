# pages/01_seed_database.py
import streamlit as st
from supabase import create_client, Client
import time

st.set_page_config(
    page_title="Cargar Partidos",
    page_icon="🌱",
    layout="centered"
)

st.title("🌱 Cargar Partidos a Supabase")
st.markdown("---")

# Inicializar conexión a Supabase
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# Verificar autenticación
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.expander("🔐 Acceso Administrador", expanded=True):
        password = st.input_text("Contraseña de administrador:", type="password")
        if st.button("Verificar"):
            if password == "admin2026":
                st.session_state.authenticated = True
                st.success("✅ Acceso concedido")
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    st.stop()

# Los PARTIDOS completos
PARTIDOS = [
    ("Grupo A", "México", "Sudáfrica", "2026-06-11", "13:00", "Azteca, CDMX"),
    ("Grupo A", "Corea del Sur", "Chequia", "2026-06-11", "20:00", "Akron, Zapopan"),
    ("Grupo B", "Canadá", "Bosnia-Herzegovina", "2026-06-12", "13:00", "Toronto"),
    ("Grupo D", "Estados Unidos", "Paraguay", "2026-06-12", "19:00", "Los Ángeles"),
    ("Grupo B", "Qatar", "Suiza", "2026-06-13", "13:00", "Santa Clara"),
    ("Grupo C", "Brasil", "Marruecos", "2026-06-13", "16:00", "Nueva York/NJ"),
    ("Grupo C", "Haití", "Escocia", "2026-06-13", "19:00", "Boston"),
    ("Grupo D", "Australia", "Turquía", "2026-06-13", "22:00", "Vancouver"),
    ("Grupo E", "Alemania", "Curazao", "2026-06-14", "11:00", "Houston"),
    ("Grupo F", "Países Bajos", "Japón", "2026-06-14", "14:00", "Dallas"),
    ("Grupo E", "Costa de Marfil", "Ecuador", "2026-06-14", "17:00", "Filadelfia"),
    ("Grupo F", "Túnez", "Suecia", "2026-06-14", "19:00", "Monterrey"),
    ("Grupo H", "España", "Cabo Verde", "2026-06-15", "10:00", "Atlanta"),
    ("Grupo G", "Bélgica", "Egipto", "2026-06-15", "13:00", "Seattle"),
    ("Grupo H", "Arabia Saudita", "Uruguay", "2026-06-15", "16:00", "Miami"),
    ("Grupo G", "Irán", "Nueva Zelanda", "2026-06-15", "19:00", "Los Ángeles"),
    ("Grupo I", "Francia", "Senegal", "2026-06-16", "13:00", "Nueva York/NJ"),
    ("Grupo I", "Irak", "Noruega", "2026-06-16", "16:00", "Boston"),
    ("Grupo J", "Argentina", "Argelia", "2026-06-16", "19:00", "Kansas City"),
    ("Grupo J", "Austria", "Jordania", "2026-06-16", "22:00", "Santa Clara"),
    ("Grupo K", "Portugal", "Congo DR", "2026-06-17", "11:00", "Houston"),
    ("Grupo L", "Inglaterra", "Croacia", "2026-06-17", "14:00", "Dallas"),
    ("Grupo L", "Ghana", "Panamá", "2026-06-17", "17:00", "Toronto"),
    ("Grupo K", "Uzbekistán", "Colombia", "2026-06-17", "19:00", "Azteca, CDMX"),
    ("Grupo A", "Chequia", "Sudáfrica", "2026-06-18", "10:00", "Atlanta"),
    ("Grupo B", "Suiza", "Bosnia-Herzegovina", "2026-06-18", "13:00", "Los Ángeles"),
    ("Grupo B", "Canadá", "Qatar", "2026-06-18", "16:00", "Vancouver"),
    ("Grupo A", "México", "Corea del Sur", "2026-06-18", "18:00", "Akron, Zapopan"),
    ("Grupo D", "Estados Unidos", "Australia", "2026-06-19", "13:00", "Seattle"),
    ("Grupo C", "Escocia", "Marruecos", "2026-06-19", "16:00", "Boston"),
    ("Grupo C", "Brasil", "Haití", "2026-06-19", "18:30", "Filadelfia"),
    ("Grupo D", "Turquía", "Paraguay", "2026-06-19", "21:00", "Santa Clara"),
    ("Grupo F", "Países Bajos", "Suecia", "2026-06-20", "11:00", "Houston"),
    ("Grupo E", "Alemania", "Costa de Marfil", "2026-06-20", "14:00", "Toronto"),
    ("Grupo E", "Ecuador", "Curazao", "2026-06-20", "18:00", "Kansas City"),
    ("Grupo F", "Túnez", "Japón", "2026-06-20", "19:00", "Monterrey"),
    ("Grupo H", "España", "Arabia Saudita", "2026-06-21", "10:00", "Atlanta"),
    ("Grupo G", "Bélgica", "Irán", "2026-06-21", "13:00", "Los Ángeles"),
    ("Grupo H", "Uruguay", "Cabo Verde", "2026-06-21", "16:00", "Miami"),
    ("Grupo G", "Nueva Zelanda", "Egipto", "2026-06-21", "19:00", "Vancouver"),
    ("Grupo J", "Argentina", "Austria", "2026-06-22", "11:00", "Dallas"),
    ("Grupo I", "Francia", "Irak", "2026-06-22", "15:00", "Filadelfia"),
    ("Grupo I", "Noruega", "Senegal", "2026-06-22", "18:00", "Nueva York/NJ"),
    ("Grupo J", "Jordania", "Argelia", "2026-06-22", "21:00", "Santa Clara"),
    ("Grupo K", "Portugal", "Uzbekistán", "2026-06-23", "11:00", "Houston"),
    ("Grupo L", "Inglaterra", "Ghana", "2026-06-23", "14:00", "Boston"),
    ("Grupo L", "Panamá", "Croacia", "2026-06-23", "17:00", "Toronto"),
    ("Grupo K", "Colombia", "Congo DR", "2026-06-23", "19:00", "Akron, Zapopan"),
    ("Grupo B", "Suiza", "Canadá", "2026-06-24", "13:00", "Vancouver"),
    ("Grupo B", "Bosnia-Herzegovina", "Qatar", "2026-06-24", "13:00", "Seattle"),
    ("Grupo C", "Brasil", "Escocia", "2026-06-24", "16:00", "Miami"),
    ("Grupo C", "Marruecos", "Haití", "2026-06-24", "16:00", "Atlanta"),
    ("Grupo A", "Chequia", "México", "2026-06-24", "18:00", "Azteca, CDMX"),
    ("Grupo A", "Sudáfrica", "Corea del Sur", "2026-06-24", "18:00", "Monterrey"),
    ("Grupo E", "Curazao", "Costa de Marfil", "2026-06-25", "14:00", "Filadelfia"),
    ("Grupo E", "Ecuador", "Alemania", "2026-06-25", "14:00", "Nueva York/NJ"),
    ("Grupo F", "Japón", "Suecia", "2026-06-25", "17:00", "Dallas"),
    ("Grupo F", "Túnez", "Países Bajos", "2026-06-25", "17:00", "Kansas City"),
    ("Grupo D", "Turquía", "Estados Unidos", "2026-06-25", "20:00", "Los Ángeles"),
    ("Grupo D", "Paraguay", "Australia", "2026-06-25", "20:00", "Santa Clara"),
    ("Grupo I", "Noruega", "Francia", "2026-06-26", "13:00", "Boston"),
    ("Grupo I", "Senegal", "Irak", "2026-06-26", "13:00", "Toronto"),
    ("Grupo H", "Cabo Verde", "Arabia Saudita", "2026-06-26", "18:00", "Houston"),
    ("Grupo H", "Uruguay", "España", "2026-06-26", "17:00", "Akron, Zapopan"),
    ("Grupo G", "Egipto", "Irán", "2026-06-26", "21:00", "Seattle"),
    ("Grupo G", "Nueva Zelanda", "Bélgica", "2026-06-26", "21:00", "Vancouver"),
    ("Grupo L", "Panamá", "Inglaterra", "2026-06-27", "15:00", "Nueva York/NJ"),
    ("Grupo L", "Croacia", "Ghana", "2026-06-27", "15:00", "Filadelfia"),
    ("Grupo K", "Colombia", "Portugal", "2026-06-27", "17:30", "Miami"),
    ("Grupo K", "Congo DR", "Uzbekistán", "2026-06-27", "17:30", "Atlanta"),
    ("Grupo J", "Argelia", "Austria", "2026-06-27", "20:00", "Kansas City"),
    ("Grupo J", "Jordania", "Argentina", "2026-06-27", "20:00", "Dallas"),
]

# Botón para cargar partidos
if st.button("🚀 Cargar todos los partidos", type="primary"):
    try:
        supabase = init_supabase()
        
        with st.spinner("Eliminando partidos anteriores sin resultados..."):
            # Eliminar partidos sin resultados
            response = supabase.table('partidos').delete().eq('cerrado', 0).execute()
            st.info(f"🗑 Partidos eliminados: {len(response.data) if response.data else 0}")
        
        # Insertar partidos en batches
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        insertados = 0
        errores = 0
        
        for i, partido in enumerate(PARTIDOS):
            fase, local, visita, fecha, hora, sede = partido
            status_text.text(f"Insertando: {local} vs {visita}")
            
            try:
                data = {
                    'fase': fase,
                    'equipo_local': local,
                    'equipo_visita': visita,
                    'fecha': fecha,
                    'hora_inicio': hora,
                    'sede': sede,
                    'cerrado': 0
                }
                supabase.table('partidos').insert(data).execute()
                insertados += 1
            except Exception as e:
                errores += 1
                if errores <= 5:
                    st.warning(f"Error con {local} vs {visita}: {e}")
            
            progress_bar.progress((i + 1) / len(PARTIDOS))
        
        status_text.empty()
        
        st.success(f"✅ {insertados} partidos insertados correctamente")
        if errores:
            st.warning(f"⚠️ {errores} errores")
        
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Error general: {e}")
        st.info("Verifica que las credenciales de Supabase estén correctas en Secrets")

st.markdown("---")
st.info("💡 Usando API REST de Supabase (puerto 443)")