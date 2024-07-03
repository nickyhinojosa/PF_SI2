import os
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px
from streamlit_folium import folium_static
import folium

# Function to load data with handling different delimiters
def cargar_datos():
    archivos = {        
        'aeropuertos': 'aeropuertos_detalle.csv',
        '2019': '2019_informe_ministerio.csv',
        '2020': '2020_informe_ministerio.csv',
        '2021': '202112_informe_ministerio.csv',
        '2022': '202212-informe-ministerio.csv',
        '2023': '202312-informe-ministerio.csv',
        '2024': '202405-informe-ministerio.csv'
    }
    base_path = 'data/'
    datos = {}
    for key, filename in archivos.items():
        full_path = os.path.join(base_path, filename)
        try:
            df = pd.read_csv(full_path, delimiter=';', dayfirst=True)
            df.columns = df.columns.str.strip()  # Remove extra spaces in column names
            df.columns = [col.replace(' ', '_') for col in df.columns]  # Replace spaces with underscores
            datos[key] = df
        except Exception as e:
            st.error(f"Error al cargar {filename}: {str(e)}")
            datos[key] = pd.DataFrame()  # Use an empty DataFrame in case of error
    return datos

# Function to create airline analysis page
def analizar_por_aerolinea(datos):
    st.header("✈️ Análisis por Aerolínea")
    
    # Airline selection
    aerolineas = datos['2024']['Aerolinea_Nombre'].unique().tolist()
    aerolineas.insert(0, "Todas")
    aerolinea_seleccionada = st.multiselect("Selecciona una o más Aerolíneas", aerolineas, default="Todas")
    
    # Filter data by selected airlines
    if "Todas" in aerolinea_seleccionada:
        datos_aerolinea = datos['2024']
    else:
        datos_aerolinea = datos['2024'][datos['2024']['Aerolinea_Nombre'].isin(aerolinea_seleccionada)]

    # Ensure 'Fecha UTC' column exists
    if 'Fecha_UTC' not in datos_aerolinea.columns:
        st.error("La columna 'Fecha UTC' no está disponible en los datos.")
        return

    # KPIs
    st.subheader("📊 KPIs")
    total_vuelos = len(datos_aerolinea)
    total_pasajeros = datos_aerolinea['Pasajeros'].sum()
    promedio_pasajeros = datos_aerolinea['Pasajeros'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vuelos", total_vuelos)
    col2.metric("Total de Pasajeros", total_pasajeros)
    col3.metric("Promedio de Pasajeros por Vuelo", round(promedio_pasajeros, 2))

    # Line chart for flights per month
    st.subheader("📅 Vuelos por Mes")
    datos_aerolinea['Fecha_UTC'] = pd.to_datetime(datos_aerolinea['Fecha_UTC'], dayfirst=True)
    datos_aerolinea['Mes'] = datos_aerolinea['Fecha_UTC'].dt.to_period('M').astype(str)
    vuelos_por_mes = datos_aerolinea.groupby('Mes').size().reset_index(name='Vuelos')
    fig_vuelos_mes = px.line(vuelos_por_mes, x='Mes', y='Vuelos', title=f"Vuelos por Mes para {', '.join(aerolinea_seleccionada)}", markers=True)
    st.plotly_chart(fig_vuelos_mes)

    # Bar chart for passengers per flight
    st.subheader("🧍‍♂️ Pasajeros por Vuelo")
    fig_pasajeros_vuelo = px.bar(datos_aerolinea, x='Fecha_UTC', y='Pasajeros', title=f"Pasajeros por Vuelo para {', '.join(aerolinea_seleccionada)}", color='Pasajeros')
    st.plotly_chart(fig_pasajeros_vuelo)
    
    # Interactive map showing flight routes
    st.subheader("🗺️ Mapa de Rutas de Vuelo")
    aeropuertos = datos['aeropuertos']
    m = folium.Map(location=[-34.6037, -58.3816], zoom_start=5)
    for index, row in datos_aerolinea.iterrows():
        origen = aeropuertos[aeropuertos['Aeropuerto'] == row['Origen_/_Destino']]
        destino = aeropuertos[aeropuertos['Aeropuerto'] == row['Aeropuerto']]
        if not origen.empty and not destino.empty:
            folium.PolyLine([(origen['latitud'].values[0], origen['longitud'].values[0]),
                             (destino['latitud'].values[0], destino['longitud'].values[0])],
                            color="blue", weight=2.5, opacity=1).add_to(m)
    folium_static(m)

    # Detailed flight table
    st.subheader("📋 Tabla Detallada de Vuelos")
    st.dataframe(datos_aerolinea)

# Main application function
def main():
    # Load the data
    datos = cargar_datos()

    # Navigation menu configuration
    with st.sidebar:
        selection = option_menu(
            "Navegación",
            ["Introducción", "General", "Análisis Por Año", "Análisis por Aeropuerto",
             "Análisis por Aerolínea", "Análisis de Pasajeros", "Análisis de Tipo de Movimiento",
             "Mapas Interactivos", "Conclusiones", "Acerca de"],
            icons=["house", "file-earmark-text", "clock", "building",
                   "airplane", "people", "clipboard", "map", "check-circle", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    # Page: Análisis por Aerolínea
    if selection == "Análisis por Aerolínea":
        analizar_por_aerolinea(datos)

if __name__ == "__main__":
    main()
