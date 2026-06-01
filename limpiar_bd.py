"""
limpiar_bd.py — Limpia duplicados y deja la BD con 6 partidos por grupo.
Corre esto UNA sola vez con: python limpiar_bd.py
"""
import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "quiniela.db")

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# ── 1. Ver estado actual ──────────────────────────────────────────────────────
total_antes = c.execute("SELECT COUNT(*) FROM partidos").fetchone()[0]
print(f"Partidos antes: {total_antes}")

por_grupo = c.execute("""
    SELECT fase, COUNT(*) FROM partidos GROUP BY fase ORDER BY fase
""").fetchall()
for g in por_grupo:
    status = "✅" if g[1] == 6 else f"❌ ({g[1]})"
    print(f"  {status} {g[0]}")

# ── 2. Borrar pronósticos huérfanos primero ───────────────────────────────────
c.execute("""
    DELETE FROM pronosticos 
    WHERE partido_id NOT IN (SELECT id FROM partidos)
""")
huerfanos = conn.total_changes
print(f"\nPronósticos huérfanos eliminados: {huerfanos}")

# ── 3. Borrar partidos sin hora_inicio (seeds viejos de ejemplo) ──────────────
c.execute("DELETE FROM partidos WHERE hora_inicio IS NULL")
sin_hora = conn.total_changes - huerfanos
print(f"Partidos sin hora_inicio eliminados: {sin_hora}")

# ── 4. Si aún hay duplicados, dejar solo el más reciente por partido único ────
# Detectar duplicados por (fase, equipo_local, equipo_visita, fecha)
duplicados = c.execute("""
    SELECT fase, equipo_local, equipo_visita, fecha, COUNT(*) as n
    FROM partidos
    GROUP BY fase, equipo_local, equipo_visita, fecha
    HAVING n > 1
""").fetchall()

if duplicados:
    print(f"\nDuplicados encontrados: {len(duplicados)}")
    for d in duplicados:
        # Mantener el de mayor id (más reciente), borrar los viejos
        ids = c.execute("""
            SELECT id FROM partidos
            WHERE fase=? AND equipo_local=? AND equipo_visita=? AND fecha=?
            ORDER BY id DESC
        """, (d[0], d[1], d[2], d[3])).fetchall()
        ids_borrar = [r[0] for r in ids[1:]]  # todos menos el primero (más reciente)
        # Borrar pronósticos de esos partidos primero
        c.execute(f"DELETE FROM pronosticos WHERE partido_id IN ({','.join('?'*len(ids_borrar))})", ids_borrar)
        c.execute(f"DELETE FROM partidos WHERE id IN ({','.join('?'*len(ids_borrar))})", ids_borrar)
        print(f"  Limpiado: {d[1]} vs {d[2]} ({d[0]}, {d[3]}) — borrados {len(ids_borrar)}")
else:
    print("\nNo hay duplicados por (fase, local, visita, fecha) ✅")

conn.commit()

# ── 5. Resultado final ────────────────────────────────────────────────────────
total_despues = c.execute("SELECT COUNT(*) FROM partidos").fetchone()[0]
print(f"\nPartidos después: {total_despues}")

por_grupo = c.execute("""
    SELECT fase, COUNT(*) FROM partidos GROUP BY fase ORDER BY fase
""").fetchall()
for g in por_grupo:
    status = "✅" if g[1] == 6 else f"❌ ({g[1]})"
    print(f"  {status} {g[0]}")

conn.close()
print("\n¡Listo! Reinicia Streamlit.")