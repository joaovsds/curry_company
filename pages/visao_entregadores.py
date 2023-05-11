 #importando bibliotecas
import pandas as pd
import numpy as np
import plotly.express as px
import re
import folium
import streamlit as st
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title="Visão Entregadores", page_icon=":truck:", layout ='wide' )

#===================================================#
#     Funções
#===================================================#
def top_delivers (df,top_asc):
    """
        Esta função vai retornar os 10 entregadores mais rapidos ou os 10 
        entregadores mais lentos de cada cidade.
        
        Parâmetros:
            1- df: dataframe com os dados para o calculo
            2- top_asc: True para selecionar os entregadores rapidos e False para 
            os mais lentos.
            
        Input: dataframe, top_asc = True ou top_asc = False
        output: Dataframe
    """
    df2 = (df.loc[:,['Time_taken(min)','Delivery_person_ID','City']]
             .groupby(['City','Delivery_person_ID'])
             .max()
             .sort_values(['City','Time_taken(min)'],ascending = top_asc)
             .reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban',:].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban',:].head(10)

    df3 = pd.concat ([df_aux01,df_aux02,df_aux03]).reset_index(drop = True)
    return df3

def clean_code(df):
    """Esta função tem a responsabilidade de limpar o dataframe
    
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

        col1,col2,col3,col4 = st.columns(4, gap = 'large')
        with col1:
            #maior idade dos entregadores
            maior_idade = df.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)

        with col2:
            #menor idade dos entregadores
            menor_idade = df.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        
        with col3:
            #melhor condição de veiculo
            melhor_condicao = df.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição de veiculo', melhor_condicao)

        with col4:
            #pior condição de veiculo
            pior_condicao = df.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condição de veiculo', pior_condicao)
    
    with st.container():
        st.markdown('''---''')
        st.title('Ratings')
        
        col1,col2 = st.columns(2)
        with col1:
            st.markdown('#### Avaliação Média por Entregador')
            df_avg = (df.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
               .groupby('Delivery_person_ID')
               .mean()
               .reset_index())
            st.dataframe(df_avg)    
    
        with col2:
            st.markdown('### Avaliação Média por Trânsito')
            df_agg = (df.loc[:,['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density')
                        .agg({'Delivery_person_Ratings':['mean','std']}).reset_index())
            #mudando as colunuas
            df_agg.columns = ['Road_traffic_density','Delivery_mean', 'Delivery_std']
            st.dataframe(df_agg)    

            
            st.markdown('### Avaliação Média por Clima')
            df_aggc = (df.loc[:,['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions')
                        .agg({'Delivery_person_Ratings':['mean','std']}).reset_index())
            #mudando as colunuas
            df_aggc.columns = ['Weatherconditions','Delivery_mean', 'Delivery_std']
            st.dataframe(df_aggc)   

    with st.container():
        st.markdown('''---''')
        st.title('Delivery Speed')
        
        col1,col2 = st.columns(2)
        
        with col1:
            st.markdown('### Top Entregadores Mais Rapidos')
            df3 = top_delivers (df, top_asc = True)
            st.dataframe(df3)

        with col2:
            st.markdown('### Top Entregadores Mais Lentos')
            df3 = top_delivers (df, top_asc = False)
            st.dataframe(df3)

