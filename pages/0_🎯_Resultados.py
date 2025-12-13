"""
Resultados por Loteria - Visualização organizada por loteria
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Resultados", page_icon="🎯", layout="wide")

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
    
    .resultado-card {
        background: white;
        border: 2px solid #00C853;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    .resultado-data {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    
    .resultado-numeros {
        display: flex;
        gap: 15px;
        flex-wrap: wrap;
    }
    
    .numero-box {
        background: #f0f0f0;
        padding: 10px 15px;
        border-radius: 8px;
        text-align: center;
    }
    
    .numero-label {
        font-size: 0.7rem;
        color: #888;
        text-transform: uppercase;
    }
    
    .numero-valor {
        font-size: 1.3rem;
        font-weight: bold;
        color: #00C853;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Resultados por Loteria")

if 'dados' not in st.session_state or st.session_state.dados is None:
    st.warning("⚠️ Nenhuma base de dados carregada. Acesse a página **📤 Upload** primeiro.")
    st.stop()

from modules.data_loader import GRUPOS_ANIMAIS, filter_last_n_days

df = st.session_state.dados

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

loterias = df['loteria'].unique().tolist()
loteria_selecionada = st.sidebar.selectbox("Selecione a Loteria", options=loterias)

dias = st.sidebar.slider("Período (dias)", min_value=1, max_value=30, value=7)

# Filtrar dados
df_filtered = filter_last_n_days(df, dias)
df_loteria = df_filtered[df_filtered['loteria'] == loteria_selecionada].copy()
df_loteria = df_loteria.sort_values(['data', 'horario'], ascending=[False, True])

# Header da loteria
st.markdown(f'<div class="loteria-header">🎰 {loteria_selecionada}</div>', unsafe_allow_html=True)

# Métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total Resultados", len(df_loteria))

with col2:
    if len(df_loteria) > 0:
        grupo_top = df_loteria['grupo'].value_counts().index[0]
        st.metric("🥇 Grupo Top", f"{grupo_top:02d} - {GRUPOS_ANIMAIS.get(grupo_top, '')}")
    else:
        st.metric("🥇 Grupo Top", "N/A")

with col3:
    if len(df_loteria) > 0:
        datas_unicas = df_loteria['data'].dt.date.nunique()
        st.metric("📅 Dias", datas_unicas)
    else:
        st.metric("📅 Dias", 0)

with col4:
    if len(df_loteria) > 0:
        horarios = df_loteria['horario'].nunique()
        st.metric("⏰ Horários", horarios)
    else:
        st.metric("⏰ Horários", 0)

st.divider()

# Resultados por data
datas = df_loteria['data'].dt.date.unique()

for data in datas:
    df_dia = df_loteria[df_loteria['data'].dt.date == data]
    
    data_formatada = data.strftime('%d/%m/%Y')
    st.markdown(f"### 📅 {data_formatada}")
    
    # Grid de resultados do dia
    for _, row in df_dia.iterrows():
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
            <div style="background: #e8f5e9; padding: 10px; border-radius: 8px; text-align: center;">
                <div style="font-size: 0.7rem; color: #888;">GRUPO</div>
                <div style="font-size: 1.2rem; font-weight: bold; color: #00C853;">{row['grupo']:02d}</div>
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
    display_df = df_loteria.copy()
    display_df['data'] = pd.to_datetime(display_df['data']).dt.strftime('%d/%m/%Y')
    display_df['grupo'] = display_df['grupo'].apply(lambda x: f"{x:02d}")
    display_df['centena'] = display_df['centena'].apply(lambda x: f"{x:03d}")
    display_df['milhar'] = display_df['milhar'].apply(lambda x: f"{x:04d}")
    
    st.dataframe(
        display_df[['data', 'horario', 'grupo', 'animal', 'centena', 'milhar']].rename(columns={
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

st.caption("⚠️ Resultados organizados por loteria para análise.")
