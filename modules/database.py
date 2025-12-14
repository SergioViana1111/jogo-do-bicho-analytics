"""
Módulo de banco de dados SQLite para persistência de dados
O banco é interno, simples e invisível ao usuário
"""
import sqlite3
import pandas as pd
from datetime import datetime
from pathlib import Path

# Caminho do banco de dados (na mesma pasta do projeto)
DB_PATH = Path(__file__).parent.parent / "data" / "jogo_bicho.db"

def get_connection():
    """Retorna conexão com o banco de dados"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)

def init_database():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_connection()
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
    conn.close()

def insert_resultados(df: pd.DataFrame) -> tuple[int, int]:
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
    conn.close()
    
    return inseridos, duplicados

def load_all_data() -> pd.DataFrame:
    """Carrega todos os dados do banco de dados"""
    conn = get_connection()
    
    df = pd.read_sql_query('''
        SELECT data, loteria, horario, grupo, centena, milhar, animal
        FROM resultados
        ORDER BY data DESC, horario
    ''', conn)
    
    conn.close()
    
    if len(df) > 0:
        df['data'] = pd.to_datetime(df['data'])
    
    return df

def load_data_by_loteria(loteria: str) -> pd.DataFrame:
    """Carrega dados de uma loteria específica"""
    conn = get_connection()
    
    df = pd.read_sql_query('''
        SELECT data, loteria, horario, grupo, centena, milhar, animal
        FROM resultados
        WHERE loteria = ?
        ORDER BY data DESC, horario
    ''', conn, params=(loteria,))
    
    conn.close()
    
    if len(df) > 0:
        df['data'] = pd.to_datetime(df['data'])
    
    return df

def get_unique_loterias() -> list:
    """Retorna lista de loterias únicas no banco"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT loteria FROM resultados ORDER BY loteria')
    loterias = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return loterias

def get_record_count() -> int:
    """Retorna total de registros no banco"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM resultados')
    count = cursor.fetchone()[0]
    
    conn.close()
    return count

def delete_old_data(days_to_keep: int = 30):
    """Remove dados mais antigos que X dias (para manutenção)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM resultados 
        WHERE data < date('now', ?)
    ''', (f'-{days_to_keep} days',))
    
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted

# Inicializar banco ao importar o módulo
init_database()
