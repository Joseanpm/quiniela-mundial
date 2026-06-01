import streamlit as st
from utils.db import (get_partidos, upsert_partido, agregar_partido,
                      get_all_colaboradores, get_pronosticos_partido,
                      cargar_lista_blanca, get_lista_blanca, eliminar_de_lista_blanca,
                      lista_blanca_activa)

def render():
    st.markdown("### ⚙️ Panel de Administración")
    st.caption("Solo visible para administradores.")

    tab_res, tab_add, tab_col, tab_lb = st.tabs(["📝 Ingresar Resultados", "➕ Agregar Partido", "👥 Colaboradores", "🔐 Lista Blanca"])

    # ── Tab 1: Resultados ─────────────────────────────────────────────────────
    with tab_res:
        st.markdown("#### Registrar resultado de un partido")
        partidos = get_partidos()
        pendientes = [p for p in partidos if not p["cerrado"]]
        terminados = [p for p in partidos if  p["cerrado"]]

        if not pendientes:
            st.success("✅ Todos los partidos tienen resultado registrado.")
        else:
            opciones = {
                f"{p['equipo_local']} vs {p['equipo_visita']} ({p['fecha']})": p
                for p in pendientes
            }
            sel = st.selectbox("Partido a cerrar", list(opciones.keys()))
            partido = opciones[sel]

            c1, c2 = st.columns(2)
            with c1:
                gl = st.number_input(f"Goles {partido['equipo_local']}", min_value=0, max_value=20, key="admin_gl")
            with c2:
                gv = st.number_input(f"Goles {partido['equipo_visita']}", min_value=0, max_value=20, key="admin_gv")

            if st.button("Registrar resultado y calcular puntos", type="primary"):
                upsert_partido(partido["id"], gl, gv)
                st.success(f"Resultado registrado: {gl} — {gv}. Puntos actualizados ✅")
                st.rerun()

        if terminados:
            st.markdown("#### Partidos cerrados")
            for p in terminados:
                prons = get_pronosticos_partido(p["id"])
                exactos   = sum(1 for x in prons if x["puntos"] == 3)
                parciales = sum(1 for x in prons if x["puntos"] == 1)
                st.markdown(f"""
                <div class="card" style="padding:12px 18px;">
                    <b>{p['equipo_local']} {p['goles_local']} — {p['goles_visita']} {p['equipo_visita']}</b>
                    &nbsp;·&nbsp; {p['fecha']}
                    &nbsp;·&nbsp; <span style="color:#00B37D">✔ {exactos} exactos</span>
                    &nbsp; <span style="color:#D69E2E">≈ {parciales} parciales</span>
                    &nbsp; <span style="color:#718096">{len(prons)} pronósticos</span>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 2: Agregar partido ────────────────────────────────────────────────
    with tab_add:
        st.markdown("#### Nuevo partido")
        fase  = st.text_input("Fase (ej. Grupo C, Octavos de Final)")
        local = st.text_input("Equipo local")
        visita = st.text_input("Equipo visitante")
        fecha = st.date_input("Fecha del partido")

        if st.button("Agregar partido", type="primary"):
            if not all([fase, local, visita]):
                st.warning("Completa todos los campos.")
            else:
                agregar_partido(fase, local, visita, str(fecha))
                st.success(f"Partido {local} vs {visita} agregado ✅")
                st.rerun()

    # ── Tab 3: Colaboradores ──────────────────────────────────────────────────
    with tab_col:
        st.markdown("#### Colaboradores registrados")
        cols = get_all_colaboradores()
        for c in cols:
            rol = "👑 Admin" if c["es_admin"] else "👤 Colaborador"
            st.markdown(f"""
            <div style="padding:8px 0; border-bottom:1px solid #EDF2F7;">
                <b>{c['nombre']}</b> &nbsp; <span style="color:#718096; font-size:13px;">
                Emp. {c['numero_emp']} · {rol}</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Tab 4: Lista Blanca ───────────────────────────────────────────────────
    with tab_lb:
        st.markdown("#### 🔐 Lista Blanca de Empleados")

        activa = lista_blanca_activa()
        if activa:
            st.success("✅ Control de acceso **activo** — solo números en la lista pueden registrarse.")
        else:
            st.warning("⚠️ Lista blanca **vacía** — cualquier número puede registrarse. Sube tu Excel para activar el control.")

        st.markdown("---")
        st.markdown("##### Cargar desde Excel")
        st.caption("El archivo debe tener una columna **numero_emp** y opcionalmente **nombre_ref**.")

        archivo = st.file_uploader("Sube tu Excel (.xlsx)", type=["xlsx"])
        if archivo:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(archivo)
                ws = wb.active
                headers = [str(cell.value).strip().lower() for cell in next(ws.iter_rows(min_row=1, max_row=1))]

                if "numero_emp" not in headers:
                    st.error("❌ El Excel debe tener una columna llamada 'numero_emp'.")
                else:
                    col_num  = headers.index("numero_emp")
                    col_nom  = headers.index("nombre_ref") if "nombre_ref" in headers else None

                    registros = []
                    for row in ws.iter_rows(min_row=2, values_only=True):
                        num = str(row[col_num]).strip() if row[col_num] else ""
                        nom = str(row[col_nom]).strip() if col_nom is not None and row[col_nom] else ""
                        if num and num != "None":
                            registros.append({"numero_emp": num, "nombre_ref": nom})

                    st.info(f"📋 {len(registros)} empleados encontrados en el Excel.")

                    if st.button("Cargar lista blanca", type="primary"):
                        insertados = cargar_lista_blanca(registros)
                        st.success(f"✅ {insertados} números cargados correctamente.")
                        st.rerun()
            except Exception as e:
                st.error(f"Error al leer el Excel: {e}")

        st.markdown("---")
        st.markdown("##### Empleados autorizados")
        lista = get_lista_blanca()
        empleados = [l for l in lista if l["numero_emp"] != "0000"]
        st.caption(f"Total: {len(empleados)} empleados")

        for emp in empleados:
            c1, c2, c3 = st.columns([2, 3, 1])
            with c1:
                st.markdown(f"**{emp['numero_emp']}**")
            with c2:
                st.markdown(f"{emp.get('nombre_ref') or '—'}")
            with c3:
                if st.button("🗑", key=f"del_{emp['numero_emp']}"):
                    eliminar_de_lista_blanca(emp["numero_emp"])
                    st.rerun()