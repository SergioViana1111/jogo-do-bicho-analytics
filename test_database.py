"""
Teste manual para verificar se o banco de dados está salvando e carregando dados corretamente
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
from datetime import date, datetime

print("=" * 60)
print("TESTE MANUAL DE BANCO DE DADOS")
print("=" * 60)

# Simular o ambiente do Streamlit para teste
class MockSessionState:
    def __init__(self):
        self._data = {}
    
    def __contains__(self, key):
        return key in self._data
    
    def __getattr__(self, key):
        if key.startswith('_'):
            return super().__getattribute__(key)
        return self._data.get(key)
    
    def __setattr__(self, key, value):
        if key.startswith('_'):
            super().__setattr__(key, value)
        else:
            self._data[key] = value

# Mock streamlit
import streamlit
streamlit.session_state = MockSessionState()

# Agora importar o módulo de database
from modules.database import (
    get_connection,
    init_database,
    insert_resultados,
    load_all_data,
    get_record_count
)

print("\n1. Testando conexão com banco de dados...")
try:
    conn = get_connection()
    print(f"   ✓ Conexão obtida: {conn}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)

print("\n2. Inicializando banco de dados...")
try:
    init_database()
    print("   ✓ Banco inicializado")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)

print("\n3. Verificando contagem inicial...")
try:
    count_before = get_record_count()
    print(f"   ✓ Registros antes: {count_before}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)

print("\n4. Inserindo dados de teste...")
# Dados de teste (simulando resultados do Nacional 13/12)
test_data = pd.DataFrame([
    {'data': date(2025, 12, 13), 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 14, 'centena': 56, 'milhar': 1056, 'animal': 'GATO'},
    {'data': date(2025, 12, 13), 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 10, 'centena': 640, 'milhar': 8640, 'animal': 'COELHO'},
    {'data': date(2025, 12, 13), 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 6, 'centena': 124, 'milhar': 7124, 'animal': 'CABRA'},
    {'data': date(2025, 12, 13), 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 3, 'centena': 810, 'milhar': 8810, 'animal': 'BURRO'},
    {'data': date(2025, 12, 13), 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 13, 'centena': 849, 'milhar': 7849, 'animal': 'GALO'},
])

print(f"   Dados a inserir:")
for _, row in test_data.iterrows():
    print(f"     - {row['milhar']:04d} G.{row['grupo']:02d} {row['animal']}")

try:
    inseridos, duplicados = insert_resultados(test_data)
    print(f"   ✓ Inseridos: {inseridos}, Duplicados: {duplicados}")
except Exception as e:
    print(f"   ✗ Erro ao inserir: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n5. Verificando contagem após inserção...")
try:
    count_after = get_record_count()
    print(f"   ✓ Registros depois: {count_after}")
    if count_after > count_before:
        print(f"   ✓ SUCESSO: {count_after - count_before} novos registros!")
    else:
        print(f"   ⚠ Nenhum novo registro (podem ser duplicados)")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    sys.exit(1)

print("\n6. Carregando todos os dados...")
try:
    df = load_all_data()
    print(f"   ✓ Dados carregados: {len(df)} registros")
    if len(df) > 0:
        print(f"\n   Primeiros registros:")
        for _, row in df.head(5).iterrows():
            print(f"     {row['data']} | {row['loteria']} | {row['horario']} | {row['milhar']:04d} G.{row['grupo']:02d}")
except Exception as e:
    print(f"   ✗ Erro ao carregar: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n7. Testando nova conexão (simulando nova página)...")
# Simular que está vindo de outra página
conn2 = get_connection()
print(f"   ✓ Segunda conexão: {conn2}")
print(f"   ✓ Mesma conexão? {conn is conn2}")

print("\n8. Carregando dados novamente...")
try:
    df2 = load_all_data()
    print(f"   ✓ Dados na segunda conexão: {len(df2)} registros")
except Exception as e:
    print(f"   ✗ Erro: {e}")

print("\n" + "=" * 60)
if len(df) > 0:
    print("✓ TESTE PASSOU - Banco de dados funcionando!")
else:
    print("✗ TESTE FALHOU - Verificar implementação")
print("=" * 60)
