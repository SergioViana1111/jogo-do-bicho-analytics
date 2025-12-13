"""
Análise de Repetições - Identificação de padrões de repetição
"""
import streamlit as st

st.set_page_config(page_title="Repetições", page_icon="🔁", layout="wide")

st.title("🔁 Análise de Repetições")
st.markdown("Identificação de padrões onde grupos, centenas ou milhares se repetem em sequência.")

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse a página **📤 Upload** primeiro.")
    st.stop()

from modules.data_loader import (
    filter_last_n_days, filter_by_loteria,
    get_unique_loterias, GRUPOS_ANIMAIS
)
from modules import statistics as stats
import pandas as pd

df = st.session_state.dados

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")
dias = st.sidebar.slider("Período (dias)", min_value=7, max_value=90, value=30)

loterias_disponiveis = get_unique_loterias(df)
loterias_selecionadas = st.sidebar.multiselect(
    "Loterias",
    options=loterias_disponiveis,
    default=loterias_disponiveis
)

# Aplicar filtros
df_filtered = filter_last_n_days(df, dias)
df_filtered = filter_by_loteria(df_filtered, loterias_selecionadas)

# Tabs para cada tipo de repetição
tab1, tab2, tab3 = st.tabs(["🎯 Grupos", "💯 Centenas", "🎰 Milhares"])

with tab1:
    st.subheader("🎯 Repetições de Grupos")
    
    repeticoes_grupos = stats.get_repeticoes_grupos(df_filtered)
    
    if len(repeticoes_grupos) > 0:
        # Métricas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Repetições", len(repeticoes_grupos))
        
        with col2:
            grupo_mais_repete = repeticoes_grupos['grupo'].value_counts()
            if len(grupo_mais_repete) > 0:
                top_grupo = grupo_mais_repete.index[0]
                st.metric("Grupo que Mais Repete", f"{top_grupo:02d} - {GRUPOS_ANIMAIS.get(top_grupo, '')}")
        
        with col3:
            loteria_mais_repete = repeticoes_grupos['loteria'].value_counts()
            if len(loteria_mais_repete) > 0:
                st.metric("Loteria com Mais Repetições", loteria_mais_repete.index[0])
        
        st.divider()
        
        # Ranking de grupos que mais repetem
        st.markdown("### 📊 Ranking de Repetições por Grupo")
        
        grupo_count = repeticoes_grupos['grupo'].value_counts().reset_index()
        grupo_count.columns = ['grupo', 'repetições']
        grupo_count['animal'] = grupo_count['grupo'].map(GRUPOS_ANIMAIS)
        grupo_count['grupo_fmt'] = grupo_count.apply(lambda x: f"{x['grupo']:02d} - {x['animal']}", axis=1)
        
        import plotly.express as px
        
        fig = px.bar(
            grupo_count.head(10),
            x='grupo_fmt',
            y='repetições',
            color='repetições',
            color_continuous_scale=['#1e2130', '#E91E63']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            xaxis_tickangle=-45,
            coloraxis_showscale=False,
            xaxis_title='Grupo',
            yaxis_title='Repetições'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.markdown("### 📋 Detalhamento das Repetições")
        
        display_df = repeticoes_grupos.copy()
        display_df['grupo_fmt'] = display_df.apply(lambda x: f"{x['grupo']:02d} - {x['animal']}", axis=1)
        display_df['data_anterior'] = pd.to_datetime(display_df['data_anterior']).dt.strftime('%d/%m/%Y')
        display_df['data_atual'] = pd.to_datetime(display_df['data_atual']).dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            display_df[['loteria', 'grupo_fmt', 'data_anterior', 'horario_anterior', 'data_atual', 'horario_atual']].rename(columns={
                'loteria': 'Loteria',
                'grupo_fmt': 'Grupo',
                'data_anterior': 'Data Anterior',
                'horario_anterior': 'Horário Anterior',
                'data_atual': 'Data Repetição',
                'horario_atual': 'Horário Repetição'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("🔍 Nenhuma repetição de grupo encontrada no período selecionado.")

with tab2:
    st.subheader("💯 Repetições de Centenas")
    
    repeticoes_centenas = stats.get_repeticoes_centenas(df_filtered)
    
    if len(repeticoes_centenas) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de Repetições", len(repeticoes_centenas))
        
        with col2:
            centena_mais = repeticoes_centenas['centena'].value_counts()
            if len(centena_mais) > 0:
                st.metric("Centena que Mais Repete", centena_mais.index[0])
        
        st.divider()
        
        # Ranking
        st.markdown("### 📊 Centenas que Mais Repetem")
        
        centena_count = repeticoes_centenas['centena'].value_counts().reset_index().head(10)
        centena_count.columns = ['centena', 'repetições']
        
        import plotly.express as px
        
        fig = px.bar(
            centena_count,
            x='centena',
            y='repetições',
            color='repetições',
            color_continuous_scale=['#1e2130', '#1E88E5']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela
        st.markdown("### 📋 Detalhamento")
        display_df = repeticoes_centenas.copy()
        display_df['data_anterior'] = pd.to_datetime(display_df['data_anterior']).dt.strftime('%d/%m/%Y')
        display_df['data_atual'] = pd.to_datetime(display_df['data_atual']).dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            display_df.rename(columns={
                'loteria': 'Loteria',
                'centena': 'Centena',
                'data_anterior': 'Data Anterior',
                'data_atual': 'Data Repetição'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("🔍 Nenhuma repetição de centena encontrada no período selecionado.")

with tab3:
    st.subheader("🎰 Repetições de Milhares")
    
    repeticoes_milhares = stats.get_repeticoes_milhares(df_filtered)
    
    if len(repeticoes_milhares) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total de Repetições", len(repeticoes_milhares))
        
        with col2:
            milhar_mais = repeticoes_milhares['milhar'].value_counts()
            if len(milhar_mais) > 0:
                st.metric("Milhar que Mais Repete", milhar_mais.index[0])
        
        st.divider()
        
        # Ranking
        st.markdown("### 📊 Milhares que Mais Repetem")
        
        milhar_count = repeticoes_milhares['milhar'].value_counts().reset_index().head(10)
        milhar_count.columns = ['milhar', 'repetições']
        
        import plotly.express as px
        
        fig = px.bar(
            milhar_count,
            x='milhar',
            y='repetições',
            color='repetições',
            color_continuous_scale=['#1e2130', '#FF9800']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela
        st.markdown("### 📋 Detalhamento")
        display_df = repeticoes_milhares.copy()
        display_df['data_anterior'] = pd.to_datetime(display_df['data_anterior']).dt.strftime('%d/%m/%Y')
        display_df['data_atual'] = pd.to_datetime(display_df['data_atual']).dt.strftime('%d/%m/%Y')
        
        st.dataframe(
            display_df.rename(columns={
                'loteria': 'Loteria',
                'milhar': 'Milhar',
                'data_anterior': 'Data Anterior',
                'data_atual': 'Data Repetição'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("🔍 Nenhuma repetição de milhar encontrada no período selecionado.")

st.caption("⚠️ Análise estatística para fins informativos. Resultados passados não garantem resultados futuros.")
