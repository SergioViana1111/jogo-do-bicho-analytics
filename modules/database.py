"""
Módulo de banco de dados para persistência de dados
Usa SQLite in-memory para Streamlit Cloud (filesystem read-only)
"""
import sqlite3
import pandas as pd
from datetime import datetime
import streamlit as st

# Usar banco de dados em memória que é armazenado no session_state
def get_connection():
    """Retorna conexão com o banco de dados em memória"""
    # Usar connection persistente no session_state
    if '_db_conn' not in st.session_state:
        st.session_state._db_conn = sqlite3.connect(':memory:', check_same_thread=False)
        _init_tables(st.session_state._db_conn)
    return st.session_state._db_conn

def _init_tables(conn):
    """Inicializa as tabelas no banco de dados"""
    cursor = conn.cursor()
    
    # Tabela principal de resultados
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
    
    # Índices para performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_loteria ON resultados(loteria)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_data ON resultados(data)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_loteria_data ON resultados(loteria, data)')
    
    conn.commit()

def init_database():
    """Inicializa o banco de dados - apenas dispara get_connection"""
    get_connection()

def insert_resultados(df: pd.DataFrame) -> tuple:
    """
    Insere resultados no banco de dados.
    Retorna (inseridos, duplicados)
    """
    if df is None or len(df) == 0:
        return 0, 0
    
    conn = get_connection()
    cursor = conn.cursor()
    
    inseridos = 0
    duplicados = 0
    
    for _, row in df.iterrows():
        try:
            # Converter data para string se necessário
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
            print(f"Erro ao inserir registro: {e}")
            duplicados += 1
    
    conn.commit()
    
    return inseridos, duplicados

def load_all_data() -> pd.DataFrame:
    """Carrega todos os dados do banco de dados"""
    try:
        conn = get_connection()
        
        df = pd.read_sql_query('''
            SELECT data, loteria, horario, grupo, centena, milhar, animal
            FROM resultados
            ORDER BY data DESC, horario
        ''', conn)
        
        if len(df) > 0:
            df['data'] = pd.to_datetime(df['data'])
        
        return df
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def load_data_by_loteria(loteria: str) -> pd.DataFrame:
    """Carrega dados de uma loteria específica"""
    try:
        conn = get_connection()
        
        df = pd.read_sql_query('''
            SELECT data, loteria, horario, grupo, centena, milhar, animal
            FROM resultados
            WHERE loteria = ?
            ORDER BY data DESC, horario
        ''', conn, params=(loteria,))
        
        if len(df) > 0:
            df['data'] = pd.to_datetime(df['data'])
        
        return df
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

def get_unique_loterias() -> list:
    """Retorna lista de loterias únicas no banco"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT loteria FROM resultados ORDER BY loteria')
        loterias = [row[0] for row in cursor.fetchall()]
        
        return loterias
    except Exception as e:
        print(f"Erro ao buscar loterias: {e}")
        return []

def get_record_count() -> int:
    """Retorna total de registros no banco"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM resultados')
        count = cursor.fetchone()[0]
        
        return count
    except Exception as e:
        print(f"Erro ao contar registros: {e}")
        return 0

def delete_old_data(days_to_keep: int = 30):
    """Remove dados mais antigos que X dias (para manutenção)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM resultados 
            WHERE data < date('now', ?)
        ''', (f'-{days_to_keep} days',))
        
        deleted = cursor.rowcount
        conn.commit()
        
        return deleted
    except Exception as e:
        print(f"Erro ao deletar dados: {e}")
        return 0
