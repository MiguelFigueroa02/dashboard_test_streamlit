from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
import warnings

warnings.filterwarnings('ignore')

## Funciones
def formato_numero(valor, prefijo=""):
    for unidad in ['','mil']:
        if valor < 1000:
            return f'{prefijo}{valor:.2f}{unidad}'
        valor /= 1000
    return f'{prefijo}{valor:.2f} millones'

def main():
    st.title('Dashboard de prueba 👀')

    url = 'https://ahcamachod.github.io/productos'

    response = requests.get(url=url)
    soup=BeautifulSoup(response.content, 'html.parser')

    datos = pd.read_json(soup.pre.contents[0])

    col1,col2 = st.columns(2)

    with col1:
        st.metric('Facturacion',formato_numero(datos['Precio'].sum(),'COP'))
        
    with col2:
        st.metric('Cantidad de ventas',formato_numero(datos.shape[0]))

    st.dataframe(datos)


if __name__=='__main__':
    main()