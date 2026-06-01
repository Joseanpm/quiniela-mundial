"""
seed_partidos_v4.py — Horarios en hora MÉRIDA (CST, UTC-6, sin horario de verano)
Fuente: FIFA oficial (ET/EDT = UTC-4 en verano)

Conversión a hora Mérida (UTC-6):
  EDT cities (NY/Fila/Boston/Atlanta/Miami/Toronto) UTC-4 → Mérida UTC-6 = ET - 2h
  CDT cities (Dallas/Houston/KC)                   UTC-5 → Mérida UTC-6 = ET - 1h  (o local - 1h)
  PDT cities (LA/Seattle/SF/Vancouver)             UTC-7 → Mérida UTC-6 = ET + 0h  (igual a ET... no)
    → PDT = UTC-7, Mérida = UTC-6, diferencia = +1h → hora PDT + 1h = Mérida
    → Más fácil: ET(EDT,UTC-4) - 2h = Mérida para TODAS las ciudades USA/CAN
  México CDMX/GDL/Monterrey CDT (UTC-5) → Mérida (UTC-6) = hora local - 1h

Regla unificada desde ET:
  TODAS las sedes: hora Mérida = ET - 2h  ✅
  (porque ET=EDT=UTC-4, Mérida=UTC-6, diferencia siempre 2h)

Excepto México (CDMX/GDL/Monterrey usan CDT=UTC-5 en verano):
  hora Mérida = hora local México - 1h
"""

import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "quiniela.db")

# (fase, local, visita, fecha, hora_MERIDA, sede)
# Regla: ET - 2h = hora Mérida SIEMPRE
# México local (CDT) - 1h = hora Mérida

PARTIDOS = [
    # ── JORNADA 1 ─────────────────────────────────────────────────
    # Azteca CDMX: 3PM ET → local CDMX = 1PM CDT → Mérida = 12:00
    ("Grupo A", "México",               "Sudáfrica",            "2026-06-11", "13:00", "Azteca, CDMX"),
    # Akron GDL: 10PM ET → local GDL = 8PM CDT → Mérida = 19:00 (7PM)
    # Espera: ET-2h = 10PM-2h = 8PM Mérida... pero GDL es CDT=ET-1h → local=9PM CDT → Mérida=8PM
    # Usamos ET-2h siempre = 20:00
    ("Grupo A", "Corea del Sur",        "Chequia",              "2026-06-11", "20:00", "Akron, Zapopan"),

    # Toronto EDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo B", "Canadá",               "Bosnia-Herzegovina",   "2026-06-12", "13:00", "Toronto"),
    # SoFi LA PDT: 9PM ET - 2h = 7PM Mérida
    ("Grupo D", "Estados Unidos",       "Paraguay",             "2026-06-12", "19:00", "Los Ángeles"),

    # Santa Clara PDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo B", "Qatar",                "Suiza",                "2026-06-13", "13:00", "Santa Clara"),
    # MetLife NY EDT: 6PM ET - 2h = 4PM Mérida
    ("Grupo C", "Brasil",               "Marruecos",            "2026-06-13", "16:00", "Nueva York/NJ"),
    # Gillette Boston EDT: 9PM ET - 2h = 7PM Mérida
    ("Grupo C", "Haití",                "Escocia",              "2026-06-13", "19:00", "Boston"),
    # Vancouver PDT: 12AM ET - 2h = 10PM Mérida (Jun 13)
    ("Grupo D", "Australia",            "Turquía",              "2026-06-13", "22:00", "Vancouver"),

    # NRG Houston CDT: 1PM ET - 2h = 11AM Mérida
    ("Grupo E", "Alemania",             "Curazao",              "2026-06-14", "11:00", "Houston"),
    # AT&T Dallas CDT: 4PM ET - 2h = 2PM Mérida
    ("Grupo F", "Países Bajos",         "Japón",                "2026-06-14", "14:00", "Dallas"),
    # Filadelfia EDT: 7PM ET - 2h = 5PM Mérida
    ("Grupo E", "Costa de Marfil",      "Ecuador",              "2026-06-14", "17:00", "Filadelfia"),
    # BBVA Monterrey CDT: 10PM ET → local Monterrey 8PM CDT → Mérida 7PM
    ("Grupo F", "Túnez",                "Suecia",               "2026-06-14", "19:00", "Monterrey"),

    # Atlanta EDT: 12PM ET - 2h = 10AM Mérida
    ("Grupo H", "España",               "Cabo Verde",           "2026-06-15", "10:00", "Atlanta"),
    # Seattle PDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo G", "Bélgica",              "Egipto",               "2026-06-15", "13:00", "Seattle"),
    # Miami EDT: 6PM ET - 2h = 4PM Mérida
    ("Grupo H", "Arabia Saudita",       "Uruguay",              "2026-06-15", "16:00", "Miami"),
    # LA PDT: 9PM ET - 2h = 7PM Mérida
    ("Grupo G", "Irán",                 "Nueva Zelanda",        "2026-06-15", "19:00", "Los Ángeles"),

    # MetLife NY EDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo I", "Francia",              "Senegal",              "2026-06-16", "13:00", "Nueva York/NJ"),
    # Boston EDT: 6PM ET - 2h = 4PM Mérida
    ("Grupo I", "Irak",                 "Noruega",              "2026-06-16", "16:00", "Boston"),
    # Kansas City CDT: 9PM ET - 2h = 7PM Mérida
    ("Grupo J", "Argentina",            "Argelia",              "2026-06-16", "19:00", "Kansas City"),
    # Santa Clara PDT: 12AM ET - 2h = 10PM Mérida (Jun 16)
    ("Grupo J", "Austria",              "Jordania",             "2026-06-16", "22:00", "Santa Clara"),

    # Houston CDT: 1PM ET - 2h = 11AM Mérida
    ("Grupo K", "Portugal",             "Congo DR",             "2026-06-17", "11:00", "Houston"),
    # Dallas CDT: 4PM ET - 2h = 2PM Mérida
    ("Grupo L", "Inglaterra",           "Croacia",              "2026-06-17", "14:00", "Dallas"),
    # Toronto EDT: 7PM ET - 2h = 5PM Mérida
    ("Grupo L", "Ghana",                "Panamá",               "2026-06-17", "17:00", "Toronto"),
    # Azteca CDMX CDT: 10PM ET → local 8PM CDT → Mérida 7PM
    ("Grupo K", "Uzbekistán",           "Colombia",             "2026-06-17", "19:00", "Azteca, CDMX"),

    # ── JORNADA 2 ─────────────────────────────────────────────────
    # Atlanta EDT: 12PM ET - 2h = 10AM Mérida
    ("Grupo A", "Chequia",              "Sudáfrica",            "2026-06-18", "10:00", "Atlanta"),
    # LA PDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo B", "Suiza",                "Bosnia-Herzegovina",   "2026-06-18", "13:00", "Los Ángeles"),
    # Vancouver PDT: 6PM ET - 2h = 4PM Mérida
    ("Grupo B", "Canadá",               "Qatar",                "2026-06-18", "16:00", "Vancouver"),
    # Akron GDL CDT: 9PM ET → local 7PM CDT → Mérida 6PM
    ("Grupo A", "México",               "Corea del Sur",        "2026-06-18", "18:00", "Akron, Zapopan"),

    # Seattle PDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo D", "Estados Unidos",       "Australia",            "2026-06-19", "13:00", "Seattle"),
    # Boston EDT: 6PM ET - 2h = 4PM Mérida
    ("Grupo C", "Escocia",              "Marruecos",            "2026-06-19", "16:00", "Boston"),
    # Filadelfia EDT: 8:30PM ET - 2h = 6:30PM Mérida
    ("Grupo C", "Brasil",               "Haití",                "2026-06-19", "18:30", "Filadelfia"),
    # Santa Clara PDT: 11PM ET - 2h = 9PM Mérida
    ("Grupo D", "Turquía",              "Paraguay",             "2026-06-19", "21:00", "Santa Clara"),

    # Houston CDT: 1PM ET - 2h = 11AM Mérida
    ("Grupo F", "Países Bajos",         "Suecia",               "2026-06-20", "11:00", "Houston"),
    # Toronto EDT: 4PM ET - 2h = 2PM Mérida
    ("Grupo E", "Alemania",             "Costa de Marfil",      "2026-06-20", "14:00", "Toronto"),
    # Kansas City CDT: 8PM ET - 2h = 6PM Mérida
    ("Grupo E", "Ecuador",              "Curazao",              "2026-06-20", "18:00", "Kansas City"),
    # Monterrey CDT: 10PM ET → local 8PM CDT → Mérida 7PM  (partido 1000)
    ("Grupo F", "Túnez",                "Japón",                "2026-06-20", "19:00", "Monterrey"),

    # Atlanta EDT: 12PM ET - 2h = 10AM Mérida
    ("Grupo H", "España",               "Arabia Saudita",       "2026-06-21", "10:00", "Atlanta"),
    # LA PDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo G", "Bélgica",              "Irán",                 "2026-06-21", "13:00", "Los Ángeles"),
    # Miami EDT: 6PM ET - 2h = 4PM Mérida
    ("Grupo H", "Uruguay",              "Cabo Verde",           "2026-06-21", "16:00", "Miami"),
    # Vancouver PDT: 9PM ET - 2h = 7PM Mérida
    ("Grupo G", "Nueva Zelanda",        "Egipto",               "2026-06-21", "19:00", "Vancouver"),

    # Dallas CDT: 1PM ET - 2h = 11AM Mérida
    ("Grupo J", "Argentina",            "Austria",              "2026-06-22", "11:00", "Dallas"),
    # Filadelfia EDT: 5PM ET - 2h = 3PM Mérida
    ("Grupo I", "Francia",              "Irak",                 "2026-06-22", "15:00", "Filadelfia"),
    # MetLife NY EDT: 8PM ET - 2h = 6PM Mérida
    ("Grupo I", "Noruega",              "Senegal",              "2026-06-22", "18:00", "Nueva York/NJ"),
    # Santa Clara PDT: 11PM ET - 2h = 9PM Mérida
    ("Grupo J", "Jordania",             "Argelia",              "2026-06-22", "21:00", "Santa Clara"),

    # Houston CDT: 1PM ET - 2h = 11AM Mérida
    ("Grupo K", "Portugal",             "Uzbekistán",           "2026-06-23", "11:00", "Houston"),
    # Boston EDT: 4PM ET - 2h = 2PM Mérida
    ("Grupo L", "Inglaterra",           "Ghana",                "2026-06-23", "14:00", "Boston"),
    # Toronto EDT: 7PM ET - 2h = 5PM Mérida
    ("Grupo L", "Panamá",               "Croacia",              "2026-06-23", "17:00", "Toronto"),
    # Akron GDL CDT: 10PM ET → local 8PM CDT → Mérida 7PM
    ("Grupo K", "Colombia",             "Congo DR",             "2026-06-23", "19:00", "Akron, Zapopan"),

    # ── JORNADA 3 (simultáneos) ───────────────────────────────────
    # Vancouver PDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo B", "Suiza",                "Canadá",               "2026-06-24", "13:00", "Vancouver"),
    # Seattle PDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo B", "Bosnia-Herzegovina",   "Qatar",                "2026-06-24", "13:00", "Seattle"),
    # Miami EDT: 6PM ET - 2h = 4PM Mérida
    ("Grupo C", "Brasil",               "Escocia",              "2026-06-24", "16:00", "Miami"),
    # Atlanta EDT: 6PM ET - 2h = 4PM Mérida
    ("Grupo C", "Marruecos",            "Haití",                "2026-06-24", "16:00", "Atlanta"),
    # Azteca CDMX CDT: 9PM ET → local 7PM CDT → Mérida 6PM
    ("Grupo A", "Chequia",              "México",               "2026-06-24", "18:00", "Azteca, CDMX"),
    # Monterrey CDT: 9PM ET → local 7PM CDT → Mérida 6PM
    ("Grupo A", "Sudáfrica",            "Corea del Sur",        "2026-06-24", "18:00", "Monterrey"),

    # Filadelfia EDT: 4PM ET - 2h = 2PM Mérida
    ("Grupo E", "Curazao",              "Costa de Marfil",      "2026-06-25", "14:00", "Filadelfia"),
    # MetLife NY EDT: 4PM ET - 2h = 2PM Mérida
    ("Grupo E", "Ecuador",              "Alemania",             "2026-06-25", "14:00", "Nueva York/NJ"),
    # Dallas CDT: 7PM ET - 2h = 5PM Mérida
    ("Grupo F", "Japón",                "Suecia",               "2026-06-25", "17:00", "Dallas"),
    # Kansas City CDT: 7PM ET - 2h = 5PM Mérida
    ("Grupo F", "Túnez",                "Países Bajos",         "2026-06-25", "17:00", "Kansas City"),
    # LA PDT: 10PM ET - 2h = 8PM Mérida
    ("Grupo D", "Turquía",              "Estados Unidos",       "2026-06-25", "20:00", "Los Ángeles"),
    # Santa Clara PDT: 10PM ET - 2h = 8PM Mérida
    ("Grupo D", "Paraguay",             "Australia",            "2026-06-25", "20:00", "Santa Clara"),

    # Boston EDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo I", "Noruega",              "Francia",              "2026-06-26", "13:00", "Boston"),
    # Toronto EDT: 3PM ET - 2h = 1PM Mérida
    ("Grupo I", "Senegal",              "Irak",                 "2026-06-26", "13:00", "Toronto"),
    # Houston CDT: 8PM ET - 2h = 6PM Mérida
    ("Grupo H", "Cabo Verde",           "Arabia Saudita",       "2026-06-26", "18:00", "Houston"),
    # Akron GDL CDT: 8PM ET → local 6PM CDT → Mérida 5PM
    ("Grupo H", "Uruguay",              "España",               "2026-06-26", "17:00", "Akron, Zapopan"),
    # Seattle PDT: 11PM ET - 2h = 9PM Mérida
    ("Grupo G", "Egipto",               "Irán",                 "2026-06-26", "21:00", "Seattle"),
    # Vancouver PDT: 11PM ET - 2h = 9PM Mérida
    ("Grupo G", "Nueva Zelanda",        "Bélgica",              "2026-06-26", "21:00", "Vancouver"),

    # MetLife NY EDT: 5PM ET - 2h = 3PM Mérida
    ("Grupo L", "Panamá",               "Inglaterra",           "2026-06-27", "15:00", "Nueva York/NJ"),
    # Filadelfia EDT: 5PM ET - 2h = 3PM Mérida
    ("Grupo L", "Croacia",              "Ghana",                "2026-06-27", "15:00", "Filadelfia"),
    # Miami EDT: 7:30PM ET - 2h = 5:30PM Mérida
    ("Grupo K", "Colombia",             "Portugal",             "2026-06-27", "17:30", "Miami"),
    # Atlanta EDT: 7:30PM ET - 2h = 5:30PM Mérida
    ("Grupo K", "Congo DR",             "Uzbekistán",           "2026-06-27", "17:30", "Atlanta"),
    # Kansas City CDT: 10PM ET - 2h = 8PM Mérida
    ("Grupo J", "Argelia",              "Austria",              "2026-06-27", "20:00", "Kansas City"),
    # Dallas CDT: 10PM ET - 2h = 8PM Mérida
    ("Grupo J", "Jordania",             "Argentina",            "2026-06-27", "20:00", "Dallas"),
]

def seed():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    cols = [row[1] for row in c.execute("PRAGMA table_info(partidos)").fetchall()]
    if "hora_inicio" not in cols:
        c.execute("ALTER TABLE partidos ADD COLUMN hora_inicio TEXT")
    if "sede" not in cols:
        c.execute("ALTER TABLE partidos ADD COLUMN sede TEXT")

    c.execute("DELETE FROM partidos WHERE goles_local IS NULL")
    eliminados = conn.total_changes
    print(f"🗑  Partidos anteriores eliminados: {eliminados}")

    insertados = 0
    for fase, local, visita, fecha, hora, sede in PARTIDOS:
        try:
            c.execute("""
                INSERT INTO partidos (fase, equipo_local, equipo_visita, fecha, hora_inicio, sede)
                VALUES (?,?,?,?,?,?)
            """, (fase, local, visita, fecha, hora, sede))
            insertados += 1
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
    print(f"✅ Partidos insertados: {insertados}")
    print(f"\n🕐 Todos los horarios en hora MÉRIDA (CST, UTC-6, sin horario de verano)")
    print(f"   México vs Sudáfrica → 13:00 Mérida (1PM) ✅")
    print(f"\n¡Listo! Reinicia Streamlit para ver los cambios.")

if __name__ == "__main__":
    seed()