"""Inserir os 5 registros de exemplo"""
import os
os.environ['SUPABASE_URL'] = 'https://migwutooyjwpzfygjcbh.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pZ3d1dG9veWp3cHpmeWdqY2JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MjMzOTIsImV4cCI6MjA4MTI5OTM5Mn0.cD0l7kA4zeOWNn8hKz_9MxNXXb1MhpMhcaUNl1q9hG0'

from supabase import create_client

client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# Os 5 registros do exemplo
# 1: 1.056 G.14, 2: 8.640 G.10, 3: 7.124 G.06, 4: 8.810 G.03, 5: 7.849 G.13
records = [
    {'data': '2025-12-13', 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 3, 'centena': 810, 'milhar': 8810, 'animal': 'BURRO'},
    {'data': '2025-12-13', 'loteria': 'Nacional', 'horario': '02:00', 'grupo': 13, 'centena': 849, 'milhar': 7849, 'animal': 'GALO'},
]

print("Inserindo registros faltantes...")
for rec in records:
    try:
        result = client.table('resultados').insert(rec).execute()
        print(f"✓ {rec['milhar']} G.{rec['grupo']} {rec['animal']}")
    except Exception as e:
        if 'duplicate' in str(e).lower():
            print(f"- {rec['milhar']} já existe")
        else:
            print(f"✗ Erro: {e}")

# Mostrar total
result = client.table('resultados').select('*').execute()
print(f"\nTotal no Supabase: {len(result.data)} registros")
for row in result.data:
    print(f"  {row['milhar']:04d} G.{row['grupo']:02d} {row['animal']}")
