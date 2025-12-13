"""
Processador de Resultados - Cole e processe resultados automaticamente
"""
import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(page_title="Processador", page_icon="✨", layout="wide")

# CSS customizado
st.markdown("""
<style>
    .processor-box {
        border: 3px solid #00C853;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .processor-title {
        color: #00C853;
        font-size: 1.3rem;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    .success-box {
        background: rgba(0, 200, 83, 0.1);
        border: 1px solid #00C853;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .error-box {
        background: rgba(244, 67, 54, 0.1);
        border: 1px solid #f44336;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .day-input {
        background: #f8f9fa;
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
    }
    
    .day-label {
        color: #00C853;
        font-weight: bold;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ Processador de Resultados")

from modules.data_loader import GRUPOS_ANIMAIS

# Inverter mapeamento para buscar grupo pelo nome
ANIMAIS_GRUPOS = {v.upper(): k for k, v in GRUPOS_ANIMAIS.items()}

st.markdown("""
<div class="processor-box">
    <div class="processor-title">📝 PROCESSADOR AUTOMÁTICO DE RESULTADOS</div>
    <p>Cole aqui os resultados para processar automaticamente.</p>
    <p><strong>Formato esperado:</strong> "1: 3.640 G.10 COELHO" ou "3640 10 COELHO"</p>
</div>
""", unsafe_allow_html=True)

# Seleção de dia
col1, col2 = st.columns([1, 3])
with col1:
    dia_selecionado = st.radio(
        "Escolha o dia para processar:",
        ["DIA 1 (HOJE)", "DIA 2 (ONTEM)", "DIA 3", "DIA 4", "DIA 5"],
        horizontal=False
    )

with col2:
    # Seleção de loteria para adicionar
    loterias = ["RJ", "Nacional", "Look GO", "Federal", "Capital"]
    loteria_selecionada = st.selectbox("Loteria:", loterias)
    
    horarios_padrao = ["09:00", "11:00", "14:00", "16:00", "18:00", "21:00"]
    horario_selecionado = st.selectbox("Horário:", horarios_padrao)

# Área de texto para colar resultados
resultados_texto = st.text_area(
    "Cole aqui os resultados:",
    height=200,
    placeholder="""Exemplo:
1: 3.640 G.10 COELHO
2: 9.140 G.10 ÁGUIA
3: 4.476 G.19 PAVÃO
4: 3.551 G.13 GALO
5: 3.152 G.13 GALO"""
)

col1, col2 = st.columns(2)

with col1:
    processar = st.button("✨ PROCESSAR E PREENCHER", type="primary", use_container_width=True)

with col2:
    limpar = st.button("🗑️ LIMPAR", use_container_width=True)

st.info("💡 **Dica:** Cole os resultados completos. O sistema identifica automaticamente milhar, centena, grupo e animal!")

# Processar resultados
if processar and resultados_texto:
    linhas = resultados_texto.strip().split('\n')
    resultados_processados = []
    erros = []
    
    for linha in linhas:
        if not linha.strip():
            continue
        
        try:
            # Tentar extrair padrão "1: 3.640 G.10 COELHO"
            # Regex para capturar milhar (com ou sem ponto), grupo e animal
            
            # Limpar a linha
            linha_limpa = linha.strip()
            
            # Remover número de ordem se existir (ex: "1:", "2:")
            linha_limpa = re.sub(r'^\d+[:\.\)]\s*', '', linha_limpa)
            
            # Extrair milhar (número de 4 dígitos, pode ter ponto)
            milhar_match = re.search(r'(\d[\d\.]*\d)', linha_limpa)
            if milhar_match:
                milhar_str = milhar_match.group(1).replace('.', '')
                milhar = int(milhar_str)
            else:
                raise ValueError("Milhar não encontrado")
            
            # Extrair centena (últimos 3 dígitos da milhar)
            centena = milhar % 1000
            
            # Extrair grupo
            grupo_match = re.search(r'G\.?(\d+)|grupo\s*(\d+)', linha_limpa, re.IGNORECASE)
            if grupo_match:
                grupo = int(grupo_match.group(1) or grupo_match.group(2))
            else:
                # Tentar deduzir do animal
                for animal_nome, animal_grupo in ANIMAIS_GRUPOS.items():
                    if animal_nome in linha_limpa.upper():
                        grupo = animal_grupo
                        break
                else:
                    # Tentar deduzir da dezena (últimos 2 dígitos)
                    dezena = milhar % 100
                    grupo = ((dezena - 1) % 25) + 1 if dezena > 0 else 25
            
            animal = GRUPOS_ANIMAIS.get(grupo, 'Desconhecido')
            
            # Determinar data baseado no dia selecionado
            hoje = datetime.now().date()
            if "HOJE" in dia_selecionado or "DIA 1" in dia_selecionado:
                data = hoje
            elif "ONTEM" in dia_selecionado or "DIA 2" in dia_selecionado:
                data = hoje - pd.Timedelta(days=1)
            elif "DIA 3" in dia_selecionado:
                data = hoje - pd.Timedelta(days=2)
            elif "DIA 4" in dia_selecionado:
                data = hoje - pd.Timedelta(days=3)
            elif "DIA 5" in dia_selecionado:
                data = hoje - pd.Timedelta(days=4)
            else:
                data = hoje
            
            resultados_processados.append({
                'data': data,
                'loteria': loteria_selecionada,
                'horario': horario_selecionado,
                'grupo': grupo,
                'centena': centena,
                'milhar': milhar,
                'animal': animal,
                'linha_original': linha
            })
            
        except Exception as e:
            erros.append(f"❌ Erro ao processar: '{linha}' - {str(e)}")
    
    # Mostrar resultados
    if resultados_processados:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.success(f"✅ {len(resultados_processados)} resultados processados com sucesso!")
        
        # Criar DataFrame
        df_novos = pd.DataFrame(resultados_processados)
        
        # Preview
        st.markdown("### 📋 Resultados Processados")
        st.dataframe(
            df_novos[['data', 'loteria', 'horario', 'grupo', 'animal', 'centena', 'milhar']].rename(columns={
                'data': 'Data',
                'loteria': 'Loteria',
                'horario': 'Horário',
                'grupo': 'Grupo',
                'animal': 'Animal',
                'centena': 'Centena',
                'milhar': 'Milhar'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Botão para adicionar à base
        if st.button("➕ ADICIONAR À BASE DE DADOS", type="primary"):
            # Preparar dados para adicionar
            df_add = df_novos[['data', 'loteria', 'horario', 'grupo', 'centena', 'milhar', 'animal']].copy()
            df_add['data'] = pd.to_datetime(df_add['data'])
            
            if 'dados' in st.session_state and st.session_state.dados is not None:
                # Concatenar com dados existentes
                st.session_state.dados = pd.concat([st.session_state.dados, df_add], ignore_index=True)
                st.session_state.dados = st.session_state.dados.sort_values('data', ascending=False)
            else:
                st.session_state.dados = df_add
            
            st.success(f"✅ {len(df_add)} registros adicionados à base! Total: {len(st.session_state.dados)} registros.")
            st.balloons()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Mostrar erros
    if erros:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        for erro in erros:
            st.error(erro)
        st.markdown('</div>', unsafe_allow_html=True)

if limpar:
    st.rerun()

st.divider()

# Mostrar dados existentes
if 'dados' in st.session_state and st.session_state.dados is not None:
    st.subheader("📊 Base de Dados Atual")
    st.metric("Total de Registros", len(st.session_state.dados))
    
    with st.expander("Ver últimos 20 registros"):
        display_df = st.session_state.dados.head(20).copy()
        if 'data' in display_df.columns:
            display_df['data'] = pd.to_datetime(display_df['data']).dt.strftime('%d/%m/%Y')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

st.caption("⚠️ Use este processador para adicionar resultados rapidamente à base de dados.")
