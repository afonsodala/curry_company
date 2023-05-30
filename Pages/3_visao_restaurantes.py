#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

#bibliotecas necessárias
import pandas as pd
import streamlit as st
import numpy as np
from PIL import Image
import folium
from streamlit_folium import folium_static

import re

st.set_page_config (page_title = 'Visão Restaurante', page_icon ='🥗' , layout = 'wide')

#======================================================
#Funções
#======================================================

def distance(df):
    cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

    df['distance'] = df.loc[:, cols].apply( lambda x:
                            haversine(  (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis = 1 )

    avg_distance = np.round(df['distance'].mean(), 2)
    return avg_distance

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

st.header ('Marketplace - Visão Restaurantes')
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


tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6, gap='large')
        
        with col1:
            st.markdown('##### Col 1')
            delivery_unique = len( df.loc[:, 'Delivery_person_ID'].unique() )
            col1.metric('Entregadores unicos', delivery_unique)
            
        with col2:
            
            avg_distance = distance(df)
            col2.metric('A distancia media das entregas', avg_distance)
            
        with col3:
            df_aux = (df.loc[:, ['Festival', 'Time_taken(min)']]
                        .groupby('Festival')
                        .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            df_aux = df_aux.loc [df_aux['Festival'] == 'Yes', 'avg_time']
            col3.metric('Tempo medio de entrega c/ Festival', df_aux)

    
            
        with col4:
            df_aux = (df.loc[:, ['Festival', 'Time_taken(min)']]
                        .groupby('Festival')
                        .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            df_aux = df_aux.loc [df_aux['Festival'] == 'Yes', 'std_time']
            col4.metric('Desvio padrão de entrega c/ Festival', df_aux)
            
        with col5:
            df_aux = (df.loc[:, ['Festival', 'Time_taken(min)']]
                        .groupby('Festival')
                        .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            df_aux = df_aux.loc [df_aux['Festival'] == 'No', 'avg_time']
            col3.metric('Tempo medio s/ Festival', df_aux)
            
        with col6:
            df_aux = (df.loc[:, ['Festival', 'Time_taken(min)']]
                        .groupby('Festival')
                        .agg({'Time_taken(min)': ['mean', 'std']}))

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            
            df_aux = df_aux.loc [df_aux['Festival'] == 'No', 'std_time']
            col4.metric('Std entrega s/ Festival', df_aux)
        
    with st.container():
        st.markdown("""---""")
        st.markdown('##### Col 1')
        cols = ['City', 'Time_taken(min)']
        df_aux = df.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})

        df_aux.columns = ['avg_time', 'std_time']

        df_aux = df_aux.reset_index()

        fig = go.Figure()
        fig.add_trace( go.Bar ( name = 'Control',
                                x = df_aux['City'],
                                y = df_aux['avg_time' ],
                                error_y = dict (type = 'data', array = df_aux['std_time'])))
        fig.update_layout (barmode = 'group')
        st.plotly_chart(fig)
        
        
    with st.container():
        st.markdown("""---""")
        st.title('C3')
        
        col1, col2 = st.columns(2)
        
        with col1:
            
            st.title('Tempo médio de entrega por cidade')
            cols =['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']

            df['diatance'] = (df.loc[: , cols].apply(lambda x:
                       haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                  (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis = 1 ))

            avg_distance = df.loc[:, ['City','distance']].groupby('City').mean().reset_index()
            fig = go.Figure (data =[go.Pie (labels = avg_distance ['City'], values = avg_distance['distance'], pull = [0, 0.1, 0 ])])
            st.plotly_chart(fig)
        
            
            
        with col2:
            ## O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego
            st.markdown('##### Col 1')
            cols = ['City', 'Time_taken(min)','Road_traffic_density']

            df_aux = df.loc[:, cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path = ['City', 'Road_traffic_density'], values = 'avg_time', 
                                color = 'std_time', color_continuous_scale= 'RdBu', 
                                color_continuous_midpoint= np.average(df_aux['std_time']))
            st.plotly_chart(fig)
        
    with st.container():
        ## O tempo médio e o desvio padrão de entrega por cidade e tipo de tráfego
        st.markdown("""---""")
        st.title('C4')
        cols = ['City', 'Time_taken(min)','Type_of_order']

        df_aux = df.loc[:, cols].groupby(['City','Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
        df_aux.columns = ['avg_time', 'std_time']

        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)
        