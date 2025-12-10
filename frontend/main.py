import streamlit as st
import sys
import os

# --- FIX DE RUTAS (CRÍTICO) ---
# Esto asegura que Python encuentre tus carpetas 'components' y 'views'
# sin importar desde dónde ejecutes el comando.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- CONFIGURACIÓN DE PÁGINA ---
# Debe ser siempre el primer comando de Streamlit
st.set_page_config(
    page_title="Gisee | Panel de Control",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- IMPORTS LOCALES ---
# Ahora sí podemos importar todo sin miedo al éxito
from components.sidebar import render_sidebar
from views.dashboard import render_dashboard
from views.users import render_users_view  # <--- ¡Aquí está la magia nueva!

# --- CARGAR ESTILOS CSS ---
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Si no encuentra el CSS, sigue funcionando aunque se vea feito
        pass

# Asegúrate de que la ruta apunte a tu archivo css real
load_css("assets/custom_style.css")

# --- INICIALIZAR ESTADO DE NAVEGACIÓN ---
if 'view' not in st.session_state:
    st.session_state.view = 'dashboard'

# --- FUNCIÓN PRINCIPAL (ORQUESTADOR) ---
def main():
    # 1. Renderizar la Barra Lateral
    render_sidebar()
    
    # 2. Controlar qué vista se muestra en el centro
    current_view = st.session_state.view
    
    if current_view == 'dashboard':
        render_dashboard()
        
    elif current_view == 'users':
        # Aquí llamamos a la función que creaste en users.py
        render_users_view() 
                
    elif current_view == 'settings':
        st.title("Configuración")
        st.write("Configuración del endpoint y credenciales.")

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    main()