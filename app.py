# ============================================================
# 📊 DASHBOARD DE DESPESAS PÚBLICAS — STREAMLIT + PANDAS + PLOTLY
# Com autenticação simples para acesso seguro
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# ⚙️ Configuração da página
# ------------------------------------------------------------
st.set_page_config(page_title="Transparência Pública", layout="wide")


# ============================================================
# 🔐 SISTEMA DE LOGIN
# ============================================================

# Usuários autorizados (altere depois)
users = {
    "admin": "230398",          # Exemplo admin
    "cliente": "tutoia"       # Exemplo cliente
}

def check_login():
    """Função para controle de login"""
    if "logged" not in st.session_state:
        st.session_state.logged = False

    if st.session_state.logged:
        return True

    st.title("🔐 Acesso Restrito ao Sistema")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    btn = st.button("Entrar")

    if btn:
        if user in users and users[user] == password:
            st.session_state.logged = True
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos")

    return False

# Se não estiver logado, encerra execução aqui
if not check_login():
    st.stop()

# Botão logout
with st.sidebar:
    if st.button("🚪 Sair"):
        st.session_state.logged = False
        st.rerun()


# ============================================================
# 📥 CARREGAMENTO E TRATAMENTO DOS DADOS
# ============================================================

df_dadaset = pd.read_csv(
    "archive/Portal Transparencia Despesas Gerais - Exercício 2025.csv",
    encoding="latin1",
    sep=";"
)

# ✅ Converter datas
df_dadaset["Data"] = pd.to_datetime(df_dadaset["Data"], dayfirst=True, errors="coerce")
df_dadaset["Ano"] = df_dadaset["Data"].dt.year
df_dadaset["Mes"] = df_dadaset["Data"].dt.month_name()

# ✅ Converter valores
cols_valores = ["Valor Empenhado", "Valor Liquidado", "Valor Pago"]
for col in cols_valores:
    df_dadaset[col] = (
        df_dadaset[col]
        .astype(str)
        .str.replace(".", "")
        .str.replace(",", ".")
    )
    df_dadaset[col] = pd.to_numeric(df_dadaset[col], errors="coerce")


# ============================================================
# 🎛️ FILTROS
# ============================================================

st.sidebar.title("Filtros")

anos = sorted(df_dadaset["Ano"].dropna().unique())
ano_sel = st.sidebar.selectbox("Selecione o Ano", anos)

fornecedores = sorted(df_dadaset["Nome Fornecedor"].dropna().unique())
fornecedor_sel = st.sidebar.multiselect("Selecione Fornecedor(es)", fornecedores)

df_filt = df_dadaset[df_dadaset["Ano"] == ano_sel]

if fornecedor_sel:
    df_filt = df_filt[df_filt["Nome Fornecedor"].isin(fornecedor_sel)]


# ============================================================
# 📦 MÉTRICAS (KPI CARDS)
# ============================================================

total_empenhado = df_filt["Valor Empenhado"].sum() 
total_liquidado = df_filt["Valor Liquidado"].sum()
total_pago = df_filt["Valor Pago"].sum()
saldo_pagar = total_empenhado - total_pago

st.title("📊 Painel de Transparência Pública — Tutóia/MA")

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Valor Empenhado", f"R$ {total_empenhado:,.2f}")
col2.metric("✅ Valor Liquidado", f"R$ {total_liquidado:,.2f}")
col3.metric("📦 Valor Pago", f"R$ {total_pago:,.2f}")
col4.metric("⚠️ Saldo a Pagar", f"R$ {saldo_pagar:,.2f}")


# ============================================================
# 🏆 TOP 10 FORNECEDORES — GRÁFICO
# ============================================================

st.subheader("🏅 Top 10 Fornecedores por Valor Pago")

top_fornec = (
    df_filt.groupby("Nome Fornecedor")["Valor Pago"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

fig = px.bar(
    top_fornec,
    orientation="h",
    labels={"value": "Total Pago", "index": "Fornecedor"},
)

st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 📄 TABELA E DOWNLOAD
# ============================================================

st.subheader("📄 Dados Detalhados")

st.dataframe(df_filt)

st.download_button(
    "⬇️ Baixar dados filtrados",
    df_filt.to_csv(index=False).encode("utf-8"),
    file_name="dados_filtrados.csv",
    mime="text/csv"
)
