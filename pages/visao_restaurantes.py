#importando bibliotecas
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import re
import folium
import streamlit as st
import matplotlib.pyplot as plt

from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title="Visão Restaurantes", page_icon="🍽️", layout ='wide')

#===================================================#
#     Funções
#===================================================#
def avg_std_time_on_traffic(df):
    """ 
        Esta função retorna um grafico onde mostra a media e o desvio padrão do tempo de
        entrega de cada condição de tráfego em cada uma das cidades
    """
    df_aux = (df.loc[:,['City','Time_taken(min)','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .agg({'Time_taken(min)': ['mean','std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', 
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph(df):
    """
        Esta função vai retornar um grafico de barras onde ele mostra a media e o
        desvio padrão do tempo de entregas de cada cidade.
    
    """
    df_aux = (df.loc[:,['City','Time_taken(min)']]
                .groupby(['City'])
                .agg({'Time_taken(min)': ['mean','std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar(name = 'Control', x = df_aux['City'], y = df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time(df,op1,op2):
    """
        Esta função calcula o tempo medio e o desvio padrão do tempo de entrega.
        parâmetros:
            Input:
                - df: dataframe com os dados para o cálculo.
                - op1:
                    0 - para selecionar so dia que não tiveram festival.
                    1 - para selecionar so dia que tiveram festival.
                - op2:
                    1 - para calcular o tempo médio.
                    2 - para calcular o desvio padrão do tempo.
             Output = numero que foi calculado         
    """
    df_aux = (df.loc[:,['Festival','Time_taken(min)']]
                .groupby('Festival')
                .agg({'Time_taken(min)': ['mean','std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    aux = np.round(df_aux.iloc[op1,op2],2)
    return aux
    
def distance(df,fig):
    """
        Esta funçao possui dois parâmetros:
        1- dataframe com os dados para o calculo
        2-fig onde possui duas condições:
            caso o fig for False, a função vai retornar a distancia media dos restaurantes até o local de entraga
            caso o fig for True, a função vai retornar um grafico onde mostra a distancia media dos restaurantes até o local de entrega
            de cada cidade.
    """
    if fig == False:
        cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
        df['distance'] = (df.loc[:, cols]
                            .apply(lambda x:haversine((x ['Restaurant_latitude'], x['Restaurant_longitude']),
                                                      (x ['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis = 1 ))
        avg_distance = np.round(df['distance'].mean(),2)
        return avg_distance
    else:
        cols = ['Restaurant_latitude','Restaurant_longitude',
                'Delivery_location_latitude','Delivery_location_longitude']
        df['distance'] = df.loc[:, cols].apply( lambda x:
                                               haversine ( (x ['Restaurant_latitude'], x['Restaurant_longitude'] ),
                                                          (x ['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis = 1 )
        avg_distance = (df.loc[:,['City','distance']]
                          .groupby('City')
                          .mean()
                          .reset_index())
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'],values=avg_distance['distance'], pull= [0,0.1,0])])
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
st.header('Marketplace - Visão Entregadores')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image,width = 160)

 # criação de uma aba na esquerda
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in town')
st.sidebar.markdown('''---''') 

st.sidebar.markdown('## Selecione uma data limite')

#===================================================#
#     Filtro de datas
#===================================================#
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022, 2, 11), # inicio do filtro
    max_value = pd.datetime(2022, 4, 6), # final do filtro
    format='DD-MM-YYYY')

st.sidebar.markdown('''---''') 
st.sidebar.markdown('## Selecione o tipo de condição')
#===================================================#
#     Filtro de transito
#===================================================#

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High', 'Jam'],
    default = ['Low','Medium','High', 'Jam'])

#===================================================#
#     Filtro de clima
#===================================================#
Weatherconditions = st.sidebar.multiselect(
    'Quais as condições climáticas',
    ['conditions Cloudy','conditions Fog','conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'],
    default = ['conditions Cloudy','conditions Fog','conditions Sandstorms', 'conditions Stormy','conditions Sunny','conditions Windy'])


# adicionando o dataframe no filtro das datas da barra lateral
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas,:]

# filtro de transito da barra lateral
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas,:]

# filtro de transito da barra lateral
linhas_selecionadas = df['Weatherconditions'].isin(Weatherconditions)
df = df.loc[linhas_selecionadas,:]

#===================================================#
#     layout no streamlit
#===================================================#

tab1,tab2,tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            unq = len(df.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores Cadastrados', unq)

        with col2:
            avg_distance = distance (df,fig = False)
            col2.metric('Distancia Média das Entregas',avg_distance)

        with col3:
            aux = avg_std_time (df,1,1)
            col3.metric('Tempo Médio das Entregas c/ Festival', aux)
            
        with col4:
            aux = avg_std_time (df,1,2)
            col4.metric('Desvio Padrão das Entregas c/ festival', aux)

        with col5:
            aux = avg_std_time (df,0,1)
            col5.metric('Tempo Médio das Entregas s/ Festival', aux)
            
        with col6:
            aux = avg_std_time (df,0,2)
            col6.metric('Desvio Padrão das Entregas s/ festival', aux)

    with st.container():
        st.markdown('''---''')
        st.markdown('## Tempo Médio e Desvio Padrão das Entregas')

        col1, col2 = st.columns([3,3])
        
        with col1:
            fig = avg_std_time_graph(df)
            st.plotly_chart(fig, use_container_width = True)
    
        with col2:
            df_aux = (df.loc[:,['City','Time_taken(min)','Type_of_order']]
                        .groupby(['City','Type_of_order'])
                        .agg({'Time_taken(min)': ['mean','std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux.reset_index()
            
            st.dataframe(df_aux)
            
    with st.container():
        st.markdown('''---''')
        st.markdown('## Distribuição do Tempo')
        
        col1,col2 = st.columns(2)    
        with col1:
            fig = distance(df, fig=True)
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            fig = avg_std_time_on_traffic(df)
            #utilizando use_container para que os graficos fiquem bem posicionados lada a lado                 
            st.plotly_chart(fig, use_container_width = True)
