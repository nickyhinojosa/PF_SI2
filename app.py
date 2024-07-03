import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from datetime import datetime
import pytz
import os
import time
import threading
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Función para cargar datos con manejo de diferentes delimitadores
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
            datos[key] = pd.read_csv(full_path, delimiter=';')
        except Exception as e:
            st.error(f"Error al cargar {filename}: {str(e)}")
            datos[key] = pd.DataFrame()  # Usa un DataFrame vacío en caso de error
    return datos

# Función para agregar una pequeña animación de carga
def load_animation():
    with st.spinner('Cargando...'):
        time.sleep(2)

# Función para mostrar el tiempo en un formato visualmente atractivo
def current_time():
    return datetime.now(pytz.timezone('America/La_Paz')).strftime('%Y-%m-%d %H:%M:%S')

# Función para actualizar la fecha y hora cada minuto
def update_datetime(placeholder):
    while True:
        now = current_time()
        placeholder.markdown(f"<p style='text-align: center; color: #FF5722; font-size:24px;'>{now}</p>", unsafe_allow_html=True)
        time.sleep(60)  # Actualizar cada 60 segundos

# Llamar a la animación de carga
load_animation()
def limpiar_valores_nan(texto):
    return texto if pd.notna(texto) else ""
# Función para verificar credenciales de inicio de sesión
def verificar_credenciales(usuario, contraseña):
    # Aquí puedes añadir lógica para verificar usuario y contraseña
    # Por ahora, asumimos un usuario y contraseña fijos
    return usuario == "admin" and contraseña == "password"

# Función principal de la aplicación
def main():
    # Estado de la sesión de inicio de sesión
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    # Formulario de inicio de sesión
    if not st.session_state.logged_in:
        st.title("Inicio de Sesión")
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            if verificar_credenciales(usuario, contraseña):
                st.session_state.logged_in = True
                st.success("Inicio de sesión exitoso")
            else:
                st.error("Usuario o contraseña incorrectos")
        return

    # Cargar los datos
    datos = cargar_datos()

    # Configuración del menú de navegación
    with st.sidebar:
        selection = option_menu(
            "Navegación",
            ["Introducción", "Consolidado de Datos", "Análisis Temporal", "Análisis por Aeropuerto",
             "Análisis por Aerolínea", "Análisis de Pasajeros", "Análisis de Tipo de Movimiento",
             "Mapas Interactivos", "Conclusiones", "Acerca de"],
            icons=["house", "file-earmark-text", "clock", "building",
                   "airplane", "people", "clipboard", "map", "check-circle", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    # Página: Introducción
    # Página: Introducción
    if selection == "Introducción":
        # Título y subtítulo con estilos CSS
        st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Dashboard de Análisis de Vuelos ✈️</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #9E9E9E;'>Introducción al propósito del dashboard y la importancia de los datos analizados.</h3>", unsafe_allow_html=True)

        # Fecha y Hora Actual con animación
        st.write("## 📅 Fecha y Hora Actual")
        placeholder = st.empty()
        threading.Thread(target=update_datetime, args=(placeholder,), daemon=True).start()

        # Resumen de Datos por Dataset en cuadros bonitos
        st.write("## 📊 Resumen de Datos por Dataset")
        total_datos = 0
        cuadros_datos = []
        for year, df in datos.items():
            num_datos = df.shape[0]
            total_datos += num_datos
            cuadros_datos.append((year, num_datos))

        # Mostrar datos en cuadros separados con colores y animación
        col1, col2, col3 = st.columns([1, 1, 1])
        cuadro_style = """
        <style>
        .metric {
            background-color: #444444;
            border-radius: 10px;
            padding: 10px;
            margin: 10px;
            text-align: center;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        .metric:hover {
            transform: scale(1.05);
        }
        .metric h2 {
            color: #FF5722;
            font-size: 24px;
            margin: 0;
        }
        .metric .value {
            font-size: 20px;
            color: #4CAF50;
        }
        </style>
        """
        st.markdown(cuadro_style, unsafe_allow_html=True)

        for i, (year, num_datos) in enumerate(cuadros_datos):
            if i % 3 == 0:
                with col1:
                    st.markdown(f"<div class='metric'><h2>📅 Datos en {year}</h2><div class='value'>{num_datos}</div></div>", unsafe_allow_html=True)
            elif i % 3 == 1:
                with col2:
                    st.markdown(f"<div class='metric'><h2>📅 Datos en {year}</h2><div class='value'>{num_datos}</div></div>", unsafe_allow_html=True)
            else:
                with col3:
                    st.markdown(f"<div class='metric'><h2>📅 Datos en {year}</h2><div class='value'>{num_datos}</div></div>", unsafe_allow_html=True)

        # Espacio extra después de los cuadros
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        # Total de Datos Cargados en un cuadro bonito
        st.write("## 📈 Total de Datos Cargados")
        st.markdown("<div style='display: flex; justify-content: center;'>"
                    f"<div class='metric'><h2>🔢 Total de Datos</h2><div class='value'>{total_datos}</div></div>"
                    "</div>", unsafe_allow_html=True)

        # Pie de página con animación suave
        st.markdown("""
            <style>
            @keyframes fadeIn {
                0% { opacity: 0; }
                100% { opacity: 1; }
            }
            .footer {
                text-align: center;
                animation: fadeIn 3s ease-in-out;
                color: #757575;
                font-size: 18px;
            }
            </style>
            <div class='footer'>
                📊 Datos actualizados continuamente para ofrecer la mejor experiencia de análisis.
            </div>
            """, unsafe_allow_html=True)

    # Página: Consolidado de Datos
    elif selection == "Consolidado de Datos":
        st.title("Consolidado de Datos")
        st.write("En esta página se muestra el conjunto de datos consolidado.")
        df_consolidado = pd.concat(datos.values())
        st.dataframe(df_consolidado)
        # Añadir filtros según sea necesario

    # Página: Análisis Temporal
    elif selection == "Análisis Temporal":
        st.title("Análisis Temporal")
        # Crear gráficos y añadir filtros según sea necesario

    # Página: Análisis por Aeropuerto
    elif selection == "Análisis por Aeropuerto":
        st.title("Análisis por Aeropuerto")
        # Crear gráficos y mapas según sea necesario

    # Página: Análisis por Aerolínea
    elif selection == "Análisis por Aerolínea":
        st.title("Análisis por Aerolínea")
        # Crear gráficos y añadir filtros según sea necesario

    # Página: Análisis de Pasajeros
    elif selection == "Análisis de Pasajeros":
        st.title("Análisis de Pasajeros")
        # Crear gráficos y añadir filtros según sea necesario

    # Página: Análisis de Tipo de Movimiento
    elif selection == "Análisis de Tipo de Movimiento":
        st.title("Análisis de Tipo de Movimiento")
        # Crear gráficos y añadir filtros según sea necesario

    # Página: Mapas Interactivos
    elif selection == "Mapas Interactivos":
        st.title("Mapas de Aeropuertos")
        
        # Cargar datos
        datos = cargar_datos()
        aeropuertos = datos['aeropuertos']
        
        # Crear el mapa
        m = folium.Map(location=[-34.61315, -58.37723], zoom_start=5, tiles='cartodb positron')
        
        # Añadir un clúster de marcadores
        marker_cluster = MarkerCluster().add_to(m)
        
        for idx, row in aeropuertos.iterrows():
            if not pd.isna(row['longitud']) and not pd.isna(row['latitud']):
                popup_text = f"""
                <strong>{row['denominacion']} ({row['iata']})</strong><br>
                OACI: {row['oaci'] if pd.notna(row['oaci']) else '-'}<br>
                Tipo: {row['tipo'] if pd.notna(row['tipo']) else '-'}<br>
                Elevación: {row['elev']} {row['uom_elev'] if pd.notna(row['uom_elev']) else 'Metros'}<br>
                Provincia: {row['provincia'] if pd.notna(row['provincia']) else '-'}<br>
                Uso: {row['uso'] if pd.notna(row['uso']) else '-'}
                """
                folium.Marker(
                    location=[row['longitud'], row['latitud']],
                    popup=popup_text,
                    tooltip=row['denominacion'],
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(marker_cluster)
        
        # Mostrar el mapa en Streamlit
        folium_static(m)

    # Página: Conclusiones
    elif selection == "Conclusiones":
        st.title("Conclusiones")
        # Resumen y recomendaciones según sea necesario

    # Página: Acerca de
    elif selection == "Acerca de":
        st.title("Acerca de")
        st.write("Información sobre el equipo de desarrollo y contacto.")

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
