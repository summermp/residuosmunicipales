import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="DISPOSICIÓN FINAL DE RRSS") # Nombre para configurar la pagina web
# st.write('##### DISPOSICIÓN FINAL DE RESIDUOS SÓLIDOS MUNICIPALES EN EL PERÚ') #Va a ser el titulo de la pagina
st.header('DISPOSICIÓN FINAL DE RESIDUOS SÓLIDOS MUNICIPALES EN EL PERÚ') #Va a ser el titulo de la pagina
st.subheader('¿Qué cantidad de RRSS generan las comunidades del país?') #Subtitulo

csv_file = '2a_Dataset_Disposicion_final_de_RRSS_V2.0.csv'

@st.cache_data
def load_data():
    df = pd.read_csv(csv_file,sep=';' , encoding='latin-1')
    return df

st.sidebar.image('https://www.precayetanovirtual.pe/moodle/pluginfile.php/1/theme_mb2nl/loadinglogo/1692369360/logo-cayetano.png', use_column_width=True)
# Menú con opciones
option = st.sidebar.selectbox('Seleccione una opción:', ('Acerca', 'Gráfico 1', 'Gráfico 2', 'Gráfico 3', 'Gráfico 4', 'Gráfico 5', 'Nosotros'))
df = load_data()
# Limpiar espacios en blanco en la columna DEPARTAMENTO
df['DEPARTAMENTO'] = df['DEPARTAMENTO'].str.strip()
def contar_residuos():
    df_personas = df.groupby(['DEPARTAMENTO'], as_index = False)['DISPOSICION_FINAL_ADECUADA'].count()
    df_personas2 = df_personas #la guardo en otro dataframe (NO ES NECESARIO)
    st.dataframe(df) #de esta forma nos va a mostrar el dataframe en Streamlit
    st.write(df_personas2) #este nos sirve cuando no tenemos dataframe sino object****
    #Crear un grafico de torta (pie chart)
    pie_chart = px.pie(df_personas2, #tomo el dataframe2
                    title = 'Residuos por departamento', #El titulo
                        values='DISPOSICION_FINAL_ADECUADA',
                    names='DEPARTAMENTO')
    st.plotly_chart(pie_chart) # de esta forma se va a mostrar el dataframe en Streamlit
#Crear una lista con los parametros de una columna
ciudad = df['REGION_NATURAL'].unique().tolist() # se crea una lista unica de la columna CIUDAD
calificacion = df['POB_TOTAL_INEI'].unique().tolist() # se crea una lista unica de la columna CALIFICACION
edad = df['DISPOSICION_FINAL_ADECUADA'].unique().tolist() # se crea una lista unica de la columna EDAD PERSONA ENCUESTADA

#Crear un slider de edad

#crear multiselectores
def residuos_region():
    ciudad_selector = st.multiselect('Región:', ciudad, default = ciudad)                              
    #Ahora necesito que esos selectores y slider me filtren la informacion
    mask = (df['REGION_NATURAL'].isin(ciudad_selector))&(df['POB_TOTAL_INEI'])
    numero_resultados = df[mask].shape[0] ##number of availables rows
    st.markdown(f'*Resultados Disponibles:{numero_resultados}*') ## sale como un titulo que dice cuantos resultados tiene para ese filtro
    # Aplicar el filtro y agrupar por REGION_NATURAL contando DISPOSICION_FINAL_ADECUADA
    df_agrupado = df[mask].groupby(by=['REGION_NATURAL']).count()[['DISPOSICION_FINAL_ADECUADA']]
    df_agrupado = df_agrupado.rename(columns={'DISPOSICION_FINAL_ADECUADA': 'Disposición de RRSS'})
    df_agrupado = df_agrupado.reset_index()
    # Crear un gráfico de barras con diferentes colores
    colors = px.colors.qualitative.Plotly  # Puedes usar cualquier secuencia de colores predefinida de Plotly
    bar_chart = px.bar(df_agrupado, 
                    x='REGION_NATURAL',
                    y='Disposición de RRSS',
                    text='Disposición de RRSS',
                    color='REGION_NATURAL',  # Usar REGION_NATURAL para asignar colores diferentes
                    color_discrete_sequence=colors,
                    template='plotly_white')
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(bar_chart)

def residuos_departamento():
    # Agrupar por DEPARTAMENTO y sumar DISPOSICION_FINAL_ADECUADA
    data_agrupada = df.groupby('DEPARTAMENTO')['DISPOSICION_FINAL_ADECUADA'].sum().reset_index()
    # Aplicación Streamlit
    st.markdown('**Gráfico Circular de Disposición Final Adecuada por Departamento**')
    # Crear el gráfico circular con Plotly
    fig = px.pie(data_agrupada, values='DISPOSICION_FINAL_ADECUADA', names='DEPARTAMENTO',title='Disposición Final Adecuada por Departamento')
    # Actualizar la configuración del texto dentro del gráfico
    fig.update_traces(textposition='inside', textinfo='percent+label')
    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

def residuos_departamento_anio():
    # Agrupar por DEPARTAMENTO y ANIO, y sumar DISPOSICION_FINAL_ADECUADA
    data_agrupada = df.groupby(['ANIO', 'DEPARTAMENTO'])['DISPOSICION_FINAL_ADECUADA'].sum().reset_index()

    # Definir una lista de colores oscuros y sólidos
    dark_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # Aplicación Streamlit
    st.markdown('**Gráfico de Líneas de Disposición Final Adecuada por Año y Departamento**')

   # Crear subplots por cada año
    anios = data_agrupada['ANIO'].unique()
    fig = make_subplots(rows=len(anios), cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=[f'Año {anio}' for anio in anios])

    # Añadir trazos para cada año
    for i, anio in enumerate(anios, start=1):
        data_anio = data_agrupada[data_agrupada['ANIO'] == anio]
        fig.add_trace(
            go.Scatter(
                x=data_anio['DEPARTAMENTO'], 
                y=data_anio['DISPOSICION_FINAL_ADECUADA'], 
                mode='lines+markers',
                name=f'Año {anio}',
                line=dict(color=dark_colors[i % len(dark_colors)])
            ),
            row=i, col=1
        )

        # Configurar etiquetas del eje x para cada subplot
        # fig.update_xaxes(title_text='Departamento', row=i, col=1)

    # Ajustes finales
    fig.update_layout(
        height=300*len(anios), 
        title_text='Disposición Final Adecuada por Año y Departamento',
        showlegend=True
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

def total_sitios_disposicion_final():
    # Título de la aplicación
    st.markdown('**Filtrar y Contar Sitios de Disposición Final Adecuada**')

    # Filtrar por DEPARTAMENTO
    departamento_seleccionado = st.selectbox('Seleccione el Departamento', df['DEPARTAMENTO'].unique())
    df_filtrado = df[df['DEPARTAMENTO'] == departamento_seleccionado]

    # Filtrar por PROVINCIA
    # provincia_seleccionada = st.selectbox('Seleccione la Provincia', df_filtrado['PROVINCIA'].unique())
    # df_filtrado = df_filtrado[df_filtrado['PROVINCIA'] == provincia_seleccionada]

    # Filtrar por DISTRITO
    # distrito_seleccionado = st.selectbox('Seleccione el Distrito', df_filtrado['DISTRITO'].unique())
    # df_filtrado = df_filtrado[df_filtrado['DISTRITO'] == distrito_seleccionado]

    # Asegurar que los valores de NOMBRE_SITIO_DISPOSICION_FINAL_ADECUADA sean únicos y sumar DISPOSICION_FINAL_ADECUADA
    suma_sitios = df_filtrado.groupby('NOMBRE_SITIO_DISPOSICION_FINAL_ADECUADA')['DISPOSICION_FINAL_ADECUADA'].sum().reset_index()

    # Crear el gráfico de barras con Plotly
    fig = px.bar(
        suma_sitios,
        x='NOMBRE_SITIO_DISPOSICION_FINAL_ADECUADA',
        y='DISPOSICION_FINAL_ADECUADA',
        color='NOMBRE_SITIO_DISPOSICION_FINAL_ADECUADA',
        title='Suma de Disposición Final Adecuada por Sitio'
    )

    # Mostrar el gráfico en Streamlit
    st.plotly_chart(fig)

    # Opcional: Mostrar el DataFrame filtrado
    st.write('DataFrame Filtrado:', df_filtrado)

def acerca():
    # st.markdown('**¿Qué cantidad de RRSS generan las comunidades del país?**') #Subtitulo
    # st.write("Dashboard sobre residuos municipales")
    st.image("https://fastly.picsum.photos/id/13/2500/1667.jpg?hmac=SoX9UoHhN8HyklRA4A3vcCWJMVtiBXUg0W4ljWTor7s")
    
def nosotros():
    st.write("Somos estudiantes de la UPCH de la carrera de ingenieria ambiental")
    st.image("https://fastly.picsum.photos/id/64/4326/2884.jpg?hmac=9_SzX666YRpR_fOyYStXpfSiJ_edO3ghlSRnH2w09Kg")
if option =='Acerca':
    acerca()
elif option == 'Gráfico 1':
    contar_residuos()
elif option == 'Gráfico 2':
    residuos_region()
elif option == 'Gráfico 3':
    residuos_departamento()
elif option == 'Gráfico 4':
    residuos_departamento_anio()
elif option == 'Gráfico 5':
    total_sitios_disposicion_final()
elif option == 'Nosotros':
    nosotros()
st.sidebar.markdown("""
**Integrantes:**
- Item 1
- Item 2
- Item 3
- Item 4
""")

st.sidebar.write("Ingenieria ambiental - 2024")