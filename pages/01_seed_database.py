import streamlit as st
import psycopg2
from datetime import datetime

st.set_page_config(
    page_title="Cargar Partidos",
    page_icon="🌱",
    layout="centered"
)

st.title("🌱 Cargar Partidos a la Base de Datos")
st.markdown("---")

# Verificar credenciales de admin (opcional por ahora)
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.expander("🔐 Acceso Administrador", expanded=True):
        password = st.text_input("Contraseña de administrador:", type="password")
        if st.button("Verificar"):
            # Contraseña simple por ahora - puedes cambiarla después
            if password == "admin2026":
                st.session_state.authenticated = True
                st.success("✅ Acceso concedido")
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta")
    st.stop()

# Los PARTIDOS completos (usando los que ya tienes en seed_partidos_v4.py)
PARTIDOS = [
    # JORNADA 1
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
    # JORNADA 2
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
    # JORNADA 3
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

def conectar_bd():
    """Conectar a Supabase"""
    try:
        conn = psycopg2.connect(st.secrets["DATABASE_URL"])
        return conn
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# Mostrar estado actual
st.subheader("📊 Estado Actual")

try:
    conn = conectar_bd()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM partidos")
        total_partidos = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM partidos WHERE goles_local IS NULL")
        partidos_pendientes = cur.fetchone()[0]
        
        col1, col2 = st.columns(2)
        col1.metric("Total Partidos", total_partidos)
        col2.metric("Partidos Pendientes", partidos_pendientes)
        
        cur.close()
        conn.close()
except Exception as e:
    st.warning(f"No se pudo conectar: {e}")

st.markdown("---")

# Botón para cargar partidos
st.subheader("🚀 Cargar/Actualizar Partidos")

col1, col2 = st.columns([3, 1])
with col1:
    st.warning("⚠️ Esto eliminará los pronósticos de partidos sin resultado y recargará todos los partidos")
with col2:
    ejecutar = st.button("🌱 Cargar Partidos", type="primary", use_container_width=True)

if ejecutar:
    with st.spinner("Cargando partidos a Supabase..."):
        try:
            conn = conectar_bd()
            if conn:
                cur = conn.cursor()
                
                # Paso 1: Eliminar pronósticos de partidos sin resultado
                cur.execute("""
                    DELETE FROM pronosticos 
                    WHERE partido_id IN (
                        SELECT id FROM partidos WHERE goles_local IS NULL
                    )
                """)
                st.info(f"🗑 Pronósticos eliminados: {cur.rowcount}")
                
                # Paso 2: Eliminar partidos sin resultado
                cur.execute("DELETE FROM partidos WHERE goles_local IS NULL")
                st.info(f"🗑 Partidos eliminados: {cur.rowcount}")
                
                # Paso 3: Insertar nuevos partidos
                insertados = 0
                errores = 0
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, (fase, local, visita, fecha, hora, sede) in enumerate(PARTIDOS):
                    status_text.text(f"Insertando: {local} vs {visita}")
                    try:
                        cur.execute("""
                            INSERT INTO partidos (fase, equipo_local, equipo_visita, fecha, hora_inicio, sede, cerrado)
                            VALUES (%s, %s, %s, %s, %s, %s, 0)
                        """, (fase, local, visita, fecha, hora, sede))
                        insertados += 1
                    except Exception as e:
                        errores += 1
                        if errores <= 5:  # Mostrar solo primeros 5 errores
                            st.warning(f"Error con {local} vs {visita}: {e}")
                    
                    progress_bar.progress((i + 1) / len(PARTIDOS))
                
                conn.commit()
                status_text.empty()
                
                st.success(f"✅ {insertados} partidos insertados correctamente")
                if errores:
                    st.warning(f"⚠️ {errores} errores (posiblemente partidos duplicados)")
                
                # Mostrar resumen por grupo
                st.subheader("📊 Partidos por Grupo")
                grupos = {}
                for fase, _, _, _, _, _ in PARTIDOS:
                    grupos[fase] = grupos.get(fase, 0) + 1
                
                cols = st.columns(4)
                for i, (grupo, count) in enumerate(sorted(grupos.items())):
                    cols[i % 4].metric(grupo, count)
                
                cur.close()
                conn.close()
                
                st.balloons()
                st.success("🎉 ¡Todos los partidos han sido cargados exitosamente!")
                
        except Exception as e:
            st.error(f"❌ Error general: {e}")

st.markdown("---")
st.info("💡 **Nota:** Esta acción solo inserta partidos nuevos. Los resultados ya cargados no se modifican.")