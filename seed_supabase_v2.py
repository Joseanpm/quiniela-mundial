"""
seed_supabase_v2.py — Carga partidos con horarios Mérida a Supabase
Ejecutar: streamlit run seed_supabase_v2.py
O: python seed_supabase_v2.py (si DATABASE_URL está en entorno)
"""

import psycopg2
import streamlit as st
import os
from datetime import datetime

# Configuración
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "quiniela.db")

# PARTIDOS con horarios MÉRIDA (de tu seed_partidos_v4.py)
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

def get_db_connection():
    """Obtener conexión a Supabase"""
    try:
        # Intenta primero con Streamlit secrets
        DATABASE_URL = st.secrets["DATABASE_URL"]
        return psycopg2.connect(DATABASE_URL)
    except:
        # Fallback a variable de entorno
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL:
            return psycopg2.connect(DATABASE_URL)
        raise Exception("No se encontró DATABASE_URL en secrets.toml ni en variables de entorno")

def seed_supabase():
    """Cargar partidos a Supabase"""
    conn = None
    cur = None
    
    try:
        print("🔄 Conectando a Supabase...")
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Limpiar partidos existentes (sin resultados)
        cur.execute("DELETE FROM pronosticos WHERE partido_id IN (SELECT id FROM partidos WHERE goles_local IS NULL)")
        cur.execute("DELETE FROM partidos WHERE goles_local IS NULL")
        eliminados = cur.rowcount
        print(f"🗑  Partidos anteriores eliminados: {eliminados}")
        
        # Insertar nuevos partidos
        insertados = 0
        for fase, local, visita, fecha, hora, sede in PARTIDOS:
            cur.execute("""
                INSERT INTO partidos (fase, equipo_local, equipo_visita, fecha, hora_inicio, sede, cerrado)
                VALUES (%s, %s, %s, %s, %s, %s, 0)
                ON CONFLICT (fecha, hora_inicio, equipo_local, equipo_visita) 
                DO UPDATE SET 
                    fase = EXCLUDED.fase,
                    sede = EXCLUDED.sede,
                    cerrado = 0,
                    goles_local = NULL,
                    goles_visita = NULL
                RETURNING id
            """, (fase, local, visita, fecha, hora, sede))
            
            if cur.fetchone():
                insertados += 1
        
        conn.commit()
        print(f"✅ Partidos insertados/actualizados: {insertados}")
        print(f"\n🕐 Horarios en hora MÉRIDA (CST, UTC-6)")
        
        # Verificar grupos
        grupos = set()
        for fase, _, _, _, _, _ in PARTIDOS:
            grupos.add(fase)
        
        print(f"\n📊 Grupos disponibles: {', '.join(sorted(grupos))}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def mostrar_partidos_por_grupo():
    """Función auxiliar para verificar que los partidos se cargaron bien"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        for grupo in ['Grupo A', 'Grupo B', 'Grupo C', 'Grupo D', 'Grupo E', 
                      'Grupo F', 'Grupo G', 'Grupo H', 'Grupo I', 'Grupo J', 
                      'Grupo K', 'Grupo L']:
            cur.execute("""
                SELECT equipo_local, equipo_visita, fecha, hora_inicio 
                FROM partidos 
                WHERE fase = %s 
                ORDER BY fecha, hora_inicio
            """, (grupo,))
            partidos = cur.fetchall()
            if partidos:
                print(f"\n{grupo}: {len(partidos)} partidos")
                for local, visita, fecha, hora in partidos[:3]:  # Mostrar primeros 3
                    print(f"  - {local} vs {visita} ({fecha} {hora})")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error mostrando grupos: {e}")

if __name__ == "__main__":
    seed_supabase()
    mostrar_partidos_por_grupo()
    print("\n🎉 ¡Listo! Reinicia Streamlit para ver los grupos.")