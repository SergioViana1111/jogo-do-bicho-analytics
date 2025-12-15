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
    loterias = ["Nacional", "Look GO", "Capital", "RJ", "Federal"]
    loteria_selecionada = st.selectbox(
        "🎰 Loteria:",
        loterias,
        key="proc_loteria",
        help="Cada loteria é analisada separadamente. Nunca misturar dados entre loterias."
    )
    
    # Horários específicos por loteria (conforme documentação)
    HORARIOS_POR_LOTERIA = {
        "Nacional": ["02:00", "08:00", "10:00", "12:00", "15:00", "17:00", "21:00", "23:00"],
        "Look GO": ["07:00", "09:00", "11:00", "14:00", "16:00", "18:00", "21:00", "23:00"],
        "Capital": ["10:00", "11:00", "13:00", "14:00", "16:00", "18:00", "20:00", "22:00"],
        "RJ": ["09:00", "11:00", "14:00", "16:00", "18:00", "21:00"],  # Horários RJ
        "Federal": ["19:00"],  # Federal tem horário único
    }
    
    # Seleção de horário (baseado na loteria selecionada)
    horarios_loteria = HORARIOS_POR_LOTERIA.get(loteria_selecionada, ["11:00", "14:00", "18:00", "21:00"])
    horario_selecionado = st.selectbox(
        "⏰ Horário:", 
        horarios_loteria,
        key="proc_horario"
    )
    
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
            # Formatos suportados: G.10, G10, grupo 10, ou apenas número após o milhar
            grupo = None
            grupo_match = re.search(r'G\.?\s*(\d{1,2})\b|grupo\s*(\d{1,2})', linha_limpa, re.IGNORECASE)
            if grupo_match:
                grupo = int(grupo_match.group(1) or grupo_match.group(2))
            else:
                # Tentar formato "milhar grupo animal" (ex: "3640 10 COELHO")
                # Procurar número após o milhar que seja 1-25
                parts = linha_limpa.split()
                for part in parts[1:]:  # Pular o primeiro (milhar)
                    if part.isdigit():
                        num = int(part)
                        if 1 <= num <= 25:
                            grupo = num
                            break
            
            if grupo is None:
                # Tentar deduzir do nome do animal
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
        
        # Criar DataFrame e SALVAR no session_state
        df_novos = pd.DataFrame(resultados_processados)
        st.session_state.df_processados = df_novos
        
        # Preview - Formatar números com zeros à esquerda para visualização
        st.markdown("### 📋 Resultados Processados")
        
        # Criar cópia para exibição com formatação
        df_display = df_novos.copy()
        df_display['grupo'] = df_display['grupo'].apply(lambda x: f"{x:02d}")
        df_display['centena'] = df_display['centena'].apply(lambda x: f"{x:03d}")
        df_display['milhar'] = df_display['milhar'].apply(lambda x: f"{x:04d}")
        
        st.dataframe(
            df_display[['data', 'loteria', 'horario', 'grupo', 'animal', 'centena', 'milhar']].rename(columns={
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
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Mostrar erros
    if erros:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        for erro in erros:
            st.error(erro)
        st.markdown('</div>', unsafe_allow_html=True)

# Mostrar dados processados salvos no session_state e botão de adicionar
if 'df_processados' in st.session_state and st.session_state.df_processados is not None and len(st.session_state.df_processados) > 0:
    df_novos = st.session_state.df_processados
    
    st.markdown("---")
    st.markdown("### 📦 Dados Prontos para Adicionar")
    
    # Mostrar resumo
    st.info(f"📊 **{len(df_novos)} registros** prontos para adicionar | Data: {df_novos['data'].iloc[0]} | Loteria: {df_novos['loteria'].iloc[0]} | Horário: {df_novos['horario'].iloc[0]}")
    
    # Botão para adicionar à base
    col_add, col_cancel = st.columns(2)
    
    with col_add:
        if st.button("➕ ADICIONAR À BASE DE DADOS", type="primary", use_container_width=True):
            try:
                # Preparar dados para adicionar
                df_add = df_novos[['data', 'loteria', 'horario', 'grupo', 'centena', 'milhar', 'animal']].copy()
                df_add['data'] = pd.to_datetime(df_add['data'])
                
                # Salvar no banco de dados
                inseridos, duplicados = save_data_to_database(df_add)
                
                # Recarregar dados do banco para session_state
                st.session_state.dados = load_data_from_database()
                st.session_state.dados_loaded = True
                
                # Limpar dados processados
                st.session_state.df_processados = None
                
                if inseridos > 0:
                    st.success(f"✅ {inseridos} registros salvos! Total: {len(st.session_state.dados)} registros.")
                    st.balloons()
                if duplicados > 0:
                    st.info(f"ℹ️ {duplicados} registros já existiam.")
                
            except Exception as e:
                st.error(f"❌ Erro ao salvar: {str(e)}")
    
    with col_cancel:
        if st.button("🗑️ CANCELAR", use_container_width=True):
            st.session_state.df_processados = None
            st.rerun()

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
    
    # Seção de gerenciamento de registros
    st.divider()
    st.subheader("🗑️ Gerenciar Registros")
    
    with st.expander("⚠️ Excluir Registros por Filtro"):
        st.warning("**Atenção:** Esta ação é irreversível! Os registros serão permanentemente excluídos.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            del_loteria = st.selectbox("Loteria:", loterias, key="del_loteria")
        with col2:
            del_data = st.date_input("Data:", key="del_data")
        with col3:
            del_horarios = HORARIOS_POR_LOTERIA.get(del_loteria, ["11:00", "14:00", "18:00", "21:00"])
            del_horario = st.selectbox("Horário:", del_horarios, key="del_horario")
        
        # Mostrar quantos registros serão afetados
        del_data_str = del_data.strftime('%Y-%m-%d')
        registros_filtro = st.session_state.dados[
            (st.session_state.dados['loteria'] == del_loteria) &
            (st.session_state.dados['data'].dt.strftime('%Y-%m-%d') == del_data_str) &
            (st.session_state.dados['horario'] == del_horario)
        ]
        
        if len(registros_filtro) > 0:
            st.info(f"📊 **{len(registros_filtro)} registro(s)** encontrado(s) com este filtro:")
            preview_df = registros_filtro.copy()
            preview_df['data'] = pd.to_datetime(preview_df['data']).dt.strftime('%d/%m/%Y')
            preview_df['milhar'] = preview_df['milhar'].apply(lambda x: f"{x:04d}")
            preview_df['grupo'] = preview_df['grupo'].apply(lambda x: f"{x:02d}")
            st.dataframe(preview_df[['data', 'loteria', 'horario', 'grupo', 'animal', 'milhar']], 
                        use_container_width=True, hide_index=True)
            
            if st.button("🗑️ EXCLUIR ESTES REGISTROS", type="secondary", key="btn_excluir"):
                from modules.database import delete_records_by_filter
                deleted = delete_records_by_filter(del_loteria, del_data_str, del_horario)
                if deleted > 0:
                    st.success(f"✅ {deleted} registro(s) excluído(s) com sucesso!")
                    st.session_state.dados = load_data_from_database()
                    st.rerun()
                else:
                    st.error("❌ Erro ao excluir registros. Verifique se a política DELETE está habilitada no Supabase.")
        else:
            st.info("ℹ️ Nenhum registro encontrado com este filtro.")
    
    with st.expander("🔥 Zerar Toda a Base de Dados"):
        st.error("**⚠️ PERIGO:** Esta ação irá deletar TODOS os registros do banco de dados! Esta ação é IRREVERSÍVEL!")
        
        confirmacao = st.text_input("Digite 'CONFIRMAR' para habilitar o botão de exclusão:", key="confirm_delete_all")
        
        if confirmacao == "CONFIRMAR":
            if st.button("🔥 ZERAR TODA A BASE", type="primary", key="btn_zerar"):
                from modules.database import delete_all_records
                deleted = delete_all_records()
                if deleted > 0:
                    st.success(f"✅ {deleted} registro(s) excluído(s)! Base zerada.")
                    st.session_state.dados = load_data_from_database()
                    st.rerun()
                else:
                    st.warning("⚠️ Nenhum registro foi excluído. Pode ser que a base já estivesse vazia ou a política DELETE não está habilitada no Supabase.")
        else:
            st.button("🔥 ZERAR TODA A BASE", type="primary", disabled=True, key="btn_zerar_disabled")

st.caption("⚠️ Use este processador para adicionar resultados rapidamente à base de dados. Cada loteria é processada separadamente.")
