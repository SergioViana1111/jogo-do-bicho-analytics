"""
Módulo de carregamento e validação de dados do Jogo do Bicho
"""
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

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
