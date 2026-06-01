from datetime import datetime
import pytz
import os
import streamlit as st

# ── Conexión: Supabase (PostgreSQL) en prod, SQLite local en dev ──────────────
def get_conn():
    """
    Retorna conexión según entorno:
    - Si existe st.secrets["DATABASE_URL"] → PostgreSQL (Supabase)
    - Si no → SQLite local (desarrollo)
    """
    try:
        db_url = st.secrets["DATABASE_URL"]
        import psycopg2
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        return conn, "pg"
    except Exception:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), "..", "data", "quiniela.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn, "sqlite"

def fetchall(cur, sql, params=()):
    cur.execute(sql, params)
    rows = cur.fetchall()
    if not rows:
        return []
    # psycopg2 retorna tuples, sqlite3 retorna Rows → normalizamos a dicts
    if hasattr(rows[0], "keys"):
        return [dict(r) for r in rows]
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]

def fetchone(cur, sql, params=()):
    cur.execute(sql, params)
    row = cur.fetchone()
    if row is None:
        return None
    if hasattr(row, "keys"):
        return dict(row)
    cols = [d[0] for d in cur.description]
    return dict(zip(cols, row))

def ph(db_type):
    """Placeholder: %s para pg, ? para sqlite."""
    return "%s" if db_type == "pg" else "?"

# ── Init DB ───────────────────────────────────────────────────────────────────
def init_db():
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        id          SERIAL PRIMARY KEY,
        nombre      TEXT NOT NULL,
        numero_emp  TEXT UNIQUE NOT NULL,
        es_admin    INTEGER DEFAULT 0,
        creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""") if db == "pg" else cur.execute("""
    CREATE TABLE IF NOT EXISTS colaboradores (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre      TEXT NOT NULL,
        numero_emp  TEXT UNIQUE NOT NULL,
        es_admin    INTEGER DEFAULT 0,
        creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS partidos (
        id            SERIAL PRIMARY KEY,
        fase          TEXT NOT NULL,
        equipo_local  TEXT NOT NULL,
        equipo_visita TEXT NOT NULL,
        fecha         TEXT NOT NULL,
        hora_inicio   TEXT,
        sede          TEXT,
        goles_local   INTEGER,
        goles_visita  INTEGER,
        cerrado       INTEGER DEFAULT 0
    )""") if db == "pg" else cur.execute("""
    CREATE TABLE IF NOT EXISTS partidos (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        fase          TEXT NOT NULL,
        equipo_local  TEXT NOT NULL,
        equipo_visita TEXT NOT NULL,
        fecha         TEXT NOT NULL,
        hora_inicio   TEXT,
        sede          TEXT,
        goles_local   INTEGER,
        goles_visita  INTEGER,
        cerrado       INTEGER DEFAULT 0
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS pronosticos (
        id             SERIAL PRIMARY KEY,
        colaborador_id INTEGER NOT NULL,
        partido_id     INTEGER NOT NULL,
        goles_local    INTEGER NOT NULL,
        goles_visita   INTEGER NOT NULL,
        puntos         INTEGER DEFAULT 0,
        UNIQUE(colaborador_id, partido_id)
    )""") if db == "pg" else cur.execute("""
    CREATE TABLE IF NOT EXISTS pronosticos (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        colaborador_id INTEGER NOT NULL,
        partido_id     INTEGER NOT NULL,
        goles_local    INTEGER NOT NULL,
        goles_visita   INTEGER NOT NULL,
        puntos         INTEGER DEFAULT 0,
        UNIQUE(colaborador_id, partido_id)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS lista_blanca (
        id          SERIAL PRIMARY KEY,
        numero_emp  TEXT UNIQUE NOT NULL,
        nombre_ref  TEXT,
        agregado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""") if db == "pg" else cur.execute("""
    CREATE TABLE IF NOT EXISTS lista_blanca (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_emp  TEXT UNIQUE NOT NULL,
        nombre_ref  TEXT,
        agregado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")

    # Admin por defecto
    if db == "pg":
        cur.execute("""
        INSERT INTO colaboradores (nombre, numero_emp, es_admin)
        VALUES (%s, %s, %s) ON CONFLICT (numero_emp) DO NOTHING
        """, ("Admin", "0000", 1))
        cur.execute("""
        INSERT INTO lista_blanca (numero_emp, nombre_ref)
        VALUES (%s, %s) ON CONFLICT (numero_emp) DO NOTHING
        """, ("0000", "Admin"))
    else:
        cur.execute("INSERT OR IGNORE INTO colaboradores (nombre, numero_emp, es_admin) VALUES (?,?,?)", ("Admin","0000",1))
        cur.execute("INSERT OR IGNORE INTO lista_blanca (numero_emp, nombre_ref) VALUES (?,?)", ("0000","Admin"))

    conn.commit()
    cur.close()
    conn.close()

# ── Bloqueo ───────────────────────────────────────────────────────────────────
def partido_bloqueado(partido: dict) -> bool:
    if partido.get("cerrado"):
        return True
    hora  = partido.get("hora_inicio")
    fecha = partido.get("fecha")
    if not hora or not fecha:
        return False
    try:
        merida = pytz.timezone("America/Merida")
        inicio = merida.localize(datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M"))
        return datetime.now(merida) >= inicio
    except Exception:
        return False

# ── Colaboradores ─────────────────────────────────────────────────────────────
def get_colaborador(numero_emp: str):
    conn, db = get_conn()
    cur = conn.cursor()
    row = fetchone(cur, f"SELECT * FROM colaboradores WHERE numero_emp = {ph(db)}", (numero_emp,))
    cur.close(); conn.close()
    return row

def crear_colaborador(nombre: str, numero_emp: str):
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)
    try:
        cur.execute(f"INSERT INTO colaboradores (nombre, numero_emp) VALUES ({P},{P})", (nombre, numero_emp))
        conn.commit()
        row = fetchone(cur, f"SELECT * FROM colaboradores WHERE numero_emp = {P}", (numero_emp,))
        return row
    except Exception:
        conn.rollback()
        return None
    finally:
        cur.close(); conn.close()

def get_all_colaboradores():
    conn, db = get_conn()
    cur = conn.cursor()
    rows = fetchall(cur, "SELECT * FROM colaboradores ORDER BY nombre")
    cur.close(); conn.close()
    return rows

# ── Partidos ──────────────────────────────────────────────────────────────────
def get_partidos():
    conn, db = get_conn()
    cur = conn.cursor()
    rows = fetchall(cur, "SELECT * FROM partidos ORDER BY fecha, id")
    cur.close(); conn.close()
    return rows

def get_partido(partido_id: int):
    conn, db = get_conn()
    cur = conn.cursor()
    row = fetchone(cur, f"SELECT * FROM partidos WHERE id = {ph(db)}", (partido_id,))
    cur.close(); conn.close()
    return row

def upsert_partido(partido_id, goles_local, goles_visita, cerrado=1):
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)
    cur.execute(f"UPDATE partidos SET goles_local={P}, goles_visita={P}, cerrado={P} WHERE id={P}",
                (goles_local, goles_visita, cerrado, partido_id))
    conn.commit()
    cur.close(); conn.close()
    _recalcular_puntos(partido_id)

def agregar_partido(fase, local, visita, fecha, hora=None, sede=None):
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)
    cur.execute(f"""
        INSERT INTO partidos (fase, equipo_local, equipo_visita, fecha, hora_inicio, sede)
        VALUES ({P},{P},{P},{P},{P},{P})
    """, (fase, local, visita, fecha, hora, sede))
    conn.commit()
    cur.close(); conn.close()

# ── Pronósticos ───────────────────────────────────────────────────────────────
def get_pronostico(colaborador_id, partido_id):
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)
    row = fetchone(cur, f"SELECT * FROM pronosticos WHERE colaborador_id={P} AND partido_id={P}",
                   (colaborador_id, partido_id))
    cur.close(); conn.close()
    return row

def upsert_pronostico(colaborador_id, partido_id, goles_local, goles_visita):
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)
    if db == "pg":
        cur.execute(f"""
            INSERT INTO pronosticos (colaborador_id, partido_id, goles_local, goles_visita)
            VALUES ({P},{P},{P},{P})
            ON CONFLICT (colaborador_id, partido_id)
            DO UPDATE SET goles_local=EXCLUDED.goles_local, goles_visita=EXCLUDED.goles_visita
        """, (colaborador_id, partido_id, goles_local, goles_visita))
    else:
        cur.execute(f"""
            INSERT INTO pronosticos (colaborador_id, partido_id, goles_local, goles_visita)
            VALUES ({P},{P},{P},{P})
            ON CONFLICT(colaborador_id, partido_id)
            DO UPDATE SET goles_local=excluded.goles_local, goles_visita=excluded.goles_visita
        """, (colaborador_id, partido_id, goles_local, goles_visita))
    conn.commit()
    cur.close(); conn.close()

def get_pronosticos_partido(partido_id):
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)
    rows = fetchall(cur, f"""
        SELECT p.*, c.nombre FROM pronosticos p
        JOIN colaboradores c ON c.id = p.colaborador_id
        WHERE p.partido_id = {P}
    """, (partido_id,))
    cur.close(); conn.close()
    return rows

# ── Puntos ────────────────────────────────────────────────────────────────────
FASES_ELIMINATORIAS = {
    "Ronda de 32", "Octavos de Final", "Cuartos de Final",
    "Semifinal", "Tercer Lugar", "Final"
}

def es_eliminatoria(fase: str) -> bool:
    return fase in FASES_ELIMINATORIAS

def _calcular_puntos(pron_local, pron_visita, real_local, real_visita, fase=""):
    if es_eliminatoria(fase):
        pron_pasa = "local" if pron_local > pron_visita else "visita"
        real_pasa = "local" if real_local > real_visita else "visita"
        return 2 if pron_pasa == real_pasa else 0
    if pron_local == real_local and pron_visita == real_visita:
        return 3
    pron_g = 1 if pron_local > pron_visita else (-1 if pron_local < pron_visita else 0)
    real_g = 1 if real_local > real_visita else (-1 if real_local < real_visita else 0)
    return 1 if pron_g == real_g else 0

def _recalcular_puntos(partido_id):
    partido = get_partido(partido_id)
    if not partido or partido["goles_local"] is None:
        return
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)
    prons = fetchall(cur, f"SELECT * FROM pronosticos WHERE partido_id={P}", (partido_id,))
    for p in prons:
        pts = _calcular_puntos(p["goles_local"], p["goles_visita"],
                               partido["goles_local"], partido["goles_visita"],
                               partido.get("fase", ""))
        cur.execute(f"UPDATE pronosticos SET puntos={P} WHERE id={P}", (pts, p["id"]))
    conn.commit()
    cur.close(); conn.close()

def get_tabla_general():
    conn, db = get_conn()
    cur = conn.cursor()
    rows = fetchall(cur, """
        SELECT c.nombre, c.numero_emp,
               COUNT(pr.id)                            AS pronosticos,
               COALESCE(SUM(pr.puntos), 0)             AS puntos_total,
               SUM(CASE WHEN pr.puntos=3 THEN 1 ELSE 0 END) AS exactos,
               SUM(CASE WHEN pr.puntos=1 THEN 1 ELSE 0 END) AS parciales
        FROM colaboradores c
        LEFT JOIN pronosticos pr ON pr.colaborador_id = c.id
        WHERE c.es_admin = 0
        GROUP BY c.id, c.nombre, c.numero_emp
        ORDER BY puntos_total DESC, exactos DESC
    """)
    cur.close(); conn.close()
    return rows

# ── Lista Blanca ──────────────────────────────────────────────────────────────
def numero_en_lista_blanca(numero_emp: str) -> bool:
    conn, db = get_conn()
    cur = conn.cursor()
    row = fetchone(cur, f"SELECT id FROM lista_blanca WHERE numero_emp = {ph(db)}", (numero_emp,))
    cur.close(); conn.close()
    return row is not None

def cargar_lista_blanca(numeros: list):
    conn, db = get_conn()
    cur = conn.cursor()
    P = ph(db)
    insertados = 0
    for item in numeros:
        numero = str(item.get("numero_emp", "")).strip()
        nombre = str(item.get("nombre_ref", "")).strip()
        if not numero or numero == "None":
            continue
        try:
            if db == "pg":
                cur.execute(f"""
                    INSERT INTO lista_blanca (numero_emp, nombre_ref)
                    VALUES ({P},{P}) ON CONFLICT (numero_emp) DO NOTHING
                """, (numero, nombre))
            else:
                cur.execute(f"INSERT OR IGNORE INTO lista_blanca (numero_emp, nombre_ref) VALUES ({P},{P})", (numero, nombre))
            insertados += 1
        except Exception:
            pass
    conn.commit()
    cur.close(); conn.close()
    return insertados

def get_lista_blanca():
    conn, db = get_conn()
    cur = conn.cursor()
    rows = fetchall(cur, "SELECT * FROM lista_blanca ORDER BY numero_emp")
    cur.close(); conn.close()
    return rows

def eliminar_de_lista_blanca(numero_emp: str):
    conn, db = get_conn()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM lista_blanca WHERE numero_emp = {ph(db)}", (numero_emp,))
    conn.commit()
    cur.close(); conn.close()

def lista_blanca_activa() -> bool:
    conn, db = get_conn()
    cur = conn.cursor()
    row = fetchone(cur, "SELECT COUNT(*) as n FROM lista_blanca WHERE numero_emp != '0000'")
    cur.close(); conn.close()
    return (row["n"] if row else 0) > 0
