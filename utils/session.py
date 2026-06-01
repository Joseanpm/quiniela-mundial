import streamlit as st

def check_session():
    """Retorna el dict del usuario si ya inició sesión, sino None."""
    return st.session_state.get("user", None)

def set_session(user: dict):
    st.session_state["user"] = user

def clear_session():
    st.session_state.clear()
