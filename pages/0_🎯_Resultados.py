"""
Resultados por Loteria - Visualização organizada por loteria
Sistema adaptado para o novo escopo com ciclo de 5 dias
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Resultados", page_icon="🎯", layout="wide")

# Verificação de autenticação
from modules.auth import check_authentication
check_authentication()

st.markdown("""
<style>
    .loteria-header {
        background: linear-gradient(90deg, #00C853, #00E676);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    .day-indicator {
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
    }
    
    .resultado-row {
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        margin: 5px 0;
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

st.title("🎯 Resultados por Loteria")

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse **✨ Processador** para inserir resultados.")
    st.stop()

from modules.data_loader import (
    GRUPOS_ANIMAIS, DIA_CORES, 
    filter_5_day_cycle, get_day_number, get_last_5_unique_dates, get_day_color,
    filter_day_data_by_prize
)

df = st.session_state.dados

# Sidebar - Filtro por Loteria (OBRIGATÓRIO)
st.sidebar.header("🔍 Filtro por Loteria")
loterias = df['loteria'].unique().tolist()
loteria_selecionada = st.sidebar.selectbox(
    "Selecione a Loteria:", 
    options=loterias,
    help="Cada loteria é analisada separadamente."
)

# Filtrar dados - apenas últimos 5 dias
df_5dias = filter_5_day_cycle(df, loteria_selecionada)
df_5dias = df_5dias.sort_values(['data', 'horario'], ascending=[False, True])

# Legenda de cores
st.markdown("""
<div class="color-legend">
    <div class="color-item"><span style="color:#FF0000;">●</span> DIA 1 (Mais Recente)</div>
    <div class="color-item"><span style="color:#00C853;">●</span> DIA 2</div>
    <div class="color-item"><span style="color:#2196F3;">●</span> DIA 3</div>
    <div class="color-item"><span style="color:#FF9800;">●</span> DIA 4</div>
    <div class="color-item"><span style="color:#333333;">●</span> DIA 5 (Mais Antigo)</div>
</div>
""", unsafe_allow_html=True)

# Header da loteria
st.markdown(f'<div class="loteria-header">🎰 {loteria_selecionada}</div>', unsafe_allow_html=True)

# Métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Resultados", len(df_5dias))

with col2:
    if len(df_5dias) > 0:
        grupo_top = df_5dias['grupo'].value_counts().index[0]
        st.metric("🥇 Grupo Top", f"{grupo_top:02d} - {GRUPOS_ANIMAIS.get(grupo_top, '')}")
    else:
        st.metric("🥇 Grupo Top", "N/A")

with col3:
    if len(df_5dias) > 0:
        datas_unicas = df_5dias['data'].dt.date.nunique()
        st.metric("📅 Dias Ativos", f"{datas_unicas}/5")
    else:
        st.metric("📅 Dias Ativos", 0)

with col4:
    if len(df_5dias) > 0:
        horarios = df_5dias['horario'].nunique()
        st.metric("⏰ Horários", horarios)
    else:
        st.metric("⏰ Horários", 0)

st.divider()

# Resultados organizados por DIA (1-5)
datas_5dias = get_last_5_unique_dates(df, loteria_selecionada)

for idx, data in enumerate(datas_5dias):
    dia_num = idx + 1
    cor_info = get_day_color(dia_num)
    
    df_dia = df_5dias[df_5dias['data'].dt.date == data]
    data_formatada = data.strftime('%d/%m/%Y')
    
    # Aplicar regra de prêmio
    df_dia_filtrado = filter_day_data_by_prize(df_dia, dia_num)
    
    # Label de regra
    regra_label = "TODOS" if dia_num <= 2 else "1° PRÊMIO"
    
    # Header do dia com cor
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 10px; margin: 15px 0;">
        <span class="day-indicator" style="background: {cor_info['cor']}; color: {cor_info['text_color']};">
            {cor_info['emoji']} DIA {dia_num} — {regra_label}
        </span>
        <span style="font-size: 1.2rem; font-weight: bold;">{data_formatada}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Grid de resultados do dia (usando dados filtrados)
    for _, row in df_dia_filtrado.iterrows():
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
        
        with col1:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.7rem; color: #888;">HORÁRIO</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #333;">{row['horario']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: {cor_info['cor']}; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.7rem; color: {cor_info['text_color']};">GRUPO</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: {cor_info['text_color']};">{row['grupo']:02d}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="background: #e3f2fd; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.7rem; color: #888;">CENTENA</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #1E88E5;">{row['centena']:03d}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div style="background: #fff3e0; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.7rem; color: #888;">MILHAR</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #FF9800;">{row['milhar']:04d}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            animal = GRUPOS_ANIMAIS.get(row['grupo'], '')
            st.markdown(f"""
            <div style="background: #f0f0f0; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.7rem; color: #888;">ANIMAL</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #333;">{animal}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")

# Tabela completa
with st.expander("📋 Ver tabela completa"):
    display_df = df_5dias.copy()
    
    # Adicionar coluna de dia
    display_df['dia'] = display_df['data'].apply(
        lambda x: get_day_number(df, loteria_selecionada, x)
    )
    
    display_df['data'] = pd.to_datetime(display_df['data']).dt.strftime('%d/%m/%Y')
    display_df['grupo'] = display_df['grupo'].apply(lambda x: f"{x:02d}")
    display_df['centena'] = display_df['centena'].apply(lambda x: f"{x:03d}")
    display_df['milhar'] = display_df['milhar'].apply(lambda x: f"{x:04d}")
    
    st.dataframe(
        display_df[['dia', 'data', 'horario', 'grupo', 'animal', 'centena', 'milhar']].rename(columns={
            'dia': 'Dia',
            'data': 'Data',
            'horario': 'Horário',
            'grupo': 'Grupo',
            'animal': 'Animal',
            'centena': 'Centena',
            'milhar': 'Milhar'
        }),
        use_container_width=True,
        hide_index=True
    )

st.caption("⚠️ Exibindo apenas os últimos 5 dias da loteria selecionada. Cores indicam o dia, não frequência.")
