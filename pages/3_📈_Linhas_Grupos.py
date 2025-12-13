"""
Análise de Linhas por Grupo - Ranking das linhas mais recorrentes
"""
import streamlit as st

st.set_page_config(page_title="Linhas por Grupo", page_icon="📈", layout="wide")

st.title("📈 Análise de Linhas por Grupo")

st.markdown("""
As linhas agrupam os 25 grupos em 5 categorias de 5 animais cada:
- **Linha 1** (01-05): Avestruz, Águia, Burro, Borboleta, Cachorro
- **Linha 2** (06-10): Cabra, Carneiro, Camelo, Cobra, Coelho
- **Linha 3** (11-15): Cavalo, Elefante, Galo, Gato, Jacaré
- **Linha 4** (16-20): Leão, Macaco, Porco, Pavão, Peru
- **Linha 5** (21-25): Touro, Tigre, Urso, Veado, Vaca
""")

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse a página **📤 Upload** primeiro.")
    st.stop()

from modules.data_loader import (
    filter_last_n_days, filter_by_loteria,
    get_unique_loterias, GRUPOS_ANIMAIS
)
from modules import statistics as stats
import plotly.express as px
import plotly.graph_objects as go
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

st.divider()

# Análise de linhas
linhas = stats.get_linhas_grupos(df_filtered)

if len(linhas) > 0:
    # Métricas da linha mais quente
    linha_top = linhas.iloc[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔥 Linha Mais Quente", f"Linha {int(linha_top['linha'])}")
    
    with col2:
        st.metric("📊 Frequência", f"{int(linha_top['frequencia'])}")
    
    with col3:
        total = linhas['frequencia'].sum()
        pct = (linha_top['frequencia'] / total * 100) if total > 0 else 0
        st.metric("📈 Percentual", f"{pct:.1f}%")
    
    st.divider()
    
    # Gráfico de barras
    st.subheader("📊 Ranking de Linhas")
    
    linhas_display = linhas.copy()
    linhas_display['linha_label'] = linhas_display['linha'].apply(lambda x: f"Linha {int(x)}")
    
    fig = px.bar(
        linhas_display,
        x='linha_label',
        y='frequencia',
        color='frequencia',
        color_continuous_scale=['#1e2130', '#9C27B0'],
        text='frequencia'
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#fff',
        coloraxis_showscale=False,
        xaxis_title='Linha',
        yaxis_title='Frequência'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de pizza
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🥧 Distribuição Percentual")
        
        fig = px.pie(
            linhas_display,
            values='frequencia',
            names='linha_label',
            color_discrete_sequence=['#00C853', '#1E88E5', '#FF9800', '#E91E63', '#9C27B0']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📋 Tabela Detalhada")
        
        linhas_table = linhas.copy()
        linhas_table['linha'] = linhas_table['linha'].apply(lambda x: f"Linha {int(x)}")
        linhas_table['percentual'] = (linhas_table['frequencia'] / linhas_table['frequencia'].sum() * 100).round(1)
        linhas_table['percentual'] = linhas_table['percentual'].apply(lambda x: f"{x}%")
        
        st.dataframe(
            linhas_table[['linha', 'frequencia', 'percentual', 'descricao']].rename(columns={
                'linha': 'Linha',
                'frequencia': 'Frequência',
                'percentual': 'Percentual',
                'descricao': 'Grupos'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    
    # Comparação entre períodos
    st.subheader("📆 Comparação Entre Períodos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Últimos 15 dias")
        df_15d = filter_last_n_days(df, 15)
        df_15d = filter_by_loteria(df_15d, loterias_selecionadas)
        linhas_15d = stats.get_linhas_grupos(df_15d)
        
        if len(linhas_15d) > 0:
            for _, row in linhas_15d.iterrows():
                pct = (row['frequencia'] / linhas_15d['frequencia'].sum() * 100) if linhas_15d['frequencia'].sum() > 0 else 0
                st.progress(pct / 100, text=f"Linha {int(row['linha'])}: {int(row['frequencia'])} ({pct:.1f}%)")
        else:
            st.info("Sem dados")
    
    with col2:
        st.markdown("#### Últimos 30 dias")
        
        for _, row in linhas.iterrows():
            pct = (row['frequencia'] / linhas['frequencia'].sum() * 100) if linhas['frequencia'].sum() > 0 else 0
            st.progress(pct / 100, text=f"Linha {int(row['linha'])}: {int(row['frequencia'])} ({pct:.1f}%)")
    
    st.divider()
    
    # Detalhamento por grupo dentro da linha mais quente
    st.subheader(f"🔥 Detalhamento da {linha_top['descricao'].split(':')[0]}")
    
    linha_num = int(linha_top['linha'])
    grupo_inicio = (linha_num - 1) * 5 + 1
    grupo_fim = linha_num * 5
    
    df_linha = df_filtered[(df_filtered['grupo'] >= grupo_inicio) & (df_filtered['grupo'] <= grupo_fim)]
    
    if len(df_linha) > 0:
        grupos_linha = stats.get_grupo_frequency(df_linha, top_n=5)
        
        fig = px.bar(
            grupos_linha,
            x='grupo_animal',
            y='frequencia',
            color='frequencia',
            color_continuous_scale=['#1e2130', '#00C853'],
            text='frequencia'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            coloraxis_showscale=False,
            xaxis_title='Grupo',
            yaxis_title='Frequência'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados detalhados")

else:
    st.info("🔍 Sem dados para análise no período selecionado.")

st.caption("⚠️ Análise estatística para fins informativos. Resultados passados não garantem resultados futuros.")
