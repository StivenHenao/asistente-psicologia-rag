import streamlit as st
import os


def render_sidebar():
    """
    Renderiza la barra lateral de navegación y gestiona el estado de la vista.
    """
    with st.sidebar:
        # --- LOGO E IDENTIDAD ---
        # 1. Definir la ruta de la imagen de forma robusta (Ingeniero Pro)
        # Esto busca la ruta donde está ESTE archivo (sidebar.py) y baja a assets
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "..", "assets", "logo.png")

        # 2. Centrar la imagen usando columnas
        col_logo, col_text = st.columns([1, 2])
        
        with col_logo:
            # Verificamos si existe para que no explote si se borra el archivo
            if os.path.exists(logo_path):
                st.image(logo_path, width=80) 
            else:
                st.warning("⚠️ logo.png")

        with col_text:
            # Alineación vertical simulada con markdown
            st.markdown("""
            <div style="margin-top: 15px;">
                <h3 style="margin: 0; font-size: 1.6rem; color: #FFFFFF; font-weight: 800; letter-spacing: -1px;">Gisee</h3>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")
        
        # Opciones del Menú
        # Usamos un diccionario para mapear claves internas a textos legibles
        menu_options = {
            "dashboard": " Dashboard General",
            "users": " Gestión de Pacientes"
        }
        
        # Renderizar el radio button estilizado
        selected = st.radio(
            "Navegación", 
            list(menu_options.keys()), 
            format_func=lambda x: menu_options[x],
            label_visibility="collapsed"
        )
        
        # Actualizar el estado de la sesión
        # Esto permite que main.py sepa qué renderizar
        st.session_state.view = selected
        
        st.markdown("---")
        
        # Zona de Control de Estado (Mock vs Real)
        # Útil para desarrollo vs producción
        with st.expander(" Estado del Sistema", expanded=True):
            if 'use_mock' not in st.session_state:
                st.session_state.use_mock = True

            mode = st.toggle("Modo Demo (Mock)", value=st.session_state.use_mock)
            st.session_state.use_mock = mode
            
            status_color = "🟢" if mode else "🟠"
            status_text = "Datos Simulados" if mode else "Conexión API"
            
            st.caption(f"{status_color} {status_text}")
            
        # Footer motivacional (Toque personal Sebas)
        st.markdown("---")
        st.caption("✨ *'El orden y la constancia traen la paz.'*")