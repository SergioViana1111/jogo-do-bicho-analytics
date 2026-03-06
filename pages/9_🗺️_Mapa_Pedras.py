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

# Renderizador do novo grid visual (Padrão Cliente)
def render_pedras_grid(titulo, freq_by_day):
    html = f'''
    <div style="font-family: sans-serif; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; background: white;">
        <!-- Header -->
        <div style="background-color: #111; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 16px; letter-spacing: 1px;">
            {titulo}
        </div>
        
        <!-- Categorias -->
        <table style="width: 100%; border-collapse: collapse; text-align: center;">
            <tr>
                <th colspan="4" style="background-color: #e8f5e9; color: #2e7d32; font-size: 12px; padding: 8px; border-right: 1px solid #ddd; border-bottom: 1px solid #ddd;">PEDRAS<br>BAIXAS</th>
                <th colspan="3" style="background-color: #eeeeee; color: #424242; font-size: 12px; padding: 8px; border-right: 1px solid #ddd; border-bottom: 1px solid #ddd;">PEDRAS<br>MÉDIAS</th>
                <th colspan="3" style="background-color: #e3f2fd; color: #1565c0; font-size: 12px; padding: 8px; border-bottom: 1px solid #ddd;">PEDRAS<br>ALTAS</th>
            </tr>
            <tr>
                <th colspan="4" style="background-color: #e8f5e9; color: #333; border-right: 1px solid #ddd; padding: 4px; font-size: 11px; border-bottom: 1px solid #ddd;">0, 1, 2, 3</th>
                <th colspan="3" style="background-color: #eeeeee; color: #333; border-right: 1px solid #ddd; padding: 4px; font-size: 11px; border-bottom: 1px solid #ddd;">4, 5, 6</th>
                <th colspan="3" style="background-color: #e3f2fd; color: #333; padding: 4px; font-size: 11px; border-bottom: 1px solid #ddd;">7, 8, 9</th>
            </tr>
    '''
    
    # Render linhas (Dias 1 a 5)
    for dia in range(1, 6):
        html += '<tr>'
        for digito in range(10):
            # Cores de fundo (exatas da imagem)
            if digito <= 3:
                bg = "#81c784" # Verde
                color = "#1b5e20"
            elif digito <= 6:
                bg = "#424242" # Cinza escuro
                color = "#ffffff"
            else:
                bg = "#64b5f6" # Azul
                color = "#0d47a1"
                
            border_right = "border-right: 1px solid rgba(255,255,255,0.3);" if digito in [3, 6] else "border-right: 1px solid rgba(255,255,255,0.1);"
            border_bottom = "border-bottom: 1px solid rgba(255,255,255,0.1);"
            
            pontos = freq_by_day.get(dia, {}).get(digito, 0)
            
            dots_html = ""
            for _ in range(pontos):
                dots_html += '<span style="display: inline-block; width: 10px; height: 10px; background-color: #ef5350; border-radius: 50%; border: 1.5px solid white; margin: 0 1px; box-shadow: 0 1px 2px rgba(0,0,0,0.3);"></span>'

            # Estilo da célula: layout flex pra colocar os pontos no topo e o número no centro
            html += f'''
                <td style="background-color: {bg}; color: {color}; height: 60px; position: relative; padding: 0; {border_right} {border_bottom}">
                    <div style="position: absolute; top: 4px; left: 0; right: 0; text-align: center; height: 12px; display: flex; justify-content: center; align-items: center;">
                        {dots_html}
                    </div>
                    <div style="display: flex; justify-content: center; align-items: center; height: 100%; font-weight: bold; font-size: 16px;">
                        {digito}
                    </div>
                </td>
            '''
        html += '</tr>'
        
    html += '''
        </table>
    </div>
    '''
    return html

# Calcular dados de frequência diária
freq_milhar_by_day = get_digit_freq_by_day(df_5dias, df, loteria_sel, 'milhar')
freq_centena_by_day = get_digit_freq_by_day(df_5dias, df, loteria_sel, 'centena')

# Mapa de Pedras - Milhar e Centena lado a lado (estilo cliente)
col1, col2 = st.columns(2)

with col1:
    st.markdown(render_pedras_grid("PEDRAS DE MILHAR", freq_milhar_by_day), unsafe_allow_html=True)

with col2:
    st.markdown(render_pedras_grid("PEDRAS DE CENTENA", freq_centena_by_day), unsafe_allow_html=True)

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
