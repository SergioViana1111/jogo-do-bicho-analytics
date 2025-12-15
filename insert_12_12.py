"""Inserir dados do dia 12/12 (baseado nas imagens do usuário)"""
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

# Dados do dia 12/12 (baseado na screenshot do usuário)
# Os dados mostrados são para 02:00
dados_12 = [
    ('02:00', 7602, 1),   # AVESTRUZ
    ('02:00', 6754, 14),  # GATO
    ('02:00', 9217, 5),   # CACHORRO
    ('02:00', 9518, 5),   # CACHORRO
    ('02:00', 1792, 23),  # URSO
]

print("Inserindo dados do dia 12/12...")
inseridos = 0
for horario, milhar, grupo in dados_12:
    centena = milhar % 1000
    animal = ANIMAIS.get(grupo, 'DESCONHECIDO')
    
    record = {
        'data': '2025-12-12',
        'loteria': 'Nacional',
        'horario': horario,
        'grupo': grupo,
        'centena': centena,
        'milhar': milhar,
        'animal': animal
    }
    
    try:
        client.table('resultados').insert(record).execute()
        print(f"   ✓ {milhar:04d} G.{grupo:02d} {animal}")
        inseridos += 1
    except Exception as e:
        if 'duplicate' in str(e).lower():
            print(f"   - {milhar:04d} já existe")
        else:
            print(f"   Erro: {e}")

print(f"\nTotal inseridos: {inseridos}")

# Verificar total
result = client.table('resultados').select('*').execute()
print(f"Total no banco: {len(result.data)} registros")
