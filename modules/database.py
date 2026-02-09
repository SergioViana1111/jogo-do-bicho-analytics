"""
Módulo de armazenamento de dados - Supabase + SQLite fallback
- Cloud: Supabase PostgreSQL (persistência permanente)
- Local sem Supabase: SQLite em arquivo
"""
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
import streamlit as st

# ========================
# CONFIGURAÇÃO SUPABASE
# ========================

def _get_supabase_client():
    """Retorna cliente Supabase se configurado"""
    try:
        from supabase import create_client, Client
        
        # Tentar obter credenciais do secrets do Streamlit
        url = st.secrets.get("SUPABASE_URL") if hasattr(st, 'secrets') else os.environ.get("SUPABASE_URL")
        key = st.secrets.get("SUPABASE_KEY") if hasattr(st, 'secrets') else os.environ.get("SUPABASE_KEY")
        
        if url and key:
            return create_client(url, key)
    except Exception as e:
        print(f"[DB] Supabase não disponível: {e}")
    
    return None

def _is_supabase_available():
    """Verifica se Supabase está configurado"""
    if '_supabase_available' not in st.session_state:
        client = _get_supabase_client()
        st.session_state._supabase_available = client is not None
        if client:
            st.session_state._supabase_client = client
    return st.session_state._supabase_available

# ========================
# SQLITE FALLBACK
# ========================

DB_PATH = Path(__file__).parent.parent / "data" / "jogo_bicho.db"

def _get_sqlite_connection():
    """Retorna conexão SQLite para uso local"""
    import sqlite3
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
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

# ========================
# FUNÇÕES PÚBLICAS
# ========================

def init_database():
    """Inicializa o banco de dados"""
    if _is_supabase_available():
        print("[DB] Usando Supabase (cloud)")
    else:
        try:
            conn = _get_sqlite_connection()
            _init_sqlite_tables(conn)
            conn.close()
            print(f"[DB] Usando SQLite local: {DB_PATH}")
        except Exception as e:
            print(f"[DB] Erro SQLite: {e}")

def get_connection():
    """Retorna conexão (compatibilidade)"""
    if not _is_supabase_available():
        return _get_sqlite_connection()
    return None

def insert_resultados(df: pd.DataFrame) -> tuple:
    """
    Insere resultados no armazenamento.
    Retorna (inseridos, duplicados, erros)
    """
    if df is None or len(df) == 0:
        return 0, 0, None
    
    if _is_supabase_available():
        return _insert_supabase(df)
    else:
        return _insert_sqlite(df)

def _insert_supabase(df: pd.DataFrame) -> tuple:
    """Insere no Supabase"""
    client = st.session_state._supabase_client
    
    inseridos = 0
    duplicados = 0
    
    for _, row in df.iterrows():
        try:
            data = row['data']
            if hasattr(data, 'strftime'):
                data_str = data.strftime('%Y-%m-%d')
            elif hasattr(data, 'date'):
                data_str = data.date().strftime('%Y-%m-%d')
            else:
                data_str = str(data)[:10]
            
            record = {
                'data': data_str,
                'loteria': row['loteria'],
                'horario': row['horario'],
                'grupo': int(row['grupo']),
                'centena': int(row['centena']),
                'milhar': int(row['milhar']),
                'animal': row.get('animal', '')
            }
            
            # Usar INSERT simples (não upsert)
            result = client.table('resultados').insert(record).execute()
            
            if result.data:
                inseridos += 1
                print(f"[DB] Inserido: {record['milhar']} G.{record['grupo']}")
            else:
                duplicados += 1
                
        except Exception as e:
            error_msg = str(e)
            if 'duplicate' in error_msg.lower() or 'unique' in error_msg.lower():
                duplicados += 1
                print(f"[DB] Duplicado: {record['milhar']}")
            else:
                print(f"[DB] Erro Supabase: {e}")
                duplicados += 1
    
    print(f"[DB] Supabase: {inseridos} inseridos, {duplicados} duplicados")
    return inseridos, duplicados, None 

def _insert_sqlite(df: pd.DataFrame) -> tuple:
    """Insere no SQLite local"""
    import sqlite3
    conn = _get_sqlite_connection()
    _init_sqlite_tables(conn)
    cursor = conn.cursor()
    
    inseridos = 0
    duplicados = 0
    erros = 0
    msg_erro = ""
    
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
            print(f"[DB] Erro SQLite insert: {e}")
            erros += 1
            msg_erro = str(e)
    
    conn.commit()
    conn.close()
    print(f"[DB] SQLite: {inseridos} inseridos, {duplicados} duplicados, {erros} erros")
    if erros > 0:
        return inseridos, duplicados, msg_erro
    return inseridos, duplicados, None

def load_all_data() -> pd.DataFrame:
    """Carrega todos os dados"""
    if _is_supabase_available():
        return _load_supabase()
    else:
        return _load_sqlite()

# Colunas esperadas no banco de dados
COLUNAS_DB = ['id', 'data', 'loteria', 'horario', 'grupo', 'centena', 'milhar', 'animal']

def _load_supabase() -> pd.DataFrame:
    """Carrega do Supabase"""
    try:
        client = st.session_state._supabase_client
        result = client.table('resultados').select('*').order('data', desc=True).execute()
        
        if result.data:
            df = pd.DataFrame(result.data)
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'])
            
            # Garantir que todas as colunas existem
            for col in COLUNAS_DB:
                if col not in df.columns and col != 'id':
                    df[col] = None
                    
            print(f"[DB] Supabase: {len(df)} registros carregados")
            return df
        return pd.DataFrame(columns=COLUNAS_DB)
    except Exception as e:
        print(f"[DB] Erro Supabase load: {e}")
        return pd.DataFrame(columns=COLUNAS_DB)

def _load_sqlite() -> pd.DataFrame:
    """Carrega do SQLite"""
    try:
        import sqlite3
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
        print(f"[DB] Erro SQLite load: {e}")
        return pd.DataFrame(columns=COLUNAS_DB)

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
    if _is_supabase_available():
        try:
            client = st.session_state._supabase_client
            result = client.table('resultados').select('*', count='exact').execute()
            return result.count or 0
        except:
            return 0
    else:
        try:
            import sqlite3
            conn = _get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM resultados')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0

def delete_records_by_filter(loteria: str, data: str, horario: str) -> int:
    """
    Deleta registros por filtro (loteria, data, horário).
    Retorna número de registros deletados.
    """
    if _is_supabase_available():
        try:
            client = st.session_state._supabase_client
            result = client.table('resultados').delete().eq('loteria', loteria).eq('data', data).eq('horario', horario).execute()
            deleted_count = len(result.data) if result.data else 0
            print(f"[DB] Supabase: {deleted_count} registros deletados")
            return deleted_count
        except Exception as e:
            print(f"[DB] Erro ao deletar Supabase: {e}")
            return 0
    else:
        try:
            import sqlite3
            conn = _get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM resultados 
                WHERE loteria = ? AND data = ? AND horario = ?
            ''', (loteria, data, horario))
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            print(f"[DB] SQLite: {deleted_count} registros deletados")
            return deleted_count
        except Exception as e:
            print(f"[DB] Erro ao deletar SQLite: {e}")
            return 0

def delete_all_records() -> int:
    """
    Deleta TODOS os registros do banco de dados.
    ⚠️ Use com cuidado!
    Retorna número de registros deletados.
    """
    if _is_supabase_available():
        try:
            client = st.session_state._supabase_client
            # Deletar onde id != 0 (pega todos)
            result = client.table('resultados').delete().neq('id', 0).execute()
            deleted_count = len(result.data) if result.data else 0
            print(f"[DB] Supabase: {deleted_count} registros deletados")
            return deleted_count
        except Exception as e:
            print(f"[DB] Erro ao deletar Supabase: {e}")
            return 0
    else:
        try:
            import sqlite3
            conn = _get_sqlite_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM resultados')
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            print(f"[DB] SQLite: {deleted_count} registros deletados")
            return deleted_count
        except Exception as e:
            print(f"[DB] Erro ao deletar SQLite: {e}")
            return 0

# Inicializar ao importar
try:
    init_database()
except Exception as e:
    print(f"[DB] Erro na inicialização: {e}")
