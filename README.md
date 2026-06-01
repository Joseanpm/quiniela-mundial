# ⚽ Quiniela Mundial 2026 — Danone México

App web para quiniela del Mundial, construida con **Streamlit + SQLite**.

---

## 🚀 Cómo correrla localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy en Streamlit Cloud (gratis)

1. Sube este proyecto a un repositorio de GitHub (puede ser privado).
2. Entra a [share.streamlit.io](https://share.streamlit.io) con tu cuenta de GitHub.
3. Haz clic en **New app** → selecciona el repo → `app.py` como archivo principal.
4. ¡Listo! Obtienes un link que puedes compartir con todos los colaboradores.

> **Nota**: En Streamlit Cloud la base de datos SQLite se reinicia al redesplegar.  
> Para persistencia permanente, puedes usar **Supabase** (gratis) o **PlanetScale** como BD externa.

---

## 🔐 Acceso Admin

- Número de empleado: `0000`
- Desde el tab **⚙️ Admin** puedes:
  - Registrar resultados de partidos
  - Agregar partidos nuevos (fases eliminatorias, etc.)
  - Ver todos los colaboradores registrados

---

## 📊 Sistema de puntos

| Acierto                        | Puntos |
|-------------------------------|--------|
| Resultado exacto (ej. 2-1)    | **3**  |
| Ganador o empate correcto     | **1**  |
| Falla                         | **0**  |

---

## 🗂 Estructura del proyecto

```
quiniela-mundial/
├── app.py              ← Entrada principal
├── requirements.txt
├── data/
│   └── quiniela.db     ← Base de datos SQLite (se crea automáticamente)
├── utils/
│   ├── db.py           ← Toda la lógica de base de datos
│   └── session.py      ← Manejo de sesión
└── pages/
    ├── login.py        ← Pantalla de acceso
    ├── quiniela.py     ← Pronósticos por partido
    ├── tabla.py        ← Tabla general / leaderboard
    └── admin.py        ← Panel de administración
```
