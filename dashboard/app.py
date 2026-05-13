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
# IDENTIDADE VISUAL IESB
# =====================================================

COR_PRIMARIA = "#A6192E"
COR_SECUNDARIA = "#6C757D"
COR_FUNDO = "#F5F7FA"
COR_CARD = "#FFFFFF"
COR_TEXTO = "#1F1F1F"

PALETA = {
    "azul": "#0056B3",
    "vermelho": "#A6192E",
    "verde": "#198754",
    "laranja": "#FD7E14",
    "roxo": "#6F42C1",
    "cinza": "#6C757D",
    "amarelo": "#FFC107"
}
# =====================================================
# CSS CUSTOMIZADO
# =====================================================
st.markdown("""
<style>

.main {
    background-color: #F5F7FA;
}

section[data-testid="stSidebar"] {
    background-color: #A6192E;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 15px;
    border-left: 6px solid #A6192E;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

[data-testid="stMetricValue"] {
    font-size: 30px;
    color: #A6192E;
    font-weight: bold;
}

.stTabs [data-baseweb="tab"] {
    background-color: white;
    border-radius: 10px 10px 0px 0px;
    padding: 12px 20px;
    margin-right: 4px;
}

.stTabs [aria-selected="true"] {
    background-color: #A6192E !important;
    color: white !important;
}

h1, h2, h3 {
    color: #A6192E;
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

# =====================================================
# DICIONÁRIO
# =====================================================

def gerar_dicionario():

    dados = {
        "Coluna": [

            # =================================================
            # GERAIS
            # =================================================

            "Ano",
            "Nascidos_Vivos",
            "NascVivos_Pesados",
            "NascVivos_<2500g",

            # =================================================
            # ÓBITOS INFANTIS
            # =================================================

            "Óbitos<28d_Diarr",
            "Óbitos<28d_IRA",
            "Óbitos<28d_OutCau",
            "Óbit_28a11m_Diarr",
            "Óbit_28a11m_IRA",
            "Óbit_28a11m_OutCau",
            "Óbitos<1a_Diarr",
            "Óbitos<1a_IRA",
            "Óbitos<1a_OutCau",

            # =================================================
            # ÓBITOS FEMININOS / VIOLÊNCIA
            # =================================================

            "Óbitos_Fem.10a14a",
            "Óbitos_Fem.15a49a",
            "Óbitos_Adol_violên",
            "Outros_óbitos",

            # =================================================
            # INTERNAÇÕES
            # =================================================

            "Hosp.<5a_Pneumonia",
            "Hosp.<5a_Desitrat",
            "Hosp.Abuso_Álcool",
            "Hosp.Complic.Diab.",
            "Hosp.p/Out.Causas",
            "Hosp.Psiquiátricas",

            # =================================================
            # ATENDIMENTO
            # =================================================

            "Nº_Visitas",
            "Famílias_Acompanh.",

            # =================================================
            # SAÚDE MATERNA
            # =================================================

            "Nº_Gestantes",
            "Nº_Gest._Acompanh",
            "Nº_Gest._<20_anos",
            "Gest.c/PN_no_mês",
            "Gest.c/PN_1ºTrim",
            "Gest.c/Vacina_Dia",

            # =================================================
            # SAÚDE INFANTIL
            # =================================================

            "Crianças_até_4m",
            "Cr<4m_AleitMatExcl",
            "Cr<4m_Aleit_Misto",
            "Crianças_<1_ano",
            "Cr<1a_c/Vacin.dia",
            "Cr<1a_pesadas",
            "Cr<1a_desnutridas",
            "Cr_12-23meses",
            "Cr_12-23m_Vac.Dia",
            "Cr_12-23m_Pesadas",
            "Cr_12-23m_Desnutr.",
            "Cr<2a_c/diarr",
            "Cr<2a_usaram_TRO",
            "Cr<2a_c/IRA",

            # =================================================
            # DOENÇAS
            # =================================================

            "Diabetes_Cadastr.",
            "Diabetes_Acompan.",
            "Hiperten.Cadastr.",
            "Hiperten.Acompan.",
            "Tubercul.Cadastr.",
            "Tubercul_Acompan.",
            "Hansenia.Cadastr.",
            "Hansenia.Acompan.",

            # =================================================
            # INDICADORES CALCULADOS
            # =================================================

            "Total_Obitos_Inf",
            "Taxa_Mortalidade_Infantil",
            "Perc_Vacina_Dia"
        ],

        "Descrição": [

            # =================================================
            # GERAIS
            # =================================================

            "Ano de referência dos dados",
            "Quantidade de nascidos vivos",
            "Nascidos vivos acompanhados/pesados",
            "Nascidos vivos com peso inferior a 2500g",

            # =================================================
            # ÓBITOS INFANTIS
            # =================================================

            "Óbitos neonatais por diarreia (<28 dias)",
            "Óbitos neonatais por infecção respiratória aguda (<28 dias)",
            "Óbitos neonatais por outras causas (<28 dias)",
            "Óbitos de 28 dias a 11 meses por diarreia",
            "Óbitos de 28 dias a 11 meses por IRA",
            "Óbitos de 28 dias a 11 meses por outras causas",
            "Óbitos infantis (<1 ano) por diarreia",
            "Óbitos infantis (<1 ano) por IRA",
            "Óbitos infantis (<1 ano) por outras causas",

            # =================================================
            # ÓBITOS FEMININOS / VIOLÊNCIA
            # =================================================

            "Óbitos femininos entre 10 e 14 anos",
            "Óbitos femininos entre 15 e 49 anos",
            "Óbitos de adolescentes relacionados à violência",
            "Outros óbitos registrados",

            # =================================================
            # INTERNAÇÕES
            # =================================================

            "Internações de crianças <5 anos por pneumonia",
            "Internações de crianças <5 anos por desidratação",
            "Internações relacionadas ao abuso de álcool",
            "Internações por complicações da diabetes",
            "Internações por outras causas",
            "Internações psiquiátricas",

            # =================================================
            # ATENDIMENTO
            # =================================================

            "Número de visitas domiciliares",
            "Famílias acompanhadas pela ESF",

            # =================================================
            # SAÚDE MATERNA
            # =================================================

            "Número de gestantes cadastradas",
            "Gestantes acompanhadas",
            "Gestantes menores de 20 anos",
            "Gestantes com pré-natal no mês",
            "Gestantes com pré-natal iniciado no 1º trimestre",
            "Gestantes vacinadas em dia",

            # =================================================
            # SAÚDE INFANTIL
            # =================================================

            "Crianças acompanhadas até 4 meses",
            "Aleitamento materno exclusivo até 4 meses",
            "Aleitamento misto até 4 meses",
            "Crianças menores de 1 ano",
            "Crianças <1 ano com vacinação em dia",
            "Crianças <1 ano pesadas",
            "Crianças <1 ano desnutridas",
            "Crianças entre 12 e 23 meses",
            "Crianças 12-23 meses vacinadas",
            "Crianças 12-23 meses pesadas",
            "Crianças 12-23 meses desnutridas",
            "Crianças menores de 2 anos com diarreia",
            "Uso de TRO em crianças menores de 2 anos",
            "Crianças menores de 2 anos com IRA",

            # =================================================
            # DOENÇAS
            # =================================================

            "Pacientes diabéticos cadastrados",
            "Pacientes diabéticos acompanhados",
            "Pacientes hipertensos cadastrados",
            "Pacientes hipertensos acompanhados",
            "Casos cadastrados de tuberculose",
            "Casos acompanhados de tuberculose",
            "Casos cadastrados de hanseníase",
            "Casos acompanhados de hanseníase",

            # =================================================
            # INDICADORES CALCULADOS
            # =================================================

            "Total de óbitos infantis calculado",
            "Óbitos menores de 1 ano por mil nascidos vivos",
            "Percentual de vacinação infantil"
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
# PADRONIZAÇÃO DOS GRÁFICOS
# =====================================================

def estilizar_grafico(fig):

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=14,
            color=COR_TEXTO
        ),
        title_font=dict(
            size=22,
            color=COR_PRIMARIA
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="#DDD",
            borderwidth=1
        )
    )

    return fig

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
# ABA 1
# =====================================================

with tabs[0]:

    col1, col2 = st.columns([2, 1])

    with col1:

        fig = go.Figure()

        if 'Nascidos_Vivos' in df_filtrado.columns:

            fig.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Nascidos_Vivos'],
                    name='Nascidos Vivos'
                )
            )

        if 'Total_Obitos_Inf' in df_filtrado.columns:

            fig.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Total_Obitos_Inf'],
                    mode='lines+markers',
                    name='Óbitos <1 ano'
                )
            )

        fig.update_layout(
            title="Nascimentos x Óbitos Infantis"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with col2:

        st.subheader("📝 Informações")

        st.success(
            f"Análise epidemiológica entre {ano_inicio} e {ano_fim}."
        )
# =====================================================
# ABA 2 - ATENDIMENTO
# =====================================================

with tabs[1]:

    st.subheader("📈 Atendimento")

    colunas = []

    if 'Nº_Visitas' in df_filtrado.columns:
        colunas.append('Nº_Visitas')

    if 'Famílias_Acompanh.' in df_filtrado.columns:
        colunas.append('Famílias_Acompanh.')

    if len(colunas) > 0:

        try:

            fig = px.line(
                df_filtrado,
                x='Ano',
                y=colunas,
                markers=True,
                title="Evolução do Atendimento"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:
            st.warning(f"Erro: {e}")

# =====================================================
# ABA 3 - SAÚDE INFANTIL
# =====================================================

with tabs[2]:

    st.subheader("👶 Saúde Infantil")

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

            try:

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
                    hole=0.5,
                    title="Óbitos Infantis"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            except Exception as e:
                st.warning(f"Erro: {e}")

    with c2:

        if 'Taxa_Mortalidade_Infantil' in df_filtrado.columns:

            try:

                fig = px.area(
                    df_filtrado,
                    x='Ano',
                    y='Taxa_Mortalidade_Infantil',
                    title="Taxa de Mortalidade Infantil"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            except Exception as e:
                st.warning(f"Erro: {e}")

# =====================================================
# ABA 4 - SAÚDE MATERNA
# =====================================================

with tabs[3]:

    st.subheader("🤰 Saúde Materna e Gestacional")

    st.markdown("""
    Esta análise apresenta a evolução do acompanhamento pré-natal,
    gestação na adolescência e possíveis relações com doenças crônicas.
    """)

    # =================================================
    # CARDS
    # =================================================

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        total_gest = (
            df_filtrado['Nº_Gestantes'].sum()
            if 'Nº_Gestantes' in df_filtrado.columns
            else 0
        )

        st.metric(
            "Gestantes",
            f"{total_gest:,.0f}".replace(",", ".")
        )

    with c2:

        gest_adol = (
            df_filtrado['Nº_Gest._<20_anos'].sum()
            if 'Nº_Gest._<20_anos' in df_filtrado.columns
            else 0
        )

        st.metric(
            "Gestantes <20 anos",
            f"{gest_adol:,.0f}".replace(",", ".")
        )

    with c3:

        pre_natal = (
            df_filtrado['Gest.c/PN_1ºTrim'].sum()
            if 'Gest.c/PN_1ºTrim' in df_filtrado.columns
            else 0
        )

        st.metric(
            "Pré-natal 1º trimestre",
            f"{pre_natal:,.0f}".replace(",", ".")
        )

    with c4:

        vacina = (
            df_filtrado['Gest.c/Vacina_Dia'].sum()
            if 'Gest.c/Vacina_Dia' in df_filtrado.columns
            else 0
        )

        st.metric(
            "Gestantes vacinadas",
            f"{vacina:,.0f}".replace(",", ".")
        )

    st.markdown("---")

    # =================================================
    # GRÁFICOS
    # =================================================

    col1, col2 = st.columns(2)

    # =================================================
    # EVOLUÇÃO GESTACIONAL
    # =================================================

    with col1:

        cols_materna = []

        for col in [
            'Nº_Gestantes',
            'Nº_Gest._<20_anos',
            'Gest.c/PN_1ºTrim'
        ]:

            if col in df_filtrado.columns:
                cols_materna.append(col)

        fig_materna = px.bar(
            df_filtrado,
            x='Ano',
            y=cols_materna,
            barmode='group',
            title='Evolução da Saúde Materna',
            color_discrete_sequence=[
                '#990000',
                '#CC0000',
                '#004A99'
            ]
        )

        fig_materna.update_traces(
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Quantidade:</b> %{y}<extra></extra>"
        )

        fig_materna.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(size=14),
            title_font_size=22
        )

        st.plotly_chart(
            fig_materna,
            use_container_width=True
        )

    # =================================================
    # CORRELAÇÃO GESTAÇÃO X DOENÇAS
    # =================================================

    with col2:

        rel_cols = []

        for col in [
            'Nº_Gest._<20_anos',
            'Diabetes_Cadastr.',
            'Hiperten.Cadastr.',
            'Taxa_Mortalidade_Infantil'
        ]:

            if col in df_filtrado.columns:
                rel_cols.append(col)

        if len(rel_cols) >= 2:

            corr_materna = (
                df_filtrado[rel_cols]
                .corr(numeric_only=True)
                .round(2)
            )

            fig_corr = px.imshow(
                corr_materna,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                title='Gestação x Doenças'
            )

            fig_corr.update_traces(
                hovertemplate=
                "<b>X:</b> %{x}<br>" +
                "<b>Y:</b> %{y}<br>" +
                "<b>Correlação:</b> %{z}<extra></extra>"
            )

            fig_corr.update_layout(
                height=500,
                plot_bgcolor='white',
                paper_bgcolor='white',
                title_font_size=22
            )

            st.plotly_chart(
                fig_corr,
                use_container_width=True
            )

    st.markdown("---")

    # =================================================
    # ANÁLISE AUTOMÁTICA
    # =================================================

    st.info("""
    ### 📌 Análise da Saúde Materna

    • O acompanhamento pré-natal apresentou crescimento ao longo dos anos.  

    • Gestação na adolescência continua sendo um fator importante de risco social e obstétrico.  

    • Hipertensão e diabetes possuem impacto significativo na gravidez,
    aumentando o risco de parto prematuro e complicações neonatais.  

    • A vacinação gestacional e o pré-natal precoce ajudam na redução
    da mortalidade infantil e complicações maternas.  

    • Regiões com menor acesso ao saneamento e atenção básica
    tendem a apresentar piores indicadores materno-infantis.
    """)

    # =================================================
    # QUADRO DE RISCO
    # =================================================

    risco1, risco2, risco3 = st.columns(3)

    with risco1:

        st.warning("""
        ### ⚠️ Gravidez na Adolescência

        • Maior risco obstétrico  
        • Maior evasão escolar  
        • Relação com vulnerabilidade social  
        • Necessidade de pré-natal intensivo
        """)

    with risco2:

        st.error("""
        ### ❤️ Hipertensão na Gravidez

        • Pode causar pré-eclâmpsia  
        • Risco de parto prematuro  
        • Relacionada à mortalidade materna  
        • Exige acompanhamento contínuo
        """)

    with risco3:

        st.info("""
        ### 🩺 Diabetes Gestacional

        • Pode aumentar peso fetal  
        • Risco de parto complicado  
        • Relacionada à obesidade  
        • Controle alimentar é essencial
        """)
# =====================================================
# ABA 6 - INTERNAÇÕES
# =====================================================

with tabs[5]:

    st.subheader("🏥 Internações Hospitalares")

    internacoes = {
        "Pneumonia": "Hosp.<5a_Pneumonia",
        "Desidratação": "Hosp.<5a_Desitrat",
        "Abuso de Álcool": "Hosp.Abuso_Álcool"
    }

    for nome, coluna in internacoes.items():

        if coluna in df_filtrado.columns:

            fig = go.Figure()

            fig.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado[coluna],
                    marker_color=COR_PRIMARIA,
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Internações:</b> %{y}<extra></extra>"
                )
            )

            fig.update_layout(
                title=f"Internações por {nome}"
            )

            estilizar_grafico(fig)

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            if nome == "Pneumonia":

                st.warning("""
                A pneumonia possui forte relação com vulnerabilidade social,
                baixa vacinação e saneamento inadequado.
                """)

            elif nome == "Desidratação":

                st.error("""
                Casos de desidratação infantil possuem forte relação
                com falta de saneamento básico e água potável.
                """)

            elif nome == "Abuso de Álcool":

                st.info("""
                Internações relacionadas ao álcool possuem impacto
                social e psiquiátrico elevado.
                """)

# =====================================================
# ABA 7 - CORRELAÇÃO
# =====================================================

with tabs[6]:

    st.subheader("📊 Correlação Epidemiológica")

    st.markdown("""
    A correlação mede o grau de relação entre variáveis numéricas.

    - Valores próximos de +1 → relação positiva forte
    - Valores próximos de -1 → relação negativa forte
    - Valores próximos de 0 → pouca ou nenhuma relação
    """)

    cols_corr = []

    for col in [
        'Nº_Visitas',
        'Taxa_Mortalidade_Infantil',
        'Perc_Vacina_Dia',
        'Hiperten.Cadastr.',
        'Diabetes_Cadastr.',
        'Tubercul.Cadastr.',
        'Hansenia.Cadastr.',
        'Hosp.<5a_Pneumonia'
    ]:

        if col in df_filtrado.columns:
            cols_corr.append(col)

    if len(cols_corr) > 1:

        corr = (
            df_filtrado[cols_corr]
            .corr(numeric_only=True)
            .round(2)
        )

        fig = px.imshow(
            corr,
            text_auto=True,
            color_continuous_scale='RdBu_r',
            aspect='auto',
            title='Mapa de Correlação Epidemiológica'
        )

        fig.update_traces(
            hovertemplate=
            "<b>Variável X:</b> %{x}<br>" +
            "<b>Variável Y:</b> %{y}<br>" +
            "<b>Correlação:</b> %{z}<extra></extra>"
        )

        fig.update_layout(
            height=700,
            title_font_size=24,
            hovermode='closest',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(
                family="Arial",
                size=14,
                color="#1F2937"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.info("""
        ### 📌 Análise Automática

        • Hipertensão e Diabetes possuem correlação extremamente alta.  
        • A cobertura vacinal apresenta relação positiva com visitas domiciliares.  
        • Tuberculose e Hanseníase possuem associação moderada com indicadores sociais.  
        • Pneumonia infantil apresenta baixa correlação com doenças crônicas.
        """)

    else:

        st.warning("Não há colunas suficientes para calcular correlação.")

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