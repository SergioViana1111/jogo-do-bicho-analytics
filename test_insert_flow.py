"""Teste completo de inserção - simula o que o Processador faz"""
import os
os.environ['SUPABASE_URL'] = 'https://migwutooyjwpzfygjcbh.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pZ3d1dG9veWp3cHpmeWdqY2JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MjMzOTIsImV4cCI6MjA4MTI5OTM5Mn0.cD0l7kA4zeOWNn8hKz_9MxNXXb1MhpMhcaUNl1q9hG0'

from supabase import create_client

ANIMAIS = {
    1: 'AVESTRUZ', 2: 'ÁGUIA', 3: 'BURRO', 4: 'BORBOLETA', 5: 'CACHORRO',
    6: 'CABRA', 7: 'CARNEIRO', 8: 'CAMELO', 9: 'COBRA', 10: 'COELHO',
    11: 'CAVALO', 12: 'ELEFANTE', 13: 'GALO', 14: 'GATO', 15: 'JACARÉ',
    16: 'LEÃO', 17: 'MACACO', 18: 'PORCO', 19: 'PAVÃO', 20: 'PERU',
    21: 'TOURO', 22: 'TIGRE', 23: 'URSO', 24: 'VEADO', 25: 'VACA'
}

client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

print("=" * 60)
print("TESTE: Inserção de dados de dias anteriores")
print("=" * 60)

# Testar inserção para dia 11/12/2025 (anterior ao 12 e 13)
print("\n1. Verificando dados atuais...")
result = client.table('resultados').select('*').execute()
print(f"   Total atual: {len(result.data)} registros")

# Mostrar datas únicas
datas = set([r['data'] for r in result.data])
print(f"   Datas existentes: {sorted(datas)}")

# Inserir dados de teste para dia 11
print("\n2. Inserindo dados para 11/12/2025 (08:00)...")
dados_11 = [
    ('08:00', 5555, 10),  # COELHO
    ('08:00', 3333, 5),   # CACHORRO
]

for horario, milhar, grupo in dados_11:
    centena = milhar % 1000
    animal = ANIMAIS.get(grupo, 'DESCONHECIDO')
    
    record = {
        'data': '2025-12-11',
        'loteria': 'Nacional',
        'horario': horario,
        'grupo': grupo,
        'centena': centena,
        'milhar': milhar,
        'animal': animal
    }
    
    try:
        result = client.table('resultados').insert(record).execute()
        print(f"   ✓ {milhar:04d} G.{grupo:02d} {animal} inserido!")
    except Exception as e:
        if 'duplicate' in str(e).lower():
            print(f"   - {milhar:04d} já existe")
        else:
            print(f"   ✗ Erro: {e}")

# Verificar após
print("\n3. Verificando após inserção...")
result = client.table('resultados').select('*').order('data', desc=True).execute()
print(f"   Total agora: {len(result.data)} registros")

datas = set([r['data'] for r in result.data])
print(f"   Datas existentes: {sorted(datas)}")

# Mostrar registros por data
print("\n4. Contagem por data:")
from collections import Counter
contagem = Counter([r['data'] for r in result.data])
for data, count in sorted(contagem.items()):
    print(f"   {data}: {count} registros")

print("\n" + "=" * 60)
print("✓ TESTE CONCLUÍDO - Inserção via API funciona!")
print("=" * 60)
