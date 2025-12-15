"""Script para zerar a base de dados do Supabase"""
import os
os.environ['SUPABASE_URL'] = 'https://migwutooyjwpzfygjcbh.supabase.co'
os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pZ3d1dG9veWp3cHpmeWdqY2JoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU3MjMzOTIsImV4cCI6MjA4MTI5OTM5Mn0.cD0l7kA4zeOWNn8hKz_9MxNXXb1MhpMhcaUNl1q9hG0'

from supabase import create_client

print("=" * 60)
print("🗑️  ZERANDO BASE DE DADOS - SUPABASE")
print("=" * 60)

client = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# Verificar quantos registros existem
print("\n1. Verificando registros atuais...")
try:
    result = client.table('resultados').select('*').execute()
    total_antes = len(result.data)
    print(f"   ✓ Total de registros: {total_antes}")
except Exception as e:
    print(f"   ✗ Erro: {e}")
    exit(1)

# Deletar todos os registros
print("\n2. Deletando TODOS os registros...")
try:
    # DELETE WHERE id != 0 (pega todos os registros)
    client.table('resultados').delete().neq('id', 0).execute()
    print("   ✓ Todos os registros foram deletados!")
except Exception as e:
    print(f"   ✗ Erro ao deletar: {e}")
    exit(1)

# Verificar se realmente zerou
print("\n3. Verificando base após limpeza...")
try:
    result = client.table('resultados').select('*').execute()
    total_depois = len(result.data)
    print(f"   ✓ Total de registros agora: {total_depois}")
except Exception as e:
    print(f"   ✗ Erro: {e}")

print("\n" + "=" * 60)
print(f"✅ BASE ZERADA! Removidos {total_antes} registros.")
print("   O cliente pode começar os testes do zero.")
print("=" * 60)
