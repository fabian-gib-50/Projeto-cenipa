# Projeto de Análise de incidentes aéreos no Brasil
# Importando as bibliotecas necessárias 

import streamlit_folium as st_folium 
import streamlit as st 
import numpy as np
import pandas as pd 
import pydeck as pdk
import datetime 
import calendar 
import plotly.express as px
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
# from catboost import CatBoostClassifier, Pool
# from sklearn.model_selection import train_test_split
# from catboost.utils import get_confusion_matrix
# from catboost import cv
from PIL import Image

# Set de configurações da pagina inícial e tratamentos para a cenarização das ocorrências aéras no Brasil 

st.set_page_config( 
                   page_icon = ' bar_chart:',
                               layout='wide' 
                  ) 


# Função para customização dos botões com css_html_styles, com o arquivo style.css na mesma pasta do projeto

with open(r'./style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)      
    
# Carregando a logo e o nome da empresa
# Logo da sidebar 
logo = Image.open(
                  "logo_sdb.png"
                 )
st.sidebar.image(logo,
		   caption="",
		   use_column_width=True)

logo = Image.open(
                  "banner_st.png"
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

# Get datasets cenipa para novos procedimentos 

ocorrencias = pd.read_csv(r'./ocorrencias_aviacao.csv')
tipo_ocorrencias = pd.read_csv(r'./ocorrencia_tipo.csv', delimiter=';')
aeronave = pd.read_csv(r'./aeronave.csv', delimiter=';')
fator_contribuinte = pd.read_csv(r'./fator_contribuinte.csv', delimiter=';')
recomendacoes = pd.read_csv(r'./recomendacao.csv', delimiter=';')

columns = {
            'ocorrencia_latitude': 'latitude',
            'ocorrencia_longitude': 'longitude',
            'ocorrencia_dia': 'ano',
            'ocorrencia_uf':'uf',
           }   

ocorrencias = ocorrencias.rename(columns=columns)


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
            disk_resolution=15,
            radius=50000,
            get_position='[longitude,latitude]',
            get_fill_color='[255, 255, 255, 255]',
            get_line_color="[255, 255, 255]",
            auto_highlight=True,
            elevation_scale=1000,
            elevation_range=[0, 5000],
            get_elevation="norm_price",
            pickable=False,
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
# if tabela.checkbox("Abrir relatório"):
#     st.write(filtered_df)

# Aqui o placehoder vazio finalmente é atualizado com dados do filtered_df

info_sidebar.info("***{}***\n\n***Qtde. Reg. Ocorrências***".format(ocorrencias.shape[0])) 

# st.sidebar.header("ℹ️ MENU DE FILTROS")
info_sidebar = st.sidebar.empty()    # placeholder, para informações filtradas que só serão carregadas depois
    
# st.write(ocorrencias)
# raw data (tabela) dependente do checkbox
if tabela.checkbox("Abrir relatório"):
    st.write(ocorrencias)
    
# Criando histograma

st.markdown(
    "<h6 style='text-align: center; color:Grey;'>CENARIZAÇÃO DOS HORÁRIOS COM MAIOR DEMANDA</h6>", 
    unsafe_allow_html=True)
hist_values = np.histogram(df["data"].dt.hour,bins=24,range=(0, 24))[0]
st.bar_chart(hist_values)

#transformando as datas em formato de data
ocorrencias['ano'] = pd.to_datetime(ocorrencias['ano'])
ocorrencias['ano'] = ocorrencias['ano'].apply(lambda x : x.date())
# Separando dias, meses e anos
ocorrencias['oc_ano'] = pd.DatetimeIndex(ocorrencias['ano']).year
ocorrencias['oc_mes'] = pd.DatetimeIndex(ocorrencias['ano']).month
ocorrencias['oc_dia'] = pd.DatetimeIndex(ocorrencias['ano']).day
ocorrencias['oc_mes_str'] = ocorrencias['oc_mes'].apply(lambda x: calendar.month_abbr[x]) 

def recomendacoes_data (recomendacoes):
# Função para converter data para formato datetime e extrair mês, dia e ano.

    def convert_date(value):        
        try:
            converte = pd.to_datetime.datetime.strptime(value,'%Y-%m-%d').date()
            return converte 
        except:
            return np.nan
        
# Função para retornar o tempo em dias entre a notificação e o retorno

    def dif_days(x):
        try:
            diff = int((x[1] - x[0]).days)
            return diff
        except:
            return np.nan 
    recomendacoes['recomendacao_dia_encaminhamento_date'] = recomendacoes['recomendacao_dia_encaminhamento'].apply(lambda x: \
    datetime.datetime.strptime(x, '%Y-%m-%d').date())
    recomendacoes['recomendacao_dia_feedback_date'] = recomendacoes['recomendacao_dia_feedback'].apply(lambda x: \
                                                                                                convert_date(x))
    recomendacoes['Dias_de_Processo'] = recomendacoes[['recomendacao_dia_encaminhamento_date', 'recomendacao_dia_feedback_date']]\
                                                                                            .apply(lambda x : dif_days(x), axis=1)
    return recomendacoes

    recomendacoes = recomendacoes_data(recomendacoes)
    return ocorrencias, tipos_de_ocorrencias, aeronaves, fatores, recomendacoes, voos


#Criar gráfico de pareto
#Trazendo os dados
    ocorrencias, tipos_de_ocorrencias, aeronaves, fatores, recomendacoes, voos = get_data()
#Funções para todas as abas
#Criar gráfico de pareto
def pareto_chart(data):
    fig = make_subplots(specs= [[{'secondary_y': True}]])
    fig.add_trace(go.Bar(x=data[data.columns[0]],
    y=data[data.columns[1]],
    marker_color='#bfa878'))
    fig.add_trace(go.Scatter(x=data[data.columns[0]],
    y=data[data.columns[2]],
    marker_color='#7a4b4b',
    mode='lines+markers'
    ),
    secondary_y = True)
    fig.update_layout(yaxis_title = 'Nº de Registros',
    showlegend = False)
    fig.update_yaxes(title_text = '% do Total Acumulado',
    secondary_y = True)
    fig.update_xaxes(tickangle=-90)
    return fig

#Ocorrencias
st.sidebar.title('Menu')
tipo_info = st.sidebar.selectbox('Selecione uma página', ['Ocorrências', 'Tipos de Ocorrências' , 'Aeronaves', 'Fatores', 'Recomendações de Segurança', 'Machine Learning'])
if tipo_info == 'Ocorrências':
   st.title('Análise das Ocorrências')
col1, col2 = st.columns(2)
with col1:
   st.header('Ocorrências por ano')
#Comportamento das ocorrencias anualmente
oc_fig1 = ocorrencias[['oc_ano', 'ocorrencia_classificacao','codigo_ocorrencia']]\
                                 .groupby(['oc_ano', 'ocorrencia_classificacao']).agg({'codigo_ocorrencia' : 'count'})\
                                 .reset_index().rename({'codigo_ocorrencia' : 'Nº de registros'}, axis=1)
oc_fig1 = oc_fig1.pivot_table(index='oc_ano', columns='ocorrencia_classificacao',
values='Nº de registros').rename_axis(None, axis=1).reset_index()
fig1 = px.bar(oc_fig1, x="oc_ano", y=['INCIDENTE', 'INCIDENTE GRAVE', 'ACIDENTE'], barmode='group', height=600, width=900)
fig1.update_layout(yaxis_title='Registros', xaxis_title='')
st.plotly_chart(fig1)
#Relação de nº de ocorrências por mês
ano_filtro = list(ocorrencias['oc_ano'].unique())
st.header('Ocorrências por mês')
multiselect = st.multiselect('Ano Ocorrência', ano_filtro, default=ano_filtro)
oc_fig2 = ocorrencias[ocorrencias['oc_ano'].isin(multiselect)][['oc_mes', 'ocorrencia_classificacao','codigo_ocorrencia']]
oc_fig2 = oc_fig2.groupby(['oc_mes', 'ocorrencia_classificacao']).agg({'codigo_ocorrencia' : 'count'})\
.reset_index().rename({'codigo_ocorrencia' : 'Nº de registros'}, axis=1)
oc_fig2 = oc_fig2.pivot_table(index='oc_mes', columns='ocorrencia_classificacao',
values='Nº de registros').rename_axis(None, axis=1).reset_index()
fig2 = px.bar(oc_fig2, x='oc_mes', y=['INCIDENTE', 'INCIDENTE GRAVE', 'ACIDENTE'], barmode='group', height=600, width=900)
fig2.update_layout(yaxis_title='Registros', xaxis_title='')
st.plotly_chart(fig2)

# st.write(recomendacoes)