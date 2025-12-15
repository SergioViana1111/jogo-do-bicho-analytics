"""
Teste de conexão Supabase
"""
import os
os.environ['SUPABASE_URL'] = 'https://migwutooyjwpzfygjcbh.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pZ3d1dG9veWp3cHpmeWdqY2JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MjMzOTIsImV4cCI6MjA4MTI5OTM5Mn0.cD0l7kA4zeOWNn8hKz_9MxNXXb1MhpMhcaUNl1q9hG0'

from supabase import create_client
import pandas as pd
from datetime import date

print("=" * 60)
print("TESTE DE CONEXÃO SUPABASE")
print("=" * 60)

# Conectar
print("\n1. Conectando ao Supabase...")
try:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_KEY')
    client = create_client(url, key)
    print(f"   ✓ Conectado: {url}")
except Exception as e:
    print(f"   ✗ Erro de conexão: {e}")
    exit(1)

# Verificar se tabela existe
print("\n2. Verificando tabela resultados...")
try:
    result = client.table('resultados').select('*').limit(1).execute()
    print(f"   ✓ Tabela existe!")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    print(f"   → Você executou o SQL para criar a tabela?")
    exit(1)

# Inserir dados de teste
print("\n3. Inserindo dados de teste...")
test_record = {
    'data': '2025-12-13',
    'loteria': 'Nacional',
    'horario': '02:00',
    'grupo': 14,
    'centena': 56,
    'milhar': 1056,
    'animal': 'GATO'
}

try:
    result = client.table('resultados').upsert(
        test_record,
        on_conflict='data,loteria,horario,milhar'
    ).execute()
    print(f"   ✓ Inserido: {result.data}")
except Exception as e:
    print(f"   ✗ Erro ao inserir: {e}")

# Carregar dados
print("\n4. Carregando todos os dados...")
try:
    result = client.table('resultados').select('*').order('data', desc=True).execute()
    print(f"   ✓ Total de registros: {len(result.data)}")
    if result.data:
        print(f"\n   Dados encontrados:")
        for row in result.data[:5]:
            print(f"     {row['data']} | {row['loteria']} | {row['horario']} | {row['milhar']:04d} G.{row['grupo']:02d}")
except Exception as e:
    print(f"   ✗ Erro ao carregar: {e}")

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")
print("=" * 60)
