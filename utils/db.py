from datetime import datetime
import pytz
import os
import streamlit as st
from supabase import create_client, Client
 
# ── Cliente Supabase ──────────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
 
# ── Bloqueo automático ────────────────────────────────────────────────────────
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
 
# ── Init DB (crea tablas vía SQL en Supabase si no existen) ──────────────────
def init_db():
    # Con supabase-py las tablas se crean desde el dashboard de Supabase.
    # Esta función solo verifica la conexión.
    try:
        sb = get_supabase()
        sb.table("colaboradores").select("id").limit(1).execute()
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")
 
# ── Colaboradores ─────────────────────────────────────────────────────────────
def get_colaborador(numero_emp: str):
    sb = get_supabase()
    res = sb.table("colaboradores").select("*").eq("numero_emp", numero_emp).execute()
    return res.data[0] if res.data else None
 
def crear_colaborador(nombre: str, numero_emp: str):
    sb = get_supabase()
    try:
        res = sb.table("colaboradores").insert({
            "nombre": nombre, "numero_emp": numero_emp, "es_admin": 0
        }).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None
 
def get_all_colaboradores():
    sb = get_supabase()
    res = sb.table("colaboradores").select("*").order("nombre").execute()
    return res.data or []
 
# ── Partidos ──────────────────────────────────────────────────────────────────
def get_partidos():
    sb = get_supabase()
    res = sb.table("partidos").select("*").order("fecha").order("id").execute()
    return res.data or []
 
def get_partido(partido_id: int):
    sb = get_supabase()
    res = sb.table("partidos").select("*").eq("id", partido_id).execute()
    return res.data[0] if res.data else None
 
def upsert_partido(partido_id, goles_local, goles_visita, cerrado=1, equipo_pasa=None):
    sb = get_supabase()
    data = {
        "goles_local": goles_local,
        "goles_visita": goles_visita,
        "cerrado": cerrado
    }
    if equipo_pasa:
        data["equipo_pasa"] = equipo_pasa
    sb.table("partidos").update(data).eq("id", partido_id).execute()
    _recalcular_puntos(partido_id)
 
def agregar_partido(fase, local, visita, fecha, hora=None, sede=None):
    sb = get_supabase()
    sb.table("partidos").insert({
        "fase": fase, "equipo_local": local, "equipo_visita": visita,
        "fecha": fecha, "hora_inicio": hora, "sede": sede, "cerrado": 0
    }).execute()
 
# ── Pronósticos ───────────────────────────────────────────────────────────────
def get_pronostico(colaborador_id, partido_id):
    sb = get_supabase()
    res = sb.table("pronosticos")\
        .select("*")\
        .eq("colaborador_id", colaborador_id)\
        .eq("partido_id", partido_id)\
        .execute()
    return res.data[0] if res.data else None
 
def upsert_pronostico(colaborador_id, partido_id, goles_local, goles_visita):
    sb = get_supabase()
    # Verificar si ya existe
    existing = get_pronostico(colaborador_id, partido_id)
    if existing:
        sb.table("pronosticos").update({
            "goles_local": goles_local, "goles_visita": goles_visita
        }).eq("id", existing["id"]).execute()
    else:
        sb.table("pronosticos").insert({
            "colaborador_id": colaborador_id, "partido_id": partido_id,
            "goles_local": goles_local, "goles_visita": goles_visita, "puntos": 0
        }).execute()
 
def get_pronosticos_partido(partido_id):
    sb = get_supabase()
    res = sb.table("pronosticos").select("*, colaboradores(nombre)")\
        .eq("partido_id", partido_id).execute()
    rows = []
    for r in (res.data or []):
        r["nombre"] = r.get("colaboradores", {}).get("nombre", "") if isinstance(r.get("colaboradores"), dict) else ""
        rows.append(r)
    return rows
 
# ── Puntos ────────────────────────────────────────────────────────────────────
FASES_ELIMINATORIAS = {
    "Ronda de 32", "Octavos de Final", "Cuartos de Final",
    "Semifinal", "Tercer Lugar", "Final"
}
 
def es_eliminatoria(fase: str) -> bool:
    return fase in FASES_ELIMINATORIAS
 
def _calcular_puntos(pron_local, pron_visita, real_local, real_visita,
                     fase="", equipo_local="", equipo_pasa=None):
    if es_eliminatoria(fase):
        # El pronóstico: 1-0 = local pasa, 0-1 = visita pasa
        pron_pasa = "local" if pron_local > pron_visita else "visita"
        # El resultado real: si hay equipo_pasa explícito úsalo, sino infiere del marcador
        if equipo_pasa:
            real_pasa = "local" if equipo_pasa == equipo_local else "visita"
        else:
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
    sb = get_supabase()
    res = sb.table("pronosticos").select("*").eq("partido_id", partido_id).execute()
    for p in (res.data or []):
        pts = _calcular_puntos(
            p["goles_local"], p["goles_visita"],
            partido["goles_local"], partido["goles_visita"],
            partido.get("fase", ""),
            equipo_local=partido.get("equipo_local", ""),
            equipo_pasa=partido.get("equipo_pasa")
        )
        sb.table("pronosticos").update({"puntos": pts}).eq("id", p["id"]).execute()
 
def get_tabla_general():
    sb = get_supabase()
    cols = sb.table("colaboradores").select("*").eq("es_admin", 0).execute()
    tabla = []
    for c in (cols.data or []):
        res = sb.table("pronosticos").select("puntos").eq("colaborador_id", c["id"]).execute()
        prons = res.data or []
        puntos_total = sum(p["puntos"] or 0 for p in prons)
        exactos      = sum(1 for p in prons if p["puntos"] == 3)
        parciales    = sum(1 for p in prons if p["puntos"] == 1)
        tabla.append({
            "nombre": c["nombre"], "numero_emp": c["numero_emp"],
            "pronosticos": len(prons), "puntos_total": puntos_total,
            "exactos": exactos, "parciales": parciales
        })
    return sorted(tabla, key=lambda x: (-x["puntos_total"], -x["exactos"]))
 
# ── Lista Blanca ──────────────────────────────────────────────────────────────
def numero_en_lista_blanca(numero_emp: str) -> bool:
    sb = get_supabase()
    res = sb.table("lista_blanca").select("id").eq("numero_emp", numero_emp).execute()
    return len(res.data) > 0
 
def cargar_lista_blanca(numeros: list):
    sb = get_supabase()
    insertados = 0
    for item in numeros:
        numero = str(item.get("numero_emp", "")).strip()
        nombre = str(item.get("nombre_ref", "")).strip()
        if not numero or numero == "None":
            continue
        try:
            sb.table("lista_blanca").upsert({
                "numero_emp": numero, "nombre_ref": nombre
            }, on_conflict="numero_emp").execute()
            insertados += 1
        except Exception:
            pass
    return insertados
 
def get_lista_blanca():
    sb = get_supabase()
    res = sb.table("lista_blanca").select("*").order("numero_emp").execute()
    return res.data or []
 
def eliminar_de_lista_blanca(numero_emp: str):
    sb = get_supabase()
    sb.table("lista_blanca").delete().eq("numero_emp", numero_emp).execute()
 
def lista_blanca_activa() -> bool:
    sb = get_supabase()
    res = sb.table("lista_blanca").select("id").neq("numero_emp", "0000").execute()
    return len(res.data) > 0

def agregar_a_lista_blanca(numero_emp: str, nombre_ref: str = "") -> bool:
    """Agrega un empleado individual a la lista blanca. Retorna False si ya existe."""
    sb = get_supabase()
    res = sb.table("lista_blanca").select("id").eq("numero_emp", numero_emp).execute()
    if res.data:
        return False
    sb.table("lista_blanca").insert({
        "numero_emp": numero_emp, "nombre_ref": nombre_ref
    }).execute()
    return True

def eliminar_colaborador(colaborador_id: int):
    """Elimina un colaborador y todos sus pronósticos."""
    sb = get_supabase()
    sb.table("pronosticos").delete().eq("colaborador_id", colaborador_id).execute()
    sb.table("colaboradores").delete().eq("id", colaborador_id).execute()
    
def eliminar_partido(partido_id: int):
    """Elimina un partido sin resultado y sus pronósticos."""
    sb = get_supabase()
    sb.table("pronosticos").delete().eq("partido_id", partido_id).execute()
    sb.table("partidos").delete().eq("id", partido_id).execute()