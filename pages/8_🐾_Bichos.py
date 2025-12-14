"""
Tabela dos 25 Bichos - Visualização com cores automáticas por dia
Sistema adaptado para o novo escopo com ciclo de 5 dias
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Tabela dos Bichos", page_icon="🐾", layout="wide")

st.markdown("""
<style>
    .bicho-card {
        background: white;
        border: 2px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 5px;
        min-height: 140px;
    }
    
    .bicho-numero {
        font-size: 1.5rem;
        font-weight: bold;
        color: #333;
    }
    
    .bicho-nome {
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
    
    .bicho-emoji {
        font-size: 2rem;
    }
    
    .day-dots {
        display: flex;
        gap: 5px;
        justify-content: center;
        margin-top: 8px;
    }
    
    .day-dot {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .color-legend {
        display: flex;
        gap: 15px;
        margin: 15px 0;
        flex-wrap: wrap;
        justify-content: center;
    }
    
    .color-item {
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 8px 12px;
        border-radius: 8px;
        background: #f8f9fa;
        border: 1px solid #ddd;
    }
    
    .legend-dot {
        width: 16px;
        height: 16px;
        border-radius: 50%;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

st.title("🐾 Tabela dos 25 Bichos")

from modules.data_loader import (
    GRUPOS_ANIMAIS, DIA_CORES, 
    filter_5_day_cycle, get_grupo_days, get_day_color
)

# Emojis para cada animal
EMOJIS = {
    1: '🦢', 2: '🦅', 3: '🫏', 4: '🦋', 5: '🐕',
    6: '🐐', 7: '🐏', 8: '🐫', 9: '🐍', 10: '🐰',
    11: '🐴', 12: '🐘', 13: '🐓', 14: '🐱', 15: '🐊',
    16: '🦁', 17: '🐵', 18: '🐷', 19: '🦚', 20: '🦃',
    21: '🐂', 22: '🐅', 23: '🐻', 24: '🦌', 25: '🐄'
}

# Dezenas de cada grupo
DEZENAS = {
    1: ['01', '02', '03', '04'],
    2: ['05', '06', '07', '08'],
    3: ['09', '10', '11', '12'],
    4: ['13', '14', '15', '16'],
    5: ['17', '18', '19', '20'],
    6: ['21', '22', '23', '24'],
    7: ['25', '26', '27', '28'],
    8: ['29', '30', '31', '32'],
    9: ['33', '34', '35', '36'],
    10: ['37', '38', '39', '40'],
    11: ['41', '42', '43', '44'],
    12: ['45', '46', '47', '48'],
    13: ['49', '50', '51', '52'],
    14: ['53', '54', '55', '56'],
    15: ['57', '58', '59', '60'],
    16: ['61', '62', '63', '64'],
    17: ['65', '66', '67', '68'],
    18: ['69', '70', '71', '72'],
    19: ['73', '74', '75', '76'],
    20: ['77', '78', '79', '80'],
    21: ['81', '82', '83', '84'],
    22: ['85', '86', '87', '88'],
    23: ['89', '90', '91', '92'],
    24: ['93', '94', '95', '96'],
    25: ['97', '98', '99', '00']
}

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse **✨ Processador** para inserir resultados.")
    st.stop()

df = st.session_state.dados

# Sidebar - Filtro por Loteria (OBRIGATÓRIO)
st.sidebar.header("🔍 Filtro por Loteria")
loterias = df['loteria'].unique().tolist()
loteria_selecionada = st.sidebar.selectbox(
    "Selecione a Loteria:",
    options=loterias,
    help="Cada loteria é analisada separadamente."
)

# Legenda de cores - CRÍTICO: cores indicam APENAS o dia
st.markdown("""
### 📖 Legenda de Cores por Dia
<div class="color-legend">
    <div class="color-item"><span class="legend-dot" style="background:#FF0000;"></span> DIA 1 (Mais Recente)</div>
    <div class="color-item"><span class="legend-dot" style="background:#00C853;"></span> DIA 2</div>
    <div class="color-item"><span class="legend-dot" style="background:#2196F3;"></span> DIA 3</div>
    <div class="color-item"><span class="legend-dot" style="background:#FF9800;"></span> DIA 4</div>
    <div class="color-item"><span class="legend-dot" style="background:#333333;"></span> DIA 5 (Mais Antigo)</div>
</div>
""", unsafe_allow_html=True)

st.info("💡 **Importante:** As cores indicam EXCLUSIVAMENTE em quais dias o bicho apareceu nos últimos 5 dias. Não representam frequência ou probabilidade.")

st.divider()

# Exibir tabela de bichos
st.subheader(f"📋 Bichos - {loteria_selecionada}")

# Grid 5x5
for linha in range(5):
    cols = st.columns(5)
    for col_idx in range(5):
        grupo = linha * 5 + col_idx + 1
        animal = GRUPOS_ANIMAIS.get(grupo, '')
        emoji = EMOJIS.get(grupo, '🐾')
        dezenas = ', '.join(DEZENAS.get(grupo, []))
        
        # Obter dias em que o grupo apareceu (cores automáticas)
        dias_apareceu = get_grupo_days(df, loteria_selecionada, grupo)
        
        with cols[col_idx]:
            # Gerar HTML dos círculos de cores
            dots_html = ""
            if dias_apareceu:
                for dia_num in dias_apareceu:
                    cor_info = get_day_color(dia_num)
                    dots_html += f'<span class="day-dot" style="background:{cor_info["cor"]};" title="Dia {dia_num}"></span>'
            else:
                dots_html = '<span style="color:#999; font-size:0.8rem;">—</span>'
            
            # Card do bicho
            st.markdown(f"""
            <div class="bicho-card">
                <div class="bicho-emoji">{emoji}</div>
                <div class="bicho-numero">{grupo:02d}</div>
                <div class="bicho-nome">{animal}</div>
                <div style="font-size: 0.7rem; color: #888; margin-top: 3px;">{dezenas}</div>
                <div class="day-dots">{dots_html}</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# Resumo estatístico
st.subheader("📊 Resumo dos Últimos 5 Dias")

df_5dias = filter_5_day_cycle(df, loteria_selecionada)

if len(df_5dias) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total de Resultados", len(df_5dias))
    
    with col2:
        grupos_unicos = df_5dias['grupo'].nunique()
        st.metric("Grupos que Saíram", f"{grupos_unicos}/25")
    
    with col3:
        # Grupo mais frequente
        grupo_top = df_5dias['grupo'].value_counts().index[0]
        freq_top = df_5dias['grupo'].value_counts().values[0]
        st.metric("Grupo Top", f"{grupo_top:02d} - {GRUPOS_ANIMAIS.get(grupo_top, '')} ({freq_top}x)")
    
    # Tabela de frequência ordenada por frequência (não cronológica)
    st.markdown("### 📈 Frequência por Grupo (Ordenado por Frequência)")
    
    freq_df = df_5dias['grupo'].value_counts().reset_index()
    freq_df.columns = ['Grupo', 'Frequência']
    freq_df['Animal'] = freq_df['Grupo'].map(GRUPOS_ANIMAIS)
    freq_df['Grupo'] = freq_df['Grupo'].apply(lambda x: f"{x:02d}")
    freq_df = freq_df[['Grupo', 'Animal', 'Frequência']]
    
    st.dataframe(freq_df, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum dado encontrado para esta loteria nos últimos 5 dias.")

st.caption("⚠️ As cores nos cards indicam em quais dias o bicho apareceu. Isso é uma marcação visual por dia, não indica frequência ou probabilidade.")
