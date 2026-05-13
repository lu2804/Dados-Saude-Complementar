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
    /* 1. Fundo Geral da Página */
    .main {
        background-color: #F5F7FA;
    }

    /* 2. Estilização da Sidebar (Vinho) */
    section[data-testid="stSidebar"] {
        background-color: #A6192E;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    /* 3. Cards de Métricas (KPIs) */
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

    /* 4. Estilização das Abas */
    /* Abas NÃO selecionadas (Tom Creme/Bege) */
    .stTabs [data-baseweb="tab"] {
        background-color: #FDF5E6 !important; /* Cor Creme/OldLace */
        border-radius: 10px 10px 0px 0px;
        padding: 12px 20px;
        margin-right: 4px;
        border: 1px solid #f0ede9; /* Borda sutil em tom trigo */
        transition: all 0.3s ease;
    }

    /* Texto das abas NÃO selecionadas (Preto para contraste) */
    .stTabs [data-baseweb="tab"] p {
        color: #333333 !important;
        font-weight: 500;
    }

    /* Aba SELECIONADA (Vinho com texto Branco) */
    .stTabs [aria-selected="true"] {
        background-color: #A6192E !important;
        border: 1px solid #A6192E !important;
    }

    .stTabs [aria-selected="true"] p {
        color: white !important;
        font-weight: bold;
    }

    /* 5. Títulos e Subtítulos */
    h1, h2, h3 {
        color: #A6192E;
    }
    
    /* 6. Ajuste de Hover (Passar o mouse) nas abas */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #F5DEB3 !important; /* Escurece o bege levemente no hover */
    }

</style>
""", unsafe_allow_html=True)

# =====================================================
# NOMES LEGÍVEIS DOS GRÁFICOS
# =====================================================

nomes_legiveis = {
    'Nº_Visitas': 'Visitas Domiciliares',
    'Famílias_Acompanh.': 'Famílias Acompanhadas',
    'Óbitos<1a_Diarr': 'Óbitos por Diarreia',
    'Óbitos<1a_IRA': 'Óbitos por Infecção Respiratória',
    'Óbitos<1a_OutCau': 'Óbitos por Outras Causas',
    'Cr<1a_c/Vacin.dia': 'Vacinação em Dia',
    'Cr<1a_desnutridas': 'Desnutrição Infantil',
    'Cr_12-23m_Desnutr.': 'Desnutrição 12-23 meses',
    'Cr<4m_AleitMatExcl': 'Aleitamento Exclusivo',
    'Cr<4m_Aleit_Misto': 'Aleitamento Misto',
    'Cr<2a_c/diarr': 'Casos de Diarreia',
    'Cr<2a_c/IRA': 'Infecção Respiratória',
    'Hosp.<5a_Pneumonia': 'Internações Pneumonia',
    'Hosp.<5a_Desitrat': 'Internações Desidratação',
    'Hiperten.Cadastr.': 'Hipertensão',
    'Diabetes_Cadastr.': 'Diabetes',
    'Tubercul.Cadastr.': 'Tuberculose',
    'Hansenia.Cadastr.': 'Hanseníase',
    'Nº_Gestantes': 'Gestantes',
    'Nº_Gest._<20_anos': 'Gestantes <20 anos',
    'Gest.c/PN_1ºTrim': 'Pré-natal 1º Trimestre',
    'Gest.c/Vacina_Dia': 'Vacinação Gestacional'
}

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

   # Mortalidade Infantil (Transformada para Porcentagem)
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

        # Cálculo para % (porcentagem)
        df['Taxa_Mortalidade_Infantil'] = (
            df['Total_Obitos_Inf']
            / total_nv.replace(0, pd.NA)
        ) * 100

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
# ABA 1 - VISÃO GERAL
# =====================================================

with tabs[0]:

    st.subheader("🏠 Panorama Geral da Saúde Pública")

    st.markdown("""
    Esta visão consolida os principais indicadores epidemiológicos,
    permitindo acompanhar a evolução da saúde pública, mortalidade infantil,
    vacinação e assistência básica ao longo dos anos.
    """)

    # =================================================
    # KPIs
    # =================================================

    k1, k2, k3, k4 = st.columns(4)

    with k1:

        valor = (
            df_filtrado['Nº_Visitas'].sum()
            if 'Nº_Visitas' in df_filtrado.columns
            else 0
        )

        st.metric(
            "👨‍⚕️ Total de Visitas",
            f"{valor:,.0f}".replace(",", "."),
            delta=int(calcular_delta('Nº_Visitas'))
        )

    with k2:

        if 'Taxa_Mortalidade_Infantil' in df_filtrado.columns and not df_filtrado.empty:
            valor = df_filtrado['Taxa_Mortalidade_Infantil'].iloc[-1]
        else:
            valor = 0

        st.metric(
            "👶 Mortalidade Infantil",
            f"{valor:.2f}%",  # Adicionado o %
            delta=f"{calcular_delta('Taxa_Mortalidade_Infantil'):.2f}%", # Adicionado o %
            delta_color="inverse"
        )

    with k3:

        valor = (
            df_filtrado['Perc_Vacina_Dia'].iloc[-1]
            if 'Perc_Vacina_Dia' in df_filtrado.columns
            else 0
        )

        st.metric(
            "💉 Cobertura Vacinal",
            f"{valor:.2f}%",
            delta=f"{calcular_delta('Perc_Vacina_Dia'):.2f}%"
        )

    with k4:

        if (
            'NascVivos_<2500g' in df_filtrado.columns
            and 'Nascidos_Vivos' in df_filtrado.columns
        ):

            total_nv = df_filtrado['Nascidos_Vivos'].sum()

            baixo_peso = (
                (
                    df_filtrado['NascVivos_<2500g'].sum()
                    / total_nv
                ) * 100
            ) if total_nv > 0 else 0

        else:
            baixo_peso = 0

        st.metric(
            "⚠️ Baixo Peso ao Nascer",
            f"{baixo_peso:.2f}%"
        )

    st.markdown("---")

    # =================================================
    # CARDS EPIDEMIOLÓGICOS
    # =================================================

    st.subheader("📌 Indicadores Epidemiológicos")

    c1, c2, c3 = st.columns(3)

    with c1:

        taxa = (
            df_filtrado['Taxa_Mortalidade_Infantil'].iloc[-1]
            if 'Taxa_Mortalidade_Infantil' in df_filtrado.columns
            else 0
        )

        st.error(f"""
        ### 👶 Mortalidade Infantil

        **Taxa Atual:** {taxa:.2f} óbitos por mil nascidos vivos.

        A mortalidade infantil está diretamente relacionada às condições
        socioeconômicas, acesso à saúde, saneamento básico,
        vacinação e acompanhamento pré-natal.

        Taxas elevadas podem indicar fragilidade na atenção básica.
        """)

    with c2:

        st.success("""
        ### 💉 Cobertura Vacinal

        A vacinação reduz significativamente:

        • mortalidade infantil  
        • doenças respiratórias  
        • surtos epidemiológicos  
        • internações hospitalares

        Altas coberturas vacinais refletem eficiência das políticas públicas.
        """)

    with c3:

        st.warning("""
        ### ⚠️ Fatores de Risco

        Principais fatores associados aos agravos:

        • baixo peso ao nascer  
        • ausência de pré-natal  
        • desnutrição infantil  
        • baixa vacinação  
        • pobreza e falta de saneamento

        Esses fatores impactam diretamente a saúde coletiva.
        """)

    st.markdown("---")

    # =================================================
    # GRÁFICOS PRINCIPAIS
    # =================================================

    g1, g2 = st.columns(2)

    # =================================================
    # GRÁFICO 1
    # =================================================

    with g1:

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
                    "<b>Nascimentos:</b> %{y:,.0f}<extra></extra>"
                )
            )

        if 'Total_Obitos_Inf' in df_filtrado.columns:

            fig.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Total_Obitos_Inf'],
                    mode='lines+markers',
                    name='Óbitos Infantis',
                    line=dict(color=COR_SECUNDARIA, width=4),
                    marker=dict(size=8),
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Óbitos:</b> %{y:,.0f}<extra></extra>"
                )
            )

        fig.update_layout(
            title="Nascimentos x Mortalidade Infantil",
            xaxis_title="Ano",
            yaxis_title="Quantidade"
        )

        fig = estilizar_grafico(fig)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.info("""
        **Análise:**  
        O gráfico compara a evolução dos nascimentos com os óbitos infantis,
        permitindo identificar períodos críticos e tendências epidemiológicas.
        """)

    # =================================================
    # GRÁFICO 2
    # =================================================

    with g2:

        fig2 = go.Figure()

        if 'Perc_Vacina_Dia' in df_filtrado.columns:

            fig2.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Perc_Vacina_Dia'],
                    mode='lines+markers',
                    name='Cobertura Vacinal',
                    line=dict(color="#00875A", width=4),
                    marker=dict(size=8),
                    fill='tozeroy',
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Vacinação:</b> %{y:.2f}%<extra></extra>"
                )
            )

        fig2.update_layout(
            title="Cobertura Vacinal Infantil",
            xaxis_title="Ano",
            yaxis_title="% Cobertura"
        )

        fig2 = estilizar_grafico(fig2)

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

        st.info("""
        **Análise:**  
        Altas coberturas vacinais contribuem para a redução da mortalidade infantil,
        prevenção de doenças infecciosas e diminuição das internações.
        """)

    st.markdown("---")

    # =================================================
    # GRÁFICO FINAL
    # =================================================

    fig3 = go.Figure()

    if 'Nº_Visitas' in df_filtrado.columns:

        fig3.add_trace(
            go.Bar(
                x=df_filtrado['Ano'],
                y=df_filtrado['Nº_Visitas'],
                name='Visitas Domiciliares',
                marker_color="#C8102E",
                hovertemplate=
                "<b>Ano:</b> %{x}<br>" +
                "<b>Visitas:</b> %{y:,.0f}<extra></extra>"
            )
        )

    if 'Famílias_Acompanh.' in df_filtrado.columns:

        fig3.add_trace(
            go.Scatter(
                x=df_filtrado['Ano'],
                y=df_filtrado['Famílias_Acompanh.'],
                mode='lines+markers',
                name='Famílias Acompanhadas',
                line=dict(color="#004A99", width=4),
                marker=dict(size=8),
                hovertemplate=
                "<b>Ano:</b> %{x}<br>" +
                "<b>Famílias:</b> %{y:,.0f}<extra></extra>"
            )
        )

    fig3.update_layout(
        title="Cobertura da Atenção Básica",
        xaxis_title="Ano",
        yaxis_title="Quantidade"
    )

    fig3 = estilizar_grafico(fig3)

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    st.info("""
    **Análise Geral:**  
    O aumento das visitas domiciliares e do acompanhamento familiar
    demonstra fortalecimento da Estratégia Saúde da Família,
    ampliando a prevenção, monitoramento epidemiológico e acesso à saúde.
    """)

# =====================================================
# ABA 2 - ATENDIMENTO
# =====================================================

with tabs[1]:

    st.subheader("📈 Atendimento e Cobertura da Atenção Básica")

    st.markdown("""
    Esta seção apresenta indicadores relacionados ao atendimento domiciliar,
    acompanhamento familiar e alcance da Estratégia Saúde da Família.
    
    Os dados permitem avaliar a expansão da atenção básica,
    acesso aos serviços públicos e fortalecimento das ações preventivas.
    """)

    # =================================================
    # KPIs DE ATENDIMENTO
    # =================================================

    a1, a2, a3 = st.columns(3)

    with a1:

        total_visitas = (
            df_filtrado['Nº_Visitas'].sum()
            if 'Nº_Visitas' in df_filtrado.columns
            else 0
        )

        st.metric(
            "🏠 Visitas Domiciliares",
            f"{total_visitas:,.0f}".replace(",", ".")
        )

    with a2:

        familias = (
            df_filtrado['Famílias_Acompanh.'].iloc[-1]
            if 'Famílias_Acompanh.' in df_filtrado.columns
            else 0
        )

        st.metric(
            "👨‍👩‍👧 Famílias Acompanhadas",
            f"{familias:,.0f}".replace(",", ".")
        )

    with a3:

        gestantes = (
            df_filtrado['Nº_Gestantes'].iloc[-1]
            if 'Nº_Gestantes' in df_filtrado.columns
            else 0
        )

        st.metric(
            "🤰 Gestantes Monitoradas",
            f"{gestantes:,.0f}".replace(",", ".")
        )

    st.markdown("---")

    # =================================================
    # GRÁFICO PRINCIPAL
    # =================================================

    fig = go.Figure()

    if 'Nº_Visitas' in df_filtrado.columns:

        fig.add_trace(
            go.Bar(
                x=df_filtrado['Ano'],
                y=df_filtrado['Nº_Visitas'],
                name='Visitas Domiciliares',
                marker_color=COR_PRIMARIA,
                hovertemplate=
                "<b>Ano:</b> %{x}<br>" +
                "<b>Visitas:</b> %{y:,.0f}<extra></extra>"
            )
        )

    if 'Famílias_Acompanh.' in df_filtrado.columns:

        fig.add_trace(
            go.Scatter(
                x=df_filtrado['Ano'],
                y=df_filtrado['Famílias_Acompanh.'],
                mode='lines+markers',
                name='Famílias Acompanhadas',
                line=dict(color="#004A99", width=4),
                marker=dict(size=8),
                hovertemplate=
                "<b>Ano:</b> %{x}<br>" +
                "<b>Famílias:</b> %{y:,.0f}<extra></extra>"
            )
        )

    fig.update_layout(
        title="Cobertura da Atenção Básica",
        xaxis_title="Ano",
        yaxis_title="Quantidade"
    )

    fig = estilizar_grafico(fig)

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.info("""
    **Análise do gráfico:**  
    O crescimento das visitas domiciliares e do acompanhamento familiar
    indica fortalecimento das políticas públicas de saúde preventiva,
    ampliação do acesso aos serviços básicos e maior monitoramento da população.
    """)

    st.markdown("---")

    # =================================================
    # SEGUNDA LINHA DE GRÁFICOS
    # =================================================

    c1, c2 = st.columns(2)

    # =================================================
    # GRÁFICO - GESTANTES
    # =================================================

    with c1:

        fig_gest = go.Figure()

        if 'Nº_Gestantes' in df_filtrado.columns:

            fig_gest.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Nº_Gestantes'],
                    name='Gestantes Cadastradas',
                    marker_color="#C8102E",
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Gestantes:</b> %{y:,.0f}<extra></extra>"
                )
            )

        if 'Nº_Gest._Acompanh' in df_filtrado.columns:

            fig_gest.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Nº_Gest._Acompanh'],
                    mode='lines+markers',
                    name='Gestantes Acompanhadas',
                    line=dict(color="#00875A", width=4),
                    marker=dict(size=8),
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Acompanhadas:</b> %{y:,.0f}<extra></extra>"
                )
            )

        fig_gest.update_layout(
            title="Monitoramento de Gestantes",
            xaxis_title="Ano",
            yaxis_title="Quantidade"
        )

        fig_gest = estilizar_grafico(fig_gest)

        st.plotly_chart(
            fig_gest,
            use_container_width=True
        )

        st.success("""
        **Análise:**  
        O acompanhamento contínuo das gestantes reduz riscos obstétricos,
        melhora o pré-natal e contribui diretamente para a redução
        da mortalidade materna e infantil.
        """)

    # =================================================
    # GRÁFICO - PRÉ-NATAL
    # =================================================

    with c2:

        fig_pre = go.Figure()

        if 'Gest.c/PN_no_mês' in df_filtrado.columns:

            fig_pre.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Gest.c/PN_no_mês'],
                    name='Pré-Natal no Mês',
                    marker_color="#004A99",
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Pré-Natal:</b> %{y:,.0f}<extra></extra>"
                )
            )

        if 'Gest.c/PN_1ºTrim' in df_filtrado.columns:

            fig_pre.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Gest.c/PN_1ºTrim'],
                    mode='lines+markers',
                    name='Pré-Natal no 1º Trimestre',
                    line=dict(color="#FF8C00", width=4),
                    marker=dict(size=8),
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>1º Trimestre:</b> %{y:,.0f}<extra></extra>"
                )
            )

        fig_pre.update_layout(
            title="Cobertura do Pré-Natal",
            xaxis_title="Ano",
            yaxis_title="Quantidade"
        )

        fig_pre = estilizar_grafico(fig_pre)

        st.plotly_chart(
            fig_pre,
            use_container_width=True
        )

        st.warning("""
        **Análise:**  
        O início precoce do pré-natal está associado à prevenção
        de complicações gestacionais, identificação de doenças
        e melhoria da saúde materno-infantil.
        """)

    st.markdown("---")

    # =================================================
    # CARD FINAL
    # =================================================

    st.info("""
    ### 📌 Conclusão da Aba

    Os indicadores demonstram a importância da atenção básica
    como principal mecanismo de prevenção, monitoramento e promoção da saúde.

    O aumento da cobertura assistencial fortalece:
    
    • prevenção de doenças  
    • acompanhamento familiar  
    • controle epidemiológico  
    • redução de internações  
    • melhoria da qualidade de vida da população
    """)

# =====================================================
# ABA 3 - SAÚDE INFANTIL
# =====================================================

with tabs[2]:

    st.subheader("👶 Saúde Infantil e Desenvolvimento")

    st.markdown("""
    Monitoramento epidemiológico da saúde infantil,
    vacinação, nutrição, aleitamento materno e mortalidade.
    """)

    # =================================================
    # KPIs INFANTIS (CORRIGIDO)
    # =================================================

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        criancas = (
            df_filtrado['Crianças_<1_ano'].sum()
            if 'Crianças_<1_ano' in df_filtrado.columns
            else 0
        )
        st.metric(
            "Crianças <1 ano",
            f"{criancas:,.0f}".replace(",", ".")
        )

    with k2:
        if 'Perc_Vacina_Dia' in df_filtrado.columns and not df_filtrado.empty:
            valor_vacinacao = df_filtrado['Perc_Vacina_Dia'].iloc[-1]
        else:
            valor_vacinacao = 0

        # Agora este bloco está corretamente identado dentro do 'with k2'
        st.metric(
            label="💉 Vacinação em Dia",
            value=f"{valor_vacinacao:.2f}%",
            delta=f"{calcular_delta('Perc_Vacina_Dia'):.2f}%"
        )       

    with k3:
        desnutridas = (
            df_filtrado['Cr<1a_desnutridas'].sum()
            if 'Cr<1a_desnutridas' in df_filtrado.columns
            else 0
        )
        st.metric(
            "Desnutrição infantil",
            f"{desnutridas:,.0f}".replace(",", "."),
            delta=int(calcular_delta('Cr<1a_desnutridas')), # Adicionado delta para manter padrão
            delta_color="inverse"
        )

    with k4:
        if 'Taxa_Mortalidade_Infantil' in df_filtrado.columns and not df_filtrado.empty:
            valor_morte = df_filtrado['Taxa_Mortalidade_Infantil'].iloc[-1]
        else:
            valor_morte = 0

        # Removida a métrica duplicada que estava quebrando o layout
        st.metric(
            "👶 Mortalidade Infantil",
            f"{valor_morte:.2f}%",
            delta=f"{calcular_delta('Taxa_Mortalidade_Infantil'):.2f}%",
            delta_color="inverse"
        )

    st.markdown("---")

    # =================================================
    # PRIMEIRA LINHA
    # =================================================

    col1, col2 = st.columns(2)

    # =================================================
    # MORTALIDADE INFANTIL
    # =================================================

    with col1:

        cols_obitos = []

        for col in [
            'Óbitos<1a_Diarr',
            'Óbitos<1a_IRA',
            'Óbitos<1a_OutCau'
        ]:

            if col in df_filtrado.columns:
                cols_obitos.append(col)

        fig_obitos = px.bar(
            df_filtrado,
            x='Ano',
            y=cols_obitos,
            barmode='group',
            title='Óbitos Infantis por Causa',
            color_discrete_sequence=[
                '#990000',
                '#CC0000',
                '#004A99'
            ]
        )

        fig_obitos.update_traces(
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Quantidade:</b> %{y}<extra></extra>"
        )

        fig_obitos.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=22
        )

        st.plotly_chart(
            fig_obitos,
            use_container_width=True
        )

    # =================================================
    # VACINAÇÃO
    # =================================================

    with col2:

        fig_vac = go.Figure()

        fig_vac.add_trace(
            go.Scatter(
                x=df_filtrado['Ano'],
                y=df_filtrado['Perc_Vacina_Dia'],
                mode='lines+markers',
                name='Cobertura Vacinal',
                line=dict(
                    color='#004A99',
                    width=4
                ),
                marker=dict(size=8),
                hovertemplate=
                "<b>Ano:</b> %{x}<br>" +
                "<b>Cobertura:</b> %{y:.2f}%<extra></extra>"
            )
        )

        fig_vac.update_layout(
            title='Cobertura Vacinal Infantil',
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=22
        )

        st.plotly_chart(
            fig_vac,
            use_container_width=True
        )

    st.markdown("---")

    # =================================================
    # SEGUNDA LINHA
    # =================================================

    col3, col4 = st.columns(2)

    # =================================================
    # NUTRIÇÃO
    # =================================================

    with col3:

        cols_nutricao = []

        for col in [
            'Cr<1a_desnutridas',
            'Cr_12-23m_Desnutr.'
        ]:

            if col in df_filtrado.columns:
                cols_nutricao.append(col)

        fig_nutricao = px.bar(
            df_filtrado,
            x='Ano',
            y=cols_nutricao,
            barmode='group',
            title='Desnutrição Infantil',
            color_discrete_sequence=[
                '#CC0000',
                '#FF9900'
            ]
        )

        fig_nutricao.update_traces(
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Casos:</b> %{y}<extra></extra>"
        )

        fig_nutricao.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=22
        )

        st.plotly_chart(
            fig_nutricao,
            use_container_width=True
        )

    # =================================================
    # ALEITAMENTO MATERNO
    # =================================================

    with col4:

        cols_aleitamento = []

        for col in [
            'Cr<4m_AleitMatExcl',
            'Cr<4m_Aleit_Misto'
        ]:

            if col in df_filtrado.columns:
                cols_aleitamento.append(col)

        fig_aleit = px.bar(
            df_filtrado,
            x='Ano',
            y=cols_aleitamento,
            barmode='group',
            title='Aleitamento Materno',
            color_discrete_sequence=[
                '#004A99',
                '#66B2FF'
            ]
        )

        fig_aleit.update_traces(
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Total:</b> %{y}<extra></extra>"
        )

        fig_aleit.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=22
        )

        st.plotly_chart(
            fig_aleit,
            use_container_width=True
        )

    st.markdown("---")

    # =================================================
    # TERCEIRA LINHA
    # =================================================

    col5, col6 = st.columns(2)

    # =================================================
    # DIARREIA E IRA
    # =================================================

    with col5:

        cols_doencas = []

        for col in [
            'Cr<2a_c/diarr',
            'Cr<2a_c/IRA'
        ]:

            if col in df_filtrado.columns:
                cols_doencas.append(col)

        fig_doencas = px.line(
            df_filtrado,
            x='Ano',
            y=cols_doencas,
            markers=True,
            title='Doenças Respiratórias e Diarreicas',
            color_discrete_sequence=[
                '#990000',
                '#004A99'
            ]
        )

        fig_doencas.update_traces(
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Casos:</b> %{y}<extra></extra>"
        )

        fig_doencas.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=22
        )

        st.plotly_chart(
            fig_doencas,
            use_container_width=True
        )

    # =================================================
    # INTERNAÇÕES INFANTIS
    # =================================================

    with col6:

        cols_hosp = []

        for col in [
            'Hosp.<5a_Pneumonia',
            'Hosp.<5a_Desitrat'
        ]:

            if col in df_filtrado.columns:
                cols_hosp.append(col)

        fig_hosp = px.bar(
            df_filtrado,
            x='Ano',
            y=cols_hosp,
            barmode='group',
            title='Internações Infantis',
            color_discrete_sequence=[
                '#CC0000',
                '#FF9900'
            ]
        )

        fig_hosp.update_traces(
            hovertemplate=
            "<b>Ano:</b> %{x}<br>" +
            "<b>Internações:</b> %{y}<extra></extra>"
        )

        fig_hosp.update_layout(
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font_size=22
        )

        st.plotly_chart(
            fig_hosp,
            use_container_width=True
        )

    st.markdown("---")

    # =================================================
    # ANÁLISE AUTOMÁTICA
    # =================================================

    st.info("""
    ### 📌 Análise Epidemiológica Infantil

    • A mortalidade infantil apresenta forte relação com condições socioeconômicas,
    saneamento básico e cobertura vacinal.

    • Casos de diarreia e desidratação infantil são altamente associados
    à ausência de saneamento adequado e água potável.

    • A vacinação infantil reduz significativamente hospitalizações,
    pneumonias e doenças infecciosas.

    • O aleitamento materno exclusivo apresenta impacto positivo
    na imunidade e redução da mortalidade neonatal.

    • Crianças desnutridas possuem maior vulnerabilidade
    a doenças respiratórias e infecciosas.
    """)

    # =================================================
    # CARDS INFORMATIVOS
    # =================================================

    info1, info2, info3 = st.columns(3)

    with info1:

        st.warning("""
        ### 💧 Diarreia Infantil

        • Relacionada à falta de saneamento  
        • Associada à água contaminada  
        • Pode causar desidratação grave  
        • Alta prevenção com higiene
        """)

    with info2:

        st.error("""
        ### 🫁 Infecção Respiratória

        • Alta incidência infantil  
        • Pode evoluir para pneumonia  
        • Maior risco em desnutridos  
        • Vacinação reduz complicações
        """)

    with info3:

        st.success("""
        ### 🍼 Aleitamento Materno

        • Fortalece imunidade  
        • Reduz mortalidade infantil  
        • Protege contra infecções  
        • Recomendado até 6 meses
        """)

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
# ABA 5 - DOENÇAS
# =====================================================

with tabs[4]:

    st.subheader("🦠 Monitoramento Epidemiológico de Doenças")

    st.markdown("""
    Esta aba apresenta a evolução temporal das principais doenças monitoradas
    pela Atenção Básica, permitindo avaliar o crescimento dos casos,
    acompanhamento clínico e impacto epidemiológico na população.
    """)

    # =================================================
    # KPI DAS DOENÇAS
    # =================================================

    d1, d2, d3, d4 = st.columns(4)

    with d1:

        valor = (
            df_filtrado['Hiperten.Cadastr.'].iloc[-1]
            if 'Hiperten.Cadastr.' in df_filtrado.columns
            else 0
        )

        st.metric(
            "❤️ Hipertensão",
            f"{valor:,.0f}".replace(",", ".")
        )

    with d2:

        valor = (
            df_filtrado['Diabetes_Cadastr.'].iloc[-1]
            if 'Diabetes_Cadastr.' in df_filtrado.columns
            else 0
        )

        st.metric(
            "🩸 Diabetes",
            f"{valor:,.0f}".replace(",", ".")
        )

    with d3:

        valor = (
            df_filtrado['Tubercul.Cadastr.'].iloc[-1]
            if 'Tubercul.Cadastr.' in df_filtrado.columns
            else 0
        )

        st.metric(
            "🫁 Tuberculose",
            f"{valor:,.0f}".replace(",", ".")
        )

    with d4:

        valor = (
            df_filtrado['Hansenia.Cadastr.'].iloc[-1]
            if 'Hansenia.Cadastr.' in df_filtrado.columns
            else 0
        )

        st.metric(
            "⚠️ Hanseníase",
            f"{valor:,.0f}".replace(",", ".")
        )

    st.markdown("---")

    # =================================================
    # HIPERTENSÃO
    # =================================================

    st.markdown("## ❤️ Hipertensão Arterial")

    c1, c2 = st.columns([2, 1])

    with c1:

        fig_hip = go.Figure()

        if 'Hiperten.Cadastr.' in df_filtrado.columns:

            fig_hip.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Hiperten.Cadastr.'],
                    name='Cadastrados',
                    marker_color="#C8102E",
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Pacientes:</b> %{y:,.0f}<extra></extra>"
                )
            )

        if 'Hiperten.Acompan.' in df_filtrado.columns:

            fig_hip.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Hiperten.Acompan.'],
                    mode='lines+markers',
                    name='Acompanhados',
                    line=dict(color="#990000", width=4),
                    marker=dict(size=8),
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Acompanhados:</b> %{y:,.0f}<extra></extra>"
                )
            )

        fig_hip.update_layout(
            title="Evolução da Hipertensão",
            xaxis_title="Ano",
            yaxis_title="Quantidade"
        )

        fig_hip = estilizar_grafico(fig_hip)

        st.plotly_chart(fig_hip, use_container_width=True)

    with c2:

        st.error("""
        ### Informações Clínicas

        **Doença:** Crônica cardiovascular

        **Contágio:** Não transmissível

        **Risco:** Alto

        **Principais causas:**
        • obesidade  
        • sedentarismo  
        • excesso de sal  
        • estresse

        **Sintomas:**
        • dor de cabeça  
        • tontura  
        • pressão elevada

        **Relação com saneamento:** indireta
        """)

    st.markdown("---")

    # =================================================
    # DIABETES
    # =================================================

    st.markdown("## 🩸 Diabetes Mellitus")

    c1, c2 = st.columns([2, 1])

    with c1:

        fig_dia = go.Figure()

        if 'Diabetes_Cadastr.' in df_filtrado.columns:

            fig_dia.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Diabetes_Cadastr.'],
                    name='Cadastrados',
                    marker_color="#004A99",
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Pacientes:</b> %{y:,.0f}<extra></extra>"
                )
            )

        if 'Diabetes_Acompan.' in df_filtrado.columns:

            fig_dia.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Diabetes_Acompan.'],
                    mode='lines+markers',
                    name='Acompanhados',
                    line=dict(color="#0077CC", width=4),
                    marker=dict(size=8),
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Acompanhados:</b> %{y:,.0f}<extra></extra>"
                )
            )

        fig_dia.update_layout(
            title="Evolução do Diabetes",
            xaxis_title="Ano",
            yaxis_title="Quantidade"
        )

        fig_dia = estilizar_grafico(fig_dia)

        st.plotly_chart(fig_dia, use_container_width=True)

    with c2:

        st.info("""
        ### Informações Clínicas

        **Doença:** Metabólica crônica

        **Contágio:** Não transmissível

        **Risco:** Alto

        **Principais causas:**
        • má alimentação  
        • obesidade  
        • sedentarismo

        **Sintomas:**
        • sede excessiva  
        • fadiga  
        • fome constante

        **Relação com saneamento:** indireta
        """)

    st.markdown("---")

    # =================================================
    # TUBERCULOSE
    # =================================================

    st.markdown("## ☣️ Tuberculose")

    c1, c2 = st.columns([2, 1])

    with c1:

        fig_tub = go.Figure()

        if 'Tubercul.Cadastr.' in df_filtrado.columns:

            fig_tub.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Tubercul.Cadastr.'],
                    name='Casos',
                    marker_color="#00875A",
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Casos:</b> %{y:,.0f}<extra></extra>"
                )
            )

        if 'Tubercul_Acompan.' in df_filtrado.columns:

            fig_tub.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Tubercul_Acompan.'],
                    mode='lines+markers',
                    name='Acompanhados',
                    line=dict(color="#006644", width=4),
                    marker=dict(size=8),
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Acompanhados:</b> %{y:,.0f}<extra></extra>"
                )
            )

        fig_tub.update_layout(
            title="Evolução da Tuberculose",
            xaxis_title="Ano",
            yaxis_title="Quantidade"
        )

        fig_tub = estilizar_grafico(fig_tub)

        st.plotly_chart(fig_tub, use_container_width=True)

    with c2:

        st.warning("""
        ### Informações Clínicas

        **Doença:** Infecciosa pulmonar

        **Contágio:** Respiratório

        **Risco:** Muito alto

        **Principais causas:**
        • ambientes fechados  
        • pobreza  
        • imunidade baixa

        **Sintomas:**
        • tosse persistente  
        • febre  
        • emagrecimento

        **Relação com saneamento:** direta
        """)

    st.markdown("---")

    # =================================================
    # HANSENÍASE
    # =================================================

    st.markdown("## ⚠️ Hanseníase")

    c1, c2 = st.columns([2, 1])

    with c1:

        fig_han = go.Figure()

        if 'Hansenia.Cadastr.' in df_filtrado.columns:

            fig_han.add_trace(
                go.Bar(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Hansenia.Cadastr.'],
                    name='Casos',
                    marker_color="#FF8C00",
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Casos:</b> %{y:,.0f}<extra></extra>"
                )
            )

        if 'Hansenia.Acompan.' in df_filtrado.columns:

            fig_han.add_trace(
                go.Scatter(
                    x=df_filtrado['Ano'],
                    y=df_filtrado['Hansenia.Acompan.'],
                    mode='lines+markers',
                    name='Acompanhados',
                    line=dict(color="#CC7000", width=4),
                    marker=dict(size=8),
                    hovertemplate=
                    "<b>Ano:</b> %{x}<br>" +
                    "<b>Acompanhados:</b> %{y:,.0f}<extra></extra>"
                )
            )

        fig_han.update_layout(
            title="Evolução da Hanseníase",
            xaxis_title="Ano",
            yaxis_title="Quantidade"
        )

        fig_han = estilizar_grafico(fig_han)

        st.plotly_chart(fig_han, use_container_width=True)

    with c2:

        st.warning("""
        ### Informações Clínicas

        **Doença:** Infecciosa crônica

        **Contágio:** Respiratório prolongado

        **Risco:** Moderado/alto

        **Principais causas:**
        • contato prolongado  
        • vulnerabilidade social

        **Sintomas:**
        • manchas na pele  
        • dormência  
        • perda de sensibilidade

        **Relação com saneamento:** direta
        """)

    st.markdown("---")

    # =================================================
    # CONCLUSÃO
    # =================================================

    st.info("""
    ### 📌 Análise Epidemiológica Geral

    As doenças crônicas não transmissíveis, como hipertensão e diabetes,
    apresentam crescimento progressivo ao longo dos anos,
    refletindo mudanças no estilo de vida da população.

    Já as doenças infecciosas, como tuberculose e hanseníase,
    possuem forte relação com vulnerabilidade social,
    condições sanitárias inadequadas e dificuldade de acesso à saúde.

    O acompanhamento contínuo pela Atenção Básica é fundamental
    para prevenção, diagnóstico precoce e redução de complicações.
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