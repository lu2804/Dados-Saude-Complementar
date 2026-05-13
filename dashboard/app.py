import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
# CSS CUSTOMIZADO
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #F5F7FA;
}

[data-testid="stMetricValue"] {
    font-size: 32px;
    color: #004A99;
    font-weight: bold;
}

[data-testid="stMetricLabel"] {
    font-size: 15px;
}

.stTabs [data-baseweb="tab"] {
    padding: 10px 20px;
    background-color: white;
    border-radius: 8px 8px 0 0;
    margin-right: 4px;
}

.stTabs [aria-selected="true"] {
    background-color: #DCEEFF !important;
    border-bottom: 3px solid #004A99 !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# CARREGAMENTO DOS DADOS
# =====================================================

@st.cache_data
def carregar_dados():

    nome_arquivo = "saude_familia_anual_formatado.csv"

    caminhos = [
        nome_arquivo,
        os.path.join("dashboard", nome_arquivo),
        os.path.join("dados", nome_arquivo),
        os.path.join("..", nome_arquivo),
    ]

    df = pd.DataFrame()

    for caminho in caminhos:

        if os.path.exists(caminho):

            try:

                df = pd.read_csv(
                    caminho,
                    encoding="utf-8-sig",
                    sep=","
                )

                st.success(f"Arquivo carregado: {caminho}")

                break

            except Exception as e:

                st.error(f"Erro ao ler CSV: {e}")

    if df.empty:
        st.error(f"Arquivo '{nome_arquivo}' não encontrado.")
        st.stop()

    # =================================================
    # LIMPEZA
    # =================================================

    df.columns = [col.strip() for col in df.columns]

    # =================================================
    # CONVERSÃO DO ANO
    # =================================================

    if 'Ano' in df.columns:

        df['Ano'] = pd.to_numeric(
            df['Ano'],
            errors='coerce'
        )

        df = df.dropna(subset=['Ano'])

        df['Ano'] = df['Ano'].astype(int)

    else:

        st.error("Coluna 'Ano' não encontrada.")
        st.stop()

    # =================================================
    # CÁLCULOS EPIDEMIOLÓGICOS
    # =================================================

    cols_obitos = [
        'Óbitos<1a_Diarr',
        'Óbitos<1a_IRA',
        'Óbitos<1a_OutCau'
    ]

    cols_existentes = [
        col for col in cols_obitos
        if col in df.columns
    ]

    if len(cols_existentes) > 0:

        df['Total_Obitos_Inf'] = (
            df[cols_existentes]
            .sum(axis=1)
        )

    else:

        df['Total_Obitos_Inf'] = 0

    # Mortalidade Infantil

    if (
        'Total_Obitos_Inf' in df.columns
        and 'Nascidos_Vivos' in df.columns
    ):

        total_nv = (
            pd.to_numeric(
                df['Nascidos_Vivos'],
                errors='coerce'
            )
            .fillna(0)
        )

        df['Taxa_Mortalidade_Infantil'] = (
            df['Total_Obitos_Inf']
            / total_nv.replace(0, pd.NA)
        ) * 1000

        df['Taxa_Mortalidade_Infantil'] = (
            df['Taxa_Mortalidade_Infantil']
            .fillna(0)
            .round(2)
        )

    else:

        df['Taxa_Mortalidade_Infantil'] = 0

    # Cobertura Vacinal

    if (
        'Cr<1a_c/Vacin.dia' in df.columns
        and 'Crianças_<1_ano' in df.columns
    ):

        total_criancas = (
            pd.to_numeric(
                df['Crianças_<1_ano'],
                errors='coerce'
            )
            .fillna(0)
        )

        df['Perc_Vacina_Dia'] = (
            df['Cr<1a_c/Vacin.dia']
            / total_criancas.replace(0, pd.NA)
        ) * 100

        df['Perc_Vacina_Dia'] = (
            df['Perc_Vacina_Dia']
            .fillna(0)
            .round(2)
        )

    else:

        df['Perc_Vacina_Dia'] = 0

    return df.sort_values('Ano')

# =====================================================
# DICIONÁRIO
# =====================================================

def gerar_dicionario():

    dados = {
        "Coluna": [
            "Ano",
            "Nascidos_Vivos",
            "Taxa_Mortalidade_Infantil",
            "Nº_Visitas",
            "Hiperten.Cadastr.",
            "Diabetes_Cadastr.",
            "Tubercul.Cadastr.",
            "Hansenia.Cadastr.",
            "Hosp.Abuso_Álcool"
        ],

        "Descrição": [
            "Ano de referência",
            "Quantidade de nascidos vivos",
            "Óbitos menores de 1 ano por 1000 nascidos vivos",
            "Visitas domiciliares",
            "Hipertensos cadastrados",
            "Diabéticos cadastrados",
            "Casos de Tuberculose",
            "Casos de Hanseníase",
            "Internações por abuso de álcool"
        ]
    }

    return pd.DataFrame(dados)

# =====================================================
# CARREGAR DATAFRAME
# =====================================================

df = carregar_dados()

if df.empty:
    st.error("O CSV foi carregado vazio.")
    st.stop()

df_dic = gerar_dicionario()

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("📊 BI Analytics")

anos = sorted(df['Ano'].unique())

ano_inicio, ano_fim = st.sidebar.select_slider(
    "Período",
    options=anos,
    value=(anos[0], anos[-1])
)

df_filtrado = df[
    (df['Ano'] >= ano_inicio)
    & (df['Ano'] <= ano_fim)
]

# =====================================================
# FUNÇÃO DELTA
# =====================================================

def calcular_delta(coluna):

    if coluna not in df_filtrado.columns:
        return 0

    if len(df_filtrado) < 2:
        return 0

    valores = (
        df_filtrado
        .sort_values('Ano')[coluna]
        .tolist()
    )

    return valores[-1] - valores[-2]

# =====================================================
# TÍTULO
# =====================================================

st.title("🏥 Sistema de Monitoramento Estratégico da Saúde")

st.info(
    "Indicadores epidemiológicos baseados em dados anuais da Estratégia Saúde da Família."
)

# =====================================================
# KPIs
# =====================================================

k1, k2, k3, k4 = st.columns(4)

# =====================================================
# KPI 1
# =====================================================

with k1:

    valor = (
        df_filtrado['Nº_Visitas'].sum()
        if 'Nº_Visitas' in df_filtrado.columns
        else 0
    )

    st.metric(
        "Total de Visitas",
        f"{valor:,.0f}".replace(",", "."),
        delta=int(calcular_delta('Nº_Visitas'))
    )

# =====================================================
# KPI 2
# =====================================================

with k2:

    if (
        'Taxa_Mortalidade_Infantil' in df_filtrado.columns
        and not df_filtrado.empty
    ):
        valor = (
            df_filtrado['Taxa_Mortalidade_Infantil']
            .iloc[-1]
        )
    else:
        valor = 0

    st.metric(
        "Taxa Mortalidade Infantil",
        valor,
        delta=f"{calcular_delta('Taxa_Mortalidade_Infantil'):.2f}",
        delta_color="inverse"
    )

# =====================================================
# KPI 3
# =====================================================

with k3:

    if (
        'Perc_Vacina_Dia' in df_filtrado.columns
        and not df_filtrado.empty
    ):
        valor = (
            df_filtrado['Perc_Vacina_Dia']
            .iloc[-1]
        )
    else:
        valor = 0

    st.metric(
        "% Cobertura Vacinal",
        f"{valor:.2f}%",
        delta=f"{calcular_delta('Perc_Vacina_Dia'):.2f}%"
    )

# =====================================================
# KPI 4
# =====================================================

with k4:

    if (
        'NascVivos_<2500g' in df_filtrado.columns
        and 'Nascidos_Vivos' in df_filtrado.columns
    ):

        total_nv = df_filtrado['Nascidos_Vivos'].sum()

        if total_nv > 0:

            baixo_peso = (
                df_filtrado['NascVivos_<2500g'].sum()
                / total_nv
            ) * 100

        else:
            baixo_peso = 0

    else:
        baixo_peso = 0

    st.metric(
        "% Baixo Peso",
        f"{baixo_peso:.2f}%"
    )
# =====================================================
# INFORMAÇÕES EPIDEMIOLÓGICAS
# =====================================================

st.markdown("---")
st.subheader("📌 Indicadores Epidemiológicos")

card1, card2, card3 = st.columns(3)

with card1:

    taxa = (
        df_filtrado['Taxa_Mortalidade_Infantil'].iloc[-1]
        if 'Taxa_Mortalidade_Infantil' in df_filtrado.columns
        else 0
    )

    st.success(
        f"""
        ### Mortalidade Infantil

        Taxa atual: {taxa:.2f} óbitos por mil nascidos vivos.

        A mortalidade infantil é um dos principais indicadores de qualidade da saúde pública.
        """
    )

with card2:

    st.info(
        """
        ### Cobertura Vacinal

        A vacinação reduz significativamente:

        - mortalidade infantil
        - doenças respiratórias
        - surtos epidemiológicos
        """
    )

with card3:

    st.warning(
        """
        ### Fatores de Risco

        Principais fatores associados:

        - baixo peso ao nascer
        - ausência de pré-natal
        - desnutrição
        - baixa vacinação
        """
    )
# =====================================================
# ABAS
# =====================================================

tabs = st.tabs([
    "🏠 Visão Geral",
    "📈 Atendimento",
    "👶 Saúde Infantil",
    "🤰 Saúde Materna",
    "🦠 Doenças",
    "🏥 Internações",
    "📊 Correlação",
    "📂 Dados"
])

# =====================================================
# ABA 1 - VISÃO GERAL
# =====================================================

with tabs[0]:

    st.markdown("## 🏥 Visão Geral Epidemiológica")

    col1, col2 = st.columns([2,1])

    with col1:

        fig = go.Figure()

        if 'Nascidos_Vivos' in df_filtrado.columns:

            fig.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Nascidos_Vivos'],
                    name='Nascidos Vivos',
                    marker_color=COR_PRIMARIA,
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Nascidos:</b> %{y}<br>" +
                    "<extra></extra>"
                )
            )

        if 'Total_Obitos_Inf' in df_filtrado.columns:

            fig.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Total_Obitos_Inf'],
                    mode='lines+markers',
                    name='Óbitos <1 ano',
                    line=dict(color=COR_SECUNDARIA, width=4),
                    marker=dict(size=10),
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Óbitos:</b> %{y}<br>" +
                    "<extra></extra>"
                )
            )

        fig.update_layout(

            title="Nascimentos x Mortalidade Infantil",

            hovermode="x unified",

            plot_bgcolor="white",
            paper_bgcolor="white",

            title_font=dict(size=22),

            xaxis=dict(
                showgrid=False
            ),

            yaxis=dict(
                gridcolor="#E5E5E5"
            ),

            legend=dict(
                orientation="h",
                y=1.1
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.markdown(f"""
        <div style="
            background-color:{COR_CARD};
            padding:25px;
            border-radius:18px;
            box-shadow:0px 4px 18px rgba(0,0,0,0.08);
            border-left:8px solid {COR_PRIMARIA};
        ">

        <h3 style="color:{COR_PRIMARIA};">
            Indicadores Estratégicos
        </h3>

        <p>
        A mortalidade infantil é um dos principais indicadores
        de qualidade da saúde pública e do saneamento básico.
        </p>

        <p>
        O monitoramento contínuo permite identificar tendências
        epidemiológicas e apoiar decisões governamentais.
        </p>

        </div>
        """, unsafe_allow_html=True)

# =====================================================
# ABA 2 - ATENDIMENTO
# =====================================================

with tabs[1]:

    st.markdown("## 📈 Indicadores de Atendimento")

    colunas = []

    if 'Nº_Visitas' in df_filtrado.columns:
        colunas.append('Nº_Visitas')

    if 'Famílias_Acompanh.' in df_filtrado.columns:
        colunas.append('Famílias_Acompanh.')

    if len(colunas) > 0:

        fig = px.line(
            df_filtrado,
            x='Ano',
            y=colunas,
            markers=True,
            color_discrete_sequence=[
                COR_PRIMARIA,
                "#1565C0"
            ]
        )

        fig.update_traces(
            line=dict(width=4),
            marker=dict(size=9),
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Valor:</b> %{y}<br>" +
            "<extra></extra>"
        )

        fig.update_layout(

            title="Evolução dos Atendimentos",

            hovermode="x unified",

            plot_bgcolor="white",
            paper_bgcolor="white",

            xaxis=dict(showgrid=False),
            yaxis=dict(gridcolor="#ECECEC")
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# ABA 3 - SAÚDE INFANTIL
# =====================================================

with tabs[2]:

    st.markdown("## 👶 Saúde Infantil")

    c1, c2 = st.columns(2)

    with c1:

        cols_pizza = [
            'Óbitos<1a_Diarr',
            'Óbitos<1a_IRA',
            'Óbitos<1a_OutCau'
        ]

        cols_existentes = [
            col for col in cols_pizza
            if col in df_filtrado.columns
        ]

        if len(cols_existentes) > 0:

            dados = (
                df_filtrado[cols_existentes]
                .sum()
                .reset_index()
            )

            dados.columns = ['Causa', 'Total']

            fig = px.pie(
                dados,
                values='Total',
                names='Causa',
                hole=0.6,
                color_discrete_sequence=[
                    COR_PRIMARIA,
                    "#EF5350",
                    "#FFB300"
                ]
            )

            fig.update_traces(
                hovertemplate=
                "<b>Causa:</b> %{label}<br>" +
                "<b>Total:</b> %{value}<br>" +
                "<b>Percentual:</b> %{percent}<br>" +
                "<extra></extra>"
            )

            fig.update_layout(
                title="Distribuição dos Óbitos Infantis",
                paper_bgcolor="white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with c2:

        if 'Taxa_Mortalidade_Infantil' in df_filtrado.columns:

            fig = px.area(
                df_filtrado,
                x='Ano',
                y='Taxa_Mortalidade_Infantil',
                color_discrete_sequence=[COR_PRIMARIA]
            )

            fig.update_traces(
                hovertemplate=
                "<b>Ano:</b> %{x}<br>" +
                "<b>Taxa:</b> %{y:.2f}<br>" +
                "<extra></extra>"
            )

            fig.update_layout(

                title="Taxa de Mortalidade Infantil",

                hovermode="x unified",

                plot_bgcolor="white",
                paper_bgcolor="white",

                xaxis=dict(showgrid=False),
                yaxis=dict(gridcolor="#ECECEC")
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

# =====================================================
# ABA 4 - SAÚDE MATERNA
# =====================================================

with tabs[3]:

    st.markdown("## 🤰 Saúde Materna")

    cols = []

    if 'Nº_Gestantes' in df_filtrado.columns:
        cols.append('Nº_Gestantes')

    if 'Gest.c/PN_1ºTrim' in df_filtrado.columns:
        cols.append('Gest.c/PN_1ºTrim')

    if len(cols) > 0:

        fig = px.bar(
            df_filtrado,
            x='Ano',
            y=cols,
            barmode='group',
            color_discrete_sequence=[
                COR_PRIMARIA,
                "#F06292"
            ]
        )

        fig.update_traces(
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Quantidade:</b> %{y}<br>" +
            "<extra></extra>"
        )

        fig.update_layout(

            title="Acompanhamento Pré-Natal",

            hovermode="x unified",

            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# ABA 6 - INTERNAÇÕES
# =====================================================

with tabs[5]:

    st.markdown("## 🏥 Internações")

    cols = [
        'Hosp.<5a_Pneumonia',
        'Hosp.<5a_Desitrat',
        'Hosp.Abuso_Álcool'
    ]

    cols_existentes = [
        col for col in cols
        if col in df_filtrado.columns
    ]

    if len(cols_existentes) > 0:

        fig = px.bar(
            df_filtrado,
            x='Ano',
            y=cols_existentes,
            barmode='group',
            color_discrete_sequence=[
                COR_PRIMARIA,
                "#FB8C00",
                "#5E35B1"
            ]
        )

        fig.update_traces(
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Internações:</b> %{y}<br>" +
            "<extra></extra>"
        )

        fig.update_layout(

            title="Internações por Causa",

            hovermode="x unified",

            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

# =====================================================
# ABA 7 - CORRELAÇÃO
# =====================================================

with tabs[6]:

    st.markdown("## 📊 Correlação entre Indicadores")

    cols_corr = []

    for col in [
        'Nº_Visitas',
        'Taxa_Mortalidade_Infantil',
        'Perc_Vacina_Dia'
    ]:
        if col in df_filtrado.columns:
            cols_corr.append(col)

    if len(cols_corr) > 1:

        corr = (
            df_filtrado[cols_corr]
            .corr()
        )

        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale=[
                "#FFF5F5",
                "#F28B82",
                "#B5121B"
            ]
        )

        fig.update_traces(
            hovertemplate=
            "<b>X:</b> %{x}<br>" +
            "<b>Y:</b> %{y}<br>" +
            "<b>Correlação:</b> %{z:.2f}<br>" +
            "<extra></extra>"
        )

        fig.update_layout(
            title="Mapa de Correlação",
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
# =====================================================
# ABA 8 - DADOS
# =====================================================

with tabs[7]:

    st.subheader("📖 Dicionário de Dados")

    st.dataframe(
        df_dic,
        use_container_width=True
    )

    st.markdown("---")

    st.subheader("📂 Dados Consolidados")

    st.dataframe(
        df_filtrado,
        use_container_width=True
    )

    csv = (
        df_filtrado
        .to_csv(index=False)
        .encode('utf-8-sig')
    )

    st.download_button(
        "📥 Baixar CSV",
        csv,
        "dados_filtrados.csv",
        "text/csv"
    )