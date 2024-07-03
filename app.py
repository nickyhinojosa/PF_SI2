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
from streamlit_option_menu import option_menu
import plotly.express as px
from streamlit_folium import folium_static
import folium

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
            df.columns = df.columns.str.strip()  
            df.columns = [col.replace(' ', '_') for col in df.columns]  
            datos[key] = df
        except Exception as e:
            st.error(f"Error al cargar {filename}: {str(e)}")
            datos[key] = pd.DataFrame()  
    return datos

def analizar_por_aerolinea(datos):
    st.header("✈ Análisis por Aerolínea")
    
    # Airline selection
    aerolineas = datos['2024']['Aerolinea_Nombre'].unique().tolist()
    aerolineas.insert(0, "Todas")
    aerolinea_seleccionada = st.multiselect("Selecciona una o más Aerolíneas", aerolineas, default="Todas")
    
    if "Todas" in aerolinea_seleccionada:
        datos_aerolinea = datos['2024']
    else:
        datos_aerolinea = datos['2024'][datos['2024']['Aerolinea_Nombre'].isin(aerolinea_seleccionada)]

    if 'Fecha_UTC' not in datos_aerolinea.columns:
        st.error("La columna 'Fecha UTC' no está disponible en los datos.")
        return

    st.subheader("📊 KPIs")
    total_vuelos = len(datos_aerolinea)
    total_pasajeros = datos_aerolinea['Pasajeros'].sum()
    promedio_pasajeros = datos_aerolinea['Pasajeros'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Vuelos", total_vuelos)
    col2.metric("Total de Pasajeros", total_pasajeros)
    col3.metric("Promedio de Pasajeros por Vuelo", round(promedio_pasajeros, 2))

    st.subheader("📅 Vuelos por Mes")
    datos_aerolinea['Fecha_UTC'] = pd.to_datetime(datos_aerolinea['Fecha_UTC'], dayfirst=True)
    datos_aerolinea['Mes'] = datos_aerolinea['Fecha_UTC'].dt.to_period('M').astype(str)
    vuelos_por_mes = datos_aerolinea.groupby('Mes').size().reset_index(name='Vuelos')
    fig_vuelos_mes = px.line(vuelos_por_mes, x='Mes', y='Vuelos', title=f"Vuelos por Mes para {', '.join(aerolinea_seleccionada)}", markers=True)
    st.plotly_chart(fig_vuelos_mes)

    st.subheader("🧍‍♂ Pasajeros por Vuelo")
    fig_pasajeros_vuelo = px.bar(datos_aerolinea, x='Fecha_UTC', y='Pasajeros', title=f"Pasajeros por Vuelo para {', '.join(aerolinea_seleccionada)}", color='Pasajeros')
    st.plotly_chart(fig_pasajeros_vuelo)
    
    st.subheader("📋 Tabla Detallada de Vuelos")
    st.dataframe(datos_aerolinea)
def get_aeropuerto_details(aeropuertos_df, aeropuerto_code):
    # Filtra los datos para encontrar el aeropuerto con el código dado
    filtro = aeropuertos_df[aeropuertos_df['local'] == aeropuerto_code]
    
    if not filtro.empty:
        return filtro.iloc[0]
    else:
        st.warning(f"No se encontró el aeropuerto con el código: {aeropuerto_code}")

def get_aeropuerto_name(aeropuertos_df, aeropuerto_code):
    return get_aeropuerto_details(aeropuertos_df, aeropuerto_code)['denominacion']
def main():
    datos = cargar_datos()
    if 'aeropuertos' in datos:
        aeropuertos = datos['aeropuertos']
    else:
        st.error("No se encontraron datos de aeropuertos.")
    all_years_data = pd.concat([datos[year] for year in ['2019', '2020', '2021', '2022', '2023', '2024']], ignore_index=True)
    all_years_data['Fecha_UTC'] = pd.to_datetime(all_years_data['Fecha_UTC'], dayfirst=True)
    all_years_data['PAX'] = pd.to_numeric(all_years_data['PAX'], errors='coerce')
    filtered_data = all_years_data[all_years_data['Fecha_UTC'] >= '2019-01-01']
    all_years_data['Mes'] = all_years_data['Fecha_UTC'].dt.to_period('M')
    pasajeros_por_mes = filtered_data.groupby(filtered_data['Fecha_UTC'].dt.to_period('M'))['PAX'].sum().reset_index()
    pasajeros_por_mes['Fecha_UTC'] = pasajeros_por_mes['Fecha_UTC'].dt.to_timestamp()

    pasajeros_por_aerolinea = filtered_data.groupby('Aerolinea_Nombre')['PAX'].sum().reset_index()
    with st.sidebar:
        selection = option_menu(
            "Navegación",
             ["Introducción", "General", "Análisis por año", "Análisis por Aerolinea","Análisis por Aeropuerto",
             "Análisis de Pasajeros","Mapas Interactivos", "Acerca de"],
            icons=["house", "file-earmark-text", "clock", 
                   "airplane", "clipboard","people", "map","checkbox"],
            menu_icon="cast",
            default_index=0,
        )

   
    if selection == "Introducción":
                 # Título y subtítulo con estilos CSS
        st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Dashboard de Análisis de Vuelos ✈</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #9E9E9E;'>Introducción al propósito del dashboard y la importancia de los datos analizados.</h3>", unsafe_allow_html=True)

        st.write("## 📊 Resumen de Datos por Dataset")
        total_datos = 0
        cuadros_datos = []
        for year, df in datos.items():
            num_datos = df.shape[0]
            total_datos += num_datos
            cuadros_datos.append((year, num_datos))

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

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

        st.write("## 📈 Total de Datos Cargados")
        st.markdown("<div style='display: flex; justify-content: center;'>"
                    f"<div class='metric'><h2>🔢 Total de Datos</h2><div class='value'>{total_datos}</div></div>"
                    "</div>", unsafe_allow_html=True)

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

            """, unsafe_allow_html=True)

    elif selection == "General":
        total_vuelos = all_years_data['Fecha_UTC'].count()
        total_pasajeros = all_years_data['PAX'].sum()
        promedio_pasajeros = all_years_data['PAX'].mean()
        num_aeropuertos = datos['aeropuertos']['local'].nunique()

        st.markdown("""
            <style>
            .metric-container {
                background-color: #2B2B2B;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3);
                text-align: center;
                margin-bottom: 15px;
            }
            .metric-label {
                font-size: 14px;
                font-weight: bold;
                color: #FFFFFF;
            }
            .metric-value {
                font-size: 20px;
                font-weight: bold;
                color: #1E90FF;
            }
            </style>
            """, unsafe_allow_html=True)

        st.subheader("Indicadores Clave de Desempeño (KPIs)")
        col1, col2, col3, col4 = st.columns(4, gap="medium")

        with col1:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">✈ Total de Vuelos</div>
                    <div class="metric-value">{total_vuelos}</div>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label"> Total de Pasajeros</div>
                    <div class="metric-value">{total_pasajeros}</div>
                </div>
                """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label"> Promedio de Pasajeros por Vuelo</div>
                    <div class="metric-value">{round(promedio_pasajeros, 2)}</div>
                </div>
                """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label"> Número de Aeropuertos</div>
                    <div class="metric-value">{num_aeropuertos}</div>
                </div>
                """, unsafe_allow_html=True)

        st.subheader("Gráficos Principales")

        vuelos_por_mes = all_years_data.groupby('Mes').size()
        vuelos_por_mes.index = vuelos_por_mes.index.astype(str)
        fig_line = px.line(vuelos_por_mes, title="Vuelos por Mes", labels={'index': 'Mes', 'value': 'Número de Vuelos'})
        fig_line.update_layout(plot_bgcolor='#2B2B2B', paper_bgcolor='#2B2B2B', font_color='#FFFFFF', xaxis_title='Mes', yaxis_title='Número de Vuelos')
        fig_line.update_traces(line=dict(color='#1E90FF'))
        st.plotly_chart(fig_line, use_container_width=True)

        vuelos_por_aerolinea = all_years_data['Aerolinea_Nombre'].value_counts().reset_index()
        vuelos_por_aerolinea.columns = ['Aerolinea', 'Vuelos']
        fig_bar_vuelos = px.bar(vuelos_por_aerolinea, x='Aerolinea', y='Vuelos', title="Vuelos por Aerolínea", labels={'Aerolinea': 'Aerolínea', 'Vuelos': 'Número de Vuelos'})
        fig_bar_vuelos.update_layout(xaxis={'categoryorder': 'total descending'}, plot_bgcolor='#2B2B2B', paper_bgcolor='#2B2B2B', font_color='#FFFFFF', xaxis_title='Aerolínea', yaxis_title='Número de Vuelos')
        fig_bar_vuelos.update_traces(marker_color='#1E90FF')
        fig_bar_vuelos.update_layout(barmode='stack', bargap=0.2)
        st.plotly_chart(fig_bar_vuelos, use_container_width=True)

        pasajeros_por_aerolinea = all_years_data.groupby(['Aerolinea_Nombre', 'Tipo_de_Movimiento'])['PAX'].sum().reset_index()
        fig_bar_pasajeros = px.bar(pasajeros_por_aerolinea, x='Aerolinea_Nombre', y='PAX', color='Tipo_de_Movimiento', title="Pasajeros por Aerolínea y Tipo de Movimiento", labels={'Aerolinea_Nombre': 'Aerolínea', 'PAX': 'Número de Pasajeros'})
        fig_bar_pasajeros.update_layout(xaxis={'categoryorder': 'total descending'}, plot_bgcolor='#2B2B2B', paper_bgcolor='#2B2B2B', font_color='#FFFFFF', xaxis_title='Aerolínea', yaxis_title='Número de Pasajeros')
        fig_bar_pasajeros.update_layout(barmode='stack', bargap=0.2)
        st.plotly_chart(fig_bar_pasajeros, use_container_width=True)

        tipo_movimiento = all_years_data['Tipo_de_Movimiento'].value_counts().reset_index()
        tipo_movimiento.columns = ['Tipo_de_Movimiento', 'count']
        fig_doughnut = px.pie(tipo_movimiento, values='count', names='Tipo_de_Movimiento', title="Distribución de Tipo de Movimiento", hole=0.3)
        fig_doughnut.update_layout(plot_bgcolor='#2B2B2B', paper_bgcolor='#2B2B2B', font_color='#FFFFFF')
        fig_doughnut.update_traces(marker=dict(colors=['#FF6384', '#36A2EB', '#FFCE56']))
        st.plotly_chart(fig_doughnut, use_container_width=True)

        st.subheader("Filtros")
        fecha_min = all_years_data['Fecha_UTC'].min().date()
        fecha_max = all_years_data['Fecha_UTC'].max().date()
        fecha = st.date_input("Seleccionar rango de fechas", value=[fecha_min, fecha_max], min_value=fecha_min, max_value=fecha_max)

        aeropuertos = ['Todos'] + list(all_years_data['Aeropuerto'].unique())
        aerolineas = ['Todos'] + list(all_years_data['Aerolinea_Nombre'].unique())
        tipos_movimiento = ['Todos'] + list(all_years_data['Tipo_de_Movimiento'].unique())

        aeropuerto = st.selectbox("Seleccionar Aeropuerto (Origen/Destino)", aeropuertos)
        aerolinea = st.selectbox("Seleccionar Aerolínea", aerolineas)
        tipo_movimiento = st.selectbox("Seleccionar Tipo de Movimiento", tipos_movimiento)

        datos_filtrados = all_years_data[
            (all_years_data['Fecha_UTC'] >= pd.to_datetime(fecha[0])) & 
            (all_years_data['Fecha_UTC'] <= pd.to_datetime(fecha[1]))
        ]

        if aeropuerto != 'Todos':
            datos_filtrados = datos_filtrados[datos_filtrados['Aeropuerto'] == aeropuerto]

        if aerolinea != 'Todos':
            datos_filtrados = datos_filtrados[datos_filtrados['Aerolinea_Nombre'] == aerolinea]

        if tipo_movimiento != 'Todos':
            datos_filtrados = datos_filtrados[datos_filtrados['Tipo_de_Movimiento'] == tipo_movimiento]

        # Detailed Table
        st.subheader("Tabla Detallada")
        st.dataframe(datos_filtrados)

        
    elif selection == "Análisis por año":
        st.title("Análisis por Año")

        year = st.selectbox("Seleccionar Año", ["2019", "2020", "2021", "2022", "2023", "2024"])

        df_year = datos[year]

        if not df_year.empty:
            total_vuelos = df_year.shape[0]
            total_pasajeros = df_year['Pasajeros'].sum()

            if 'Tipo_de_Movimiento' in df_year.columns:
                total_aterrizajes = df_year[df_year['Tipo_de_Movimiento'] == 'Aterrizaje'].shape[0]
                total_despegues = df_year[df_year['Tipo_de_Movimiento'] == 'Despegue'].shape[0]
            else:
                total_aterrizajes = 0
                total_despegues = 0

            st.metric("Total Vuelos", total_vuelos)
            st.metric("Total Pasajeros", total_pasajeros)
            st.metric("Total Aterrizajes", total_aterrizajes)
            st.metric("Total Despegues", total_despegues)

            if 'Fecha' in df_year.columns:
                df_year['Mes'] = pd.to_datetime(df_year['Fecha'], errors='coerce').dt.month
                vuelos_por_mes = df_year.groupby('Mes').size().reset_index(name='Vuelos')
                fig_line = px.line(vuelos_por_mes, x='Mes', y='Vuelos', title="Vuelos por Mes en el Año Seleccionado")
                st.plotly_chart(fig_line)

            if 'Aerolínea_Nombre' in df_year.columns:
                vuelos_por_aerolinea = df_year['Aerolínea_Nombre'].value_counts().reset_index()
                vuelos_por_aerolinea.columns = ['Aerolínea', 'Vuelos']
                fig_bar = px.bar(vuelos_por_aerolinea, x='Aerolínea', y='Vuelos', title="Vuelos por Aerolínea en el Año Seleccionado")
                st.plotly_chart(fig_bar)

            st.dataframe(df_year)

            # Filters
            if 'Aerolínea_Nombre' in df_year.columns:
                aerolinea_filter = st.multiselect("Filtrar por Aerolínea", options=df_year['Aerolínea_Nombre'].unique())
            else:
                aerolinea_filter = []

            if 'Aeropuerto' in df_year.columns:
                aeropuerto_filter = st.multiselect("Filtrar por Aeropuerto", options=df_year['Aeropuerto'].unique())
            else:
                aeropuerto_filter = []

            if aerolinea_filter:
                df_year = df_year[df_year['Aerolínea_Nombre'].isin(aerolinea_filter)]
            if aeropuerto_filter:
                df_year = df_year[df_year['Aeropuerto'].isin(aeropuerto_filter)]

            st.dataframe(df_year)

        else:
            st.warning("No hay datos disponibles para el año seleccionado.")

    elif selection == "Análisis por Aerolinea":
        analizar_por_aerolinea(datos)

    elif selection == "Análisis por Aeropuerto":
        st.title("Análisis por Aeropuerto")
        st.header("Análisis por Aeropuerto")
        
        aeropuerto_code = st.selectbox("Selecciona un Aeropuerto", aeropuertos['local'].unique())
        
        if aeropuerto_code:
            aeropuerto_details = get_aeropuerto_details(aeropuertos, aeropuerto_code)
            aeropuerto_name = aeropuerto_details['denominacion']
            st.subheader(f"Aeropuerto: {aeropuerto_name} ({aeropuerto_code})")
            
            total_vuelos = len(filtered_data[filtered_data['Aeropuerto'] == aeropuerto_code])
            total_pasajeros = filtered_data[filtered_data['Aeropuerto'] == aeropuerto_code]['PAX'].sum()
            aerolineas_operando = filtered_data[filtered_data['Aeropuerto'] == aeropuerto_code]['Aerolinea_Nombre'].nunique()
            
            st.metric("Total de Vuelos", total_vuelos)
            st.metric("Total de Pasajeros", total_pasajeros)
            st.metric("Aerolíneas Operando", aerolineas_operando)
            
            vuelos_por_mes = filtered_data[filtered_data['Aeropuerto'] == aeropuerto_code].groupby(filtered_data['Fecha_UTC'].dt.to_period("M")).size().reset_index(name='Vuelos')
            vuelos_por_mes['Fecha_UTC'] = vuelos_por_mes['Fecha_UTC'].dt.to_timestamp()
            
            fig_line = px.line(vuelos_por_mes, x='Fecha_UTC', y='Vuelos', title='Vuelos por Mes')
            st.plotly_chart(fig_line)
            
            aerolineas_operando_df = filtered_data[filtered_data['Aeropuerto'] == aeropuerto_code].groupby('Aerolinea_Nombre').size().reset_index(name='Vuelos')
            fig_bar = px.bar(aerolineas_operando_df, x='Aerolinea_Nombre', y='Vuelos', title='Aerolíneas Operando')
            st.plotly_chart(fig_bar)
            
            m = folium.Map(location=[aeropuerto_details['longitud'], aeropuerto_details['latitud']], zoom_start=10)
            folium.Marker(
                location=[aeropuerto_details['longitud'], aeropuerto_details['latitud']],
                popup=aeropuerto_name,
                tooltip=aeropuerto_name
            ).add_to(m)
            
            rutas_principales = filtered_data[filtered_data['Aeropuerto'] == aeropuerto_code]['Origen/Destino'].value_counts().head(10).index
            for ruta in rutas_principales:
                destino_details = get_aeropuerto_details(aeropuertos, ruta)
                folium.Marker(
                    location=[destino_details['longitud'], destino_details['latitud']],
                    popup=destino_details['denominacion'],
                    tooltip=destino_details['denominacion']
                ).add_to(m)
                
            folium_static(m)
            
            # Tabla detallada de vuelos
            vuelos_detallados = filtered_data[filtered_data['Aeropuerto'] == aeropuerto_code]
            st.dataframe(vuelos_detallados)

    elif selection == "Análisis de Pasajeros":
        st.title("📊 Análisis de Pasajeros")
        
        # KPIs
        total_pasajeros = filtered_data['PAX'].sum()
        promedio_pasajeros_vuelo = filtered_data['PAX'].mean()
        
        st.metric("Total de Pasajeros ✈", f"{total_pasajeros:,}")
        st.metric("Promedio de Pasajeros por Vuelo 🛫", f"{promedio_pasajeros_vuelo:.2f}")

        fig_line = px.line(pasajeros_por_mes, x='Fecha_UTC', y='PAX', title="Número de Pasajeros por Mes 📅")
        st.plotly_chart(fig_line)

        fig_bar_aerolinea = px.bar(pasajeros_por_aerolinea, x='Aerolinea_Nombre', y='PAX', title="Número de Pasajeros por Aerolínea 🛩")
        st.plotly_chart(fig_bar_aerolinea)

        pasajeros_por_vuelo = filtered_data.groupby(['Fecha_UTC', 'Aerolinea_Nombre'])['PAX'].mean().reset_index()
        fig_bar_vuelo = px.bar(pasajeros_por_vuelo, x='Fecha_UTC', y='PAX', title="Promedio de Pasajeros por Vuelo 🚀", color='Aerolinea_Nombre')
        st.plotly_chart(fig_bar_vuelo)

        st.subheader("Detalles de Pasajeros por Vuelo 📋")
        st.dataframe(filtered_data[['Fecha_UTC', 'Hora_UTC', 'Aerolinea_Nombre', 'Aeronave', 'PAX']])

        st.sidebar.header("Filtros")
        aerolineas = st.sidebar.multiselect("Selecciona Aerolíneas", options=filtered_data['Aerolinea_Nombre'].unique(), default=filtered_data['Aerolinea_Nombre'].unique())
        fechas = st.sidebar.date_input("Selecciona un rango de fechas", [filtered_data['Fecha_UTC'].min(), filtered_data['Fecha_UTC'].max()])

        filtered_data = filtered_data[(filtered_data['Aerolinea_Nombre'].isin(aerolineas)) & (filtered_data['Fecha_UTC'].between(*fechas))]
        
        st.subheader("Datos Filtrados ✨")
        st.dataframe(filtered_data[['Fecha_UTC', 'Hora_UTC', 'Aerolinea_Nombre', 'Aeronave', 'PAX']])


    elif selection == "Mapas Interactivos":
        st.title("🗺Mapas de Aeropuertos")
        
        datos = cargar_datos()
        aeropuertos = datos['aeropuertos']
        
        m = folium.Map(location=[-34.61315, -58.37723], zoom_start=5, tiles='cartodb positron')
        
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
        
        folium_static(m)

    elif selection == "Acerca de":
        st.title("Realizado por:")
        st.write("-NICOL HINOJOSA YUCRA")
        st.write("-GISELA LEVITO")

if __name__ == "_main_":
    main()