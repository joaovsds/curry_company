# importando bibliotecas
import pandas as pd
import numpy as np
import plotly.express as px
import re
import folium
import streamlit as st
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title="Visão Empresa", page_icon="📈", layout ='wide' )

#===================================================#
#     Funções
#===================================================#
def contry_maps (df):
    """
        Esta função vai retornar um mapa com a localização de cada cidade por tipo de 
        tráfego.

        Input: dataframe 
        output: mapa
    """
    data_plot = (df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                   .groupby( ['City','Road_traffic_density'])
                   .median()
                   .reset_index())

    # Desenhar o mapa
    map = folium.Map()

    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
             location_info['Delivery_location_longitude']],
             popup=location_info[['City', 'Road_traffic_density']] ).add_to( map)
    folium_static( map, width = 1024, height = 600 )
    
def order_share_by_week (df):
    """
        Esta função vai retornar um grafico de linhas com a quantidades
        de pedidos por entregador por semana.

        Input: dataframe 
        output: grafico de linhas
    """
    df_aux1 = (df.loc[:, ['ID', 'week_of_year']]
                 .groupby( 'week_of_year' )
                 .count()
                 .reset_index())
    df_aux2 = (df.loc[:, ['Delivery_person_ID', 'week_of_year']]
                 .groupby( 'week_of_year')
                 .nunique()
                 .reset_index())

    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig

def ordern_by_week (df):
    """
        Esta função vai retornar um grafico de linhas com a quantidades
        de pedidos por semana.

        Input: dataframe 
        output: grafico de linhas
    """
    # criar coluna da semana
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')
    df_aux = (df.loc[:,['ID', 'week_of_year']]
                .groupby('week_of_year')
                .count()
                .reset_index())
    #grafico
    fig = px.line(df_aux, x= 'week_of_year', y = 'ID')
    return fig

def traffic_order_city (df):
    """
        Esta função retorna um grafico de bolhas comparando o volume de pedidos
        por cidade e tipo de tráfego.
        
        Input: dataframe com os dados para realizar os calculos
        Output: grafico de bolhas
    """
    df_aux = (df.loc[:,['ID', 'City','Road_traffic_density']]
                .groupby(['Road_traffic_density','City'])
                .count()
                .reset_index())
    #grafico
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size ='ID', color = 'City')
    return fig

def traffic_order_share(df):
    """
       Esta função vai retornar um grafico de pizza com a distribuição dos
       pedidos por tipo de tráfego.
       
       Input: datafram com os dados para o calculo
       Output: grafico de pizza.
    """
    df_aux = (df.loc[:,['ID', 'Road_traffic_density']]
                .groupby('Road_traffic_density')
                .count()
                .reset_index())
    
    df_aux['perc_ID'] = 100*(df_aux['ID'] / df_aux['ID'].sum())
    
    #grafico
    fig = px.pie(df_aux, values = 'perc_ID', names = 'Road_traffic_density')
    return fig
            
def order_metric(df):
    """
        Esta função vai retornar um grafico de barras com a quantidades
        de pedidos por dia.
        
        Input: dataframe 
        output: grafico de barras
    """
    df_aux = (df.loc[:,['ID', 'Order_Date']]
                .groupby('Order_Date')
                .count()
                .reset_index())
    #grafico
    fig = px.bar(df_aux, x = 'Order_Date', y ='ID')
    return fig
        
def clean_code(df):
    """Esta função tem a responsabilidade de limapra o dataframe
    
        Tipos de limpeza:
        1. Remoção de dados do NaN
        2. Conversão de numeros e strings
        3. Mudança do tipo de coluna de dados
        4. Remoção dos espaços das variáveis
        5. Formatação da colunas de datas
        6.Limpeza da coluna tempo ( remoção do texto da variavel )
        
        Input: Dataframe
        Output: Dataframe
    """
    
    # Remover spaco da string o comando strip excluir espaços vazios no início
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()

    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )

    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # excluindo linhas fazias da coluna Estival
    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :]

    # Conversao de texto/categoria/string para numeros inteiros

    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/strings para numeros decimais

    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data

    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # conversao de texto para numeros inteiros (int)

    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    # Comando para remover o texto de números e convertendo numeros

    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split ( '(min)' ) [1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)   

    # Excluir as linhas com condicoes climaticas dos entregadores vazia
    # ( Conceitos de seleção condicional )

    linhas_vazias = df['Weatherconditions'] != 'conditions NaN'
    df = df.loc[linhas_vazias, :]

    # Excluir as linhas com condicoes trafegas dos entregadores vazia
    # ( Conceitos de seleção condicional )

    linhas_vazias = df['Road_traffic_density'] != 'NaN'
    df = df.loc[linhas_vazias, :]

    # Excluir as linhas com cidades vazias
    # ( Conceitos de seleção condicional )

    linhas_vazias = df['City'] != 'NaN'
    df = df.loc[linhas_vazias, :]
    
    return df
# -------------------------------- Inicio da Estrutura lógica do código-----------------------------------
# ------------------------
# Import dataset
# ------------------------
df1 = pd.read_csv('train.csv')

# ------------------------
# Limpando dados
# ------------------------
df = clean_code( df1 )

#===================================================#
#     Barra lateral
#===================================================#
st.header('Marketplace - Visão Cliente')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image,width = 160)

 # criação de uma aba na esquerda
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown('''---''') 

st.sidebar.markdown('## Selecione uma data limite')


date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11), # inicio do filtro
    max_value = pd.datetime(2022, 4, 6), # final do filtro
    format='DD-MM-YYYY')

st.sidebar.markdown('''---''') 

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High', 'Jam'],
    default = ['Low','Medium','High', 'Jam'])

st.sidebar.markdown('''---''') 

# adicionando o dataframe no filtro das datas da barra lateral
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas,:]

# filtro de transito da barra lateral
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas,:]

#===================================================#
#     layout no streamlit
#===================================================#

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        #order matric 
        st.markdown('# Orders by Day')
        fig = order_metric (df)
        #exibir o grafico
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        col1,col2 = st.columns(2)
        
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share (df)     
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city (df)
            st.plotly_chart(fig, use_container_width = True)
            
with tab2:
    with st.container():        
        st.markdown('# Orders By Week') 
        fig = ordern_by_week (df)
        st.plotly_chart(fig, use_container_width = True) 
        
    with st.container():        
        st.markdown('# Orders Share By Week') 
        fig = order_share_by_week (df)
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
        st.markdown('# Country Maps') 
        contry_maps (df)

        
