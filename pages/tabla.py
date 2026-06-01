import streamlit as st
from utils.db import get_tabla_general

def render():
    tabla = get_tabla_general()

    if not tabla:
        st.info("Aún no hay participantes con pronósticos registrados.")
        return

    # Métricas rápidas
    lider = tabla[0] if tabla else None
    total_participantes = len(tabla)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("👑 Líder actual", lider["nombre"] if lider else "—",
                  f"{lider['puntos_total']} pts" if lider else "")
    with col2:
        st.metric("👥 Participantes", total_participantes)
    with col3:
        total_pts = sum(r["puntos_total"] for r in tabla)
        st.metric("⚽ Puntos en juego", total_pts)

    st.markdown("---")
    st.markdown("### 🏆 Clasificación General")

    for i, row in enumerate(tabla, start=1):
        if i == 1:
            badge_class = "pos-1"
        elif i == 2:
            badge_class = "pos-2"
        elif i == 3:
            badge_class = "pos-3"
        else:
            badge_class = "pos-n"

        bg = "#FFFBEB" if i == 1 else "#FFFFFF"
        border = "2px solid #F5C518" if i == 1 else "1px solid #E2E8F0"

        st.markdown(f"""
        <div style="background:{bg}; border:{border}; border-radius:10px;
                    padding:14px 20px; margin-bottom:10px;
                    display:flex; align-items:center; gap:16px;">
            <span class="pos-badge {badge_class}">{i}</span>
            <div style="flex:1;">
                <div style="font-weight:600; font-size:16px;">{row['nombre']}</div>
                <div style="font-size:12px; color:#718096;">
                    Emp. {row['numero_emp']} &nbsp;·&nbsp;
                    {row['pronosticos']} pronósticos registrados
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-family:'Bebas Neue',sans-serif; font-size:1.8rem;
                            color:#003087; line-height:1;">{row['puntos_total']}</div>
                <div style="font-size:11px; color:#718096;">puntos</div>
            </div>
            <div style="text-align:center; min-width:70px;">
                <div style="font-size:13px; color:#00B37D; font-weight:600;">
                    ✔ {row['exactos']} exactos
                </div>
                <div style="font-size:13px; color:#D69E2E; font-weight:600;">
                    ≈ {row['parciales']} parciales
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
