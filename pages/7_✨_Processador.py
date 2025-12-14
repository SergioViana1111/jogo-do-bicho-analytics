"""
Processador de Resultados - Cole e processe resultados automaticamente
Sistema adaptado para o novo escopo com ciclo de 5 dias
"""
import streamlit as st
import pandas as pd
import re
from datetime import datetime, date

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
    
    .info-alert {
        background: rgba(33, 150, 243, 0.1);
        border: 1px solid #2196F3;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("✨ Processador de Resultados")

from modules.data_loader import GRUPOS_ANIMAIS, DIA_CORES, get_day_number, save_data_to_database, load_data_from_database

# Inverter mapeamento para buscar grupo pelo nome
ANIMAIS_GRUPOS = {v.upper(): k for k, v in GRUPOS_ANIMAIS.items()}

st.markdown("""
<div class="processor-box">
    <div class="processor-title">📝 PROCESSADOR AUTOMÁTICO DE RESULTADOS</div>
    <p>Cole aqui os resultados para processar automaticamente.</p>
    <p><strong>Formato esperado:</strong> "1: 3.640 G.10 COELHO" ou "3640 10 COELHO"</p>
</div>
""", unsafe_allow_html=True)

# Layout principal
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Informações do Resultado")
    
    # Data do resultado (usa data real, não seleção manual de dia)
    data_resultado = st.date_input(
        "📅 Data do Resultado:",
        value=date.today(),
        help="Selecione a data real do resultado. O sistema calculará automaticamente o número do dia (1-5)."
    )
    
    # Seleção de loteria (OBRIGATÓRIO - nunca misturar loterias)
    loterias = ["RJ", "Nacional", "Look GO", "Federal", "Capital"]
    loteria_selecionada = st.selectbox(
        "🎰 Loteria:",
        loterias,
        help="Cada loteria é analisada separadamente. Nunca misturar dados entre loterias."
    )
    
    # Seleção de horário
    horarios_padrao = ["09:00", "11:00", "14:00", "16:00", "18:00", "21:00"]
    horario_selecionado = st.selectbox("⏰ Horário:", horarios_padrao)
    
    # Mostrar informação sobre o dia calculado
    if 'dados' in st.session_state and st.session_state.dados is not None:
        dia_num = get_day_number(st.session_state.dados, loteria_selecionada, data_resultado)
        if dia_num > 0:
            cor_info = DIA_CORES[dia_num]
            st.markdown(f"""
            <div class="info-alert">
                <strong>{cor_info['emoji']} Esta data será o DIA {dia_num}</strong><br>
                <span style="color: {cor_info['cor']};">■</span> {cor_info['nome']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📊 Esta será uma nova data no sistema.")

with col2:
    st.subheader("📝 Cole os Resultados")
    
    # Área de texto para colar resultados
    resultados_texto = st.text_area(
        "Resultados (uma linha por resultado):",
        height=200,
        placeholder="""Exemplo:
1: 3.640 G.10 COELHO
2: 9.140 G.10 ÁGUIA
3: 4.476 G.19 PAVÃO
4: 3.551 G.13 GALO
5: 3.152 G.13 GALO"""
    )

# Botões de ação
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    processar = st.button("✨ PROCESSAR E PREENCHER", type="primary", use_container_width=True)

with col_btn2:
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
            
            resultados_processados.append({
                'data': data_resultado,
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
            
            # Salvar no banco de dados SQLite (persistência)
            inseridos, duplicados = save_data_to_database(df_add)
            
            # Recarregar dados do banco para session_state
            st.session_state.dados = load_data_from_database()
            
            if inseridos > 0:
                st.success(f"✅ {inseridos} registros salvos no banco de dados! Total: {len(st.session_state.dados)} registros.")
                st.balloons()
            if duplicados > 0:
                st.warning(f"⚠️ {duplicados} registros já existiam e foram ignorados.")
            
            # Dados persistidos - sobrevivem a reloads
        
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
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Registros", len(st.session_state.dados))
    with col2:
        loterias_count = st.session_state.dados['loteria'].nunique()
        st.metric("Loterias", loterias_count)
    with col3:
        if 'data' in st.session_state.dados.columns:
            datas = st.session_state.dados['data'].dt.date.nunique()
            st.metric("Dias", datas)
    
    with st.expander("Ver últimos 20 registros"):
        display_df = st.session_state.dados.head(20).copy()
        if 'data' in display_df.columns:
            display_df['data'] = pd.to_datetime(display_df['data']).dt.strftime('%d/%m/%Y')
        st.dataframe(display_df, use_container_width=True, hide_index=True)

st.caption("⚠️ Use este processador para adicionar resultados rapidamente à base de dados. Cada loteria é processada separadamente.")
