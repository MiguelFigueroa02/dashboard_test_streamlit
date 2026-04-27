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
    st.set_page_config(
        page_title="Lucho",
        page_icon='https://www.circuloamigosdelafilatelia.org/wp-content/uploads/2021/03/mexico-flag-round-icon-256.png',
        # layout='wide',
        initial_sidebar_state='expanded',
    )

    st.title('Dashboard de prueba 👀')

    url = 'https://ahcamachod.github.io/productos'

    response = requests.get(url=url)
    soup=BeautifulSoup(response.content, 'html.parser')

    datos = pd.read_json(soup.pre.contents[0])
    datos['Fecha de Compra'] = pd.to_datetime(datos['Fecha de Compra'], format='%d/%m/%Y')

    ## Filtrando por región y por año

    regiones_dict = {'Bogotá': 'Andina', 
                    'Medellín': 'Andina', 
                    'Cali': 'Pacífica',
                    'Pereira': 'Andina', 
                    'Barranquilla': 'Caribe', 
                    'Cartagena': 'Caribe',
                    'Cúcuta': 'Andina', 
                    'Bucaramanga': 'Andina', 
                    'Riohacha': 'Caribe', 
                    'Santa Marta': 'Caribe', 
                    'Leticia': 'Amazónica', 
                    'Pasto': 'Andina', 
                    'Manizales': 'Andina',
                    'Neiva': 'Andina', 
                    'Villavicencio': 'Orinoquía', 
                    'Armenia': 'Andina',
                    'Soacha': 'Andina', 
                    'Valledupar': 'Caribe', 
                    'Inírida': 'Amazónica'
                }
    
    datos['Region'] = datos['Lugar de Compra'].map(regiones_dict)
    datos['Año'] = datos['Fecha de Compra'].dt.year

    ## Sidebar para la interacción con la api
    regiones = ['Colombia', 'Caribe', 'Andina', 'Pacífica', 'Orinoquía', 'Amazónica']

    st.sidebar.title('Filtro')
    region = st.sidebar.selectbox('Región', regiones)
    if region == 'Colombia':
        datos = datos.loc[datos['Region'] != 'Colombia']
    else:
        datos = datos.loc[datos['Region'] == region]

    todos_anos = st.sidebar.checkbox('Datos todo el periodo', value=True)
    if todos_anos:
        datos= datos
    else:
        ano = st.sidebar.slider('Año',2020,2023)
        datos=datos.loc[datos['Año'] == ano]

    filtro_vendedores = st.sidebar.multiselect('Vendedores', datos.Vendedor.unique())
    if filtro_vendedores:
        datos = datos[datos['Vendedor'].isin(filtro_vendedores)]

    ## Creación de features

    fact_ciudades= datos.groupby('Lugar de Compra')[['Precio']].sum()

    fact_ciudades= datos.drop_duplicates(subset='Lugar de Compra')[['Lugar de Compra','lat','lon']].merge(fact_ciudades, left_on='Lugar de Compra', right_index=True).sort_values('Precio', ascending=False)

    facturacion_mensual = datos.set_index('Fecha de Compra').groupby(pd.Grouper(freq='ME'))['Precio'].sum().reset_index()

    facturacion_mensual['Año'] = facturacion_mensual['Fecha de Compra'].dt.year
    facturacion_mensual['Mes'] = facturacion_mensual['Fecha de Compra'].dt.month_name()

    facturacion_cat= datos.groupby('Categoría del Producto')[['Precio']].sum().sort_values('Precio',ascending=False)

    vendedores = pd.DataFrame(datos.groupby('Vendedor')['Precio'].agg(['sum','count']))

    cantidad_ciudades= datos.groupby('Lugar de Compra')[['Precio']].count()
    cantidad_ciudades= datos.drop_duplicates(subset='Lugar de Compra')[['Lugar de Compra','lat','lon']].merge(cantidad_ciudades, left_on='Lugar de Compra', right_index=True).sort_values('Precio', ascending=False)

    cantidad_mensual = datos.set_index('Fecha de Compra').groupby(pd.Grouper(freq='ME'))['Precio'].count().reset_index()
    cantidad_mensual['Año'] = cantidad_mensual['Fecha de Compra'].dt.year
    cantidad_mensual['Mes'] = cantidad_mensual['Fecha de Compra'].dt.month_name()

    cantidad_categoria = datos.groupby('Categoría del Producto')[['Precio']].count().sort_values('Precio',ascending=False)


    ## Creación de gráficos

    fig_fact=px.scatter_geo(fact_ciudades, lat='lat', lon='lon', scope='south america', size='Precio', template='seaborn', hover_name='Lugar de Compra',hover_data={'lat':False,'lon':False}, title='Facturación por ciudad')

    fig_fact.update_geos(fitbounds="locations")

    fig_facturacion_mensual = px.line(facturacion_mensual, x='Mes', y='Precio',markers=True,range_y=(0,facturacion_mensual.max()),color='Año',line_dash='Año',title='Facturación mensual')

    fig_facturacion_mensual.update_layout(yaxis_title='Facturación')

    fig_facturacion_ciudades = px.bar(fact_ciudades.head(), x='Lugar de Compra', y='Precio',text_auto=True, title='Top cuidades (Facturación)')

    fig_facturacion_ciudades.update_layout(yaxis_title='Facturación')

    fig_facturacion_cat = px.bar(facturacion_cat, text_auto=True, title='Facturación por categoría')
    fig_facturacion_cat.update_layout(yaxis_title='Facturación')

    fig_cant = px.scatter_geo(cantidad_ciudades, lat='lat', lon='lon', scope='south america', size='Precio', template='seaborn', hover_name='Lugar de Compra',hover_data={'lat':False,'lon':False}, title='Cantidad de ventas por estado')
    fig_cant.update_geos(fitbounds="locations")

    fig_cantidad_ciudades = px.bar(cantidad_ciudades.head(), x='Lugar de Compra', y='Precio',text_auto=True, title='Top cuidades (Cantidad)')
    fig_cantidad_ciudades.update_layout(yaxis_title='Cantidad')

    fig_cant_mensual = px.line(cantidad_mensual, x='Mes', y='Precio',markers=True,range_y=(0,facturacion_mensual.max()),color='Año',line_dash='Año',title='Cantidad de ventas mensual')
    fig_cant_mensual.update_layout(yaxis_title='Cantidad')

    fig_cantidad_cat = px.bar(cantidad_categoria, text_auto=True, title='Cantidad de ventas por categoría')
    fig_cantidad_cat.update_layout(yaxis_title='Cantidad de ventas')

    tab1, tab2, tab3 = st.tabs(['Facturación','Cantidad de ventas','Vendedores'])

    with tab1:
        col1,col2 = st.columns(2)

        with col1:
            st.metric('Facturacion',formato_numero(datos['Precio'].sum(),'COP'))
            st.plotly_chart(fig_fact, width='stretch')
            st.plotly_chart(fig_facturacion_ciudades, width='stretch')
            
        with col2:
            st.metric('Cantidad de ventas',formato_numero(datos.shape[0]))
            st.plotly_chart(fig_facturacion_mensual,width='stretch')
            st.plotly_chart(fig_facturacion_cat, width='stretch')

    with tab2:
        col1,col2 = st.columns(2)

        with col1:
            st.metric('Ingresos',formato_numero(datos['Precio'].sum(),'COP'))
            st.plotly_chart(fig_cant, width='stretch')
            st.plotly_chart(fig_cantidad_ciudades, width='stretch')
            
        with col2:
            st.metric('Cantidad de ventas',formato_numero(datos.shape[0]))
            st.plotly_chart(fig_cant_mensual,width='stretch')
            st.plotly_chart(fig_cantidad_cat, width='stretch')

    with tab3:
        ct_vendedores= st.number_input('Cantidad de vendedores', 2,10,5)
        col1,col2 = st.columns(2)

        with col1:
            st.metric('Facturacion',formato_numero(datos['Precio'].sum(),'COP'))
            fig_facturacion_vendedores=px.bar(vendedores[['sum']].sort_values('sum').head(ct_vendedores),x='sum',y=vendedores[['sum']].sort_values('sum').head(ct_vendedores).index,text_auto=True, title=f'Top {ct_vendedores} vendedores (Facturación)')
            st.plotly_chart(fig_facturacion_vendedores)
                        
        with col2:
            st.metric('Cantidad de ventas',formato_numero(datos.shape[0]))
            fig_cantidad_ventas=px.bar(vendedores[['count']].sort_values('count').head(ct_vendedores),x='count',y=vendedores[['count']].sort_values('count').head(ct_vendedores).index,text_auto=True, title=f'Top {ct_vendedores} vendedores (cantidad de ventas)')
            st.plotly_chart(fig_cantidad_ventas)

    
    # st.dataframe(datos)


if __name__=='__main__':
    main()
