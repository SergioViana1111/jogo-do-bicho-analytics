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

def get_digit_presence_by_day(df, df_full, loteria, tipo='milhar'):
    """Presença binária do primeiro dígito (pedra) por dia, com regra de prêmio.
    Retorna dict {digito: set_de_dias} indicando em quais dias o dígito apareceu.
    Não conta quantidade, apenas se apareceu (binário)."""
    presence = {d: set() for d in range(10)}
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
            presence[first_digit].add(dia_num)
    
    return presence

# Renderizador do grid visual com indicadores coloridos por dia (binário)
def render_pedras_grid(titulo, presence_by_digit):
    """Renderiza grid de pedras com bolinhas coloridas por dia.
    presence_by_digit: dict {digito: set_de_dias} indicando em quais dias cada dígito apareceu."""
    parts = []
    parts.append(f'<div style="font-family: sans-serif; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; background: white;">')
    parts.append(f'<div style="background-color: #111; color: white; text-align: center; padding: 10px; font-weight: bold; font-size: 16px; letter-spacing: 1px;">{titulo}</div>')
    parts.append('<table style="width: 100%; border-collapse: collapse; text-align: center;">')
    parts.append('<tr><th colspan="4" style="background-color: #e8f5e9; color: #2e7d32; font-size: 12px; padding: 8px; border-right: 1px solid #ddd; border-bottom: 1px solid #ddd;">PEDRAS<br>BAIXAS</th><th colspan="3" style="background-color: #eeeeee; color: #424242; font-size: 12px; padding: 8px; border-right: 1px solid #ddd; border-bottom: 1px solid #ddd;">PEDRAS<br>MÉDIAS</th><th colspan="3" style="background-color: #e3f2fd; color: #1565c0; font-size: 12px; padding: 8px; border-bottom: 1px solid #ddd;">PEDRAS<br>ALTAS</th></tr>')
    parts.append('<tr><th colspan="4" style="background-color: #e8f5e9; color: #333; border-right: 1px solid #ddd; padding: 4px; font-size: 11px; border-bottom: 1px solid #ddd;">0, 1, 2, 3</th><th colspan="3" style="background-color: #eeeeee; color: #333; border-right: 1px solid #ddd; padding: 4px; font-size: 11px; border-bottom: 1px solid #ddd;">4, 5, 6</th><th colspan="3" style="background-color: #e3f2fd; color: #333; padding: 4px; font-size: 11px; border-bottom: 1px solid #ddd;">7, 8, 9</th></tr>')
    
    # Uma única linha com todos os dígitos, mostrando bolinhas coloridas por dia
    parts.append('<tr>')
    for digito in range(10):
        if digito <= 3:
            bg, color = "#81c784", "#1b5e20"
        elif digito <= 6:
            bg, color = "#424242", "#ffffff"
        else:
            bg, color = "#64b5f6", "#0d47a1"
            
        border_right = "border-right: 1px solid rgba(255,255,255,0.3);" if digito in [3, 6] else "border-right: 1px solid rgba(255,255,255,0.1);"
        
        # Gerar bolinhas coloridas na ordem DIA 1 → DIA 5
        dias_presente = presence_by_digit.get(digito, set())
        dots = ""
        for dia in range(1, 6):
            if dia in dias_presente:
                cor_dia = DIA_CORES[dia]['cor']
                dots += f'<span style="display: inline-block; width: 10px; height: 10px; background-color: {cor_dia}; border-radius: 50%; border: 1.5px solid white; margin: 1px; box-shadow: 0 1px 2px rgba(0,0,0,0.3);" title="DIA {dia}"></span>'
        
        parts.append(f'<td style="background-color: {bg}; color: {color}; height: 70px; position: relative; padding: 0; {border_right} border-bottom: 1px solid rgba(255,255,255,0.1);"><div style="position: absolute; top: 4px; left: 0; right: 0; text-align: center; display: flex; justify-content: center; align-items: center; flex-wrap: wrap; gap: 1px;">{dots}</div><div style="display: flex; justify-content: center; align-items: center; height: 100%; font-weight: bold; font-size: 18px; padding-top: 10px;">{digito}</div></td>')
    parts.append('</tr>')
        
    parts.append('</table></div>')
    return "".join(parts)

# Calcular presença binária por dia
presence_milhar = get_digit_presence_by_day(df_5dias, df, loteria_sel, 'milhar')
presence_centena = get_digit_presence_by_day(df_5dias, df, loteria_sel, 'centena')

# Mapa de Pedras - Milhar e Centena lado a lado (estilo cliente)
col1, col2 = st.columns(2)

with col1:
    st.markdown(render_pedras_grid("PEDRAS DE MILHAR", presence_milhar), unsafe_allow_html=True)

with col2:
    st.markdown(render_pedras_grid("PEDRAS DE CENTENA", presence_centena), unsafe_allow_html=True)

st.divider()

# Análise por Dia — Presença de pedras
st.subheader("📊 Presença de Pedras por Dia")

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
            
            for digit in range(10):
                presente = dia_num in presence_milhar.get(digit, set())
                status = f"<span style='color:{cor_info['cor']};'>●</span> Presente" if presente else "—"
                st.markdown(f"`{digit}` = {status}", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="background: {cor_info['cor']}; color: {cor_info['text_color']}; 
                        padding: 10px; border-radius: 8px; text-align: center; 
                        font-weight: bold; margin-bottom: 10px;">
                CENTENA - DIA {dia_num}
            </div>
            """, unsafe_allow_html=True)
            
            for digit in range(10):
                presente = dia_num in presence_centena.get(digit, set())
                status = f"<span style='color:{cor_info['cor']};'>●</span> Presente" if presente else "—"
                st.markdown(f"`{digit}` = {status}", unsafe_allow_html=True)

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

st.divider()
st.markdown("""
<div style="background: #1a1a1a; border: 1px solid #333; border-radius: 10px; padding: 15px; margin-top: 10px;">
    <div style="color: #aaa; font-size: 13px; font-weight: bold; margin-bottom: 10px;">🎨 LEGENDA DE CORES — Significado dos indicadores:</div>
    <div style="display: flex; gap: 20px; flex-wrap: wrap; align-items: center;">
        <div style="display: flex; align-items: center; gap: 6px;"><span style="display:inline-block;width:12px;height:12px;background:#FF0000;border-radius:50%;border:1.5px solid white;"></span><span style="color:#ccc; font-size: 13px;">DIA 1 (mais recente)</span></div>
        <div style="display: flex; align-items: center; gap: 6px;"><span style="display:inline-block;width:12px;height:12px;background:#00C853;border-radius:50%;border:1.5px solid white;"></span><span style="color:#ccc; font-size: 13px;">DIA 2</span></div>
        <div style="display: flex; align-items: center; gap: 6px;"><span style="display:inline-block;width:12px;height:12px;background:#2196F3;border-radius:50%;border:1.5px solid white;"></span><span style="color:#ccc; font-size: 13px;">DIA 3</span></div>
        <div style="display: flex; align-items: center; gap: 6px;"><span style="display:inline-block;width:12px;height:12px;background:#FF9800;border-radius:50%;border:1.5px solid white;"></span><span style="color:#ccc; font-size: 13px;">DIA 4</span></div>
        <div style="display: flex; align-items: center; gap: 6px;"><span style="display:inline-block;width:12px;height:12px;background:#333333;border-radius:50%;border:1.5px solid white;"></span><span style="color:#ccc; font-size: 13px;">DIA 5 (mais antigo)</span></div>
    </div>
    <div style="color: #888; font-size: 11px; margin-top: 10px;">Cada bolinha indica que a pedra <strong>apareceu</strong> naquele dia. Não indica quantidade — apenas presença.</div>
</div>
""", unsafe_allow_html=True)

st.caption("⚠️ Análise de pedras (dígitos) nos últimos 5 dias da loteria selecionada. Janela fixa de 5 dias conforme escopo.")
