#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

import re

st.set_page_config (page_title = 'Visão Entregadores', page_icon ='🛵' , layout = 'wide')

#======================================================
#Funções
#======================================================

def top_delivers (df, top_asc):
    df1 = (df.loc[:, ['Delivery_person_ID','City','Time_taken(min)']]
             .groupby(['City','Delivery_person_ID'])
             .mean()
             .sort_values(['City','Time_taken(min)'], ascending = top_asc)
             .reset_index())
    
    df_aux01 = df1.loc[df1['City'] == 'Metropolitan' , :].head(10)
    df_aux02 = df1.loc[df1['City'] == 'Urban' , :].head(10)
    df_aux03 = df1.loc[df1['City'] == 'Semi_Urban' , :].head(10)

    df2 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    return df2

def clean_code(df):
    """ Essa funcao tem a resposabilidade de limpar o dataframe
    
        Tipo de limpeza:
        1. Remocao dos dados NaN
        2. Mudança dos tipos da colunas de dados
        3. Remocao dos espacos das variaveis de texto
        4. Formatacao da coluna de datas
        5. Limpeza da coluna tempo (remocao do txto da variavel numerica)
        
        Input: Dataframe
        Output: Dataframe
        """

    # 1. Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['Road_traffic_density'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['City'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['Festival'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    # 2. Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    # 3. Convertendo a coluna Ratings de texto/categoria/strings para numeros decimais (float)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # 4. Convertendo a coluna order_date de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # 5. Convertendo multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_selecionadas, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    # 6. Removendo espaços dentro de stings/texto/object

    df.loc[:,"ID"] = df.loc[:,"ID"].str.strip()
    df.loc[:,"Road_traffic_density"] = df.loc[:,"Road_traffic_density"].str.strip()
    df.loc[:,"Type_of_order"] = df.loc[:,"Type_of_order"].str.strip()
    df.loc[:,"Type_of_vehicle"] = df.loc[:,"Type_of_vehicle"].str.strip()
    df.loc[:,"City"] = df.loc[:,"City"].str.strip()
    df.loc[:,"Festival"] = df.loc[:,"Festival"].str.strip()

    # 7. Comando para remover o texto de números
    df['Time_taken(min)'] = df['Time_taken(min)'].apply ( lambda x: x.split ('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    
    return (df)

#-------------------- Inicio da estrutura lógica do codigo ------------------------------
#-------------------------
#import dataset
#-------------------------
df = pd.read_csv ('train.csv')

#-------------------------
#Limpando dados
#-------------------------
df = clean_code (df)

# ===================================
# Barra lateral
# ===================================

st.header ('Marketplace - Visão Entregadores')
#image_path = 'pic.jpg'
image = Image.open ('pic.jpg')
st.sidebar.image (image, width = 120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown ('## Selecione uma data limite')

date_slider = st.sidebar.slider(
       'Selecione o intervalo de tempo',
        value = pd.datetime(2022, 4, 6),
        min_value = pd. datetime(2022, 2, 11),
        max_value = pd. datetime(2022, 4, 6),
        format = 'DD/MM/YYYY' )

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect (
    'Quais as condições de trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default =  ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Porwered by Afonso Dala')

# Filtro de Data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtro de Trasito

linhas_selecionadas =  df['Road_traffic_density'].isin (traffic_options)
df = df.loc[linhas_selecionadas, :]

# ===================================
# Layout no Streamlit
# ===================================


tab1, tab2, tab3 = st.tabs (['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.title (' Overall Metrics' )
        
        col1, col2, col3, col4 = st.columns( 4, gap='large')
        with col1:
            #A maior idade dos entregadores
            maior_idade = df.loc[:,'Delivery_person_Age'].max()
            col1.metric ('Maior Idade', maior_idade)
            
        with col2:
            #A menor idade dos entregadores
            menor_idade = df.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            #A melhor condicao do veiculo
            melhor_veiculo = df.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condicao', melhor_veiculo)
            
        with col4:
            #A pior condicao do veiculo
            pior_veiculo = df.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior condicao', pior_veiculo)
            
    
    with st.container():
        st.markdown("""---""")
        st.title('Avaliacoes')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown ('##### Avaliacoes medias por entregador')
            df_avg_ratings_per_deliver = (df.loc[:, ['Delivery_person_Ratings','Delivery_person_ID']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index())
            st.dataframe( df_avg_ratings_per_deliver)

        
        with col2:
            #
            st.markdown ('##### Avaliacao media por transito')
            df_avg_std_rating_per_traffic = (  df.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                                                 .groupby('Road_traffic_density')
                                                 .agg({'Delivery_person_Ratings':['mean', 'std']})  )

            #mudança de colunas
            df_avg_std_rating_per_traffic.columns = ['delivery_mean', 'delivery_std']

            #reset do index

            df_avg_std_rating_per_traffic = df_avg_std_rating_per_traffic.reset_index()
            st.dataframe(df_avg_std_rating_per_traffic)
            
            st.markdown ('##### Avaliacao media por clima')
            df_avg_std_rating_per_weather = (df.loc[:, ['Delivery_person_Ratings','Weatherconditions']]
                                             .groupby('Weatherconditions')
                                             .agg({'Delivery_person_Ratings':['mean', 'std']}) )

            #mudança de colunas
            df_avg_std_rating_per_weather.columns = ['delivery_mean', 'delivery_std']

            #reset do index

            df_avg_std_rating_per_weather = df_avg_std_rating_per_weather.reset_index()
            st.dataframe(df_avg_std_rating_per_weather)

    with st.container():
        st.markdown ("""---""")
        st.title ('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            df2 = top_delivers (df, top_asc=True)
            st.markdown ('##### Top 10 entregadores mais rapidos')
            st.dataframe(df2)
            
        with col2:
            df2 = top_delivers (df, top_asc=False)
            st.markdown ('##### Top 10 entregadores mais lentos')
            st.dataframe(df2)





