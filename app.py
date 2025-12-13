"""
Jogo do Bicho Analytics - Painel de Análise Estatística
"""
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Jogo do Bicho Analytics",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0, 200, 83, 0.2);
    }
    
    .main-header h1 {
        color: #00C853;
        font-size: 2.5rem;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 200, 83, 0.5);
    }
    
    .main-header p {
        color: #aaa;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .stat-card {
        background: linear-gradient(145deg, #1e2130, #252836);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #00C853;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .stat-card h3 {
        color: #00C853;
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stat-card .value {
        color: #fff;
        font-size: 2rem;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Alert box */
    .info-box {
        background: rgba(0, 200, 83, 0.1);
        border: 1px solid #00C853;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .warning-box {
        background: rgba(255, 152, 0, 0.1);
        border: 1px solid #FF9800;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #00C853;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1e2130;
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #00C853;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🎲 Jogo do Bicho Analytics</h1>
    <p>Painel Interativo de Análise Estatística</p>
</div>
""", unsafe_allow_html=True)

# Verificar se há dados carregados
if 'dados' not in st.session_state or st.session_state.dados is None:
    st.markdown("""
    <div class="warning-box">
        <h3>⚠️ Nenhuma base de dados carregada</h3>
        <p>Para começar, acesse o menu <strong>📤 Upload</strong> no menu lateral e carregue sua planilha de resultados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    **Formato esperado da planilha:**
    - `data` - Data do resultado (YYYY-MM-DD)
    - `loteria` - Nome da loteria (RJ, Nacional, Look GO, Federal, Capital)
    - `horario` - Horário do sorteio
    - `grupo` - Número do grupo (01-25)
    - `centena` - Centena sorteada (000-999)
    - `milhar` - Milhar sorteada (0000-9999)
    """)
    
    # Quick stats area
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Registros", "0")
    with col2:
        st.metric("📅 Período", "N/A")
    with col3:
        st.metric("🎰 Loterias", "0")
        
else:
    from modules.data_loader import filter_last_n_days, GRUPOS_ANIMAIS
    from modules import statistics as stats
    import pandas as pd
    
    df = st.session_state.dados
    df_30d = filter_last_n_days(df, 30)
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Registros", f"{len(df):,}")
    
    with col2:
        st.metric("📅 Últimos 30 dias", f"{len(df_30d):,}")
    
    with col3:
        if len(df) > 0:
            periodo = f"{df['data'].min().strftime('%d/%m')} - {df['data'].max().strftime('%d/%m/%Y')}"
        else:
            periodo = "N/A"
        st.metric("📆 Período", periodo)
    
    with col4:
        st.metric("🎰 Loterias", len(df['loteria'].unique()))
    
    st.divider()
    
    # Top Rankings
    st.subheader("🏆 Rankings dos Últimos 30 Dias")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🎯 Top 5 Grupos")
        grupos_freq = stats.get_grupo_frequency(df_30d, top_n=5)
        if len(grupos_freq) > 0:
            for i, row in grupos_freq.iterrows():
                emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(i, 4)]
                st.markdown(f"{emoji} **{row['grupo']:02d}** - {row['animal']} ({row['frequencia']}x)")
        else:
            st.info("Sem dados")
    
    with col2:
        st.markdown("#### 💯 Top 5 Centenas")
        centenas_freq = stats.get_centena_frequency(df_30d, top_n=5)
        if len(centenas_freq) > 0:
            for i, row in centenas_freq.iterrows():
                emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(i, 4)]
                st.markdown(f"{emoji} **{row['centena_fmt']}** ({row['frequencia']}x)")
        else:
            st.info("Sem dados")
    
    with col3:
        st.markdown("#### 🎰 Top 5 Milhares")
        milhares_freq = stats.get_milhar_frequency(df_30d, top_n=5)
        if len(milhares_freq) > 0:
            for i, row in milhares_freq.iterrows():
                emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(i, 4)]
                st.markdown(f"{emoji} **{row['milhar_fmt']}** ({row['frequencia']}x)")
        else:
            st.info("Sem dados")
    
    st.divider()
    
    # Gráficos
    st.subheader("📈 Análise Visual")
    
    import plotly.express as px
    import plotly.graph_objects as go
    
    tab1, tab2, tab3 = st.tabs(["📊 Distribuição", "📈 Tendência", "🎰 Por Loteria"])
    
    with tab1:
        # Gráfico de distribuição de grupos
        grupos_freq_all = stats.get_grupo_frequency(df_30d, top_n=25)
        if len(grupos_freq_all) > 0:
            fig = px.bar(
                grupos_freq_all, 
                x='grupo_animal', 
                y='frequencia',
                title='Frequência de Grupos (Últimos 30 dias)',
                color='frequencia',
                color_continuous_scale=['#1e2130', '#00C853']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#fff',
                xaxis_title='Grupo',
                yaxis_title='Frequência',
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Tendência diária
        tendencia = stats.get_tendencia_diaria(df_30d)
        if len(tendencia) > 0:
            fig = px.line(
                tendencia,
                x='data',
                y='resultados',
                title='Resultados por Dia (Últimos 30 dias)',
                markers=True
            )
            fig.update_traces(line_color='#00C853', marker_color='#00C853')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#fff',
                xaxis_title='Data',
                yaxis_title='Quantidade'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Distribuição por loteria
        dist_loteria = stats.get_distribuicao_por_loteria(df_30d)
        if len(dist_loteria) > 0:
            fig = px.pie(
                dist_loteria,
                values='resultados',
                names='loteria',
                title='Distribuição por Loteria (Últimos 30 dias)',
                color_discrete_sequence=['#00C853', '#1E88E5', '#FF9800', '#E91E63', '#9C27B0']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#fff'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Footer disclaimer
    st.markdown("---")
    st.caption("⚠️ Este sistema é apenas para análise estatística. Os resultados passados não garantem resultados futuros.")
