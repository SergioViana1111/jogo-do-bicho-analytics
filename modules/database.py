"""
Módulo de armazenamento de dados - Híbrido
- Local: SQLite em arquivo (persistência permanente)
- Cloud: Session State (persistência durante sessão)
"""
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path
import os

# Detectar ambiente
def _is_streamlit_cloud():
    """Detecta se está rodando no Streamlit Cloud"""
    return os.environ.get('STREAMLIT_SHARING_MODE') is not None or \
           os.path.exists('/mount/src')

# Caminho do banco de dados SQLite (para uso local)
DB_PATH = Path(__file__).parent.parent / "data" / "jogo_bicho.db"

def _ensure_db_dir():
    """Garante que o diretório do banco existe"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def _get_sqlite_connection():
    """Retorna conexão SQLite para uso local"""
    _ensure_db_dir()
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    return conn

def _init_sqlite_tables(conn):
    """Inicializa tabelas no SQLite"""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE NOT NULL,
            loteria TEXT NOT NULL,
            horario TEXT NOT NULL,
            grupo INTEGER NOT NULL,
            centena INTEGER NOT NULL,
            milhar INTEGER NOT NULL,
            animal TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(data, loteria, horario, milhar)
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_loteria ON resultados(loteria)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_data ON resultados(data)')
    conn.commit()

def _get_session_store():
    """Retorna dataframe armazenado no session_state (para Cloud)"""
    import streamlit as st
    if '_dados_store' not in st.session_state:
        st.session_state._dados_store = pd.DataFrame(columns=[
            'data', 'loteria', 'horario', 'grupo', 'centena', 'milhar', 'animal'
        ])
    return st.session_state._dados_store

def _set_session_store(df):
    """Atualiza dataframe no session_state"""
    import streamlit as st
    st.session_state._dados_store = df

# ========================
# FUNÇÕES PÚBLICAS
# ========================

def init_database():
    """Inicializa o banco de dados"""
    if not _is_streamlit_cloud():
        conn = _get_sqlite_connection()
        _init_sqlite_tables(conn)
        conn.close()
        print(f"[DB] SQLite inicializado: {DB_PATH}")
    else:
        _get_session_store()
        print("[DB] Session Store inicializado (Cloud mode)")

def get_connection():
    """Retorna conexão (compatibilidade)"""
    if not _is_streamlit_cloud():
        return _get_sqlite_connection()
    return None

def insert_resultados(df: pd.DataFrame) -> tuple:
    """
    Insere resultados no armazenamento.
    Retorna (inseridos, duplicados)
    """
    if df is None or len(df) == 0:
        return 0, 0
    
    if not _is_streamlit_cloud():
        # Usar SQLite local
        return _insert_sqlite(df)
    else:
        # Usar session state no Cloud
        return _insert_session(df)

def _insert_sqlite(df: pd.DataFrame) -> tuple:
    """Insere no SQLite local"""
    conn = _get_sqlite_connection()
    _init_sqlite_tables(conn)
    cursor = conn.cursor()
    
    inseridos = 0
    duplicados = 0
    
    for _, row in df.iterrows():
        try:
            data = row['data']
            if hasattr(data, 'strftime'):
                data = data.strftime('%Y-%m-%d')
            elif hasattr(data, 'date'):
                data = data.date().strftime('%Y-%m-%d')
            
            cursor.execute('''
                INSERT OR IGNORE INTO resultados 
                (data, loteria, horario, grupo, centena, milhar, animal)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data,
                row['loteria'],
                row['horario'],
                int(row['grupo']),
                int(row['centena']),
                int(row['milhar']),
                row.get('animal', '')
            ))
            
            if cursor.rowcount > 0:
                inseridos += 1
            else:
                duplicados += 1
                
        except Exception as e:
            print(f"[DB] Erro ao inserir: {e}")
            duplicados += 1
    
    conn.commit()
    conn.close()
    print(f"[DB] SQLite: {inseridos} inseridos, {duplicados} duplicados")
    return inseridos, duplicados

def _insert_session(df: pd.DataFrame) -> tuple:
    """Insere no session state (Cloud)"""
    current_data = _get_session_store()
    
    inseridos = 0
    duplicados = 0
    new_rows = []
    
    for _, row in df.iterrows():
        data = row['data']
        if hasattr(data, 'strftime'):
            data_str = data.strftime('%Y-%m-%d')
        else:
            data_str = str(data)[:10]
        
        # Checar duplicata
        is_dup = False
        if len(current_data) > 0:
            mask = (
                (current_data['data'].astype(str).str[:10] == data_str) &
                (current_data['loteria'] == row['loteria']) &
                (current_data['horario'] == row['horario']) &
                (current_data['milhar'] == int(row['milhar']))
            )
            if mask.any():
                is_dup = True
                duplicados += 1
        
        if not is_dup:
            new_rows.append({
                'data': pd.to_datetime(data),
                'loteria': row['loteria'],
                'horario': row['horario'],
                'grupo': int(row['grupo']),
                'centena': int(row['centena']),
                'milhar': int(row['milhar']),
                'animal': row.get('animal', '')
            })
            inseridos += 1
    
    if new_rows:
        new_df = pd.DataFrame(new_rows)
        if len(current_data) > 0:
            updated = pd.concat([current_data, new_df], ignore_index=True)
        else:
            updated = new_df
        updated = updated.sort_values('data', ascending=False).reset_index(drop=True)
        _set_session_store(updated)
    
    print(f"[DB] Session: {inseridos} inseridos, {duplicados} duplicados")
    return inseridos, duplicados

def load_all_data() -> pd.DataFrame:
    """Carrega todos os dados"""
    if not _is_streamlit_cloud():
        return _load_sqlite()
    else:
        return _get_session_store().copy()

def _load_sqlite() -> pd.DataFrame:
    """Carrega do SQLite"""
    try:
        conn = _get_sqlite_connection()
        _init_sqlite_tables(conn)
        
        df = pd.read_sql_query('''
            SELECT data, loteria, horario, grupo, centena, milhar, animal
            FROM resultados
            ORDER BY data DESC, horario
        ''', conn)
        
        conn.close()
        
        if len(df) > 0:
            df['data'] = pd.to_datetime(df['data'])
        
        print(f"[DB] SQLite: {len(df)} registros carregados")
        return df
    except Exception as e:
        print(f"[DB] Erro ao carregar SQLite: {e}")
        return pd.DataFrame()

def load_data_by_loteria(loteria: str) -> pd.DataFrame:
    """Carrega dados de uma loteria específica"""
    df = load_all_data()
    if len(df) == 0:
        return pd.DataFrame()
    return df[df['loteria'] == loteria].copy()

def get_unique_loterias() -> list:
    """Retorna lista de loterias únicas"""
    df = load_all_data()
    if len(df) == 0:
        return []
    return df['loteria'].unique().tolist()

def get_record_count() -> int:
    """Retorna total de registros"""
    if not _is_streamlit_cloud():
        try:
            conn = _get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM resultados')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    else:
        return len(_get_session_store())

def delete_old_data(days_to_keep: int = 30):
    """Remove dados mais antigos que X dias"""
    # Não implementado para simplicidade
    return 0

# Inicializar ao importar
try:
    init_database()
except Exception as e:
    print(f"[DB] Erro na inicialização: {e}")
