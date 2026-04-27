from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import warnings
import time

warnings.filterwarnings('ignore')

@st.cache_data
def convierte_csv(df):
    return df.to_csv(index=False, sep='#').encode('utf-8')

def mensaje_exito():
    exito = st.success('Archivo descargado con éxito', icon='✅')
    time.sleep(8)
    exito.empty()

st.title('Datos en Bruto')

url = 'https://ahcamachod.github.io/productos'

response = requests.get(url=url)
soup=BeautifulSoup(response.content, 'html.parser')

datos = pd.read_json(soup.pre.contents[0])
datos['Fecha de Compra'] = pd.to_datetime(datos['Fecha de Compra'], format='%d/%m/%Y')

with st.expander('Columnas'):
    columnas = st.multiselect('Selecciona las columnas', list(datos.columns), list(datos.columns))

st.sidebar.title('Filtros')


with st.sidebar.expander('Nombre del Producto'):
    productos = st.multiselect('Selecciona los productos', datos['Producto'].unique(), datos['Producto'].unique())

with st.sidebar.expander('Categoria del Producto'):
    categoria = st.multiselect('Selecciona la Categoría', datos['Categoría del Producto'].unique(), datos['Categoría del Producto'].unique())


with st.sidebar.expander('Precio del Producto'):
    precio = st.slider('Selecciona los precio', 0,5000000, (0,5000000))

with st.sidebar.expander('Costo del Envío'):
    envio = st.slider('Selecciona el Costo del Envío', datos['Costo de envío'].min(),datos['Costo de envío'].max(), (datos['Costo de envío'].min(),datos['Costo de envío'].max()))


with st.sidebar.expander('Fecha de Compra'):
    fecha_compra = st.date_input('Selecciona la fecha', (datos['Fecha de Compra'].min(), datos['Fecha de Compra'].max()))

with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecciona al Vendedor', datos['Vendedor'].unique(), datos['Vendedor'].unique())

with st.sidebar.expander('Lugar de Compra'):
    lugar = st.multiselect('Selecciona rl Lugar de Compra', datos['Lugar de Compra'].unique(), datos['Lugar de Compra'].unique())

with st.sidebar.expander('Calificación'):
    calificacion = st.slider('Selecciona la Calificación', datos['Calificación'].min(),datos['Calificación'].max(), (datos['Calificación'].min(),datos['Calificación'].max()))

with st.sidebar.expander('Método de pago'):
    metodo = st.multiselect('Selecciona el Método de pago', datos['Método de pago'].unique(), datos['Método de pago'].unique())

with st.sidebar.expander('Cantidad de cuotas'):
    cuotas = st.slider('Selecciona la Cantidad de cuotas', datos['Cantidad de cuotas'].min(),datos['Cantidad de cuotas'].max(), (datos['Cantidad de cuotas'].min(),datos['Cantidad de cuotas'].max()))

query = """
Producto in @productos and \
`Categoría del Producto` in @categoria and \
@precio[0] <= `Precio` <= @precio[1] and \
@envio[0] <= `Costo de envío` <= @envio[1] and \
@fecha_compra[0] <= `Fecha de Compra` <=@fecha_compra[1] and \
Vendedor in @vendedor and \
`Lugar de Compra` in @lugar and \
@calificacion[0] <= `Calificación` <= @calificacion[1] and \
`Método de pago` in @metodo and \
@cuotas[0] <= `Cantidad de cuotas` <= @cuotas[1]
"""


datos_filtrados = datos.query(query)
datos_filtrados = datos_filtrados[columnas]


st.dataframe(datos_filtrados)

st.markdown(f'La tabla posee :blue[{datos_filtrados.shape[0]}] filas y :blue[{datos_filtrados.shape[1]}] columnas')

st.markdown('Escribe un nombre para el archivo')

col1, col2 = st.columns(2)

with col1:
    nombre_archivo = st.text_input('',label_visibility='collapsed',value='datos')
    nombre_archivo += '.csv'

with col2:
    st.download_button('Realiza la descarga de la tabla en formato csv', data=convierte_csv(datos_filtrados), file_name=nombre_archivo, mime='text/csv', on_click=mensaje_exito)



