# ============================================================
# 📊 DASHBOARD DE DESPESAS PÚBLICAS — STREAMLIT + PANDAS + PLOTLY
# ✅ Com autenticação simples
# ✅ Código limpo e sem repetições
# ✅ Estrutura organizada e didática
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------
# ⚙️ CONFIGURAÇÃO DA PÁGINA
# ------------------------------------------------------------
st.set_page_config(page_title="Transparência Pública — Tutóia/MA", layout="wide")

# ------------------------------------------------------------
# 🔐 SISTEMA DE LOGIN SIMPLES
# ------------------------------------------------------------
users = {
    "Administração": "230398",
    "Cliente": "Tutóia"
}

def check_login():
    if "logged" not in st.session_state:
        st.session_state.logged = False

    if st.session_state.logged:
        return True

    st.title("🔐 Acesso Restrito ao Sistema")
    user = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user in users and users[user] == password:
            st.session_state.logged = True
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos")

    return False

if not check_login():
    st.stop()

# Botão logout
with st.sidebar:
    if st.button("🚪 Sair"):
        st.session_state.logged = False
        st.rerun()

# ------------------------------------------------------------
# 📥 CARREGAMENTO DOS DADOS
# ------------------------------------------------------------
df = pd.read_csv(
    "archive/despesas_2025.csv",
    encoding="latin1",
    sep=";"
)


# ------------------------------------------------------------
# 🧹 TRATAMENTO DOS DADOS
# ------------------------------------------------------------
df["Data"] = pd.to_datetime(df["Data"], dayfirst=True, errors="coerce")
df["Ano"] = df["Data"].dt.year
df["Mes"] = df["Data"].dt.month_name()

for col in ["Valor Empenhado", "Valor Liquidado", "Valor Pago"]:
    df[col] = (
        df[col].astype(str)
        .str.replace('.', '')
        .str.replace(',', '.')
    )
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ------------------------------------------------------------
# 🎛️ FILTROS
# ------------------------------------------------------------
st.sidebar.title("Filtros")

anos = sorted(df["Ano"].dropna().unique())
ano_sel = st.sidebar.selectbox("Selecione o Ano", anos)

fornecedores = sorted(df["Nome Fornecedor"].dropna().unique())
fornecedor_sel = st.sidebar.multiselect("Selecione Fornecedor(es)", fornecedores)

df_filt = df[df["Ano"] == ano_sel]
if fornecedor_sel:
    df_filt = df_filt[df_filt["Nome Fornecedor"].isin(fornecedor_sel)]

# ------------------------------------------------------------
# 📦 MÉTRICAS
# ------------------------------------------------------------
st.title("📊 Painel de Transparência Pública — Tutóia/MA")

total_empenhado = df_filt["Valor Empenhado"].sum()
total_liquidado = df_filt["Valor Liquidado"].sum()
total_pago = df_filt["Valor Pago"].sum()
saldo_pagar = total_empenhado - total_pago

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Valor Empenhado", f"R$ {total_empenhado:,.2f}")
col2.metric("✅ Valor Liquidado", f"R$ {total_liquidado:,.2f}")
col3.metric("📦 Valor Pago", f"R$ {total_pago:,.2f}")
col4.metric("⚠️ Saldo a Pagar", f"R$ {saldo_pagar:,.2f}")

# ------------------------------------------------------------
# 🏆 GRÁFICO — TOP 10 FORNECEDORES
# ------------------------------------------------------------
st.subheader("🏅 Top 10 Fornecedores por Valor Pago")

top_fornec = (
    df_filt.groupby("Nome Fornecedor")["Valor Pago"]
    .sum().sort_values(ascending=False).head(10)
)

fig = px.bar(
    top_fornec,
    orientation="h",
    labels={"value": "Total Pago", "index": "Fornecedor"}
)

st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------------------
# 📄 TABELA + DOWNLOAD
# ------------------------------------------------------------
st.subheader("📄 Dados Detalhados")
st.dataframe(df_filt)

st.download_button(
    "⬇️ Baixar dados filtrados",
    df_filt.to_csv(index=False).encode("utf-8"),
    "dados_filtrados.csv",
    mime="text/csv"
)
