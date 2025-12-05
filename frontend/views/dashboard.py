import streamlit as st
import pandas as pd
import plotly.express as px
from services.api import ApiService 

def render_dashboard():
    """
    Renderiza la vista principal con métricas y gráficos.
    """
    st.title("DASHBOARD")
    st.markdown("Monitoreo en tiempo real de pacientes.")
    
    # 1. Obtener datos (Usando el servicio desacoplado)
    with st.spinner("Cargando métricas..."):
        users = ApiService.get_users()
    
    # Cálculos básicos
    total_users = len(users)
    active_users = len([u for u in users if u.get('active', False)])
    
    # Manejo seguro de dataframes vacío
    if users:
        df = pd.DataFrame(users)
        avg_age = int(df['age'].mean()) if 'age' in df.columns else 0
    else:
        avg_age = 0
        df = pd.DataFrame()
    
    # 2. Tarjetas de Métricas (KPIs)
    # Usamos columnas para distribuir el espacio
    c1, c2, c3 = st.columns(3)
    
    c1.metric(
        label="Pacientes Totales", 
        value=total_users, 
        delta="+2 esta semana"
    )
    c2.metric(
        label="Sesiones Activas", 
        value=active_users, 
        delta="95% tasa",
        delta_color="normal"
    )
    c3.metric(
        label="Edad Promedio", 
        value=f"{avg_age} años", 
        delta="Estable"
    )
    
    st.markdown("---")
    
    # 3. Gráficos Interactivos con Plotly
    st.markdown("### 📈 Análisis Demográfico")
    
    if not df.empty:
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("**Distribución por Ciudad**")
            # Gráfico de Dona
            if 'city' in df.columns:
                city_counts = df['city'].value_counts().reset_index()
                city_counts.columns = ['city', 'count']
                
                fig_city = px.pie(
                    city_counts, 
                    values='count', 
                    names='city', 
                    hole=0.6,
                    color_discrete_sequence=px.colors.sequential.Bluyl
                )
                fig_city.update_layout(showlegend=True, height=300, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_city, use_container_width=True)
            else:
                st.info("No hay datos de ciudades disponibles.")
            
        with col_chart2:
            st.markdown("**Grupos de Edad**")
            # Histograma
            if 'age' in df.columns:
                fig_age = px.histogram(
                    df, 
                    x='age', 
                    nbins=10, 
                    color_discrete_sequence=['#6C63FF']
                )
                fig_age.update_layout(
                    bargap=0.1, 
                    height=300, 
                    margin=dict(t=0, b=0, l=0, r=0),
                    xaxis_title="Edad",
                    yaxis_title="Cantidad de Pacientes"
                )
                st.plotly_chart(fig_age, use_container_width=True)
            else:
                st.info("No hay datos de edad disponibles.")
    else:
        st.warning("⚠️ No hay suficientes datos para generar las gráficas. Registra usuarios en la pestaña 'Gestión'.")

    # 4. Accesos Rápidos (Bonus UX)
    st.markdown("### Accesos Rápidos")
    col_q1, col_q2 = st.columns(2)
    
    with col_q1:
        # Reemplazo del TIP por algo funcional: Descarga de CSV
        if not df.empty:
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=" Descargar Reporte General (CSV)",
                data=csv,
                file_name="reporte_pacientes_gisee.csv",
                mime="text/csv",
                use_container_width=True,
                help="Descarga la lista completa de pacientes y estados en formato Excel/CSV."
            )
        else:
            st.warning("No hay datos para descargar aún.")

    with col_q2:
        # Botón de refrescar con ancho completo para simetría
        if st.button(" Refrescar Datos del Dashboard", use_container_width=True):
            st.rerun()