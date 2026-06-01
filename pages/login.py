import streamlit as st
from utils.db import get_colaborador, crear_colaborador, numero_en_lista_blanca, lista_blanca_activa
from utils.session import set_session

def render():
    # ── Layout centrado ───────────────────────────────────────────────────────
    col_l, col_c, col_r = st.columns([1, 1.4, 1])
    with col_c:
        st.markdown("""
        <div style="text-align:center; padding: 32px 0 24px;">
            <div style="font-size:5rem">⚽</div>
            <h1 style="font-family:'Bebas Neue',sans-serif; font-size:2.8rem;
                       color:#003087; letter-spacing:2px; margin:0;">
                QUINIELA MUNDIAL 2026
            </h1>
            <p style="color:#718096; margin-top:6px; font-size:15px;">
                Danone México &nbsp;·&nbsp; ¡Que gane el mejor!
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Ingresa con tu número de empleado")

        numero_emp = st.text_input(
            "Número de empleado", placeholder="Ej. 12345", label_visibility="collapsed"
        )

        if st.button("Entrar ➜", use_container_width=True):
            if not numero_emp.strip():
                st.warning("Ingresa tu número de empleado.")
            else:
                user = get_colaborador(numero_emp.strip())
                if user:
                    set_session(user)
                    st.rerun()
                else:
                    # Validar lista blanca antes de permitir registro
                    if lista_blanca_activa() and not numero_en_lista_blanca(numero_emp.strip()):
                        st.error("❌ Tu número de empleado no está autorizado. Contacta a RH Danone.")
                    else:
                        # Primer acceso → pide nombre
                        st.session_state["nuevo_emp"] = numero_emp.strip()

        # Registro de nuevo colaborador
        if "nuevo_emp" in st.session_state:
            st.divider()
            st.markdown("**Parece que es tu primera vez 👋 ¿Cómo te llamas?**")
            nombre = st.text_input("Tu nombre completo", key="nombre_nuevo")
            if st.button("Registrarme y entrar", use_container_width=True):
                if not nombre.strip():
                    st.warning("Escribe tu nombre para registrarte.")
                else:
                    user = crear_colaborador(nombre.strip(), st.session_state["nuevo_emp"])
                    if user:
                        del st.session_state["nuevo_emp"]
                        set_session(user)
                        st.success("¡Registro exitoso!")
                        st.rerun()
                    else:
                        st.error("Ese número ya está registrado con otro nombre.")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center; color:#A0AEC0; font-size:12px; margin-top:24px;">
            Sistema de Quiniela interno — Danone México 2026
        </p>
        """, unsafe_allow_html=True)
