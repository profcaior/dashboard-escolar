import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
# -----------------------------------
# TÍTULO
# -----------------------------------

st.title("Dashboard Pedagógico")

# -----------------------------------
# ARQUIVO EXCEL
# -----------------------------------

# -----------------------------------
# UPLOAD DO EXCEL
# -----------------------------------

arquivo = st.file_uploader(
    "Envie a planilha Excel",
    type=["xlsx"]
)

# Verificar upload
if arquivo is not None:

    # Ler abas
    abas = pd.read_excel(
        arquivo,
        sheet_name=None
    )

else:

    st.warning(
        "Envie uma planilha para continuar."
    )

    st.stop()
# -----------------------------------
# CONFIGURAÇÕES
# -----------------------------------

disciplinas_possiveis = [
    "MAT",
    "PORT",
    "ING",
    "HIST",
    "GEO",
    "CIE",
    "FIN",
    "TEC"
]

# Base geral
base_geral = []

# -----------------------------------
# LEITURA DAS ABAS
# -----------------------------------

for turma, df in abas.items():

    # Remover linhas vazias
    df = df.dropna(how='all')

    # Resetar índice
    df = df.reset_index(drop=True)

    # Encontrar cabeçalho
    for i in range(len(df)):

        linha = (
            df.iloc[i]
            .astype(str)
            .tolist()
        )

        if "MAT" in linha:

            df.columns = df.iloc[i]

            df = df[i+1:]

            break

    # Limpar colunas
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    # Encontrar coluna aluno
    coluna_nome = None

    for col in df.columns:

        texto = col.upper()

        if (
            "NOME" in texto
            or "ALUNO" in texto
        ):

            coluna_nome = col

            break

    # Se não encontrar aluno
    if coluna_nome is None:

        continue

    # Adicionar turma
    df["TURMA"] = turma

    # Descobrir disciplinas existentes
    disciplinas_encontradas = []

    for disc in disciplinas_possiveis:

        if disc in df.columns:

            disciplinas_encontradas.append(disc)

    # Colunas finais
    colunas = (
        [coluna_nome]
        + disciplinas_encontradas
        + ["TURMA"]
    )

    df = df[colunas]

    # Renomear coluna aluno
    df = df.rename(
        columns={
            coluna_nome: "ALUNO"
        }
    )

    # Adicionar base
    base_geral.append(df)

# -----------------------------------
# JUNTAR TODAS AS TURMAS
# -----------------------------------

base = pd.concat(base_geral)

# -----------------------------------
# CONVERTER NOTAS
# -----------------------------------

for coluna in base.columns:

    if coluna not in ["ALUNO", "TURMA"]:

        base[coluna] = pd.to_numeric(
            base[coluna],
            errors='coerce'
        )

# -----------------------------------
# MOSTRAR BASE
# -----------------------------------

st.subheader("Base Geral")

st.dataframe(base)

# -----------------------------------
# DISCIPLINAS DISPONÍVEIS
# -----------------------------------

disciplinas_dashboard = []

for coluna in base.columns:

    if coluna not in ["ALUNO", "TURMA"]:

        disciplinas_dashboard.append(coluna)

# -----------------------------------
# GRÁFICO POR DISCIPLINA
# -----------------------------------

st.subheader("Comparativo por Disciplina")

disciplina = st.selectbox(
    "Escolha a disciplina",
    disciplinas_dashboard
)

# Média por turma
media = (
    base
    .groupby("TURMA")[disciplina]
    .mean()
    * 100
)

# Criar gráfico
fig, ax = plt.subplots()

media.plot(
    kind='bar',
    ax=ax
)

ax.set_ylabel("Percentual")

ax.set_xlabel("Turma")

ax.set_title(
    f"Média de {disciplina} por turma"
)

st.pyplot(fig)

# -----------------------------------
# GRÁFICO POR TURMA
# -----------------------------------

st.subheader("Desempenho da Turma")

# Lista de turmas
turmas = sorted(
    base["TURMA"].unique()
)

# Seleção da turma
turma_escolhida = st.selectbox(
    "Escolha a turma",
    turmas
)

# Filtrar turma
base_turma = base[
    base["TURMA"] == turma_escolhida
]

# Médias
medias_turma = {}

for disc in disciplinas_dashboard:

    medias_turma[disc] = (
        base_turma[disc].mean() * 100
    )

# DataFrame gráfico
grafico_turma = pd.DataFrame({

    "DISCIPLINA": medias_turma.keys(),

    "MÉDIA": medias_turma.values()
})

# Criar gráfico
fig2, ax2 = plt.subplots()

ax2.bar(
    grafico_turma["DISCIPLINA"],
    grafico_turma["MÉDIA"]
)

ax2.set_ylabel("Percentual")

ax2.set_xlabel("Disciplina")

ax2.set_title(
    f"Desempenho da turma {turma_escolhida}"
)

st.pyplot(fig2)

# -----------------------------------
# RELATÓRIO PEDAGÓGICO
# -----------------------------------

st.subheader(
    "Relatório Pedagógico por Aluno"
)

# Lista relatório
relatorio = []

# Percorrer alunos
for _, linha in base.iterrows():

    aluno = linha["ALUNO"]

    turma = linha["TURMA"]

    # Percorrer disciplinas
    for disc in disciplinas_dashboard:

        valor = linha[disc]

        # Ignorar vazio
        if pd.isna(valor):

            continue

        percentual = valor

        # Classificação
        if percentual < 0.5:

            classificacao = (
                "ABAIXO DO BÁSICO"
            )

        elif percentual < 0.7:

            classificacao = (
                "BÁSICO"
            )

        else:

            classificacao = (
                "ADEQUADO"
            )

        # Adicionar relatório
        relatorio.append({

            "TURMA": turma,

            "ALUNO": aluno,

            "DISCIPLINA": disc,

            "PERCENTUAL": round(
                percentual * 100,
                1
            ),

            "CLASSIFICAÇÃO": classificacao
        })

# Criar DataFrame
relatorio_df = pd.DataFrame(
    relatorio
)
# -----------------------------------
# INDICADORES PEDAGÓGICOS
# -----------------------------------

# Total alunos
total_alunos = (
    relatorio_df["ALUNO"]
    .nunique()
)

# Total registros
total_registros = len(relatorio_df)

# Percentuais
adequado = round(

    (
        len(
            relatorio_df[
                relatorio_df[
                    "CLASSIFICAÇÃO"
                ] == "ADEQUADO"
            ]
        )
        / total_registros
    ) * 100,

    1
)

basico = round(

    (
        len(
            relatorio_df[
                relatorio_df[
                    "CLASSIFICAÇÃO"
                ] == "BÁSICO"
            ]
        )
        / total_registros
    ) * 100,

    1
)

abaixo = round(

    (
        len(
            relatorio_df[
                relatorio_df[
                    "CLASSIFICAÇÃO"
                ] == "ABAIXO DO BÁSICO"
            ]
        )
        / total_registros
    ) * 100,

    1
)

# Criar colunas
col1, col2, col3, col4 = st.columns(4)

# Card 1
col1.metric(
    "Total de Alunos",
    total_alunos
)

# Card 2
col2.metric(
    "% Adequado",
    f"{adequado}%"
)

# Card 3
col3.metric(
    "% Básico",
    f"{basico}%"
)

# Card 4
col4.metric(
    "% Abaixo do Básico",
    f"{abaixo}%"
)
# -----------------------------------
# GRÁFICO PIZZA CLASSIFICAÇÃO
# -----------------------------------

st.subheader(
    "Distribuição das Classificações"
)

# Dados gráfico
dados_pizza = [

    abaixo,

    basico,

    adequado
]

labels = [

    "ABAIXO DO BÁSICO",

    "BÁSICO",

    "ADEQUADO"
]

# Criar gráfico
fig3, ax3 = plt.subplots()

ax3.pie(

    dados_pizza,

    labels=labels,

    autopct='%1.1f%%'
)

ax3.set_title(
    "Classificação Geral"
)

# Mostrar gráfico
st.pyplot(fig3)
# -----------------------------------
# FILTROS
# -----------------------------------

st.subheader("Filtros do Relatório")

# FILTRO TURMA
turmas_filtro = (
    ["TODAS"]
    + sorted(
        relatorio_df["TURMA"].unique()
    )
)

turma_filtro = st.selectbox(
    "Filtrar Turma",
    turmas_filtro
)

# Aplicar filtro turma
if turma_filtro != "TODAS":

    relatorio_df = relatorio_df[
        relatorio_df["TURMA"]
        == turma_filtro
    ]

# FILTRO DISCIPLINA
disciplinas_filtro = (
    ["TODAS"]
    + sorted(
        relatorio_df["DISCIPLINA"].unique()
    )
)

disciplina_filtro = st.selectbox(
    "Filtrar Disciplina",
    disciplinas_filtro
)

# Aplicar filtro disciplina
if disciplina_filtro != "TODAS":

    relatorio_df = relatorio_df[
        relatorio_df["DISCIPLINA"]
        == disciplina_filtro
    ]

# FILTRO ALUNO
alunos_filtro = (
    ["TODOS"]
    + sorted(
        relatorio_df["ALUNO"]
        .dropna()
        .astype(str)
        .unique()
    )
)
aluno_filtro = st.selectbox(
    "Filtrar Aluno",
    alunos_filtro
)

# Aplicar filtro aluno
if aluno_filtro != "TODOS":

    relatorio_df = relatorio_df[
        relatorio_df["ALUNO"]
        == aluno_filtro
    ]
# -----------------------------------
# GRÁFICO INDIVIDUAL DO ALUNO
# -----------------------------------

if aluno_filtro != "TODOS":

    st.subheader(
        f"Desempenho do aluno: {aluno_filtro}"
    )

    # Filtrar aluno
    aluno_df = relatorio_df[
        relatorio_df["ALUNO"]
        == aluno_filtro
    ]

    # Definir cores
    cores = []

    for valor in aluno_df["PERCENTUAL"]:

        if valor < 50:

            cores.append("red")

        elif valor < 70:

            cores.append("yellow")

        else:

            cores.append("green")

    # Criar gráfico
    fig4, ax4 = plt.subplots()

    ax4.bar(

        aluno_df["DISCIPLINA"],

        aluno_df["PERCENTUAL"],

        color=cores
    )

    ax4.set_ylim(0, 100)

    ax4.set_ylabel("Percentual")

    ax4.set_xlabel("Disciplina")

    ax4.set_title(
        f"Desempenho de {aluno_filtro}"
    )

    st.pyplot(fig4)
# -----------------------------------
# MOSTRAR RELATÓRIO
# -----------------------------------

# -----------------------------------
# CORES PEDAGÓGICAS
# -----------------------------------

def colorir_classificacao(valor):

    if valor == "ABAIXO DO BÁSICO":

        return (
            "background-color: #ffb3b3;"
            "color: black;"
            "font-weight: bold;"
        )

    elif valor == "BÁSICO":

        return (
            "background-color: #ffe699;"
            "color: black;"
            "font-weight: bold;"
        )

    elif valor == "ADEQUADO":

        return (
            "background-color: #b6d7a8;"
            "color: black;"
            "font-weight: bold;"
        )

    return ""
# Mostrar relatório colorido
st.dataframe(

    relatorio_df.style
    .map(

        colorir_classificacao,

        subset=["CLASSIFICAÇÃO"]
    )
    .format({

        "PERCENTUAL": "{:.1f}"

    })
)
# -----------------------------------
# DOWNLOAD RELATÓRIO EXCEL
# -----------------------------------

st.subheader("Download do Relatório")

# Função para gerar Excel
def gerar_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine='xlsxwriter'
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name='Relatório'
        )

    return output.getvalue()

# Gerar arquivo
# Verificar relatório
if not relatorio_df.empty:

    # Gerar arquivo
    excel = gerar_excel(relatorio_df)

    # Botão download
    st.download_button(

        label="Baixar Relatório Excel",

        data=excel,

        file_name="relatorio_pedagogico.xlsx",

        mime=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        )
    )

else:

    st.warning(
        "Nenhum dado encontrado."
    )
