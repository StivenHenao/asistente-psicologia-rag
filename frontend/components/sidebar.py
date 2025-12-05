import streamlit as st

def render_sidebar():
    """
    Renderiza la barra lateral de navegación y gestiona el estado de la vista.
    """
    with st.sidebar:
        # Logo y Título con un poco de HTML/CSS inline para estilo
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 20px;">
            <div style="background-color: #6C63FF; width: 45px; height: 45px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-right: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <span style="color: white; font-size: 24px;">🧠</span>
            </div>
            <div>
                <h3 style="margin: 0; font-size: 1.4rem; color: #1F2937; font-weight: 700;">Gisee</h3>
                <small style="color: #6B7280; font-weight: 500;">Admin Console</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Opciones del Menú
        # Usamos un diccionario para mapear claves internas a textos legibles
        menu_options = {
            "dashboard": "📊 Dashboard General",
            "users": "👥 Gestión de Pacientes",
            "settings": "⚙️ Configuración"
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
        with st.expander("🔌 Estado del Sistema", expanded=True):
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