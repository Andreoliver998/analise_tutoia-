import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard de Despesas Públicas", layout="wide")

# ------------------------------------------------------------
# 🔒 SISTEMA DE LOGIN
# ------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔐 Login de Acesso")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if username == st.secrets["general"]["admin_user"] and password == st.secrets["general"]["admin_password"]:
            st.session_state.logged_in = True
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos!")

if not st.session_state.logged_in:
    login()
    st.stop()  # 🔥 Bloqueia o restante do app até logar

# ------------------------------------------------------------
# 💾 SE CHEGOU AQUI, ESTÁ AUTENTICADO
# ------------------------------------------------------------

st.success("Bem-vindo, acesso autorizado ✅")

# Carregando dados
df_dadaset = pd.read_csv("archive/Portal Transparencia Despesas Gerais - Exercício 2025.csv", encoding="latin1", sep=";")

# Converter datas e valores
df_dadaset["Data"] = pd.to_datetime(df_dadaset["Data"], dayfirst=True, errors="coerce")
df_dadaset["Ano"] = df_dadaset["Data"].dt.year
df_dadaset["Mes"] = df_dadaset["Data"].dt.month_name()

cols_valores = ['Valor Empenhado','Valor Liquidado','Valor Pago']
for col in cols_valores:
    df_dadaset[col] = (
        df_dadaset[col].astype(str)
        .str.replace('.', '')
        .str.replace(',', '.')
    )
    df_dadaset[col] = pd.to_numeric(df_dadaset[col], errors='coerce')

# Sidebar
st.sidebar.header("Filtros")
anos = sorted(df_dadaset["Ano"].dropna().unique())
ano_sel = st.sidebar.selectbox("Ano", anos)
fornecedores = sorted(df_dadaset["Nome Fornecedor"].dropna().unique())
fornecedor_sel = st.sidebar.multiselect("Fornecedor", fornecedores)

df_filt = df_dadaset[df_dadaset["Ano"] == ano_sel]
if fornecedor_sel:
    df_filt = df_filt[df_filt["Nome Fornecedor"].isin(fornecedor_sel)]

# Indicadores
total_empenhado = df_filt["Valor Empenhado"].sum()
total_liquidado = df_filt["Valor Liquidado"].sum()
total_pago = df_filt["Valor Pago"].sum()
saldo_pagar = total_empenhado - total_pago

st.title("📊 Dashboard de Despesas Públicas")
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Empenhado", f"R$ {total_empenhado:,.2f}")
col2.metric("✅ Liquidado", f"R$ {total_liquidado:,.2f}")
col3.metric("📦 Pago", f"R$ {total_pago:,.2f}")
col4.metric("⚠️ Saldo a Pagar", f"R$ {saldo_pagar:,.2f}")

# Gráfico
st.subheader("🏆 Top 10 Fornecedores por Valor Pago")
top_fornec = df_filt.groupby("Nome Fornecedor")["Valor Pago"].sum().sort_values(ascending=False).head(10)
fig = px.bar(top_fornec, orientation='h', labels={"value": "Valor Pago", "index": "Fornecedor"})
st.plotly_chart(fig, use_container_width=True)

# Tabela e download
st.subheader("📄 Dados detalhados")
st.dataframe(df_filt)
st.download_button("⬇️ Baixar dados filtrados", df_filt.to_csv().encode("utf-8"), "dados_filtrados.csv")
