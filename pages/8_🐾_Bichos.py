"""
Tabela dos 25 Bichos - Visualização interativa com pincel colorido
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
        transition: all 0.3s;
        cursor: pointer;
    }
    
    .bicho-card:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
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
    
    .color-picker {
        display: flex;
        gap: 10px;
        margin: 10px 0;
    }
    
    .color-btn {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        cursor: pointer;
        border: 2px solid #333;
    }
    
    .linha-header {
        background: linear-gradient(90deg, #00C853, #00E676);
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🐾 Tabela dos 25 Bichos")

from modules.data_loader import GRUPOS_ANIMAIS

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

# Sidebar com cores
st.sidebar.header("🎨 Pincel de Cores")
cores = {
    'vermelho': '#FF0000',
    'verde': '#00C853',
    'azul': '#2196F3',
    'laranja': '#FF9800',
    'preto': '#333333',
    'nenhuma': 'transparent'
}

cor_selecionada = st.sidebar.radio(
    "Selecione a cor:",
    list(cores.keys()),
    format_func=lambda x: f"🔴 Vermelho" if x == 'vermelho' else f"🟢 Verde" if x == 'verde' else f"🔵 Azul" if x == 'azul' else f"🟠 Laranja" if x == 'laranja' else f"⚫ Preto" if x == 'preto' else "⬜ Limpar"
)

# Inicializar estado de cores dos bichos
if 'bicho_colors' not in st.session_state:
    st.session_state.bicho_colors = {i: 'transparent' for i in range(1, 26)}

# Botões de controle
col1, col2 = st.columns(2)
with col1:
    if st.button("🗑️ LIMPAR TODAS AS CORES", use_container_width=True):
        st.session_state.bicho_colors = {i: 'transparent' for i in range(1, 26)}
        st.rerun()

with col2:
    if st.button("🔄 ATUALIZAR", use_container_width=True):
        st.rerun()

st.divider()

# Exibir tabela de bichos
st.subheader("📋 Clique nos bichos para marcar")

# Grid 5x5
for linha in range(5):
    cols = st.columns(5)
    for col_idx in range(5):
        grupo = linha * 5 + col_idx + 1
        animal = GRUPOS_ANIMAIS.get(grupo, '')
        emoji = EMOJIS.get(grupo, '🐾')
        dezenas = ', '.join(DEZENAS.get(grupo, []))
        cor_atual = st.session_state.bicho_colors.get(grupo, 'transparent')
        
        with cols[col_idx]:
            # Determinar cor do fundo
            bg_color = cor_atual if cor_atual != 'transparent' else '#f8f9fa'
            text_color = 'white' if cor_atual not in ['transparent', '#FF9800'] else '#333'
            
            # Card do bicho
            st.markdown(f"""
            <div style="background: {bg_color}; border: 2px solid #ddd; border-radius: 10px;
                        padding: 15px; text-align: center; margin: 5px; min-height: 120px;">
                <div style="font-size: 2rem;">{emoji}</div>
                <div style="font-size: 1.3rem; font-weight: bold; color: {text_color};">{grupo:02d}</div>
                <div style="font-size: 0.9rem; color: {text_color if text_color == 'white' else '#666'};">{animal}</div>
                <div style="font-size: 0.7rem; color: {text_color if text_color == 'white' else '#888'};">{dezenas}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para marcar
            if st.button(f"Marcar {grupo}", key=f"btn_{grupo}", use_container_width=True):
                st.session_state.bicho_colors[grupo] = cores[cor_selecionada]
                st.rerun()

st.divider()

# Estatísticas se houver dados
if 'dados' in st.session_state and st.session_state.dados is not None:
    st.subheader("📊 Frequência por Grupo (Últimos 30 dias)")
    
    from modules.data_loader import filter_last_n_days
    from modules import statistics as stats
    
    df_30d = filter_last_n_days(st.session_state.dados, 30)
    grupos_freq = stats.get_grupo_frequency(df_30d, top_n=25)
    
    if len(grupos_freq) > 0:
        # Criar grid de contagem
        for linha in range(5):
            cols = st.columns(5)
            for col_idx in range(5):
                grupo = linha * 5 + col_idx + 1
                animal = GRUPOS_ANIMAIS.get(grupo, '')
                
                # Buscar frequência
                freq_row = grupos_freq[grupos_freq['grupo'] == grupo]
                freq = freq_row['frequencia'].values[0] if len(freq_row) > 0 else 0
                
                with cols[col_idx]:
                    st.metric(f"{grupo:02d} {animal}", freq)

st.caption("⚠️ Clique nos bichos para marcá-los com a cor selecionada no pincel.")
