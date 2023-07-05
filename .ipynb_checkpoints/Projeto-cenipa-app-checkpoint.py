# Projeto de Análise de incidentes aéreos no Brasil
# Importando as bibliotecas necessárias 

import streamlit_folium as st_folium 
import streamlit as st 
import numpy as np
import pandas as pd 
import pydeck as pdk
from PIL import Image

# Set de configurações da pagina inícial e tratamentos para a cenarização das ocorrências aéras no Brasil 

st.set_page_config( 
                   page_icon = ' bar_chart:',
                               layout='wide' 
                  ) 
# Carregando a logo e o nome da empresa
# Logo da sidebar 
logo = Image.open(
                  r"./logo_sdb.png"
                 )
st.sidebar.image(logo,
		   caption="",
		   use_column_width=True)

logo = Image.open(
                  r"./banner_st.png"
                 )
st.image(logo,
		   caption="",
		   use_column_width=True)

logo = Image.open(
                  r"./cenipa.jpg"
                 )
st.image(logo,
		   caption="",
		   use_column_width=True)

#Função para guardar em cache os dados pré-selecionados 

@st.cache_resource 
#Função criada para carregar o dataset
def get_data(): 
    
    """
    Carrega os dados de ocorrências aeronáuticas do CENIPA.
    :return: DataFrame com colunas selecionadas.
    """
    columns = {
        'ocorrencia_latitude': 'latitude',
        'ocorrencia_longitude': 'longitude',
        'ocorrencia_dia': 'data',
        'ocorrencia_classificacao': 'classificacao',
        'ocorrencia_tipo': 'tipo',
        'ocorrencia_tipo_categoria': 'tipo_categoria',
        'ocorrencia_tipo_icao': 'tipo_icao',
        'ocorrencia_aerodromo': 'aerodromo',
        'ocorrencia_uf':'estado',
        'ocorrencia_cidade': 'cidade',
        'investigacao_status': 'status',
        'divulgacao_relatorio_numero': 'relatorio_numero',
        'total_aeronaves_envolvidas': 'aeronaves_envolvidas'
              }   
# Fazendo a importação e filtro conforme função acima 

    data = pd.read_csv(r'./ocorrencias_aviacao.csv',index_col='codigo_ocorrencia')
    data = data.rename(columns=columns)
    data.data = data.data + " " + data.ocorrencia_horario
    data.data = pd.to_datetime(data.data)
    data = data[list(columns.values())]
    return data

# Carregar os dados 

df = get_data()
labels = df.classificacao.unique().tolist()
# st.sidebar('Parameters ')
# Parâmetros e número de ocorrências 

st.sidebar.markdown(
    "<h4 style='text-align: center; color:darkpurple;'>PARÂMETROS DE CONSULTA ℹ️ </h4>", 
    unsafe_allow_html=True)
# st.sidebar.header("ℹ️ MENU DE FILTROS")
info_sidebar = st.sidebar.empty()    # placeholder, para informações filtradas que só serão carregadas depois

st.sidebar.subheader("ℹ️ Filtro por período")
year_to_filter = st.sidebar.slider('Escolha o ano para análise', 2008, 2018, 2013)

# Checkbox da Tabela
st.sidebar.subheader("Selecione Relatório")
tabela = st.sidebar.empty()    # placeholder que só vai ser carregado com o df_filtered

# Multiselect com os lables únicos dos tipos de classificação
label_to_filter = st.sidebar.multiselect(
    label="Classificação das ocorrências",
    options=labels,
    default=["INCIDENTE"]
)

# Informação no rodapé da Sidebar
st.sidebar.markdown("**:Blue[A base de dados de ocorrências aeronáuticas é gerenciada pelo ***Centro de Investigações e Prevenção de Acidentes Aeronáuticos***(CENIPA)]**")

# Somente aqui os dados filtrados por ano são atualizados em novo dataframe
filtered_df = df[(df.data.dt.year == year_to_filter) & (df.classificacao.isin(label_to_filter))]

# Aqui o placehoder vazio finalmente é atualizado com dados do filtered_df
info_sidebar.info("***{}***\n\n***Qtde. Reg. Ocorrências***".format(filtered_df.shape[0]))

# main
# st.title("***Acidentes Aeronáuticos no Brasil***")

st.markdown(
    "<h3 style='text-align: center; color:Blue;'>MAPEAMENTO DOS INCIDENTES AÉREOS NO BRASIL</h3>", 
    unsafe_allow_html=True)
st.markdown(f"""
            ℹ️@ Estão sendo exibidas as ocorrências classificadas como**{",".join(label_to_filter)}**
            para o ano de:**{year_to_filter}**
            """)
st.markdown(
    "<h6 style='text-align: center; color:Grey;'>MAPA DAS OCORRÊNCIAS POR ESTADO</h6>", 
    unsafe_allow_html=True)

# Mapa simples 
# st.subheader("Mapa de ocorrências")
# st.map(filtered_df)
# Mapara custoizado pydeck  

st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude =-27.6255316, #Geoposicionamento SC #-22.96592,
        longitude=-53.7246994, #Geoposicionamento SC #43.17896,
        zoom=3,
        pitch=50
    ),
 layers=[
        pdk.Layer(
            'HexagonLayer',
            data=filtered_df,
            disk_resolution=12,
            radius=30000,
            get_position='[longitude,latitude]',
            get_fill_color='[255, 255, 255, 255]',
            get_line_color="[255, 255, 255]",
            auto_highlight=True,
            elevation_scale=1000,
            elevation_range=[0, 3000],
            get_elevation="norm_price",
            pickable=True,
            extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=filtered_df,
            get_position='[longitude, latitude]',
            get_color='[255, 255, 255, 30]',
            get_radius=60000,
        ),
    ],
))

# raw data (tabela) dependente do checkbox
if tabela.checkbox("Abrir relatório"):
    st.write(filtered_df)

#Criando histograma
st.markdown(
    "<h6 style='text-align: center; color:Grey;'>CENARIZAÇÃO DOS HORÁRIOS COM MAIOR DEMANDA</h6>", 
    unsafe_allow_html=True)
hist_values = np.histogram(df["data"].dt.hour,bins=24,range=(0, 24))[0]
st.bar_chart(hist_values)
