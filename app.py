# ============================================================
# 📊 DASHBOARD DE DESPESAS PÚBLICAS — STREAMLIT + PANDAS + PLOTLY
# Código completo com explicações detalhadas em cada parte
# ============================================================

# ------------------------------------------------------------
# 🧠 Importando Bibliotecas
# ------------------------------------------------------------

import streamlit as st            # Streamlit -> cria interface web interativa
import pandas as pd              # Pandas -> leitura, tratamento e análise de dados
import plotly.express as px      # Plotly -> gráficos interativos e bonitos


# ------------------------------------------------------------
# ⚙️ Configuração inicial da página (modo tela cheia)
# ------------------------------------------------------------

st.set_page_config(layout="wide")  # Deixa o dashboard ocupar a tela inteira


# ------------------------------------------------------------
# 📥 Carregar e preparar os dados
# ------------------------------------------------------------

# Lendo o arquivo CSV com dados públicos
df_dadaset = pd.read_csv(
    "archive/Portal Transparencia Despesas Gerais - Exercício 2025.csv",
    encoding="latin1",  # Corrige acentos do português
    sep=";",            # CSV separado por ";"
)

# 🗓️ Convertendo coluna de datas para formato de data real
df_dadaset["Data"] = pd.to_datetime(
    df_dadaset["Data"], 
    dayfirst=True,      # Dia primeiro (formato brasileiro)
    errors="coerce"     # Se não conseguir converter, deixa como nulo
)

# Criando colunas de Ano e Nome do mês (para filtros e gráficos)
df_dadaset["Ano"] = df_dadaset["Data"].dt.year
df_dadaset["Mes"] = df_dadaset["Data"].dt.month_name()


# ------------------------------------------------------------
# 💰 Convertendo valores financeiros para número
# ------------------------------------------------------------

# Lista com colunas que contêm valores monetários
cols_valores = ['Valor Empenhado','Valor Liquidado','Valor Pago']

# Loop para limpar e converter valores
for col in cols_valores:
    
    # Converte para texto e remove pontos de milhar e troca vírgula por ponto
    df_dadaset[col] = (
        df_dadaset[col]
        .astype(str)       # Converte para texto
        .str.replace('.', '')   # Remove separador de milhar
        .str.replace(',', '.')  # Troca vírgula por ponto
    )
    
    # Converte para número real
    df_dadaset[col] = pd.to_numeric(df_dadaset[col], errors='coerce')


# ------------------------------------------------------------
# 🎛️ Barra lateral de filtros (menu lateral)
# ------------------------------------------------------------

st.sidebar.header("Filtros")  # Título do menu lateral

# 📅 Filtro por Ano
anos = sorted(df_dadaset["Ano"].dropna().unique())
ano_sel = st.sidebar.selectbox("Ano", anos)

# 🏢 Filtro de Fornecedor
fornecedores = sorted(df_dadaset["Nome Fornecedor"].dropna().unique())
fornecedor_sel = st.sidebar.multiselect("Fornecedor", fornecedores)

# Aplicando os filtros no DataFrame
df_filt = df_dadaset[df_dadaset["Ano"] == ano_sel]

# Se o usuário selecionar fornecedores, filtra também
if fornecedor_sel:
    df_filt = df_filt[df_filt["Nome Fornecedor"].isin(fornecedor_sel)]


# ------------------------------------------------------------
# 📦 Indicadores (cards de totais)
# ------------------------------------------------------------

# Calculando totais
total_empenhado = df_filt["Valor Empenhado"].sum()
total_liquidado = df_filt["Valor Liquidado"].sum()
total_pago = df_filt["Valor Pago"].sum()
saldo_pagar = total_empenhado - total_pago  # Diferença entre empenhado e pago

# Título principal da página
st.title("📊 Dashboard de Despesas Públicas")

# Criando 4 colunas para exibir os indicadores
col1, col2, col3, col4 = st.columns(4)

# Exibindo valores formatados como moeda brasileira
col1.metric("💰 Empenhado", f"R$ {total_empenhado:,.2f}")
col2.metric("✅ Liquidado", f"R$ {total_liquidado:,.2f}")
col3.metric("📦 Pago", f"R$ {total_pago:,.2f}")
col4.metric("⚠️ Saldo a Pagar", f"R$ {saldo_pagar:,.2f}")


# ------------------------------------------------------------
# 🏆 Gráfico — Top 10 fornecedores por Valor Pago
# ------------------------------------------------------------

st.subheader("🏆 Top 10 Fornecedores por Valor Pago")

# Agrupando dados e ordenando do maior para o menor
top_fornec = (
    df_filt.groupby("Nome Fornecedor")["Valor Pago"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

# Criando gráfico de barras horizontal
fig = px.bar(
    top_fornec,
    orientation='h',  # Barras horizontais
    labels={"value": "Valor Pago", "index": "Fornecedor"},
)

# Exibindo gráfico
st.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# 📄 Tabela com dados filtrados
# ------------------------------------------------------------

st.subheader("📄 Dados detalhados")
st.dataframe(df_filt)  # Mostra a tabela filtrada na tela


# ------------------------------------------------------------
# 💾 Botão para download dos dados filtrados
# ------------------------------------------------------------

st.download_button(
    "⬇️ Baixar dados filtrados",      # Texto do botão
    df_filt.to_csv().encode("utf-8"), # Converte dados para CSV
    "dados_filtrados.csv"             # Nome do arquivo
)
