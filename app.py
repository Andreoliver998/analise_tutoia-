import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# ⚙️ CONFIGURAÇÕES INICIAIS
# ==========================================

st.set_page_config(
    page_title="Dashboard de Despesas Públicas",
    layout="wide"
)

# ==========================================
# 🔐 SISTEMA DE LOGIN SIMPLES
# ==========================================

def login_page():
    st.title("🔐 Login de Acesso")

    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == "André" and pwd == "230398":  # ← Senha simples temporária
            st.session_state["logged"] = True
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos")

# Verifica se já está logado
if "logged" not in st.session_state or not st.session_state["logged"]:
    login_page()
    st.stop()  # Impede acesso ao app sem login


# ==========================================
# ✅ ÁREA DO SISTEMA (somente logado)
# ==========================================

st.success("✅ Login realizado com sucesso!")

st.title("📊 Dashboard de Despesas Públicas")

# ==========================================
# 📥 CARREGAMENTO DOS DADOS
# ==========================================

df = pd.read_csv(
    "archive/Portal Transparencia Despesas Gerais - Exercício 2025.csv",
    encoding="latin1",
    sep=";"
)

# ==========================================
# 🧹 TRATAMENTO DOS DADOS
# ==========================================

df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month_name()

cols_valores = ["Valor Empenhado", "Valor Liquidado", "Valor Pago"]

for col in cols_valores:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(".", "")
        .str.replace(",", ".")
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ==========================================
# 🎛️ SIDEBAR — FILTROS
# ==========================================

st.sidebar.header("Filtros")

anos = sorted(df["Ano"].dropna().unique())
filtro_ano = st.sidebar.selectbox("Ano", anos)

fornecedores = sorted(df["Nome Fornecedor"].dropna().unique())
filtro_fornec = st.sidebar.multiselect("Fornecedor", fornecedores)

df_filt = df[df["Ano"] == filtro_ano]

if filtro_fornec:
    df_filt = df_filt[df_filt["Nome Fornecedor"].isin(filtro_fornec)]

# ==========================================
# 🧮 INDICADORES
# ==========================================

total_empenhado = df_filt["Valor Empenhado"].sum()
total_liquidado = df_filt["Valor Liquidado"].sum()
total_pago = df_filt["Valor Pago"].sum()
saldo_pagar = total_empenhado - total_pago

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Empenhado", f"R$ {total_empenhado:,.2f}")
col2.metric("✅ Liquidado", f"R$ {total_liquidado:,.2f}")
col3.metric("📦 Pago", f"R$ {total_pago:,.2f}")
col4.metric("⚠️ Saldo a Pagar", f"R$ {saldo_pagar:,.2f}")

# ==========================================
# 📊 GRÁFICO — TOP FORNECEDORES
# ==========================================

st.subheader("🏆 Top 10 Fornecedores por Valor Pago")

top_fornec = (
    df_filt.groupby("Nome Fornecedor")["Valor Pago"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig = px.bar(
    top_fornec,
    orientation="h",
    labels={"value": "Valor Pago", "index": "Fornecedor"},
    title=""
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# 📄 TABELA + DOWNLOAD
# ==========================================

st.subheader("📄 Dados detalhados")
st.dataframe(df_filt)

st.download_button(
    "⬇️ Baixar dados filtrados",
    df_filt.to_csv().encode("utf-8"),
    "dados_filtrados.csv"
)
