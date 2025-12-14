"""
Consolidação Estatística - Grupos, Centenas e Milhares mais frequentes
Sistema adaptado para o novo escopo com ciclo de 5 dias
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Consolidação", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .consolidation-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    
    .stat-card {
        background: white;
        border: 2px solid #00C853;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    
    .stat-rank {
        font-size: 2rem;
        font-weight: bold;
        color: #00C853;
    }
    
    .stat-value {
        font-size: 1.5rem;
        color: #333;
        margin-top: 10px;
    }
    
    .stat-freq {
        font-size: 1rem;
        color: #666;
    }
    
    .color-legend {
        display: flex;
        gap: 15px;
        margin: 15px 0;
        flex-wrap: wrap;
    }
    
    .color-item {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 5px 10px;
        border-radius: 5px;
        background: #f0f0f0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="consolidation-header">
    <h1>📊 Consolidação Estatística</h1>
    <p>Análise consolidada dos últimos 5 dias por frequência</p>
</div>
""", unsafe_allow_html=True)

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse **✨ Processador** para inserir resultados.")
    st.stop()

from modules.data_loader import (
    GRUPOS_ANIMAIS, DIA_CORES, filter_5_day_cycle, get_last_5_unique_dates
)
from modules import statistics as stats

df = st.session_state.dados

# Sidebar - Filtro por Loteria (OBRIGATÓRIO)
st.sidebar.header("🔍 Filtro por Loteria")
loterias = df['loteria'].unique().tolist()
loteria_selecionada = st.sidebar.selectbox(
    "Selecione a Loteria:", 
    options=loterias,
    help="Cada loteria é analisada separadamente."
)

# Legenda de cores
st.markdown("""
<div class="color-legend">
    <div class="color-item"><span style="color:#FF0000;">●</span> DIA 1</div>
    <div class="color-item"><span style="color:#00C853;">●</span> DIA 2</div>
    <div class="color-item"><span style="color:#2196F3;">●</span> DIA 3</div>
    <div class="color-item"><span style="color:#FF9800;">●</span> DIA 4</div>
    <div class="color-item"><span style="color:#333333;">●</span> DIA 5</div>
</div>
""", unsafe_allow_html=True)

# Filtrar dados - apenas últimos 5 dias
df_5dias = filter_5_day_cycle(df, loteria_selecionada)
datas_5dias = get_last_5_unique_dates(df, loteria_selecionada)

if len(df_5dias) == 0:
    st.warning(f"⚠️ Nenhum dado encontrado para a loteria **{loteria_selecionada}**.")
    st.stop()

# Métricas gerais
st.subheader(f"📈 Resumo - {loteria_selecionada}")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de Resultados", len(df_5dias))
with col2:
    st.metric("Dias Ativos", len(datas_5dias))
with col3:
    grupos_unicos = df_5dias['grupo'].nunique()
    st.metric("Grupos Únicos", f"{grupos_unicos}/25")
with col4:
    centenas_unicas = df_5dias['centena'].nunique()
    st.metric("Centenas Únicas", centenas_unicas)

st.divider()

# Consolidação por Frequência (ORDENAÇÃO POR FREQUÊNCIA, NÃO CRONOLÓGICA)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🐾 Grupos Mais Frequentes")
    
    grupos_freq = df_5dias['grupo'].value_counts().reset_index()
    grupos_freq.columns = ['Grupo', 'Frequência']
    grupos_freq['Animal'] = grupos_freq['Grupo'].map(GRUPOS_ANIMAIS)
    grupos_freq['Grupo'] = grupos_freq['Grupo'].apply(lambda x: f"{x:02d}")
    
    # Top 5 com cards visuais
    for i, row in grupos_freq.head(5).iterrows():
        emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(i, 4)]
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-rank">{emoji}</div>
            <div class="stat-value">{row['Grupo']} - {row['Animal']}</div>
            <div class="stat-freq">{row['Frequência']}x nos últimos 5 dias</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabela completa
    with st.expander("Ver ranking completo"):
        st.dataframe(grupos_freq, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### 💯 Centenas Mais Frequentes")
    
    centenas_freq = df_5dias['centena'].value_counts().reset_index()
    centenas_freq.columns = ['Centena', 'Frequência']
    centenas_freq['Centena'] = centenas_freq['Centena'].apply(lambda x: f"{x:03d}")
    
    # Top 5 com cards visuais
    for i, row in centenas_freq.head(5).iterrows():
        emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(i, 4)]
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-rank">{emoji}</div>
            <div class="stat-value">{row['Centena']}</div>
            <div class="stat-freq">{row['Frequência']}x nos últimos 5 dias</div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("Ver ranking completo"):
        st.dataframe(centenas_freq, use_container_width=True, hide_index=True)

with col3:
    st.markdown("### 🔢 Milhares Mais Frequentes")
    
    milhares_freq = df_5dias['milhar'].value_counts().reset_index()
    milhares_freq.columns = ['Milhar', 'Frequência']
    milhares_freq['Milhar'] = milhares_freq['Milhar'].apply(lambda x: f"{x:04d}")
    
    # Top 5 com cards visuais
    for i, row in milhares_freq.head(5).iterrows():
        emoji = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][min(i, 4)]
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-rank">{emoji}</div>
            <div class="stat-value">{row['Milhar']}</div>
            <div class="stat-freq">{row['Frequência']}x nos últimos 5 dias</div>
        </div>
        """, unsafe_allow_html=True)
    
    with st.expander("Ver ranking completo"):
        st.dataframe(milhares_freq, use_container_width=True, hide_index=True)

st.divider()

# Análise de ausências
st.subheader("🔍 Análise de Ausências")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Grupos que NÃO saíram (últimos 5 dias)")
    
    grupos_presentes = set(df_5dias['grupo'].unique())
    grupos_ausentes = [g for g in range(1, 26) if g not in grupos_presentes]
    
    if grupos_ausentes:
        for g in grupos_ausentes:
            animal = GRUPOS_ANIMAIS.get(g, '')
            st.markdown(f"- **{g:02d}** - {animal}")
    else:
        st.success("✅ Todos os 25 grupos apareceram!")

with col2:
    st.markdown("#### Distribuição por Dia")
    
    for idx, data in enumerate(datas_5dias):
        dia_num = idx + 1
        cor_info = DIA_CORES[dia_num]
        df_dia = df_5dias[df_5dias['data'].dt.date == data]
        
        st.markdown(f"""
        {cor_info['emoji']} **DIA {dia_num}** ({data.strftime('%d/%m')}): 
        {len(df_dia)} resultados, {df_dia['grupo'].nunique()} grupos únicos
        """)

st.caption("⚠️ Consolidação estatística dos últimos 5 dias. Ordenação por FREQUÊNCIA, não cronológica. Cada loteria é analisada separadamente.")
