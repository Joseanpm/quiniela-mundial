import streamlit as st
from utils.db import get_partidos, get_pronostico, partido_bloqueado

BANDERAS = {
    "México": "🇲🇽", "Polonia": "🇵🇱", "Argentina": "🇦🇷", "Marruecos": "🇲🇦",
    "Brasil": "🇧🇷", "Alemania": "🇩🇪", "Francia": "🇫🇷", "España": "🇪🇸",
    "Estados Unidos": "🇺🇸", "Canadá": "🇨🇦", "Uruguay": "🇺🇾", "Colombia": "🇨🇴",
    "Ecuador": "🇪🇨", "Japón": "🇯🇵", "Corea del Sur": "🇰🇷", "Australia": "🇦🇺",
    "Arabia Saudita": "🇸🇦", "Portugal": "🇵🇹", "Croacia": "🇭🇷", "Suiza": "🇨🇭",
    "Países Bajos": "🇳🇱", "Senegal": "🇸🇳", "Ghana": "🇬🇭", "Marruecos": "🇲🇦",
    "Túnez": "🇹🇳", "Suecia": "🇸🇪", "Noruega": "🇳🇴", "Dinamarca": "🇩🇰",
    "Bélgica": "🇧🇪", "Irán": "🇮🇷", "Nueva Zelanda": "🇳🇿", "Egipto": "🇪🇬",
    "Irak": "🇮🇶", "Argelia": "🇩🇿", "Austria": "🇦🇹", "Jordania": "🇯🇴",
    "Congo DR": "🇨🇩", "Uzbekistán": "🇺🇿", "Cabo Verde": "🇨🇻", "Haití": "🇭🇹",
    "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "Panamá": "🇵🇦", "Bosnia-Herzegovina": "🇧🇦",
    "Qatar": "🇶🇦", "Paraguay": "🇵🇾", "Turquía": "🇹🇷", "Curazao": "🇨🇼",
    "Sudáfrica": "🇿🇦", "Chequia": "🇨🇿", "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
}

def bandera(pais):
    return BANDERAS.get(pais, "🏳️")

def render(user):
    partidos = get_partidos()
    cerrados = [p for p in partidos if p["cerrado"] or (p["goles_local"] is not None)]

    if not cerrados:
        st.info("Aún no hay partidos con resultado registrado.")
        return

    # ── Métricas resumen ──────────────────────────────────────────────────────
    total_prons   = 0
    total_exactos = 0
    total_parciales = 0
    total_puntos  = 0

    for p in cerrados:
        pron = get_pronostico(user["id"], p["id"])
        if pron:
            total_prons += 1
            pts = pron.get("puntos") or 0
            total_puntos += pts
            if pts == 3: total_exactos += 1
            elif pts == 1: total_parciales += 1

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("⚽ Partidos jugados", len(cerrados))
    c2.metric("📋 Mis pronósticos", total_prons)
    c3.metric("🏆 Mis puntos", total_puntos)
    c4.metric("✔ Exactos", f"{total_exactos} exactos / {total_parciales} parciales")

    st.markdown("---")

    # ── Detalle por partido ───────────────────────────────────────────────────
    for p in cerrados:
        pron = get_pronostico(user["id"], p["id"])
        pts  = pron.get("puntos", 0) if pron else None

        # Color de fondo según resultado
        if pts == 3:
            bg, border, emoji = "#F0FFF4", "2px solid #00B37D", "✅"
        elif pts == 1:
            bg, border, emoji = "#FFFBEB", "2px solid #F5C518", "🟡"
        elif pts == 0 and pron:
            bg, border, emoji = "#FFF5F5", "2px solid #E03131", "❌"
        else:
            bg, border, emoji = "#F7FAFC", "1px solid #E2E8F0", "⬜"

        # Pronóstico del usuario
        if pron:
            pron_txt = f"{pron['goles_local']} — {pron['goles_visita']}"
            pts_txt  = f"+{pts} pts" if pts else "0 pts"
        else:
            pron_txt = "Sin pronóstico"
            pts_txt  = "—"

        # Resultado real
        real_txt = f"{p['goles_local']} — {p['goles_visita']}"
        if p.get("equipo_pasa"):
            real_txt += f" (pasa {p['equipo_pasa']})"

        st.html(f"""
        <div style="background:{bg}; border:{border}; border-radius:12px;
                    padding:14px 20px; margin-bottom:10px;">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <div>
                    <span style="font-size:11px; color:#718096;">{p['fase']} · {p['fecha']}</span><br>
                    <span style="font-size:1rem; font-weight:600;">
                        {bandera(p['equipo_local'])} {p['equipo_local']}
                        <span style="color:#A0AEC0; font-weight:400;"> vs </span>
                        {bandera(p['equipo_visita'])} {p['equipo_visita']}
                    </span>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:11px; color:#718096;">Resultado real</div>
                    <div style="font-weight:700; font-size:1rem;">{real_txt}</div>
                </div>
            </div>
            <div style="margin-top:10px; display:flex; align-items:center; gap:12px;">
                <span style="font-size:1.2rem;">{emoji}</span>
                <span style="font-size:13px; color:#4A5568;">
                    Mi pronóstico: <b>{pron_txt}</b>
                </span>
                <span style="margin-left:auto; font-weight:700;
                             color:{'#00B37D' if pts==3 else '#D69E2E' if pts==1 else '#E03131' if pts==0 and pron else '#A0AEC0'};">
                    {pts_txt}
                </span>
            </div>
        </div>
        """)