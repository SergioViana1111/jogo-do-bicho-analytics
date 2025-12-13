"""
Dashboard - Visão geral estatística dos últimos 30 dias
"""
import streamlit as st

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard")

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse a página **📤 Upload** primeiro.")
    st.stop()

from modules.data_loader import (
    filter_last_n_days, filter_by_loteria, filter_by_horario,
    get_unique_loterias, get_unique_horarios, GRUPOS_ANIMAIS
)
from modules import statistics as stats
import plotly.express as px
import plotly.graph_objects as go

df = st.session_state.dados

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtro de período
dias = st.sidebar.slider("Período (dias)", min_value=7, max_value=90, value=30)

# Filtro de loterias
loterias_disponiveis = get_unique_loterias(df)
loterias_selecionadas = st.sidebar.multiselect(
    "Loterias",
    options=loterias_disponiveis,
    default=loterias_disponiveis
)

# Filtro de horários
horarios_disponiveis = get_unique_horarios(df)
horarios_selecionados = st.sidebar.multiselect(
    "Horários",
    options=horarios_disponiveis,
    default=horarios_disponiveis
)

# Aplicar filtros
df_filtered = filter_last_n_days(df, dias)
df_filtered = filter_by_loteria(df_filtered, loterias_selecionadas)
df_filtered = filter_by_horario(df_filtered, horarios_selecionados)

# Métricas principais
st.subheader("📈 Indicadores Principais")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Resultados Analisados", f"{len(df_filtered):,}")

with col2:
    if len(df_filtered) > 0:
        grupo_top = stats.get_grupo_frequency(df_filtered, 1)
        if len(grupo_top) > 0:
            st.metric("🥇 Grupo Mais Frequente", f"{grupo_top.iloc[0]['grupo']:02d} - {grupo_top.iloc[0]['animal']}")
        else:
            st.metric("🥇 Grupo Mais Frequente", "N/A")
    else:
        st.metric("🥇 Grupo Mais Frequente", "N/A")

with col3:
    if len(df_filtered) > 0:
        centena_top = stats.get_centena_frequency(df_filtered, 1)
        if len(centena_top) > 0:
            st.metric("💯 Centena Mais Frequente", centena_top.iloc[0]['centena_fmt'])
        else:
            st.metric("💯 Centena Mais Frequente", "N/A")
    else:
        st.metric("💯 Centena Mais Frequente", "N/A")

with col4:
    if len(df_filtered) > 0:
        milhar_top = stats.get_milhar_frequency(df_filtered, 1)
        if len(milhar_top) > 0:
            st.metric("🎰 Milhar Mais Frequente", milhar_top.iloc[0]['milhar_fmt'])
        else:
            st.metric("🎰 Milhar Mais Frequente", "N/A")
    else:
        st.metric("🎰 Milhar Mais Frequente", "N/A")

st.divider()

# Gráficos de frequência
st.subheader("📊 Frequência de Grupos")

grupos_freq = stats.get_grupo_frequency(df_filtered, top_n=25)
if len(grupos_freq) > 0:
    fig = px.bar(
        grupos_freq,
        x='grupo_animal',
        y='frequencia',
        color='frequencia',
        color_continuous_scale=['#1e2130', '#00C853'],
        labels={'grupo_animal': 'Grupo', 'frequencia': 'Frequência'}
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#fff',
        xaxis_tickangle=-45,
        showlegend=False,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sem dados para o período selecionado")

# Rankings lado a lado
st.subheader("🏆 Rankings Completos")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Top 10 Centenas")
    centenas = stats.get_centena_frequency(df_filtered, top_n=10)
    if len(centenas) > 0:
        fig = px.bar(
            centenas,
            x='centena_fmt',
            y='frequencia',
            color='frequencia',
            color_continuous_scale=['#1e2130', '#1E88E5']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title='Centena',
            yaxis_title='Frequência'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados")

with col2:
    st.markdown("#### Top 10 Milhares")
    milhares = stats.get_milhar_frequency(df_filtered, top_n=10)
    if len(milhares) > 0:
        fig = px.bar(
            milhares,
            x='milhar_fmt',
            y='frequencia',
            color='frequencia',
            color_continuous_scale=['#1e2130', '#FF9800']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            showlegend=False,
            coloraxis_showscale=False,
            xaxis_title='Milhar',
            yaxis_title='Frequência'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados")

# Análise por Loteria
st.subheader("🎰 Análise por Loteria")

dist = stats.get_distribuicao_por_loteria(df_filtered)
if len(dist) > 0:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        fig = px.pie(
            dist,
            values='resultados',
            names='loteria',
            color_discrete_sequence=['#00C853', '#1E88E5', '#FF9800', '#E91E63', '#9C27B0']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.dataframe(
            dist.rename(columns={'loteria': 'Loteria', 'resultados': 'Resultados'}),
            use_container_width=True,
            hide_index=True
        )

# Tendência temporal
st.subheader("📈 Tendência Temporal")

tendencia = stats.get_tendencia_diaria(df_filtered)
if len(tendencia) > 0:
    fig = px.area(
        tendencia,
        x='data',
        y='resultados',
        labels={'data': 'Data', 'resultados': 'Resultados'}
    )
    fig.update_traces(fill='tozeroy', line_color='#00C853', fillcolor='rgba(0, 200, 83, 0.3)')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#fff'
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sem dados para tendência")

st.caption("⚠️ Análise estatística para fins informativos. Resultados passados não garantem resultados futuros.")
