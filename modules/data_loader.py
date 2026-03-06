"""
Módulo de carregamento e validação de dados do Jogo do Bicho
"""
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def load_data_from_database():
    """
    Carrega dados do banco de dados SQLite.
    Esta é a fonte primária de dados para persistência.
    """
    # Import lazy para evitar import circular
    from modules.database import load_all_data
    return load_all_data()

def save_data_to_database(df: pd.DataFrame) -> tuple:
    """
    Salva dados no banco de dados SQLite.
    Retorna (inseridos, duplicados, erros)
    """
    # Import lazy para evitar import circular
    from modules.database import insert_resultados
    return insert_resultados(df)

# Colunas obrigatórias da planilha
REQUIRED_COLUMNS = ['data', 'loteria', 'horario', 'grupo', 'centena', 'milhar']

# Loterias suportadas
LOTERIAS = ['RJ', 'Nacional', 'Look GO', 'Federal', 'Capital']

# Mapeamento de grupos para animais
GRUPOS_ANIMAIS = {
    1: 'Avestruz', 2: 'Águia', 3: 'Burro', 4: 'Borboleta', 5: 'Cachorro',
    6: 'Cabra', 7: 'Carneiro', 8: 'Camelo', 9: 'Cobra', 10: 'Coelho',
    11: 'Cavalo', 12: 'Elefante', 13: 'Galo', 14: 'Gato', 15: 'Jacaré',
    16: 'Leão', 17: 'Macaco', 18: 'Porco', 19: 'Pavão', 20: 'Peru',
    21: 'Touro', 22: 'Tigre', 23: 'Urso', 24: 'Veado', 25: 'Vaca'
}

# Cores fixas por dia - REGRA CRÍTICA E IMUTÁVEL
# A cor indica EXCLUSIVAMENTE o dia, não representa frequência ou probabilidade
DIA_CORES = {
    1: {'cor': '#FF0000', 'nome': 'Vermelho', 'emoji': '🔴', 'text_color': '#FFFFFF'},  # Dia 1 (mais recente)
    2: {'cor': '#00C853', 'nome': 'Verde', 'emoji': '🟢', 'text_color': '#FFFFFF'},     # Dia 2
    3: {'cor': '#2196F3', 'nome': 'Azul', 'emoji': '🔵', 'text_color': '#FFFFFF'},      # Dia 3
    4: {'cor': '#FF9800', 'nome': 'Laranja', 'emoji': '🟠', 'text_color': '#000000'},   # Dia 4
    5: {'cor': '#333333', 'nome': 'Preto', 'emoji': '⚫', 'text_color': '#FFFFFF'},     # Dia 5 (mais antigo ativo)
}

def get_last_5_unique_dates(df: pd.DataFrame, loteria: str) -> list:
    """
    Retorna as últimas 5 datas únicas para uma loteria específica.
    As datas são ordenadas do mais recente ao mais antigo.
    
    Returns:
        Lista de dates (não datetime) das últimas 5 datas únicas
    """
    if df is None or len(df) == 0:
        return []
    
    df_lot = df[df['loteria'] == loteria].copy()
    if len(df_lot) == 0:
        return []
    
    # Garantir que temos a coluna de data como datetime
    df_lot['data'] = pd.to_datetime(df_lot['data'])
    
    # Pegar datas únicas ordenadas (mais recente primeiro)
    # Usar tolist() e sorted() para garantir ordenação correta
    datas_unicas = sorted(set(df_lot['data'].dt.date.tolist()), reverse=True)
    
    return datas_unicas[:5]

def get_day_number(df: pd.DataFrame, loteria: str, data) -> int:
    """
    Retorna o número do dia (1-5) para uma data específica dentro do ciclo de 5 dias.
    
    Dia 1 = dia mais recente
    Dia 5 = dia mais antigo ativo
    
    Returns:
        Número do dia (1-5) ou 0 se a data não está no ciclo ativo
    """
    datas_5dias = get_last_5_unique_dates(df, loteria)
    
    if not datas_5dias:
        return 0
    
    # Converter para date se for datetime
    if hasattr(data, 'date'):
        data = data.date()
    
    try:
        return datas_5dias.index(data) + 1
    except ValueError:
        return 0  # Data não está no ciclo de 5 dias

def filter_5_day_cycle(df: pd.DataFrame, loteria: str) -> pd.DataFrame:
    """
    Filtra dados apenas dos últimos 5 dias para uma loteria específica.
    Esta é a janela de análise principal do sistema.
    NÃO aplica regra de prêmio - retorna TODOS os registros dos 5 dias.
    
    Args:
        df: DataFrame com todos os dados
        loteria: Nome da loteria para filtrar
    
    Returns:
        DataFrame filtrado com apenas os dados dos últimos 5 dias da loteria
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    datas_5dias = get_last_5_unique_dates(df, loteria)
    
    if not datas_5dias:
        return pd.DataFrame()
    
    df_lot = df[df['loteria'] == loteria].copy()
    df_lot['data'] = pd.to_datetime(df_lot['data'])
    
    # Filtrar apenas datas dentro do ciclo de 5 dias
    df_filtered = df_lot[df_lot['data'].dt.date.isin(datas_5dias)]
    
    return df_filtered.sort_values('data', ascending=False)

def filter_by_day_prize_rules(df: pd.DataFrame, loteria: str) -> pd.DataFrame:
    """
    Filtra dados dos últimos 5 dias aplicando a REGRA DE PRÊMIO:
    - Dias 1 e 2: TODOS os prêmios (puxada de todos os bichos)
    - Dias 3, 4 e 5: SOMENTE 1° prêmio
    
    Dados legados (premio=0) são incluídos em todos os dias para compatibilidade.
    
    Args:
        df: DataFrame com todos os dados
        loteria: Nome da loteria para filtrar
    
    Returns:
        DataFrame filtrado com a regra de prêmio aplicada
    """
    df_5dias = filter_5_day_cycle(df, loteria)
    
    if len(df_5dias) == 0:
        return pd.DataFrame()
    
    datas_5dias = get_last_5_unique_dates(df, loteria)
    
    # Garantir coluna premio existe
    if 'premio' not in df_5dias.columns:
        df_5dias['premio'] = 0
    
    resultado_parts = []
    
    for idx, data in enumerate(datas_5dias):
        dia_num = idx + 1
        df_dia = df_5dias[df_5dias['data'].dt.date == data]
        
        if dia_num <= 2:
            # Dias 1 e 2: todos os prêmios
            resultado_parts.append(df_dia)
        else:
            # Dias 3, 4 e 5: somente 1° prêmio (premio==1) ou legado (premio==0)
            df_filtrado = df_dia[(df_dia['premio'] == 1) | (df_dia['premio'] == 0)]
            resultado_parts.append(df_filtrado)
    
    if resultado_parts:
        return pd.concat(resultado_parts, ignore_index=True).sort_values('data', ascending=False)
    
    return pd.DataFrame()

def filter_day_data_by_prize(df_dia: pd.DataFrame, dia_num: int) -> pd.DataFrame:
    """
    Filtra dados de um dia específico aplicando a regra de prêmio.
    
    Args:
        df_dia: DataFrame com dados de um único dia
        dia_num: Número do dia (1-5)
    
    Returns:
        DataFrame filtrado
    """
    if dia_num <= 2:
        return df_dia  # Todos os prêmios
    else:
        # Somente 1° prêmio ou legado
        if 'premio' in df_dia.columns:
            return df_dia[(df_dia['premio'] == 1) | (df_dia['premio'] == 0)]
        return df_dia

def get_day_color(day_number: int) -> dict:
    """
    Retorna as informações de cor para um número de dia específico.
    
    Args:
        day_number: Número do dia (1-5)
    
    Returns:
        Dict com 'cor', 'nome', 'emoji', 'text_color' ou valores padrão se inválido
    """
    return DIA_CORES.get(day_number, {'cor': '#CCCCCC', 'nome': 'N/A', 'emoji': '⬜', 'text_color': '#000000'})

def get_grupo_days(df: pd.DataFrame, loteria: str, grupo: int) -> list:
    """
    Retorna os números dos dias (1-5) em que um grupo específico apareceu.
    Aplica a regra de prêmio: dias 1-2 todos, dias 3-5 só 1° prêmio.
    Se o grupo apareceu múltiplas vezes no mesmo dia, retorna o dia repetido.
    
    Args:
        df: DataFrame com todos os dados
        loteria: Loteria para filtrar
        grupo: Número do grupo (1-25)
    
    Returns:
        Lista de números de dias (1-5), podendo ter repetições se apareceu várias vezes
    """
    # Usar filter com regra de prêmio
    df_filtrado = filter_by_day_prize_rules(df, loteria)
    
    if len(df_filtrado) == 0:
        return []
    
    # Filtrar pelo grupo
    df_grupo = df_filtrado[df_filtrado['grupo'] == grupo]
    
    if len(df_grupo) == 0:
        return []
    
    # Obter dias para cada aparição (incluindo repetições)
    dias = []
    for _, row in df_grupo.iterrows():
        data = row['data']
        if hasattr(data, 'date'):
            data = data.date()
        dia_num = get_day_number(df, loteria, data)
        if dia_num > 0:
            dias.append(dia_num)
    
    return sorted(dias)

def validate_dataframe(df: pd.DataFrame) -> tuple[bool, str]:
    """
    Valida se o DataFrame tem as colunas obrigatórias
    Retorna (sucesso, mensagem)
    """
    # Normalizar nomes das colunas
    df.columns = df.columns.str.lower().str.strip()
    
    # Verificar colunas obrigatórias
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    
    if missing_columns:
        return False, f"❌ Colunas faltando: {', '.join(missing_columns)}"
    
    # Verificar se há dados
    if len(df) == 0:
        return False, "❌ Planilha está vazia"
    
    return True, "✅ Planilha válida!"

def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Processa e normaliza o DataFrame
    """
    # Normalizar nomes das colunas
    df.columns = df.columns.str.lower().str.strip()
    
    # Converter data
    df['data'] = pd.to_datetime(df['data'], errors='coerce')
    
    # Garantir tipos numéricos
    df['grupo'] = pd.to_numeric(df['grupo'], errors='coerce').fillna(0).astype(int)
    df['centena'] = pd.to_numeric(df['centena'], errors='coerce').fillna(0).astype(int)
    df['milhar'] = pd.to_numeric(df['milhar'], errors='coerce').fillna(0).astype(int)
    
    # Garantir coluna premio
    if 'premio' not in df.columns:
        df['premio'] = 0
    df['premio'] = pd.to_numeric(df['premio'], errors='coerce').fillna(0).astype(int)
    
    # Normalizar loteria
    df['loteria'] = df['loteria'].str.strip()
    
    # Converter horario para string se for datetime
    if df['horario'].dtype == 'datetime64[ns]':
        df['horario'] = df['horario'].dt.strftime('%H:%M')
    else:
        df['horario'] = df['horario'].astype(str).str.strip()
    
    # Adicionar nome do animal
    df['animal'] = df['grupo'].map(GRUPOS_ANIMAIS)
    
    # Ordenar por data (mais recente primeiro)
    df = df.sort_values('data', ascending=False)
    
    return df

def load_file(uploaded_file) -> tuple[pd.DataFrame | None, str]:
    """
    Carrega arquivo CSV ou Excel
    Retorna (DataFrame ou None, mensagem)
    """
    try:
        filename = uploaded_file.name.lower()
        
        if filename.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            return None, "❌ Formato não suportado. Use CSV ou Excel (.xlsx)"
        
        # Validar estrutura
        is_valid, message = validate_dataframe(df)
        if not is_valid:
            return None, message
        
        # Processar dados
        df = process_dataframe(df)
        
        return df, f"✅ {len(df)} registros carregados com sucesso!"
        
    except Exception as e:
        return None, f"❌ Erro ao carregar arquivo: {str(e)}"

def filter_last_n_days(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """
    Filtra dados dos últimos N dias
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    return df[df['data'] >= cutoff_date]

def filter_by_loteria(df: pd.DataFrame, loterias: list) -> pd.DataFrame:
    """
    Filtra por loterias selecionadas
    """
    if not loterias or len(loterias) == 0:
        return df
    return df[df['loteria'].isin(loterias)]

def filter_by_horario(df: pd.DataFrame, horarios: list) -> pd.DataFrame:
    """
    Filtra por horários selecionados
    """
    if not horarios or len(horarios) == 0:
        return df
    return df[df['horario'].isin(horarios)]

def get_unique_loterias(df: pd.DataFrame) -> list:
    """
    Retorna loterias únicas no dataset
    """
    if df is None or len(df) == 0:
        return []
    return sorted(df['loteria'].unique().tolist())

def get_unique_horarios(df: pd.DataFrame) -> list:
    """
    Retorna horários únicos no dataset
    """
    if df is None or len(df) == 0:
        return []
    return sorted(df['horario'].unique().tolist())
