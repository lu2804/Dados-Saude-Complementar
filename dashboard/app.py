import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================

st.set_page_config(
    layout="wide",
    page_title="BI Saúde da Família",
    page_icon="🏥"
)

# =====================================================
# ESTILO
# =====================================================

st.markdown("""
<style>

[data-testid="stMetricValue"]{
    font-size:32px;
    color:#1565C0;
    font-weight:bold;
}

.main{
    background-color:#F5F7FA;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# FUNÇÃO DE CARGA
# =====================================================

@st.cache_data
def carregar_dados():

    arquivo = "dados/dados_tratados/saude_familia_anual_formatado.csv"

    if not os.path.exists(arquivo):
        st.error(f"Arquivo não encontrado: {arquivo}")
        return pd.DataFrame()

    df = pd.read_csv(arquivo, encoding="utf-8-sig")

    df.columns = [col.strip() for col in df.columns]

    if "Ano" in df.columns:
        df["Ano"] = df["Ano"].astype(int)

    return df.sort_values("Ano")

# =====================================================
# CARREGAR DADOS
# =====================================================

df = carregar_dados()

if df.empty:
    st.stop()

# =====================================================
# TÍTULO
# =====================================================

st.title("🏥 BI - Saúde da Família")
st.markdown("---")

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("🔎 Filtros")

anos = sorted(df["Ano"].unique())

ano_inicio, ano_fim = st.sidebar.select_slider(
    "Período",
    options=anos,
    value=(anos[0], anos[-1])
)

df_filtrado = df[
    (df["Ano"] >= ano_inicio) &
    (df["Ano"] <= ano_fim)
]

# =====================================================
# FILTRO DE MUNICÍPIO
# =====================================================

if "Municipio" in df.columns:

    municipios = sorted(df["Municipio"].dropna().unique())

    municipio = st.sidebar.selectbox(
        "Município",
        ["Todos"] + municipios
    )

    if municipio != "Todos":
        df_filtrado = df_filtrado[
            df_filtrado["Municipio"] == municipio
        ]

# =====================================================
# FUNÇÃO FORMATAÇÃO
# =====================================================

def formatar(valor):

    return (
        f"{valor:,.0f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

# =====================================================
# KPIs
# =====================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    total_visitas = (
        df_filtrado["Nº_Visitas"].sum()
        if "Nº_Visitas" in df_filtrado.columns
        else 0
    )

    st.metric(
        "Total de Visitas",
        formatar(total_visitas)
    )

with col2:

    nascidos = (
        df_filtrado["Nascidos_Vivos"].sum()
        if "Nascidos_Vivos" in df_filtrado.columns
        else 0
    )

    st.metric(
        "Nascidos Vivos",
        formatar(nascidos)
    )

with col3:

    gestantes = (
        df_filtrado["Nº_Gestantes"].sum()
        if "Nº_Gestantes" in df_filtrado.columns
        else 0
    )

    st.metric(
        "Gestantes",
        formatar(gestantes)
    )

with col4:

    obitos = (
        df_filtrado["Óbitos_<1"].sum()
        if "Óbitos_<1" in df_filtrado.columns
        else 0
    )

    st.metric(
        "Óbitos <1 ano",
        formatar(obitos)
    )

# =====================================================
# ABAS
# =====================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([

    "🏠 Visão Geral",
    "📈 Atendimento",
    "👶 Saúde Infantil",
    "🤰 Saúde Materna",
    "🦠 Doenças",
    "🏥 Internações",
    "📊 Correlações",
    "📂 Dados"

])

# =====================================================
# ABA 1 - VISÃO GERAL
# =====================================================

with tab1:

    st.subheader("Visão Geral da Saúde")

    if "Nº_Visitas" in df_filtrado.columns:

        fig = px.line(
            df_filtrado,
            x="Ano",
            y="Nº_Visitas",
            markers=True,
            title="Evolução das Visitas"
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ABA 2 - ATENDIMENTO
# =====================================================

with tab2:

    st.subheader("Atendimentos")

    colunas = []

    if "Nº_Visitas" in df_filtrado.columns:
        colunas.append("Nº_Visitas")

    if "Famílias_Acompanh." in df_filtrado.columns:
        colunas.append("Famílias_Acompanh.")

    if len(colunas) > 0:

        fig = px.line(
            df_filtrado,
            x="Ano",
            y=colunas,
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ABA 3 - SAÚDE INFANTIL
# =====================================================

with tab3:

    st.subheader("Mortalidade Infantil")

    cols_obitos = [
        "Óbitos<1a_Diarr",
        "Óbitos<1a_IRA",
        "Óbitos<1a_OutCau"
    ]

    existentes = [
        c for c in cols_obitos
        if c in df_filtrado.columns
    ]

    if len(existentes) > 0:

        dados = (
            df_filtrado[existentes]
            .sum()
            .reset_index()
        )

        dados.columns = ["Causa", "Total"]

        fig = px.pie(
            dados,
            values="Total",
            names="Causa",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)

    # Pneumonia infantil

    if "Hosp.<5a_Pneumonia" in df_filtrado.columns:

        fig2 = px.bar(
            df_filtrado,
            x="Ano",
            y="Hosp.<5a_Pneumonia",
            title="Internações por Pneumonia"
        )

        st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# ABA 4 - SAÚDE MATERNA
# =====================================================

with tab4:

    st.subheader("Gestantes e Pré-Natal")

    if "Nº_Gestantes" in df_filtrado.columns:

        fig = px.line(
            df_filtrado,
            x="Ano",
            y="Nº_Gestantes",
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ABA 5 - DOENÇAS
# =====================================================

with tab5:

    st.subheader("Doenças Monitoradas")

    doencas = []

    for col in [
        "Diabéticos",
        "Hipertensos",
        "Hanseníase",
        "Tuberculose"
    ]:
        if col in df_filtrado.columns:
            doencas.append(col)

    if len(doencas) > 0:

        fig = px.line(
            df_filtrado,
            x="Ano",
            y=doencas,
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ABA 6 - INTERNAÇÕES
# =====================================================

with tab6:

    st.subheader("Internações")

    internacoes = []

    for col in [
        "Hosp.<5a_Pneumonia",
        "Hosp_Desidratacao",
        "Hosp_Psiquiatria"
    ]:
        if col in df_filtrado.columns:
            internacoes.append(col)

    if len(internacoes) > 0:

        fig = px.bar(
            df_filtrado,
            x="Ano",
            y=internacoes,
            barmode="group"
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ABA 7 - CORRELAÇÕES
# =====================================================

with tab7:

    st.subheader("Correlação entre Indicadores")

    df_corr = df_filtrado.select_dtypes(include="number")

    if len(df_corr.columns) > 1:

        corr = df_corr.corr()

        fig = px.imshow(
            corr,
            text_auto=True,
            aspect="auto"
        )

        st.plotly_chart(fig, use_container_width=True)

# =====================================================
# ABA 8 - DADOS
# =====================================================

with tab8:

    st.subheader("Tabela Consolidada")

    st.dataframe(
        df_filtrado,
        use_container_width=True
    )

    csv = df_filtrado.to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "📥 Baixar CSV",
        csv,
        "dados_filtrados.csv",
        "text/csv"
    )