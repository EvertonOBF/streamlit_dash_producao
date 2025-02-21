import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go

# Configurações iniciais
st.set_page_config(
    page_title="Engenharia de Produção - Fortaleza",
    page_icon="chart_with_upwards_trend",
    layout="wide")

config = {'displayModeBar': False}

# Carregar os dados
df = pd.read_csv('dados_tratados_2.csv')

# Guardando os códigos de cada IEs e associando ao nome:
df.loc[df["NO_IES"] == "CENTRO UNIVERSITÁRIO ATENEU", "SG_IES"] = "ATENEU"
df.loc[df["NO_IES"] == "CENTRO UNIVERSITÁRIO FARIAS BRITO", "SG_IES"] = "FFB"

df.loc[:, "SG_IES"].replace({
    "Estácio FIC" : "Estácio",
    "Estácio Ceará" :"Estácio",
    "Unifametro": "FAMETRO"
}, inplace=True)

dic_ies = dict(zip(df["CO_IES"], df["SG_IES"]))

df["SG_IES"] = df["CO_IES"].map(dic_ies)

# Título do dashboard
st.subheader('Egenharia de Produção - Fortaleza')
st.text("Análise de perfil dos alunos ingressantes do curso de Engenharia de Produção nas instituições particulares de Fortaleza.")

#st.markdown("##### Quantidade de cursos por ano")
#st.image("Resultados/Total_cursos_fortaleza.png", width=1000)


# ------------------------------------ Função para remover linhas com valores zeros --------------------------------------------

def remove_linhas_zeros(df, colunas):
    return df[~(df[colunas] == 0).any(axis=1)]



# ---------------------------------------------- Criando Sidebar ----------------------------------------------

st.sidebar.markdown(
    "<h2 style='text-align: center; font-size: 16px;'>"
    "Análise de Ingressantes<br><b>Engenharia de Produção</b></h2>",
    unsafe_allow_html=True
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

ano_sel = st.sidebar.select_slider(
    'Selecione um intervalo de anos',
    options=df['NU_ANO_CENSO'],
    value=(df['NU_ANO_CENSO'].min(), df['NU_ANO_CENSO'].max())  # Intervalo inicial
)

lista_anos = np.arange(ano_sel[0], ano_sel[1]+1)
df_ano = df[df["NU_ANO_CENSO"].isin(lista_anos)]

# Selecionando a instituição:
istituicao = ["Todas"] + sorted(df["SG_IES"].unique().tolist())
inst_sel = st.sidebar.selectbox("Selecione a instituição:", istituicao)

if inst_sel == "Todas":
    df_ano = df_ano.copy()
else:
    df_ano = df_ano[df_ano["SG_IES"] == inst_sel]

st.sidebar.markdown("<br>" * 8, unsafe_allow_html=True)
st.sidebar.markdown(
    "<div style='text-align: center; font-size: 14px;'>"
    "Criado e mantido por<br><b>Everton Castro</b></div>",
    unsafe_allow_html=True
)

# ------------------------------------ Total de alunos ingressantes por ano -----------------------------------------------------
st.divider() 
st.markdown(f"#### Total de Ingressantes por ano (Instituição - {inst_sel})")

if inst_sel == "Todas":
    df_1 = df.copy()
else:
    df_1 = df[df["SG_IES"] == inst_sel]

total_aluno_ano = df_1.groupby("NU_ANO_CENSO")["QT_ING"].sum().reset_index()
total_aluno_ano.rename(columns={"NU_ANO_CENSO": "Ano", "QT_ING":"Total"}, inplace=True)

fig = px.line(total_aluno_ano, x="Ano", y="Total", markers=True)

fig.update_layout(
    width=1000, height=500, #hovermode="x unified",

    margin=dict(l=200, r=0, b=0),

    xaxis=dict(
        title="Ano",
        linecolor="black",
        linewidth=1,
        tickfont=dict(size=15),
        title_font=dict(size=16)
    ),
    yaxis=dict(
        title="Quantidade de Ingressantes",
        linecolor="black",
        linewidth=1,
        #tickvals=np.arange(0,1001,200),
        tickfont=dict(size=15), title_font=dict(size=16)
    )
)

st.plotly_chart(fig, config=config)


# Perfil do aluno:
st.divider() 
st.markdown("#### 🎓 Perfil do Aluno")
st.markdown("<div style='margin-bottom: 30px;'></div>", unsafe_allow_html=True)
# ------------------------------------------------ Faixa etária --------------------------------------------------
df_idade = df_ano[["QT_ING_0_17", "QT_ING_18_24", "QT_ING_25_29", "QT_ING_30_34", "QT_ING_35_39", "QT_ING_40_49", "QT_ING_50_59"]].sum().reset_index()
df_idade.rename(columns={"index": "Faixa Etária", 0: "Quantidade de Ingressantes"}, inplace=True)

faixa_etaria_map = {
    "QT_ING_0_17": "até 17",
    "QT_ING_18_24": "18 a 24",
    "QT_ING_25_29": "25 a 29",
    "QT_ING_30_34": "30 a 34",
    "QT_ING_35_39": "35 a 39",
    "QT_ING_40_49": "40 a 49",
    "QT_ING_50_59": "50 a 59"
}

df_idade["Faixa Etária"] = df_idade["Faixa Etária"].map(faixa_etaria_map)
# Limpa valores nulos
df_idade = remove_linhas_zeros(df_idade, ["Quantidade de Ingressantes"])


# ------------------------------------------------ Instituição de Origem --------------------------------------------------

df_inst = df_ano[["QT_ING_PROCESCPUBLICA", "QT_ING_PROCESCPRIVADA", "QT_ING_PROCNAOINFORMADA"]].sum().reset_index()

df_inst.rename(columns={"index": "Instituição de Origem", 0:"Quantidade"}, inplace=True)
df_inst["Instituição de Origem"].replace({
    "QT_ING_PROCESCPRIVADA":"Particular", 
    "QT_ING_PROCESCPUBLICA":"Pública",
    "QT_ING_PROCNAOINFORMADA":"Não Informado"}, inplace=True)

# Limpa valores nulos
df_inst = remove_linhas_zeros(df_inst, ["Quantidade"])

lag = 200
alt = 200

fig_idade = px.pie(df_idade, 
             names='Faixa Etária', 
             values='Quantidade de Ingressantes', hole=0.4)

fig_idade.update_traces(textposition='inside')

fig_idade.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    width=lag, height=alt,
    uniformtext_minsize=12, uniformtext_mode='hide',

    legend=dict(
        x=.8,  # posição horizontal
        y=0.6,  # posição vertical
        xanchor='left',  # ancorando à esquerda
        yanchor='middle'  # ancorando ao meio verticalmente
    )
)

fig_escola = px.pie(df_inst, 
             names='Instituição de Origem', 
             values='Quantidade', hole=0.4)

fig_escola.update_traces(textposition='inside')

fig_escola.update_layout(
    uniformtext_minsize=12, uniformtext_mode='hide',
    margin=dict(l=0, r=0, t=0, b=0),
    width=lag, height=alt,
    legend=dict(
        x=.9,  # posição horizontal
        y=0.7,  # posição vertical
        xanchor='left',  # ancorando à esquerda
        yanchor='middle'  # ancorando ao meio verticalmente
    )
)

# ----------------------------------- Forma de Ingresso ----------------------------------------------------
colunas = ['QT_ING_VESTIBULAR','QT_ING_ENEM', 'QT_ING_SELECAO_SIMPLIFICA',
    'QT_ING_VG_REMANESC','QT_ING_OUTRA_FORMA']

df_vest = df_ano[colunas].sum().reset_index()
df_vest.rename(columns={"index":"Forma de Ingresso", 0:"Quantidade"}, inplace=True)
df_vest.sort_values("Quantidade", ascending=False, inplace=True)

def renomear_coluna(nome):
    return nome.replace("QT_ING_", "").replace("_", " ")

df_vest['Forma de Ingresso'] = df_vest['Forma de Ingresso'].apply(renomear_coluna)
df_vest["Forma de Ingresso"] = df_vest["Forma de Ingresso"].str.title()

# Limpa valores nulos
df_vest = remove_linhas_zeros(df_vest, ["Quantidade"])

fig_ing = px.pie(df_vest, 
             names='Forma de Ingresso', 
             values='Quantidade', hole=0.4)

fig_ing.update_traces(textposition='inside')

fig_ing.update_layout(
    uniformtext_minsize=12, uniformtext_mode='hide',
    margin=dict(l=0, r=0, t=0, b=0),
    width=lag, height=alt,
    legend=dict(
        x=1,  # posição horizontal
        y=0.7,  # posição vertical
        xanchor='left',  # ancorando à esquerda
        yanchor='middle'  # ancorando ao meio verticalmente
    )
)

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        #st.markdown('<div style="font-weight: bold;">Faixa Etária</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-weight: bold; text-align: center;">Faixa Etária</div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
        st.plotly_chart(fig_idade, config=config, use_container_width=True)

    with col2:
        st.markdown('<div style="font-weight: bold; text-align: center;">Instituição de Origem</div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
        st.plotly_chart(fig_escola, config=config, use_container_width=True)

    with col3:
        st.markdown('<div style="font-weight: bold;text-align: center;">Forma de Ingresso</div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True)
        st.plotly_chart(fig_ing, config=config, use_container_width=True)

# ----------------------------------- Distribuição por instituição -----------------------------------------
st.divider() 
st.markdown("#### Distribuição de alunos por Instituição")

df_ranking = df_ano.groupby("CO_IES")["QT_ING"].sum().sort_values(ascending=False).reset_index()
df_ranking["IES"] = df_ranking["CO_IES"].map(dic_ies)

fig = px.bar(df_ranking, x="QT_ING", y="IES", text="QT_ING", orientation="h")

fig.update_layout(
    width=900, height=500,

    #title=dict(text=f"Distribuição de alunos por Instituição - {ano_sel}", font_size=18, x=0.43),
    margin=dict(l=200, r=0, b=0),

    xaxis=dict(
        title="Quantidade de Ingressantes",
        linecolor="black",
        linewidth=1,
        tickfont=dict(size=15),
        title_font=dict(size=16)
    ),
    yaxis=dict(
        title="",
        linecolor="black",
        linewidth=1,
        tickfont=dict(size=15), title_font=dict(size=16)
    )
)

st.plotly_chart(fig, config=config)