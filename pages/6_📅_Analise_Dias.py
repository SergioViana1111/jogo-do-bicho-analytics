"""
Análise por Dias - DIA 1 a DIA 5
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Análise por Dias", page_icon="📅", layout="wide")

# CSS customizado para o layout verde
st.markdown("""
<style>
    .day-header {
        background: linear-gradient(90deg, #00C853, #00E676);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 15px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .animal-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 2px;
        background: #00C853;
        padding: 2px;
        border-radius: 8px;
    }
    
    .animal-cell {
        background: #f0f0f0;
        padding: 10px;
        text-align: center;
        font-size: 0.9rem;
    }
    
    .animal-cell-header {
        background: #00C853;
        color: white;
        padding: 10px;
        text-align: center;
        font-weight: bold;
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
    
    .freq-summary {
        color: #FFD700;
        font-weight: bold;
        margin-top: 10px;
        padding: 5px 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("📅 Análise por Dias")

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse a página **📤 Upload** primeiro.")
    st.stop()

from modules.data_loader import GRUPOS_ANIMAIS

df = st.session_state.dados

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")
loterias = df['loteria'].unique().tolist()
loteria_selecionada = st.sidebar.selectbox("Loteria", options=loterias)

# Filtrar por loteria
df_lot = df[df['loteria'] == loteria_selecionada].copy()
df_lot = df_lot.sort_values('data', ascending=False)

# Pegar as últimas 5 datas únicas
datas_unicas = df_lot['data'].dt.date.unique()[:5]

# Nomes dos dias
dias_nomes = ["DIA 1 (HOJE)", "DIA 2 (ONTEM)", "DIA 3 (TERCEIRO DIA)", "DIA 4 (QUARTO DIA)", "DIA 5 (QUINTO DIA)"]

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
for idx, data in enumerate(datas_unicas):
    if idx >= 5:
        break
    
    df_dia = df_lot[df_lot['data'].dt.date == data]
    dia_nome = dias_nomes[idx] if idx < len(dias_nomes) else f"DIA {idx+1}"
    
    st.markdown(f'<div class="day-header">📊 ANÁLISE DOS BICHOS - {dia_nome}</div>', unsafe_allow_html=True)
    
    # Grid de animais (5 colunas x 5 linhas)
    animal_counts = get_animal_counts(df_dia)
    
    # Criar grid de animais
    cols = st.columns(5)
    for i in range(25):
        grupo = i + 1
        animal = GRUPOS_ANIMAIS.get(grupo, '')
        count = animal_counts.get(grupo, 0)
        
        with cols[i % 5]:
            # Cor de fundo baseada na contagem
            bg_color = "#e8f5e9" if count > 0 else "#f5f5f5"
            text_color = "#00C853" if count > 0 else "#666"
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
        st.markdown(f"### 📋 Tabela de Dezenas - {dia_nome.split(' ')[0]} {dia_nome.split(' ')[1] if len(dia_nome.split(' ')) > 1 else ''}")
        
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
                'Grupos': grupo,
                'Nomes': animal,
                'Dezenas': dezenas
            })
        
        df_dezenas = pd.DataFrame(dezenas_data)
        st.dataframe(df_dezenas, use_container_width=True, hide_index=True, height=400)
    
    with col2:
        # Frequência de Pedras - Milhar
        st.markdown(f"""
        <div style="background: #1a1a1a; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
            <div style="background: #00C853; color: white; padding: 10px; text-align: center; 
                        font-weight: bold; border-radius: 5px; margin-bottom: 10px;">
                FREQUÊNCIA DE PEDRAS - MILHAR ({dia_nome.split(' ')[0]} {dia_nome.split(' ')[1] if len(dia_nome.split(' ')) > 1 else ''})
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
            <div style="background: #00C853; color: white; padding: 10px; text-align: center; 
                        font-weight: bold; border-radius: 5px; margin-bottom: 10px;">
                FREQUÊNCIA DE PEDRAS - CENTENA ({dia_nome.split(' ')[0]} {dia_nome.split(' ')[1] if len(dia_nome.split(' ')) > 1 else ''})
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

st.caption("⚠️ Análise estatística para fins informativos. Resultados passados não garantem resultados futuros.")
