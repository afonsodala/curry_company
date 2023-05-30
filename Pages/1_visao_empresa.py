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

st.set_page_config (page_title = 'Visão Empresa', page_icon ='📈' , layout = 'wide')

#======================================================
#Funções
#======================================================
def order_metric(df):
    #seleção de colunas
    cols = ['ID','Order_Date']
    #seleção de linhas
    df_aux = df.loc[:,cols].groupby('Order_Date').count().reset_index()
    fig = px.bar (df_aux, x = 'Order_Date', y = 'ID')
            
    return fig

def traffic_order_share(df):
    #Distribuição de pedidos por tipo de tráfego
    df_aux =  (df.loc[:, ['ID', 'Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index())
    df_aux =  df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    #criar coluna de semana
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()

    fig = px.pie(df_aux , values = 'entregas_perc', names = 'Road_traffic_density')
    return fig

def traffic_order_city (df):
            
    df_aux = (df.loc[:, ['ID','City','Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .count()
                .reset_index())
    fig = px.scatter( df_aux , x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig

def order_by_week(df):
    #criar coluna de semana

    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')

    df_aux = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    fig = px.line(df_aux, x = 'week_of_year', y = 'ID')
    return fig

def order_share_by_week (df):
            
    df_aux01 = (df.loc[:, ['ID','week_of_year']]
                  .groupby('week_of_year')
                  .count()
                  .reset_index())
    df_aux02 = (df.loc[:,['Delivery_person_ID','week_of_year']]
                  .groupby('week_of_year')
                  .nunique()
                  .reset_index())

    df_aux = pd.merge(df_aux01, df_aux02, how = 'inner')

    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux,  x = 'week_of_year', y = 'order_by_deliver')
    return fig

def country_maps (df):
    df = data_plot = (df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
                           .groupby( ['City', 'Road_traffic_density'])
                           .median()
                           .reset_index())
    # Desenhar o mapa
    map = folium.Map()
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static (map, width = 1024, height = 600)

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

st.header ('Marketplace - Visão Empresa')
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


tab1, tab2, tab3 = st.tabs (['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
    # Visão Empresa
        fig = order_metric (df)
        st.markdown('# Orders by Day')
        st.plotly_chart (fig, use_container_width = True)
       
    with st.container():
    #criando 2 colunas
        col1, col2 = st.columns (2)
        with col1:
            fig = traffic_order_share (df)
            st.markdown('# Traffic Order Share')
            st.plotly_chart (fig, use_container_width = True)
        
        with col2:
            fig = traffic_order_city (df)
            st.markdown('# Traffic Order City')
            st.plotly_chart (fig, use_container_width = True)
            
                
with tab2:
    with st.container():
        
        fig = order_by_week (df)
        st.markdown('# Order by Week')
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        
        fig = order_share_by_week (df)
        st.markdown('#Order Share bt Week')
        st.plotly_chart (fig, use_container_width = True)
        
with tab3:
    st.markdown('# Country Maps')
    country_maps (df)
    
    
    
print ('estou aqui')
print ( df.head() )