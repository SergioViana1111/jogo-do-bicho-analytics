"""Apagar tudo e inserir os dados do cliente - Nacional 13/12"""
import os
os.environ['SUPABASE_URL'] = 'https://migwutooyjwpzfygjcbh.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pZ3d1dG9veWp3cHpmeWdqY2JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MjMzOTIsImV4cCI6MjA4MTI5OTM5Mn0.cD0l7kA4zeOWNn8hKz_9MxNXXb1MhpMhcaUNl1q9hG0'

from supabase import create_client

# Mapeamento grupo -> animal
ANIMAIS = {
    1: 'AVESTRUZ', 2: 'ÁGUIA', 3: 'BURRO', 4: 'BORBOLETA', 5: 'CACHORRO',
    6: 'CABRA', 7: 'CARNEIRO', 8: 'CAMELO', 9: 'COBRA', 10: 'COELHO',
    11: 'CAVALO', 12: 'ELEFANTE', 13: 'GALO', 14: 'GATO', 15: 'JACARÉ',
    16: 'LEÃO', 17: 'MACACO', 18: 'PORCO', 19: 'PAVÃO', 20: 'PERU',
    21: 'TOURO', 22: 'TIGRE', 23: 'URSO', 24: 'VEADO', 25: 'VACA'
}

client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

print("1. Apagando todos os registros...")
try:
    client.table('resultados').delete().neq('id', 0).execute()
    print("   ✓ Registros apagados")
except Exception as e:
    print(f"   Erro: {e}")

# Dados do cliente - Nacional 13/12/2025
# Formato: (horario, milhar, grupo)
dados = [
    # 02HS
    ('02:00', 1056, 14), ('02:00', 8640, 10), ('02:00', 7124, 6), ('02:00', 8810, 3), ('02:00', 7849, 13),
    # 08HS
    ('08:00', 3376, 19), ('08:00', 143, 11), ('08:00', 2502, 1), ('08:00', 5412, 3), ('08:00', 443, 11),
    # 10HS
    ('10:00', 1209, 3), ('10:00', 1630, 8), ('10:00', 1247, 12), ('10:00', 2145, 12), ('10:00', 417, 5),
    # 12HS
    ('12:00', 6002, 1), ('12:00', 2576, 19), ('12:00', 1189, 23), ('12:00', 9347, 12), ('12:00', 861, 16),
    # 15HS
    ('15:00', 3174, 19), ('15:00', 829, 8), ('15:00', 6592, 23), ('15:00', 6910, 3), ('15:00', 3726, 7),
    # 17HS
    ('17:00', 3971, 18), ('17:00', 2784, 21), ('17:00', 6595, 24), ('17:00', 9737, 10), ('17:00', 7391, 23),
    # 21HS
    ('21:00', 2372, 18), ('21:00', 6509, 3), ('21:00', 3583, 21), ('21:00', 1046, 12), ('21:00', 6718, 5),
    # 23HS
    ('23:00', 2437, 10), ('23:00', 1922, 6), ('23:00', 6334, 9), ('23:00', 6818, 5), ('23:00', 2947, 12),
]

print(f"\n2. Inserindo {len(dados)} registros...")
inseridos = 0
for horario, milhar, grupo in dados:
    centena = milhar % 1000
    animal = ANIMAIS.get(grupo, 'DESCONHECIDO')
    
    record = {
        'data': '2025-12-13',
        'loteria': 'Nacional',
        'horario': horario,
        'grupo': grupo,
        'centena': centena,
        'milhar': milhar,
        'animal': animal
    }
    
    try:
        client.table('resultados').insert(record).execute()
        inseridos += 1
    except Exception as e:
        print(f"   Erro {milhar}: {e}")

print(f"   ✓ {inseridos} registros inseridos")

# Verificar
print("\n3. Verificando dados...")
result = client.table('resultados').select('*').order('horario').execute()
print(f"   Total: {len(result.data)} registros")

# Mostrar por horário
horarios = {}
for row in result.data:
    h = row['horario']
    if h not in horarios:
        horarios[h] = []
    horarios[h].append(row)

for h in sorted(horarios.keys()):
    print(f"\n   {h}:")
    for row in horarios[h]:
        print(f"     {row['milhar']:04d} G.{row['grupo']:02d} {row['animal']}")
