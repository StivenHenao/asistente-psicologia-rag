import streamlit as st
import pandas as pd
import base64  # <--- IMPORTANTE: Agrega esto al inicio
from services.api import ApiService

def render_users_view():
    st.title(" Gestión de Pacientes")
    st.markdown("Administra los usuarios del sistema.")

    # Pestañas para organizar la navegación interna
    tab1, tab2, tab3 = st.tabs(["Listado", "Registrar Nuevo", "Editar/Eliminar"])

    # --- TAB 1: LISTADO ---
    with tab1:
        # Usamos ApiService.get_users() en lugar de get_users() suelto
        users = ApiService.get_users()
        
        if users:
            df = pd.DataFrame(users)
            # Seleccionamos columnas relevantes para mostrar
            # Aseguramos que existan las columnas en el DF para evitar errores si la lista viene vacía o con claves faltantes
            available_cols = [c for c in ["id", "name", "email", "city", "active", "voice_code", "age"] if c in df.columns]
            
            st.dataframe(
                df[available_cols], 
                use_container_width=True,
                hide_index=True,
                column_config={
                    "active": st.column_config.CheckboxColumn("Activo", disabled=True),
                    "voice_code": st.column_config.TextColumn("Código Voz"),
                    "id": st.column_config.NumberColumn("ID", format="%d")
                }
            )
            st.caption(f"Total de usuarios registrados: {len(users)}")

            # --- SECCIÓN NUEVA: GENERACIÓN DE INFORMES (MovidA AQUÍ) ---
            st.divider()
            st.subheader(" Acciones Clínicas (Informes)")
            
            # Selector de paciente específico para esta pestaña
            # Creamos un diccionario ID -> Nombre para el selectbox
            user_options_report = {f"{u['id']} - {u['name']}": u for u in users}
            selected_report_label = st.selectbox("Seleccionar Paciente para generar PDF", options=list(user_options_report.keys()), key="select_report_tab1")
            
            if selected_report_label:
                selected_report_user = user_options_report[selected_report_label]
                
                col_gen, col_info = st.columns([1, 2])

                with col_gen:
                    st.markdown(f"**Paciente: {selected_report_user['name']}**")
                    st.caption("Genera un PDF profesional basado en el contexto y factores del paciente.")
                    
                    # Botón para generar
                    generate_btn = st.button(" Generar y Previsualizar", key=f"gen_btn_tab1_{selected_report_user['id']}")

                with col_info:
                    if generate_btn:
                        with st.spinner("⏳ Analizando contexto con Gemini y generando PDF..."):
                            report_res = ApiService.generate_pdf_report(selected_report_user['id'])

                        if report_res.get('success'):
                            st.success("¡Informe generado correctamente!")
                            
                            # 1. BOTÓN DE DESCARGA
                            st.download_button(
                                label="⬇️ Descargar PDF Ahora",
                                data=report_res['data'],
                                file_name=report_res['filename'],
                                mime="application/pdf",
                                key=f"dl_btn_tab1_{selected_report_user['id']}"
                            )
                            
                            # 2. VISUALIZADOR PDF
                            base64_pdf = base64.b64encode(report_res['data']).decode('utf-8')
                            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
                            
                            st.markdown("### 👁️ Vista Previa")
                            st.markdown(pdf_display, unsafe_allow_html=True) #NOSONAR
                            
                        else:
                            st.error(f"Error al generar: {report_res.get('error')}")

        else:
            st.info("No hay usuarios registrados o no se pudo conectar con la API.")

    # --- TAB 2: CREAR ---
    with tab2:
        st.subheader("Nuevo Ingreso")
        with st.form("create_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Nombre Completo")
                email = st.text_input("Correo Electrónico")
                age = st.number_input("Edad", min_value=10, max_value=100, step=1)
                city = st.text_input("Ciudad")
            
            with col2:
                st.markdown("**Factores Psicológicos (Contexto)**")
                factor1 = st.text_area("Factor 1 (Ej. Ansiedad social)", height=68)
                factor2 = st.text_area("Factor 2 (Ej. Insomnio)", height=68)
                factor3 = st.text_area("Factor 3 (Ej. Antecedentes)", height=68)
            
            submitted = st.form_submit_button("Registrar Usuario", type="primary")
            
            if submitted:
                if not name or not email:
                    st.warning("El nombre y el correo son obligatorios.")
                else:
                    payload = {
                        "email": email, "name": name, "age": age, "city": city,
                        "factor1": factor1, "factor2": factor2, "factor3": factor3,
                        "active": True
                    }
                    
                    with st.spinner("Procesando..."):
                        res = ApiService.create_user(payload)
                    
                    if res.get('success'):
                        code = res.get('voice_code') or res.get('data', {}).get('voice_code', 'N/A')
                        st.success(f"Usuario creado con éxito! Código de voz: {code}")
                        st.balloons()
                    else:
                        err_msg = res.get('error', 'Error desconocido')
                        st.error(f"Error al crear: {err_msg}")

    # --- TAB 3: EDITAR / ELIMINAR ---
    with tab3:
        st.subheader("Modificar Registros")
        
        users_list = ApiService.get_users()
        
        if users_list:
            user_options = {f"{u['id']} - {u['name']}": u for u in users_list}
            selected_label = st.selectbox("Seleccionar Usuario", options=list(user_options.keys()))
            
            if selected_label:
                selected_user = user_options[selected_label]

                with st.expander(" Editar Datos", expanded=True):
                    with st.form("edit_user_form"):
                        st.markdown("##### Información Personal")
                        
                        col_basic1, col_basic2 = st.columns(2)
                        with col_basic1:
                            e_name = st.text_input("Nombre", value=selected_user.get('name', ''))
                            e_age = st.number_input("Edad", value=selected_user.get('age', 18), min_value=10, max_value=100)
                        
                        with col_basic2:
                            e_email = st.text_input("Correo Electrónico", value=selected_user.get('email', ''))
                            e_city = st.text_input("Ciudad", value=selected_user.get('city', ''))
                        
                        st.markdown("---")
                        col_opts1, col_opts2 = st.columns(2)
                        with col_opts1:
                            e_regen = st.checkbox("¿Regenerar código de voz?", help="Si marcas esto, el usuario recibirá un nuevo código por email.")
                        with col_opts2:
                            e_active = st.checkbox("Usuario Activo", value=selected_user.get('active', True))

                        if st.form_submit_button("Guardar Cambios"):
                            update_payload = {
                                "name": e_name,
                                "email": e_email,
                                "age": e_age,
                                "city": e_city,
                                "active": e_active,
                                "regenerate_voice_code": e_regen
                            }
                            
                            res = ApiService.update_user(selected_user['id'], update_payload)
                            
                            if res and res.get('success'):
                                st.success("Usuario actualizado correctamente.")
                                st.rerun()
                            else:
                                st.error(f"No se pudo actualizar: {res.get('error', '')}")
                
                # --- LA SECCIÓN DE REPORTE SE MOVIÓ A TAB 1 ---

                st.divider()
                
                with st.expander(" Zona de Peligro"):
                    st.markdown("Esta acción no se puede deshacer.")
                    if st.button("Eliminar Usuario Permanentemente", type="primary"):
                        res = ApiService.delete_user(selected_user['id'])
                        if res and res.get('success'):
                            st.success("Usuario eliminado.")
                            st.rerun()
                        else:
                            st.error("Error al eliminar.")
        else:
            st.write("No hay usuarios para editar.")