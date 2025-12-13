"""
Módulo de cálculos estatísticos do Jogo do Bicho
"""
import pandas as pd
from collections import Counter

def get_grupo_frequency(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Calcula frequência dos grupos
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    freq = df['grupo'].value_counts().reset_index()
    freq.columns = ['grupo', 'frequencia']
    
    # Adicionar animal
    from modules.data_loader import GRUPOS_ANIMAIS
    freq['animal'] = freq['grupo'].map(GRUPOS_ANIMAIS)
    freq['grupo_animal'] = freq.apply(lambda x: f"{x['grupo']:02d} - {x['animal']}", axis=1)
    
    return freq.head(top_n)

def get_centena_frequency(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Calcula frequência das centenas
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    freq = df['centena'].value_counts().reset_index()
    freq.columns = ['centena', 'frequencia']
    freq['centena_fmt'] = freq['centena'].apply(lambda x: f"{x:03d}")
    
    return freq.head(top_n)

def get_milhar_frequency(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Calcula frequência das milhares
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    freq = df['milhar'].value_counts().reset_index()
    freq.columns = ['milhar', 'frequencia']
    freq['milhar_fmt'] = freq['milhar'].apply(lambda x: f"{x:04d}")
    
    return freq.head(top_n)

def get_repeticoes_grupos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica grupos que se repetem em sequência
    """
    if df is None or len(df) < 2:
        return pd.DataFrame()
    
    df_sorted = df.sort_values(['loteria', 'data', 'horario'])
    repeticoes = []
    
    for loteria in df_sorted['loteria'].unique():
        df_lot = df_sorted[df_sorted['loteria'] == loteria].reset_index(drop=True)
        
        for i in range(1, len(df_lot)):
            if df_lot.loc[i, 'grupo'] == df_lot.loc[i-1, 'grupo']:
                repeticoes.append({
                    'loteria': loteria,
                    'grupo': df_lot.loc[i, 'grupo'],
                    'animal': df_lot.loc[i, 'animal'],
                    'data_anterior': df_lot.loc[i-1, 'data'],
                    'data_atual': df_lot.loc[i, 'data'],
                    'horario_anterior': df_lot.loc[i-1, 'horario'],
                    'horario_atual': df_lot.loc[i, 'horario']
                })
    
    return pd.DataFrame(repeticoes)

def get_repeticoes_centenas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica centenas que se repetem
    """
    if df is None or len(df) < 2:
        return pd.DataFrame()
    
    df_sorted = df.sort_values(['loteria', 'data', 'horario'])
    repeticoes = []
    
    for loteria in df_sorted['loteria'].unique():
        df_lot = df_sorted[df_sorted['loteria'] == loteria].reset_index(drop=True)
        
        for i in range(1, len(df_lot)):
            if df_lot.loc[i, 'centena'] == df_lot.loc[i-1, 'centena']:
                repeticoes.append({
                    'loteria': loteria,
                    'centena': f"{df_lot.loc[i, 'centena']:03d}",
                    'data_anterior': df_lot.loc[i-1, 'data'],
                    'data_atual': df_lot.loc[i, 'data']
                })
    
    return pd.DataFrame(repeticoes)

def get_repeticoes_milhares(df: pd.DataFrame) -> pd.DataFrame:
    """
    Identifica milhares que se repetem
    """
    if df is None or len(df) < 2:
        return pd.DataFrame()
    
    df_sorted = df.sort_values(['loteria', 'data', 'horario'])
    repeticoes = []
    
    for loteria in df_sorted['loteria'].unique():
        df_lot = df_sorted[df_sorted['loteria'] == loteria].reset_index(drop=True)
        
        for i in range(1, len(df_lot)):
            if df_lot.loc[i, 'milhar'] == df_lot.loc[i-1, 'milhar']:
                repeticoes.append({
                    'loteria': loteria,
                    'milhar': f"{df_lot.loc[i, 'milhar']:04d}",
                    'data_anterior': df_lot.loc[i-1, 'data'],
                    'data_atual': df_lot.loc[i, 'data']
                })
    
    return pd.DataFrame(repeticoes)

def get_linhas_grupos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula ranking de linhas de grupos
    Linha 1: grupos 1-5
    Linha 2: grupos 6-10
    Linha 3: grupos 11-15
    Linha 4: grupos 16-20
    Linha 5: grupos 21-25
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    def get_linha(grupo):
        if 1 <= grupo <= 5:
            return 1
        elif 6 <= grupo <= 10:
            return 2
        elif 11 <= grupo <= 15:
            return 3
        elif 16 <= grupo <= 20:
            return 4
        elif 21 <= grupo <= 25:
            return 5
        return 0
    
    df_copy = df.copy()
    df_copy['linha'] = df_copy['grupo'].apply(get_linha)
    
    linhas_desc = {
        1: 'Linha 1 (01-05): Avestruz, Águia, Burro, Borboleta, Cachorro',
        2: 'Linha 2 (06-10): Cabra, Carneiro, Camelo, Cobra, Coelho',
        3: 'Linha 3 (11-15): Cavalo, Elefante, Galo, Gato, Jacaré',
        4: 'Linha 4 (16-20): Leão, Macaco, Porco, Pavão, Peru',
        5: 'Linha 5 (21-25): Touro, Tigre, Urso, Veado, Vaca'
    }
    
    freq = df_copy['linha'].value_counts().reset_index()
    freq.columns = ['linha', 'frequencia']
    freq['descricao'] = freq['linha'].map(linhas_desc)
    freq = freq.sort_values('frequencia', ascending=False)
    
    return freq

def get_correlacao_grupo_centena(df: pd.DataFrame, grupo: int) -> pd.DataFrame:
    """
    Retorna centenas mais frequentes para um grupo específico
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    df_grupo = df[df['grupo'] == grupo]
    if len(df_grupo) == 0:
        return pd.DataFrame()
    
    freq = df_grupo['centena'].value_counts().reset_index().head(10)
    freq.columns = ['centena', 'frequencia']
    freq['centena_fmt'] = freq['centena'].apply(lambda x: f"{x:03d}")
    
    return freq

def get_fechamento_grupos(df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Gera fechamento de grupos baseado em frequência e repetição
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    from modules.data_loader import GRUPOS_ANIMAIS
    
    # Frequência
    freq = df['grupo'].value_counts()
    
    # Repetições (peso extra)
    repeticoes = get_repeticoes_grupos(df)
    rep_count = repeticoes['grupo'].value_counts() if len(repeticoes) > 0 else pd.Series()
    
    # Score combinado: frequência + repetições*2
    scores = {}
    for grupo in range(1, 26):
        freq_val = freq.get(grupo, 0)
        rep_val = rep_count.get(grupo, 0)
        scores[grupo] = freq_val + (rep_val * 2)
    
    result = pd.DataFrame([
        {'grupo': g, 'animal': GRUPOS_ANIMAIS.get(g, ''), 
         'score': s, 'frequencia': freq.get(g, 0)}
        for g, s in scores.items()
    ])
    
    result = result.sort_values('score', ascending=False).head(top_n)
    result['rank'] = range(1, len(result) + 1)
    result['grupo_fmt'] = result.apply(lambda x: f"{x['grupo']:02d} - {x['animal']}", axis=1)
    
    return result

def get_fechamento_centenas(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Gera fechamento de centenas baseado em frequência
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    freq = get_centena_frequency(df, top_n=top_n)
    freq['rank'] = range(1, len(freq) + 1)
    
    return freq

def get_fechamento_milhares(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Gera fechamento de milhares baseado em frequência
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    freq = get_milhar_frequency(df, top_n=top_n)
    freq['rank'] = range(1, len(freq) + 1)
    
    return freq

def get_tendencia_diaria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula quantidade de resultados por dia
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    tendencia = df.groupby('data').size().reset_index()
    tendencia.columns = ['data', 'resultados']
    tendencia = tendencia.sort_values('data')
    
    return tendencia

def get_distribuicao_por_loteria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula distribuição de resultados por loteria
    """
    if df is None or len(df) == 0:
        return pd.DataFrame()
    
    dist = df['loteria'].value_counts().reset_index()
    dist.columns = ['loteria', 'resultados']
    
    return dist
