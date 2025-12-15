"""
Diagnóstico do problema de inserção no Supabase
"""
import os
os.environ['SUPABASE_URL'] = 'https://migwutooyjwpzfygjcbh.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pZ3d1dG9veWp3cHpmeWdqY2JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MjMzOTIsImV4cCI6MjA4MTI5OTM5Mn0.cD0l7kA4zeOWNn8hKz_9MxNXXb1MhpMhcaUNl1q9hG0'

from supabase import create_client
import pandas as pd

print("=" * 60)
print("DIAGNÓSTICO SUPABASE")
print("=" * 60)

client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# Ver dados atuais
print("\n1. Dados atuais no Supabase:")
result = client.table('resultados').select('*').execute()
print(f"   Total: {len(result.data)} registros")
for row in result.data:
    print(f"   ID {row['id']}: {row['data']} | {row['loteria']} | {row['horario']} | {row['milhar']} G.{row['grupo']} {row['animal']}")

# Tentar INSERT simples (não upsert)
print("\n2. Testando INSERT simples...")
test_records = [
    {'data': '2025-12-13', 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 10, 'centena': 640, 'milhar': 8640, 'animal': 'COELHO'},
    {'data': '2025-12-13', 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 6, 'centena': 124, 'milhar': 7124, 'animal': 'CABRA'},
]

for rec in test_records:
    try:
        result = client.table('resultados').insert(rec).execute()
        print(f"   ✓ Inserido: {rec['milhar']} G.{rec['grupo']}")
    except Exception as e:
        print(f"   ✗ Erro: {e}")

# Ver dados após
print("\n3. Dados após INSERT:")
result = client.table('resultados').select('*').execute()
print(f"   Total: {len(result.data)} registros")
for row in result.data:
    print(f"   ID {row['id']}: {row['data']} | {row['loteria']} | {row['horario']} | {row['milhar']} G.{row['grupo']} {row['animal']}")

print("\n" + "=" * 60)
