"""
Upload de Base - Carregamento de planilha CSV ou Excel
"""
import streamlit as st

st.set_page_config(page_title="Upload", page_icon="📤", layout="wide")

st.title("📤 Upload de Base de Dados")

st.markdown("""
Faça upload da sua planilha de resultados para análise.

### 📋 Formato Esperado

A planilha deve conter as seguintes colunas:

| Coluna | Descrição | Exemplo |
|--------|-----------|---------|
| `data` | Data do sorteio | 2025-12-01 |
| `loteria` | Nome da loteria | RJ, Nacional, Look GO, Federal, Capital |
| `horario` | Horário do sorteio | 11:00 |
| `grupo` | Número do grupo (01-25) | 7 |
| `centena` | Centena sorteada (000-999) | 345 |
| `milhar` | Milhar sorteada (0000-9999) | 7345 |
""")

st.divider()

from modules.data_loader import load_file, LOTERIAS

# Área de upload
st.subheader("📁 Selecione o Arquivo")

uploaded_file = st.file_uploader(
    "Arraste ou clique para selecionar",
    type=['csv', 'xlsx', 'xls'],
    help="Formatos aceitos: CSV, Excel (.xlsx, .xls)"
)

if uploaded_file is not None:
    with st.spinner("🔄 Processando arquivo..."):
        df, message = load_file(uploaded_file)
    
    if df is not None:
        # Sucesso
        st.success(message)
        
        # Armazenar no session_state
        st.session_state.dados = df
        
        st.divider()
        
        # Preview dos dados
        st.subheader("📊 Preview dos Dados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Registros", f"{len(df):,}")
        
        with col2:
            if len(df) > 0:
                periodo = f"{df['data'].min().strftime('%d/%m/%Y')} - {df['data'].max().strftime('%d/%m/%Y')}"
            else:
                periodo = "N/A"
            st.metric("Período", periodo)
        
        with col3:
            st.metric("Loterias", len(df['loteria'].unique()))
        
        st.divider()
        
        # Distribuição por loteria
        st.markdown("#### 🎰 Distribuição por Loteria")
        
        import plotly.express as px
        
        dist = df['loteria'].value_counts().reset_index()
        dist.columns = ['loteria', 'resultados']
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            for _, row in dist.iterrows():
                st.markdown(f"**{row['loteria']}**: {row['resultados']:,} resultados")
        
        with col2:
            fig = px.pie(
                dist,
                values='resultados',
                names='loteria',
                color_discrete_sequence=['#00C853', '#1E88E5', '#FF9800', '#E91E63', '#9C27B0']
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#fff'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Amostra dos dados
        st.markdown("#### 📋 Amostra dos Dados (últimos 20 registros)")
        
        display_df = df.head(20).copy()
        display_df['data'] = display_df['data'].dt.strftime('%d/%m/%Y')
        display_df['grupo'] = display_df['grupo'].apply(lambda x: f"{x:02d}")
        display_df['centena'] = display_df['centena'].apply(lambda x: f"{x:03d}")
        display_df['milhar'] = display_df['milhar'].apply(lambda x: f"{x:04d}")
        
        st.dataframe(
            display_df[['data', 'loteria', 'horario', 'grupo', 'animal', 'centena', 'milhar']].rename(columns={
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
        
        st.success("✅ Dados carregados! Navegue pelas outras páginas para ver as análises.")
        
    else:
        # Erro
        st.error(message)
        
        st.markdown("""
        ### 🔧 Verifique:
        
        1. O arquivo está no formato CSV ou Excel (.xlsx)?
        2. As colunas estão com os nomes corretos?
        3. Os dados estão preenchidos corretamente?
        
        **Colunas obrigatórias:** `data`, `loteria`, `horario`, `grupo`, `centena`, `milhar`
        """)

else:
    # Mostrar status atual
    if 'dados' in st.session_state and st.session_state.dados is not None:
        st.info(f"📊 Base atual: **{len(st.session_state.dados):,}** registros carregados")
        
        if st.button("🗑️ Limpar base atual"):
            st.session_state.dados = None
            st.rerun()
    else:
        st.warning("⚠️ Nenhuma base carregada ainda.")

st.divider()

# Informações adicionais
with st.expander("ℹ️ Sobre o carregamento de dados"):
    st.markdown("""
    ### Como preparar sua planilha
    
    1. **Formato do arquivo**: CSV ou Excel (.xlsx)
    
    2. **Colunas obrigatórias**:
       - `data`: Data no formato YYYY-MM-DD (ex: 2025-12-01)
       - `loteria`: Nome da loteria (ex: RJ, Nacional, Look GO, Federal, Capital)
       - `horario`: Horário do sorteio (ex: 11:00, 14:00)
       - `grupo`: Número do grupo de 1 a 25
       - `centena`: Centena de 0 a 999
       - `milhar`: Milhar de 0 a 9999
    
    3. **Dicas**:
       - Certifique-se de que não há linhas em branco
       - Verifique se os nomes das colunas estão corretos
       - Dados numéricos não devem conter texto
    
    ### Período de análise
    
    O sistema analisa os **últimos 30 dias** por padrão, mas você pode ajustar 
    o período nos filtros de cada página.
    
    ### Atualização dos dados
    
    Para atualizar a base, basta fazer um novo upload. Os dados anteriores 
    serão substituídos pelos novos.
    """)
