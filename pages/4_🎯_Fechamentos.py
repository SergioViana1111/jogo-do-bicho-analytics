"""
Fechamentos Inteligentes - Rankings de grupo, centena e milhar
"""
import streamlit as st

st.set_page_config(page_title="Fechamentos", page_icon="🎯", layout="wide")

st.title("🎯 Fechamentos Inteligentes")

st.markdown("""
Fechamentos estatísticos baseados em frequência e padrões de repetição.

> ⚠️ **Importante:** Os fechamentos são baseados em análise estatística de dados históricos. 
> Resultados passados **não garantem** resultados futuros.
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

# Quantidade de itens no fechamento
st.sidebar.header("📊 Quantidade no Fechamento")
qtd_grupos = st.sidebar.slider("Grupos", min_value=3, max_value=10, value=5)
qtd_centenas = st.sidebar.slider("Centenas", min_value=5, max_value=20, value=10)
qtd_milhares = st.sidebar.slider("Milhares", min_value=5, max_value=20, value=10)

# Aplicar filtros
df_filtered = filter_last_n_days(df, dias)
df_filtered = filter_by_loteria(df_filtered, loterias_selecionadas)

st.divider()

# Tabs para cada tipo de fechamento
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Grupos", "💯 Centenas", "🎰 Milhares", "🔗 Correlações"])

with tab1:
    st.subheader("🎯 Fechamento de Grupos")
    st.markdown("Ranking baseado em frequência + bonus para grupos que repetem.")
    
    fechamento_grupos = stats.get_fechamento_grupos(df_filtered, top_n=qtd_grupos)
    
    if len(fechamento_grupos) > 0:
        # Cards com os grupos sugeridos
        st.markdown("### 🏆 Grupos Sugeridos")
        
        cols = st.columns(min(5, len(fechamento_grupos)))
        
        for i, (_, row) in enumerate(fechamento_grupos.iterrows()):
            with cols[i % len(cols)]:
                emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"][min(i, 9)]
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #1e2130, #252836); 
                            padding: 1rem; border-radius: 10px; text-align: center;
                            border-left: 4px solid #00C853; margin-bottom: 0.5rem;">
                    <div style="font-size: 2rem;">{emoji}</div>
                    <div style="font-size: 1.5rem; font-weight: bold; color: #00C853;">
                        {row['grupo']:02d}
                    </div>
                    <div style="color: #aaa; font-size: 0.9rem;">{row['animal']}</div>
                    <div style="color: #888; font-size: 0.8rem;">Score: {row['score']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # Gráfico
        fig = px.bar(
            fechamento_grupos,
            x='grupo_fmt',
            y='score',
            color='score',
            color_continuous_scale=['#1e2130', '#00C853'],
            text='score',
            labels={'grupo_fmt': 'Grupo', 'score': 'Score'}
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            coloraxis_showscale=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabela detalhada
        st.markdown("### 📋 Detalhamento")
        st.dataframe(
            fechamento_grupos[['rank', 'grupo', 'animal', 'frequencia', 'score']].rename(columns={
                'rank': 'Posição',
                'grupo': 'Grupo',
                'animal': 'Animal',
                'frequencia': 'Frequência',
                'score': 'Score Total'
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("🔍 Sem dados suficientes para fechamento.")

with tab2:
    st.subheader("💯 Fechamento de Centenas")
    st.markdown("Ranking das centenas mais frequentes no período.")
    
    fechamento_centenas = stats.get_fechamento_centenas(df_filtered, top_n=qtd_centenas)
    
    if len(fechamento_centenas) > 0:
        # Exibição em grid
        st.markdown("### 🏆 Centenas Sugeridas")
        
        num_cols = 5
        rows = (len(fechamento_centenas) + num_cols - 1) // num_cols
        
        for r in range(rows):
            cols = st.columns(num_cols)
            for c in range(num_cols):
                idx = r * num_cols + c
                if idx < len(fechamento_centenas):
                    row = fechamento_centenas.iloc[idx]
                    with cols[c]:
                        medal = ["🥇", "🥈", "🥉"][idx] if idx < 3 else f"{idx+1}º"
                        st.markdown(f"""
                        <div style="background: linear-gradient(145deg, #1e2130, #252836); 
                                    padding: 1rem; border-radius: 10px; text-align: center;
                                    border-left: 4px solid #1E88E5; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.8rem; color: #888;">{medal}</div>
                            <div style="font-size: 1.8rem; font-weight: bold; color: #1E88E5;">
                                {row['centena_fmt']}
                            </div>
                            <div style="color: #888; font-size: 0.8rem;">{row['frequencia']}x</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Gráfico
        fig = px.bar(
            fechamento_centenas,
            x='centena_fmt',
            y='frequencia',
            color='frequencia',
            color_continuous_scale=['#1e2130', '#1E88E5'],
            text='frequencia'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            coloraxis_showscale=False,
            xaxis_title='Centena',
            yaxis_title='Frequência'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🔍 Sem dados suficientes para fechamento.")

with tab3:
    st.subheader("🎰 Fechamento de Milhares")
    st.markdown("Ranking das milhares mais frequentes no período.")
    
    fechamento_milhares = stats.get_fechamento_milhares(df_filtered, top_n=qtd_milhares)
    
    if len(fechamento_milhares) > 0:
        # Exibição em grid
        st.markdown("### 🏆 Milhares Sugeridas")
        
        num_cols = 5
        rows = (len(fechamento_milhares) + num_cols - 1) // num_cols
        
        for r in range(rows):
            cols = st.columns(num_cols)
            for c in range(num_cols):
                idx = r * num_cols + c
                if idx < len(fechamento_milhares):
                    row = fechamento_milhares.iloc[idx]
                    with cols[c]:
                        medal = ["🥇", "🥈", "🥉"][idx] if idx < 3 else f"{idx+1}º"
                        st.markdown(f"""
                        <div style="background: linear-gradient(145deg, #1e2130, #252836); 
                                    padding: 1rem; border-radius: 10px; text-align: center;
                                    border-left: 4px solid #FF9800; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.8rem; color: #888;">{medal}</div>
                            <div style="font-size: 1.8rem; font-weight: bold; color: #FF9800;">
                                {row['milhar_fmt']}
                            </div>
                            <div style="color: #888; font-size: 0.8rem;">{row['frequencia']}x</div>
                        </div>
                        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Gráfico
        fig = px.bar(
            fechamento_milhares,
            x='milhar_fmt',
            y='frequencia',
            color='frequencia',
            color_continuous_scale=['#1e2130', '#FF9800'],
            text='frequencia'
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='#fff',
            coloraxis_showscale=False,
            xaxis_title='Milhar',
            yaxis_title='Frequência'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🔍 Sem dados suficientes para fechamento.")

with tab4:
    st.subheader("🔗 Correlações Grupo x Centena")
    st.markdown("Veja quais centenas aparecem mais para cada grupo.")
    
    # Seletor de grupo
    grupo_selecionado = st.selectbox(
        "Selecione o Grupo",
        options=list(range(1, 26)),
        format_func=lambda x: f"{x:02d} - {GRUPOS_ANIMAIS.get(x, '')}"
    )
    
    correlacao = stats.get_correlacao_grupo_centena(df_filtered, grupo_selecionado)
    
    if len(correlacao) > 0:
        st.markdown(f"### Centenas mais frequentes para o grupo {grupo_selecionado:02d} ({GRUPOS_ANIMAIS.get(grupo_selecionado, '')})")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                correlacao,
                x='centena_fmt',
                y='frequencia',
                color='frequencia',
                color_continuous_scale=['#1e2130', '#E91E63'],
                text='frequencia'
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#fff',
                coloraxis_showscale=False,
                xaxis_title='Centena',
                yaxis_title='Frequência'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📋 Top Centenas")
            for i, row in correlacao.iterrows():
                emoji = ["🥇", "🥈", "🥉"][i] if i < 3 else f"{i+1}º"
                st.markdown(f"{emoji} **{row['centena_fmt']}** - {row['frequencia']}x")
    else:
        st.info(f"🔍 Sem dados para o grupo {grupo_selecionado:02d} no período selecionado.")

st.divider()
st.caption("⚠️ Os fechamentos são baseados em análise estatística. Resultados passados não garantem resultados futuros. Use com responsabilidade.")
