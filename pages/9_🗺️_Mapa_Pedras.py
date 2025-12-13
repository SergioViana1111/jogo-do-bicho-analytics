"""
Mapa de Pedras - Visualização de pedras baixas, médias e altas
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mapa de Pedras", page_icon="🗺️", layout="wide")

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
    
    .pedra-grid {
        display: grid;
        grid-template-columns: repeat(10, 1fr);
        gap: 3px;
        padding: 10px;
        background: #1a1a1a;
    }
    
    .pedra-cell {
        padding: 12px 8px;
        text-align: center;
        font-weight: bold;
        border-radius: 5px;
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
    
    .categoria-label {
        color: #00C853;
        font-size: 0.9rem;
        padding: 5px 10px;
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
    
    .resumo-item {
        color: #aaa;
        padding: 5px 0;
    }
    
    .resumo-destaque {
        color: #00C853;
        font-weight: bold;
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
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse a página **📤 Upload** primeiro.")
    st.stop()

from modules.data_loader import filter_last_n_days, filter_by_loteria, get_unique_loterias

df = st.session_state.dados

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")
dias = st.sidebar.slider("Período (dias)", min_value=1, max_value=30, value=5)

loterias = get_unique_loterias(df)
loteria_sel = st.sidebar.selectbox("Loteria", options=["Todas"] + loterias)

# Filtrar dados
df_filtered = filter_last_n_days(df, dias)
if loteria_sel != "Todas":
    df_filtered = filter_by_loteria(df_filtered, [loteria_sel])

def get_digit_matrix(df, tipo='milhar'):
    """Cria matriz de frequência de dígitos por posição"""
    col = 'milhar' if tipo == 'milhar' else 'centena'
    num_digits = 4 if tipo == 'milhar' else 3
    
    # Matriz: linhas = registros, colunas = posição do dígito
    matrix = {pos: {d: 0 for d in range(10)} for pos in range(num_digits)}
    
    for val in df[col]:
        val_str = str(val).zfill(num_digits)
        for pos, digit in enumerate(val_str):
            matrix[pos][int(digit)] += 1
    
    return matrix

def get_total_freq(df, tipo='milhar'):
    """Frequência total de cada dígito"""
    freq = {d: 0 for d in range(10)}
    col = 'milhar' if tipo == 'milhar' else 'centena'
    
    for val in df[col]:
        for digit in str(val):
            if digit.isdigit():
                freq[int(digit)] += 1
    
    return freq

# Mapa de Pedras - Milhar e Centena lado a lado
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="pedra-box">
        <div class="pedra-header">PEDRAS DE MILHAR</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Labels das categorias
    cat_col1, cat_col2, cat_col3 = st.columns(3)
    with cat_col1:
        st.markdown("**🔵 PEDRAS BAIXAS**")
        st.caption("0, 1, 2, 3")
    with cat_col2:
        st.markdown("**🟢 PEDRAS MÉDIAS**")
        st.caption("4, 5, 6")
    with cat_col3:
        st.markdown("**🟡 PEDRAS ALTAS**")
        st.caption("7, 8, 9")
    
    # Grid de frequências
    freq_milhar = get_total_freq(df_filtered, 'milhar')
    max_freq = max(freq_milhar.values()) if sum(freq_milhar.values()) > 0 else 1
    
    # Mostrar grid visual
    st.markdown("#### Frequência por Dígito")
    
    # 5 linhas (para simular o layout do print)
    for row in range(5):
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
                
                # Intensidade baseada na frequência
                opacity = 0.3 + (freq / max_freq * 0.7) if max_freq > 0 else 0.3
                
                if row == 0:
                    st.markdown(f"""
                    <div style="background: {bg}; color: {color}; padding: 10px; 
                                text-align: center; border-radius: 5px; 
                                font-weight: bold; opacity: {opacity};">
                        {digit}
                    </div>
                    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="pedra-box">
        <div class="pedra-header">PEDRAS DE CENTENA</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Labels das categorias
    cat_col1, cat_col2, cat_col3 = st.columns(3)
    with cat_col1:
        st.markdown("**🔵 PEDRAS BAIXAS**")
        st.caption("0, 1, 2, 3")
    with cat_col2:
        st.markdown("**🟢 PEDRAS MÉDIAS**")
        st.caption("4, 5, 6")
    with cat_col3:
        st.markdown("**🟡 PEDRAS ALTAS**")
        st.caption("7, 8, 9")
    
    freq_centena = get_total_freq(df_filtered, 'centena')
    max_freq_c = max(freq_centena.values()) if sum(freq_centena.values()) > 0 else 1
    
    st.markdown("#### Frequência por Dígito")
    
    for row in range(5):
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
                
                opacity = 0.3 + (freq / max_freq_c * 0.7) if max_freq_c > 0 else 0.3
                
                if row == 0:
                    st.markdown(f"""
                    <div style="background: {bg}; color: {color}; padding: 10px; 
                                text-align: center; border-radius: 5px; 
                                font-weight: bold; opacity: {opacity};">
                        {digit}
                    </div>
                    """, unsafe_allow_html=True)

st.divider()

# Resumo da Análise (APS)
st.subheader("📋 Resumo da Análise (APS)")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="resumo-box">
        <div class="resumo-title">🎰 Linhas (bichos)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Calcular linhas presentes/ausentes
    from modules import statistics as stats
    linhas = stats.get_linhas_grupos(df_filtered)
    
    if len(linhas) > 0:
        linhas_presentes = linhas[linhas['frequencia'] > 0]['linha'].tolist()
        linhas_ausentes = [l for l in [1,2,3,4,5] if l not in linhas_presentes]
        
        st.markdown(f"**Saíram:** {', '.join([f'{l}ª LINHA' for l in linhas_presentes]) if linhas_presentes else '—'}")
        st.markdown(f"**Ausentes:** {', '.join([f'{l}ª LINHA' for l in linhas_ausentes]) if linhas_ausentes else 'Nenhuma'}")
        
        # Por dia (últimos 5)
        st.markdown("**Por dia:**")
        datas = df_filtered['data'].dt.date.unique()[:5]
        cores = ['🔴', '🟠', '🔵', '🟡', '⚫']
        for idx, data in enumerate(datas):
            df_dia = df_filtered[df_filtered['data'].dt.date == data]
            linhas_dia = stats.get_linhas_grupos(df_dia)
            linhas_str = ', '.join([f"{int(l)}ª" for l in linhas_dia[linhas_dia['frequencia'] > 0]['linha'].tolist()]) if len(linhas_dia) > 0 else '—'
            st.markdown(f"{cores[idx % len(cores)]} DIA {idx+1} → {linhas_str}")
    else:
        st.info("Sem dados para análise")

with col2:
    st.markdown("""
    <div class="resumo-box">
        <div class="resumo-title">🏓 Ping-Pong de pedras</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Análise de ping-pong (pedras que aparecem em dias consecutivos)
    st.markdown("**Entre dias consecutivos:**")
    st.markdown("• Milhar: —")
    st.markdown("• Centena: —")
    
    st.markdown("**No mesmo dia (repetições):**")
    st.markdown("• Milhar: —")
    st.markdown("• Centena: —")
    
    st.caption("• Ping-Pong entre dias = apareceu em dias consecutivos")
    st.caption("• Ping-Pong no mesmo dia = repetiu no mesmo dia (2x ou mais)")

st.divider()

# Casas de Pedras
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🎲 Casas de pedras — Milhar")
    
    # Categorizar pedras
    freq_m = get_total_freq(df_filtered, 'milhar')
    baixas = [d for d in [0,1,2,3] if freq_m[d] > 0]
    medias = [d for d in [4,5,6] if freq_m[d] > 0]
    altas = [d for d in [7,8,9] if freq_m[d] > 0]
    
    ausentes_baixas = [d for d in [0,1,2,3] if freq_m[d] == 0]
    ausentes_medias = [d for d in [4,5,6] if freq_m[d] == 0]
    ausentes_altas = [d for d in [7,8,9] if freq_m[d] == 0]
    
    st.markdown(f"**Presentes:** Baixas ({','.join(map(str, baixas))}), Médias ({','.join(map(str, medias))}), Altas ({','.join(map(str, altas))})")
    st.markdown(f"**Ausentes:** Baixas ({','.join(map(str, ausentes_baixas))}), Médias ({','.join(map(str, ausentes_medias))}), Altas ({','.join(map(str, ausentes_altas))})")

with col2:
    st.markdown("### 🎲 Casas de pedras — Centena")
    
    freq_c = get_total_freq(df_filtered, 'centena')
    baixas_c = [d for d in [0,1,2,3] if freq_c[d] > 0]
    medias_c = [d for d in [4,5,6] if freq_c[d] > 0]
    altas_c = [d for d in [7,8,9] if freq_c[d] > 0]
    
    ausentes_baixas_c = [d for d in [0,1,2,3] if freq_c[d] == 0]
    ausentes_medias_c = [d for d in [4,5,6] if freq_c[d] == 0]
    ausentes_altas_c = [d for d in [7,8,9] if freq_c[d] == 0]
    
    st.markdown(f"**Presentes:** Baixas ({','.join(map(str, baixas_c))}), Médias ({','.join(map(str, medias_c))}), Altas ({','.join(map(str, altas_c))})")
    st.markdown(f"**Ausentes:** Baixas ({','.join(map(str, ausentes_baixas_c))}), Médias ({','.join(map(str, ausentes_medias_c))}), Altas ({','.join(map(str, ausentes_altas_c))})")

st.caption("⚠️ Conceitos APS usados: Linhas (5 blocos de 5 bichos), Casas de pedras (baixas/médias/altas), Ping-Pong (ocorrências consecutivas por dígito).")
