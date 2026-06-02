import streamlit as st
from utils.db import get_partidos, get_pronostico, upsert_pronostico, partido_bloqueado, es_eliminatoria, FASES_ELIMINATORIAS
from collections import defaultdict
from datetime import datetime
import pytz

BANDERAS = {
    "México": "🇲🇽", "Polonia": "🇵🇱", "Argentina": "🇦🇷", "Marruecos": "🇲🇦",
    "Brasil": "🇧🇷", "Alemania": "🇩🇪", "Francia": "🇫🇷", "España": "🇪🇸",
    "Estados Unidos": "🇺🇸", "Canadá": "🇨🇦", "Uruguay": "🇺🇾", "Colombia": "🇨🇴",
    "Ecuador": "🇪🇨", "Venezuela": "🇻🇪", "Chile": "🇨🇱", "Perú": "🇵🇪",
    "Japón": "🇯🇵", "Corea del Sur": "🇰🇷", "Australia": "🇦🇺", "Arabia Saudita": "🇸🇦",
    "Irán": "🇮🇷", "Senegal": "🇸🇳", "Ghana": "🇬🇭", "Camerún": "🇨🇲",
    "Túnez": "🇹🇳", "Suiza": "🇨🇭", "Croacia": "🇭🇷", "Portugal": "🇵🇹",
    "Países Bajos": "🇳🇱", "Bélgica": "🇧🇪", "Dinamarca": "🇩🇰", "Serbia": "🇷🇸",
    "Sudáfrica": "🇿🇦", "Chequia": "🇨🇿", "Bosnia-Herzegovina": "🇧🇦", "Paraguay": "🇵🇾",
    "Qatar": "🇶🇦", "Haití": "🇭🇹", "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Turquía": "🇹🇷",
    "Curazao": "🇨🇼", "Suecia": "🇸🇪", "Cabo Verde": "🇨🇻", "Egipto": "🇪🇬",
    "Nueva Zelanda": "🇳🇿", "Irak": "🇮🇶", "Noruega": "🇳🇴", "Argelia": "🇩🇿",
    "Austria": "🇦🇹", "Jordania": "🇯🇴", "Congo DR": "🇨🇩", "Uzbekistán": "🇺🇿",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Panamá": "🇵🇦", "Marruecos": "🇲🇦",
}

def bandera(pais):
    return BANDERAS.get(pais, "🏳️")

def grupo_tiene_proximos(partidos_fase):
    """True si el grupo tiene al menos un partido no bloqueado."""
    return any(not partido_bloqueado(p) and not p["cerrado"] for p in partidos_fase)

def grupo_resumen(partidos_fase, user_id):
    """Retorna (pronosticados, total, puntos) del grupo para el usuario."""
    total = len(partidos_fase)
    pronosticados = 0
    puntos = 0
    for p in partidos_fase:
        pron = get_pronostico(user_id, p["id"])
        if pron:
            pronosticados += 1
            puntos += pron["puntos"] or 0
    return pronosticados, total, puntos

def render_partido(partido, user):
    pid      = partido["id"]
    cerrado  = partido["cerrado"]
    bloqueado = partido_bloqueado(partido)
    pron     = get_pronostico(user["id"], pid)

    prev_local  = pron["goles_local"]  if pron else 0
    prev_visita = pron["goles_visita"] if pron else 0
    puntos_obtenidos = pron["puntos"]  if pron else None

    # Colores card
    bg_color = ("#F0FFF4" if puntos_obtenidos == 3 else
                "#FFFBEB" if puntos_obtenidos == 1 else
                "#FFF5F5" if (pron and puntos_obtenidos == 0 and cerrado) else
                "#FFFFFF")

    # Badge de resultado
    badge = ""
    if puntos_obtenidos == 3:
        pts_label = "2 pts" if es_eliminatoria(partido["fase"]) else "3 pts — ¡Exacto!"
        badge = f'<span style="background:#00B37D;color:#fff;border-radius:4px;padding:2px 10px;font-size:12px;font-weight:600;">✔ {pts_label}</span>'
    elif puntos_obtenidos in (1, 2):
        badge = f'<span style="background:#F5C518;color:#000;border-radius:4px;padding:2px 10px;font-size:12px;font-weight:600;">✔ {puntos_obtenidos} pt{"s" if puntos_obtenidos>1 else ""}</span>'
    elif pron and puntos_obtenidos == 0 and bloqueado:
        badge = '<span style="background:#E03131;color:#fff;border-radius:4px;padding:2px 10px;font-size:12px;font-weight:600;">✘ 0 pts</span>'
    elif bloqueado:
        badge = '<span style="background:#CBD5E0;color:#4A5568;border-radius:4px;padding:2px 10px;font-size:12px;font-weight:600;">🔒 Sin pronóstico</span>'
    elif pron:
        badge = '<span style="background:#EBF8FF;color:#2B6CB0;border-radius:4px;padding:2px 10px;font-size:12px;font-weight:600;">✏️ Pronosticado</span>'

    resultado_real = ""
    if cerrado and partido["goles_local"] is not None:
        resultado_real = f'<span style="color:#718096;font-size:13px;">Resultado: <b>{partido["goles_local"]} — {partido["goles_visita"]}</b></span>'

    hora_str = partido.get("hora_inicio", "")
    sede_str = f' · 📍 {partido["sede"]}' if partido.get("sede") else ""

    st.html(f"""
    <div style="background:{bg_color}; border-radius:12px; padding:16px 20px;
                margin-bottom:4px; border:1px solid #E2E8F0;">
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px; flex-wrap:wrap;">
            <span style="font-size:12px; color:#718096;">📅 {partido['fecha']} · ⏰ {hora_str} Mérida{sede_str}</span>
            {badge}
            {resultado_real}
        </div>
        <div style="display:flex; align-items:center; gap:8px; font-size:1.05rem; font-weight:600;">
            <span>{bandera(partido['equipo_local'])} {partido['equipo_local']}</span>
            <span style="color:#A0AEC0; font-weight:400; font-size:0.9rem;">vs</span>
            <span>{bandera(partido['equipo_visita'])} {partido['equipo_visita']}</span>
        </div>
    </div>
    """)

    if bloqueado and not cerrado:
        st.html('<div style="color:#E6A817;font-size:13px;margin-bottom:6px;">🔒 Partido en curso — pronósticos cerrados</div>')

    if not bloqueado:
        es_elim = es_eliminatoria(partido["fase"])
        if es_elim:
            opciones = [partido["equipo_local"], partido["equipo_visita"]]
            prev_sel = partido["equipo_local"] if prev_local >= prev_visita else partido["equipo_visita"]
            sel = st.radio(
                "¿Quién pasa a la siguiente ronda?",
                opciones,
                index=opciones.index(prev_sel),
                horizontal=True,
                key=f"elim_{pid}"
            )
            gl = 1 if sel == partido["equipo_local"] else 0
            gv = 0 if sel == partido["equipo_local"] else 1
        else:
            c1, c2, c3 = st.columns([2, 1, 2])
            with c1:
                gl = st.number_input(
                    f"Goles {partido['equipo_local']}",
                    min_value=0, max_value=20,
                    value=int(prev_local),
                    key=f"gl_{pid}"
                )
            with c2:
                st.html("<div style='text-align:center;padding-top:32px;font-size:1.3rem;color:#CBD5E0;'>—</div>")
            with c3:
                gv = st.number_input(
                    f"Goles {partido['equipo_visita']}",
                    min_value=0, max_value=20,
                    value=int(prev_visita),
                    key=f"gv_{pid}"
                )

        col_btn, _ = st.columns([1, 3])
        with col_btn:
            if st.button("Guardar pronóstico", key=f"save_{pid}"):
                upsert_pronostico(user["id"], pid, gl, gv)
                st.success("¡Pronóstico guardado! ⚽")
                st.rerun()
    else:
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

def render(user):
    partidos = get_partidos()

    if not partidos:
        st.info("Aún no hay partidos cargados. El admin los agregará pronto.")
        return

    # Separar fase de grupos vs eliminatorias
    ORDEN_GRUPOS = ["Grupo A","Grupo B","Grupo C","Grupo D","Grupo E","Grupo F",
                    "Grupo G","Grupo H","Grupo I","Grupo J","Grupo K","Grupo L"]
    ORDEN_ELIM   = ["Ronda de 32","Octavos de Final","Cuartos de Final",
                    "Semifinal","Tercer Lugar","Final"]

    por_fase = defaultdict(list)
    for p in partidos:
        por_fase[p["fase"]].append(p)

    grupos_presentes = [f for f in ORDEN_GRUPOS if f in por_fase]
    elim_presentes   = [f for f in ORDEN_ELIM   if f in por_fase]
    otras_fases      = [f for f in por_fase if f not in ORDEN_GRUPOS and f not in ORDEN_ELIM]

    # Info de puntos
    st.html("""
    <div style="background:#EBF8FF;border-radius:10px;padding:12px 18px;
                margin-bottom:20px;border-left:4px solid #0057B8;">
        <span style="font-size:13px;color:#2C5282;">
            📋 <b>Grupos:</b> Exacto = 3 pts · Ganador/Empate = 1 pt &nbsp;|&nbsp;
            🔥 <b>Eliminatorias:</b> Quién pasa = 2 pts
        </span>
    </div>
    """)

    # ── FASE DE GRUPOS ────────────────────────────────────────────
    if grupos_presentes:
        st.markdown("## ⚽ Fase de Grupos")
        for fase in grupos_presentes:
            partidos_fase = por_fase[fase]
            pronosticados, total, puntos = grupo_resumen(partidos_fase, user["id"])
            tiene_proximos = grupo_tiene_proximos(partidos_fase)

            # Label con progreso
            todos_cerrados = all(p["cerrado"] for p in partidos_fase)
            icono = "✅" if todos_cerrados else ("🟡" if pronosticados > 0 else "⬜")
            label = f"{icono} {fase}  —  {pronosticados}/{total} pronósticos · {puntos} pts"

            with st.expander(label, expanded=tiene_proximos):
                for partido in partidos_fase:
                    render_partido(partido, user)

    # ── ELIMINATORIAS ─────────────────────────────────────────────
    if elim_presentes or otras_fases:
        st.markdown("## 🔥 Eliminatorias")
        for fase in (elim_presentes + otras_fases):
            partidos_fase = por_fase[fase]
            pronosticados, total, puntos = grupo_resumen(partidos_fase, user["id"])
            tiene_proximos = grupo_tiene_proximos(partidos_fase)
            todos_cerrados = all(p["cerrado"] for p in partidos_fase)
            icono = "✅" if todos_cerrados else ("🟡" if pronosticados > 0 else "⬜")
            label = f"{icono} {fase}  —  {pronosticados}/{total} pronósticos · {puntos} pts"

            with st.expander(label, expanded=tiene_proximos):
                for partido in partidos_fase:
                    render_partido(partido, user)