import streamlit as st
from utils.db import init_db
from utils.session import check_session
import pages.login as login
import pages.quiniela as quiniela
import pages.tabla as tabla
import pages.admin as admin
import pages.reglas as reglas
import pages.resultados as resultados

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quiniela Mundial 2026 | Danone",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Estilos globales ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600&display=swap');

:root {
    --danone-blue:   #003087;
    --danone-light:  #0057B8;
    --accent:        #E8F4FD;
    --gold:          #F5C518;
    --green:         #00B37D;
    --red:           #E03131;
    --bg:            #F0F4F8;
    --surface:       #FFFFFF;
    --text:          #1A202C;
    --muted:         #718096;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 1px;
}

/* Quita padding superior de Streamlit */
.block-container { padding-top: 1.5rem !important; }

/* Botón primario estilo Danone */
.stButton > button {
    background: var(--danone-blue);
    color: white;
    border: none;
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 14px;
    padding: 10px 28px;
    transition: background 0.2s;
}
.stButton > button:hover { background: var(--danone-light); }

/* Inputs */
.stTextInput > div > div > input {
    border-radius: 6px;
    border: 1.5px solid #CBD5E0;
    font-family: 'Inter', sans-serif;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 18px;
    letter-spacing: 1px;
    color: var(--muted);
}
.stTabs [aria-selected="true"] { color: var(--danone-blue) !important; }

/* Cards */
.card {
    background: var(--surface);
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
    margin-bottom: 16px;
}

/* Badge de posición */
.pos-badge {
    display:inline-block;
    width:32px; height:32px;
    line-height:32px;
    text-align:center;
    border-radius:50%;
    font-weight:700;
    font-size:14px;
}
.pos-1 { background:#F5C518; color:#000; }
.pos-2 { background:#A8A9AD; color:#fff; }
.pos-3 { background:#C07A3A; color:#fff; }
.pos-n { background:#EDF2F7; color:#4A5568; }

/* Header banner */
.banner {
    background: linear-gradient(135deg, #003087 0%, #0057B8 60%, #0080D6 100%);
    border-radius: 14px;
    padding: 28px 36px;
    color: white;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.banner h1 { color: white; margin:0; font-size: 2.6rem; }
.banner p  { margin:0; opacity:.85; font-size: 15px; }
</style>
""", unsafe_allow_html=True)

# ── Init DB ───────────────────────────────────────────────────────────────────
init_db()

# ── Routing ───────────────────────────────────────────────────────────────────
user = check_session()

if not user:
    login.render()
else:
    # Header
    st.markdown(f"""
    <div class="banner">
        <div style="font-size:3rem">⚽</div>
        <div>
            <h1>QUINIELA MUNDIAL 2026</h1>
            <p>Danone México &nbsp;·&nbsp; ¡Buena suerte, <strong>{user['nombre']}</strong>!</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs_list = ["🗓 Mis Pronósticos", "📊 Mis Resultados", "🏆 Tabla General", "📋 Reglas y Premios"]
    if user.get("es_admin"):
        tabs_list.append("⚙️ Admin")

    tabs = st.tabs(tabs_list)

    with tabs[0]:
        quiniela.render(user)
    with tabs[1]:
        resultados.render(user)
    with tabs[2]:
        tabla.render()
    with tabs[3]:
        reglas.render()
    if user.get("es_admin") and len(tabs) > 4:
        with tabs[4]:
            admin.render()

    # Logout
    st.sidebar.markdown(f"**{user['nombre']}**")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()
