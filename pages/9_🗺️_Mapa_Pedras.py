"""
Mapa de Pedras - Visualização de pedras por dia (ciclo de 5 dias)
Sistema adaptado para o novo escopo
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mapa de Pedras", page_icon="🗺️", layout="wide")

# Verificação de autenticação
from modules.auth import check_authentication
check_authentication()

st.markdown("""
<style>
    .pedra-box {
        background: #1a1a1a;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    .pedra-header {
        background: linear-gradient(90deg, #1a1a1a, #333);
        color: white;
        padding: 15px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        border-radius: 10px 10px 0 0;
        border: 1px solid #444;
    }
    
    .pedra-baixa {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        color: #1565c0;
    }
    
    .pedra-media {
        background: linear-gradient(135deg, #c8e6c9, #a5d6a7);
        color: #2e7d32;
    }
    
    .pedra-alta {
        background: linear-gradient(135deg, #ffecb3, #ffe082);
        color: #f57f17;
    }
    
    .resumo-box {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }
    
    .resumo-title {
        color: white;
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .color-legend {
        display: flex;
        gap: 15px;
        margin: 10px 0;
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

st.title("🗺️ Mapa de Pedras")

st.markdown("""
Visualização das pedras (dígitos 0-9) organizadas em categorias:
- **Baixas (0,1,2,3)** - Tons de azul
- **Médias (4,5,6)** - Tons de verde  
- **Altas (7,8,9)** - Tons de amarelo/laranja
""")

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse **✨ Processador** para inserir resultados.")
    st.stop()

from modules.data_loader import (
    DIA_CORES, filter_5_day_cycle, get_last_5_unique_dates, get_day_color,
    filter_by_day_prize_rules, filter_day_data_by_prize
)
from modules import statistics as stats

df = st.session_state.dados

# Sidebar - Filtro por Loteria (OBRIGATÓRIO)
st.sidebar.header("🔍 Filtro por Loteria")
loterias = df['loteria'].unique().tolist()
loteria_sel = st.sidebar.selectbox(
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

st.divider()

# Filtrar dados - últimos 5 dias (sem regra de prêmio para visualização geral)
df_5dias = filter_5_day_cycle(df, loteria_sel)
# Filtrar dados com regra de prêmio para análises
df_5dias_filtered = filter_by_day_prize_rules(df, loteria_sel)
datas_5dias = get_last_5_unique_dates(df, loteria_sel)

if len(df_5dias) == 0:
    st.warning(f"⚠️ Nenhum dado encontrado para a loteria **{loteria_sel}**.")
    st.stop()

def get_total_freq(df, tipo='milhar'):
    """Frequência total do primeiro dígito (pedra) de cada número"""
    freq = {d: 0 for d in range(10)}
    col = 'milhar' if tipo == 'milhar' else 'centena'
    
    for val in df[col]:
        val_str = str(val).zfill(4 if tipo == 'milhar' else 3)  # Garantir formato correto
        first_digit = int(val_str[0])  # Extrair apenas o primeiro dígito (pedra)
        freq[first_digit] += 1
    
    return freq

def get_digit_freq_by_day(df, df_full, loteria, tipo='milhar'):
    """Frequência do primeiro dígito (pedra) por dia, com regra de prêmio"""
    freq_by_day = {dia: {d: 0 for d in range(10)} for dia in range(1, 6)}
    col = 'milhar' if tipo == 'milhar' else 'centena'
    datas = get_last_5_unique_dates(df_full, loteria)
    
    for idx, data in enumerate(datas):
        if idx >= 5:
            break
        dia_num = idx + 1
        df_dia = df[df['data'].dt.date == data]
        
        # Aplicar regra de prêmio
        df_dia = filter_day_data_by_prize(df_dia, dia_num)
        
        for val in df_dia[col]:
            val_str = str(val).zfill(4 if tipo == 'milhar' else 3)
            first_digit = int(val_str[0])
            freq_by_day[dia_num][first_digit] += 1
    
    return freq_by_day

# Mapa de Pedras - Milhar e Centena lado a lado
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="pedra-box">
        <div class="pedra-header">PEDRAS DE MILHAR (5 DIAS)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Labels das categorias
    cat_col1, cat_col2, cat_col3 = st.columns(3)
    with cat_col1:
        st.markdown("**🔵 BAIXAS**")
        st.caption("0, 1, 2, 3")
    with cat_col2:
        st.markdown("**🟢 MÉDIAS**")
        st.caption("4, 5, 6")
    with cat_col3:
        st.markdown("**🟡 ALTAS**")
        st.caption("7, 8, 9")
    
    # Grid de frequências (usa dados filtrados com regra de prêmio)
    freq_milhar = get_total_freq(df_5dias_filtered, 'milhar')
    max_freq = max(freq_milhar.values()) if sum(freq_milhar.values()) > 0 else 1
    
    st.markdown("#### Frequência Total por Dígito")
    
    cols = st.columns(10)
    for digit in range(10):
        with cols[digit]:
            freq = freq_milhar[digit]
            # Cor baseada na categoria
            if digit <= 3:
                bg = "#e3f2fd"
                color = "#1565c0"
            elif digit <= 6:
                bg = "#c8e6c9"
                color = "#2e7d32"
            else:
                bg = "#ffe082"
                color = "#f57f17"
            
            st.markdown(f"""
            <div style="background: {bg}; color: {color}; padding: 15px 10px; 
                        text-align: center; border-radius: 5px; 
                        font-weight: bold; font-size: 1.2rem;">
                {digit}<br><span style="font-size: 0.8rem;">({freq})</span>
            </div>
            """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="pedra-box">
        <div class="pedra-header">PEDRAS DE CENTENA (5 DIAS)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Labels das categorias
    cat_col1, cat_col2, cat_col3 = st.columns(3)
    with cat_col1:
        st.markdown("**🔵 BAIXAS**")
        st.caption("0, 1, 2, 3")
    with cat_col2:
        st.markdown("**🟢 MÉDIAS**")
        st.caption("4, 5, 6")
    with cat_col3:
        st.markdown("**🟡 ALTAS**")
        st.caption("7, 8, 9")
    
    freq_centena = get_total_freq(df_5dias_filtered, 'centena')
    max_freq_c = max(freq_centena.values()) if sum(freq_centena.values()) > 0 else 1
    
    st.markdown("#### Frequência Total por Dígito")
    
    cols = st.columns(10)
    for digit in range(10):
        with cols[digit]:
            freq = freq_centena[digit]
            if digit <= 3:
                bg = "#e3f2fd"
                color = "#1565c0"
            elif digit <= 6:
                bg = "#c8e6c9"
                color = "#2e7d32"
            else:
                bg = "#ffe082"
                color = "#f57f17"
            
            st.markdown(f"""
            <div style="background: {bg}; color: {color}; padding: 15px 10px; 
                        text-align: center; border-radius: 5px; 
                        font-weight: bold; font-size: 1.2rem;">
                {digit}<br><span style="font-size: 0.8rem;">({freq})</span>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# Análise por Dia
st.subheader("📊 Frequência de Pedras por Dia")

freq_milhar_by_day = get_digit_freq_by_day(df_5dias, df, loteria_sel, 'milhar')
freq_centena_by_day = get_digit_freq_by_day(df_5dias, df, loteria_sel, 'centena')

# Criar tabs para cada dia
tabs = st.tabs([f"{DIA_CORES[d]['emoji']} DIA {d}" for d in range(1, 6)])

for idx, tab in enumerate(tabs):
    dia_num = idx + 1
    cor_info = get_day_color(dia_num)
    
    with tab:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style="background: {cor_info['cor']}; color: {cor_info['text_color']}; 
                        padding: 10px; border-radius: 8px; text-align: center; 
                        font-weight: bold; margin-bottom: 10px;">
                MILHAR - DIA {dia_num}
            </div>
            """, unsafe_allow_html=True)
            
            freq_m = freq_milhar_by_day[dia_num]
            for digit in range(10):
                count = freq_m[digit]
                bars = "█" * count if count > 0 else "—"
                st.markdown(f"`{digit}` = {bars} ({count})")
        
        with col2:
            st.markdown(f"""
            <div style="background: {cor_info['cor']}; color: {cor_info['text_color']}; 
                        padding: 10px; border-radius: 8px; text-align: center; 
                        font-weight: bold; margin-bottom: 10px;">
                CENTENA - DIA {dia_num}
            </div>
            """, unsafe_allow_html=True)
            
            freq_c = freq_centena_by_day[dia_num]
            for digit in range(10):
                count = freq_c[digit]
                bars = "█" * count if count > 0 else "—"
                st.markdown(f"`{digit}` = {bars} ({count})")

st.divider()

# Casas de Pedras
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎲 Casas de pedras — Milhar")
    
    freq_m = get_total_freq(df_5dias_filtered, 'milhar')
    baixas = [d for d in [0,1,2,3] if freq_m[d] > 0]
    medias = [d for d in [4,5,6] if freq_m[d] > 0]
    altas = [d for d in [7,8,9] if freq_m[d] > 0]
    
    ausentes_baixas = [d for d in [0,1,2,3] if freq_m[d] == 0]
    ausentes_medias = [d for d in [4,5,6] if freq_m[d] == 0]
    ausentes_altas = [d for d in [7,8,9] if freq_m[d] == 0]
    
    st.markdown(f"**Presentes:** 🔵 ({','.join(map(str, baixas)) or '—'}), 🟢 ({','.join(map(str, medias)) or '—'}), 🟡 ({','.join(map(str, altas)) or '—'})")
    st.markdown(f"**Ausentes:** 🔵 ({','.join(map(str, ausentes_baixas)) or '—'}), 🟢 ({','.join(map(str, ausentes_medias)) or '—'}), 🟡 ({','.join(map(str, ausentes_altas)) or '—'})")

with col2:
    st.markdown("### 🎲 Casas de pedras — Centena")
    
    freq_c = get_total_freq(df_5dias_filtered, 'centena')
    baixas_c = [d for d in [0,1,2,3] if freq_c[d] > 0]
    medias_c = [d for d in [4,5,6] if freq_c[d] > 0]
    altas_c = [d for d in [7,8,9] if freq_c[d] > 0]
    
    ausentes_baixas_c = [d for d in [0,1,2,3] if freq_c[d] == 0]
    ausentes_medias_c = [d for d in [4,5,6] if freq_c[d] == 0]
    ausentes_altas_c = [d for d in [7,8,9] if freq_c[d] == 0]
    
    st.markdown(f"**Presentes:** 🔵 ({','.join(map(str, baixas_c)) or '—'}), 🟢 ({','.join(map(str, medias_c)) or '—'}), 🟡 ({','.join(map(str, altas_c)) or '—'})")
    st.markdown(f"**Ausentes:** 🔵 ({','.join(map(str, ausentes_baixas_c)) or '—'}), 🟢 ({','.join(map(str, ausentes_medias_c)) or '—'}), 🟡 ({','.join(map(str, ausentes_altas_c)) or '—'})")

st.caption("⚠️ Análise de pedras (dígitos) nos últimos 5 dias da loteria selecionada. Janela fixa de 5 dias conforme escopo.")
