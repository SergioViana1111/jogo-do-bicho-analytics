"""
Análise por Dias - DIA 1 a DIA 5 com cores fixas
Sistema adaptado para o novo escopo com ciclo de 5 dias
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Análise por Dias", page_icon="📅", layout="wide")

# CSS customizado com cores por dia
st.markdown("""
<style>
    .day-header-1 {
        background: linear-gradient(90deg, #FF0000, #FF4444);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .day-header-2 {
        background: linear-gradient(90deg, #00C853, #00E676);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .day-header-3 {
        background: linear-gradient(90deg, #2196F3, #42A5F5);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .day-header-4 {
        background: linear-gradient(90deg, #FF9800, #FFB74D);
        color: #000;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .day-header-5 {
        background: linear-gradient(90deg, #333333, #555555);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .freq-table {
        background: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    
    .freq-header {
        background: #00C853;
        color: white;
        padding: 10px;
        text-align: center;
        font-weight: bold;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    .freq-row {
        color: #FFD700;
        font-family: monospace;
        padding: 2px 10px;
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

st.title("📅 Análise por Dias")

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse **✨ Processador** para inserir resultados.")
    st.stop()

from modules.data_loader import (
    GRUPOS_ANIMAIS, DIA_CORES, 
    get_last_5_unique_dates, get_day_number, filter_5_day_cycle, get_day_color
)

df = st.session_state.dados

# Sidebar - Filtro por Loteria (OBRIGATÓRIO)
st.sidebar.header("🔍 Filtro por Loteria")
loterias = df['loteria'].unique().tolist()
loteria_selecionada = st.sidebar.selectbox(
    "Selecione a Loteria:", 
    options=loterias,
    help="Cada loteria é analisada separadamente. Nunca misturar dados."
)

# Legenda de cores
st.markdown("""
<div class="color-legend">
    <div class="color-item"><span style="color:#FF0000;">●</span> DIA 1 - Vermelho (Mais Recente)</div>
    <div class="color-item"><span style="color:#00C853;">●</span> DIA 2 - Verde</div>
    <div class="color-item"><span style="color:#2196F3;">●</span> DIA 3 - Azul</div>
    <div class="color-item"><span style="color:#FF9800;">●</span> DIA 4 - Laranja</div>
    <div class="color-item"><span style="color:#333333;">●</span> DIA 5 - Preto (Mais Antigo)</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# Filtrar por loteria e obter últimos 5 dias
df_5dias = filter_5_day_cycle(df, loteria_selecionada)
datas_5dias = get_last_5_unique_dates(df, loteria_selecionada)

if len(datas_5dias) == 0:
    st.warning(f"⚠️ Nenhum dado encontrado para a loteria **{loteria_selecionada}**.")
    st.stop()

# Nomes dos dias com cores
dias_config = [
    {"nome": "DIA 1 (MAIS RECENTE)", "classe": "day-header-1", "cor": DIA_CORES[1]},
    {"nome": "DIA 2", "classe": "day-header-2", "cor": DIA_CORES[2]},
    {"nome": "DIA 3", "classe": "day-header-3", "cor": DIA_CORES[3]},
    {"nome": "DIA 4", "classe": "day-header-4", "cor": DIA_CORES[4]},
    {"nome": "DIA 5 (MAIS ANTIGO)", "classe": "day-header-5", "cor": DIA_CORES[5]},
]

def get_animal_counts(df_dia):
    """Conta quantas vezes cada animal saiu no dia"""
    counts = {i: 0 for i in range(1, 26)}
    for grupo in df_dia['grupo']:
        if 1 <= grupo <= 25:
            counts[grupo] += 1
    return counts

def get_digit_frequency(df_dia, tipo='milhar'):
    """Conta frequência de cada dígito (0-9) nas pedras"""
    freq = {i: 0 for i in range(10)}
    col = 'milhar' if tipo == 'milhar' else 'centena'
    for val in df_dia[col]:
        for digit in str(val).zfill(4 if tipo == 'milhar' else 3):
            freq[int(digit)] += 1
    return freq

# Análise por dia
for idx, data in enumerate(datas_5dias):
    if idx >= 5:
        break
    
    df_dia = df_5dias[df_5dias['data'].dt.date == data]
    config = dias_config[idx]
    dia_num = idx + 1
    cor_info = DIA_CORES[dia_num]
    
    data_formatada = data.strftime('%d/%m/%Y')
    
    # Header com cor do dia
    st.markdown(f'''
    <div class="{config['classe']}">
        {cor_info['emoji']} ANÁLISE - {config['nome']} ({data_formatada})
    </div>
    ''', unsafe_allow_html=True)
    
    # Grid de animais (5 colunas x 5 linhas)
    animal_counts = get_animal_counts(df_dia)
    
    # Criar grid de animais
    cols = st.columns(5)
    for i in range(25):
        grupo = i + 1
        animal = GRUPOS_ANIMAIS.get(grupo, '')
        count = animal_counts.get(grupo, 0)
        
        with cols[i % 5]:
            # Cor de fundo baseada na contagem e na cor do dia
            if count > 0:
                bg_color = cor_info['cor']
                text_color = cor_info['text_color']
            else:
                bg_color = "#f5f5f5"
                text_color = "#666"
            
            st.markdown(f"""
            <div style="background: {bg_color}; padding: 8px; margin: 2px; 
                        border-radius: 5px; text-align: center; border: 1px solid #ddd;">
                <span style="color: {text_color}; font-weight: {'bold' if count > 0 else 'normal'};">
                    {animal}: {count}
                </span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Tabela de Dezenas e Frequência de Pedras lado a lado
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### 📋 Tabela de Dezenas - DIA {dia_num}")
        
        # Criar tabela de dezenas
        dezenas_data = []
        dezenas_found = {}
        
        for _, row in df_dia.iterrows():
            grupo = row['grupo']
            milhar = str(row['milhar']).zfill(4)
            # Dezena é os 2 últimos dígitos
            dezena = milhar[-2:]
            if grupo not in dezenas_found:
                dezenas_found[grupo] = []
            dezenas_found[grupo].append(dezena)
        
        for grupo in range(1, 26):
            animal = GRUPOS_ANIMAIS.get(grupo, '')
            dezenas = ', '.join(dezenas_found.get(grupo, []))
            dezenas_data.append({
                'Grupo': f"{grupo:02d}",
                'Nome': animal,
                'Dezenas': dezenas if dezenas else '—'
            })
        
        df_dezenas = pd.DataFrame(dezenas_data)
        st.dataframe(df_dezenas, use_container_width=True, hide_index=True, height=400)
    
    with col2:
        # Frequência de Pedras - Milhar
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
            <div style="background: {cor_info['cor']}; color: {cor_info['text_color']}; padding: 10px; text-align: center; 
                        font-weight: bold; border-radius: 5px; margin-bottom: 10px;">
                FREQUÊNCIA DE PEDRAS - MILHAR (DIA {dia_num})
            </div>
        """, unsafe_allow_html=True)
        
        freq_milhar = get_digit_frequency(df_dia, 'milhar')
        
        # Mostrar frequências
        freq_html = ""
        for digit in range(10):
            count = freq_milhar[digit]
            freq_html += f'<div style="color: #FFD700; font-family: monospace; padding: 2px 10px;">{digit} = {"█" * count} {count}</div>'
        
        # Resumo
        max_freq = max(freq_milhar.values()) if sum(freq_milhar.values()) > 0 else 0
        min_freq = min(freq_milhar.values()) if sum(freq_milhar.values()) > 0 else 0
        max_digits = [d for d, f in freq_milhar.items() if f == max_freq and max_freq > 0]
        min_digits = [d for d, f in freq_milhar.items() if f == min_freq]
        nunca = [d for d, f in freq_milhar.items() if f == 0]
        
        freq_html += f'<div style="color: #FFD700; font-weight: bold; margin-top: 10px; padding: 5px 10px;">PEDRA MAIS FREQUENTE = {", ".join(map(str, max_digits)) if max_digits else "N/A"}</div>'
        freq_html += f'<div style="color: #FFD700; font-weight: bold; padding: 5px 10px;">PEDRA MENOS FREQUENTE = {", ".join(map(str, min_digits)) if min_digits else "N/A"}</div>'
        freq_html += f'<div style="color: #FFD700; font-weight: bold; padding: 5px 10px;">PEDRAS QUE NUNCA SAÍRAM = {", ".join(map(str, nunca)) if nunca else "Nenhuma"}</div>'
        
        freq_html += "</div>"
        st.markdown(freq_html, unsafe_allow_html=True)
        
        # Frequência de Pedras - Centena
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 15px; border-radius: 10px; margin-top: 10px;">
            <div style="background: {cor_info['cor']}; color: {cor_info['text_color']}; padding: 10px; text-align: center; 
                        font-weight: bold; border-radius: 5px; margin-bottom: 10px;">
                FREQUÊNCIA DE PEDRAS - CENTENA (DIA {dia_num})
            </div>
        """, unsafe_allow_html=True)
        
        freq_centena = get_digit_frequency(df_dia, 'centena')
        
        freq_html = ""
        for digit in range(10):
            count = freq_centena[digit]
            freq_html += f'<div style="color: #FFD700; font-family: monospace; padding: 2px 10px;">{digit} = {"█" * count} {count}</div>'
        
        max_freq_c = max(freq_centena.values()) if sum(freq_centena.values()) > 0 else 0
        min_freq_c = min(freq_centena.values()) if sum(freq_centena.values()) > 0 else 0
        max_digits_c = [d for d, f in freq_centena.items() if f == max_freq_c and max_freq_c > 0]
        min_digits_c = [d for d, f in freq_centena.items() if f == min_freq_c]
        nunca_c = [d for d, f in freq_centena.items() if f == 0]
        
        freq_html += f'<div style="color: #FFD700; font-weight: bold; margin-top: 10px; padding: 5px 10px;">PEDRA MAIS FREQUENTE = {", ".join(map(str, max_digits_c)) if max_digits_c else "N/A"}</div>'
        freq_html += f'<div style="color: #FFD700; font-weight: bold; padding: 5px 10px;">PEDRA MENOS FREQUENTE = {", ".join(map(str, min_digits_c)) if min_digits_c else "N/A"}</div>'
        freq_html += f'<div style="color: #FFD700; font-weight: bold; padding: 5px 10px;">PEDRAS QUE NUNCA SAÍRAM = {", ".join(map(str, nunca_c)) if nunca_c else "Nenhuma"}</div>'
        
        freq_html += "</div>"
        st.markdown(freq_html, unsafe_allow_html=True)
    
    st.markdown("---")

st.caption("⚠️ Análise estatística para fins informativos. Cores indicam APENAS o dia, não representam frequência ou probabilidade.")
