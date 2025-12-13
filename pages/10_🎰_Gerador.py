"""
Gerador de Milhar e Centena - Gere números baseado em pedras e animais
"""
import streamlit as st
import pandas as pd
from itertools import product

st.set_page_config(page_title="Gerador", page_icon="🎰", layout="wide")

st.markdown("""
<style>
    .generator-box {
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        padding: 25px;
        border-radius: 15px;
        margin-bottom: 20px;
    }
    
    .generator-title {
        color: #333;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .generator-subtitle {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 20px;
    }
    
    .results-box {
        background: white;
        border: 2px solid #00C853;
        border-radius: 10px;
        padding: 20px;
        margin-top: 20px;
    }
    
    .results-header {
        color: #00C853;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .animal-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 5px;
    }
    
    .animal-btn {
        padding: 8px 12px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .example-box {
        background: #fff9c4;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎰 Gerador de Milhar e Centena")

st.markdown("""
<div class="generator-box">
    <div class="generator-title">💡 Gerador de Milhar e Centena</div>
    <div class="generator-subtitle">Digite as pedras e animais para gerar automaticamente</div>
</div>
""", unsafe_allow_html=True)

from modules.data_loader import GRUPOS_ANIMAIS

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

EMOJIS = {
    1: '🦢', 2: '🦅', 3: '🫏', 4: '🦋', 5: '🐕',
    6: '🐐', 7: '🐏', 8: '🐫', 9: '🐍', 10: '🐰',
    11: '🐴', 12: '🐘', 13: '🐓', 14: '🐱', 15: '🐊',
    16: '🦁', 17: '🐵', 18: '🐷', 19: '🦚', 20: '🦃',
    21: '🐂', 22: '🐅', 23: '🐻', 24: '🦌', 25: '🐄'
}

# Inputs
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Pedras de Milhar (0-9)**")
    pedras_milhar = st.text_input(
        "Pedras Milhar",
        placeholder="Ex: 1,2,3",
        help="Separe por vírgula",
        label_visibility="collapsed"
    )
    st.caption("Separe por vírgula")

with col2:
    st.markdown("**Pedras de Centena (0-9)**")
    pedras_centena = st.text_input(
        "Pedras Centena",
        placeholder="Ex: 4,5,6",
        help="Separe por vírgula",
        label_visibility="collapsed"
    )
    st.caption("Separe por vírgula")

with col3:
    st.markdown("**Animais (1-25)**")
    animais_input = st.text_input(
        "Animais",
        placeholder="Ex: 1,5,10",
        help="Separe por vírgula",
        label_visibility="collapsed"
    )
    st.caption("Separe por vírgula")

# Grid de animais para seleção rápida
st.markdown("**Clique nos emojis para selecionar os animais:**")

# Inicializar estado de animais selecionados
if 'animais_selecionados' not in st.session_state:
    st.session_state.animais_selecionados = []

# Grid de emojis (5x5)
for linha in range(5):
    cols = st.columns(10)
    for col_idx in range(5):
        grupo = linha * 5 + col_idx + 1
        emoji = EMOJIS.get(grupo, '🐾')
        
        with cols[col_idx * 2]:
            selecionado = grupo in st.session_state.animais_selecionados
            bg = "#00C853" if selecionado else "#f0f0f0"
            
            if st.button(emoji, key=f"emoji_{grupo}", help=f"{grupo} - {GRUPOS_ANIMAIS.get(grupo, '')}"):
                if grupo in st.session_state.animais_selecionados:
                    st.session_state.animais_selecionados.remove(grupo)
                else:
                    st.session_state.animais_selecionados.append(grupo)
                st.rerun()

# Mostrar selecionados
if st.session_state.animais_selecionados:
    selecionados_str = ', '.join([f"{g} ({GRUPOS_ANIMAIS.get(g, '')})" for g in sorted(st.session_state.animais_selecionados)])
    st.info(f"**Animais selecionados:** {selecionados_str}")

# Botão gerar
gerar = st.button("🎰 Gerar Números", type="primary", use_container_width=True)

if gerar:
    # Processar inputs
    milhares_geradas = []
    centenas_geradas = []
    
    # Parse pedras
    try:
        p_milhar = [int(x.strip()) for x in pedras_milhar.split(',') if x.strip().isdigit()] if pedras_milhar else []
        p_centena = [int(x.strip()) for x in pedras_centena.split(',') if x.strip().isdigit()] if pedras_centena else []
    except:
        p_milhar = []
        p_centena = []
    
    # Parse animais (do input ou da seleção)
    animais = []
    if animais_input:
        try:
            animais = [int(x.strip()) for x in animais_input.split(',') if x.strip().isdigit()]
        except:
            pass
    
    if st.session_state.animais_selecionados:
        animais = list(set(animais + st.session_state.animais_selecionados))
    
    # Gerar milhares
    if p_milhar and animais:
        for animal in animais:
            dezenas = DEZENAS.get(animal, [])
            for dezena in dezenas:
                for p1 in p_milhar:
                    for p2 in p_milhar:
                        milhar = f"{p1}{p2}{dezena}"
                        if milhar not in milhares_geradas:
                            milhares_geradas.append(milhar)
    
    # Gerar centenas
    if p_centena and animais:
        for animal in animais:
            dezenas = DEZENAS.get(animal, [])
            for dezena in dezenas:
                for p in p_centena:
                    centena = f"{p}{dezena}"
                    if centena not in centenas_geradas:
                        centenas_geradas.append(centena)
    
    # Exibir resultados
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="results-box">
            <div class="results-header">🎰 Milhares Geradas ({len(milhares_geradas)})</div>
        </div>
        """, unsafe_allow_html=True)
        
        if milhares_geradas:
            # Mostrar em grid
            cols_per_row = 5
            for i in range(0, len(milhares_geradas), cols_per_row):
                row = milhares_geradas[i:i+cols_per_row]
                cols = st.columns(cols_per_row)
                for j, milhar in enumerate(row):
                    with cols[j]:
                        st.markdown(f"""
                        <div style="background: #e8f5e9; padding: 10px; border-radius: 8px;
                                    text-align: center; font-weight: bold; color: #2e7d32;
                                    margin: 2px; font-size: 1.1rem;">
                            {milhar}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Preencha os campos para gerar milhares")
    
    with col2:
        st.markdown(f"""
        <div class="results-box">
            <div class="results-header">💯 Centenas Geradas ({len(centenas_geradas)})</div>
        </div>
        """, unsafe_allow_html=True)
        
        if centenas_geradas:
            cols_per_row = 5
            for i in range(0, len(centenas_geradas), cols_per_row):
                row = centenas_geradas[i:i+cols_per_row]
                cols = st.columns(cols_per_row)
                for j, centena in enumerate(row):
                    with cols[j]:
                        st.markdown(f"""
                        <div style="background: #e3f2fd; padding: 10px; border-radius: 8px;
                                    text-align: center; font-weight: bold; color: #1565c0;
                                    margin: 2px; font-size: 1.1rem;">
                            {centena}
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Preencha os campos para gerar centenas")

# Exemplo de uso
st.markdown("""
<div class="example-box">
    <strong>💡 Exemplo de uso:</strong><br><br>
    <strong>Pedras de Milhar:</strong> 1, 2, 3 (dígitos iniciais da milhar)<br>
    <strong>Pedras de Centena:</strong> 4, 5, 6 (dígitos iniciais da centena)<br>
    <strong>Animais:</strong> 1 (Avestruz), 5 (Cachorro), 10 (Coelho)<br><br>
    O sistema gera todas as combinações possíveis usando as dezenas dos animais selecionados
    combinadas com as pedras informadas.
</div>
""", unsafe_allow_html=True)

st.caption("⚠️ Os números gerados são combinações matemáticas. Use com responsabilidade.")
