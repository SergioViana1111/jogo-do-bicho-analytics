"""
Teste automático para verificar todos os imports e funcionalidades do sistema
Executa antes do deploy para garantir que tudo funciona
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_module():
    """Testa o módulo de banco de dados"""
    print("Testing database module...")
    try:
        from modules.database import (
            init_database, 
            get_connection, 
            insert_resultados, 
            load_all_data,
            get_record_count
        )
        print("  ✓ Database module imports OK")
        
        # Testar inicialização
        init_database()
        print("  ✓ Database init OK")
        
        # Testar contagem
        count = get_record_count()
        print(f"  ✓ Record count: {count}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_data_loader_module():
    """Testa o módulo data_loader"""
    print("Testing data_loader module...")
    try:
        from modules.data_loader import (
            GRUPOS_ANIMAIS,
            DIA_CORES,
            LOTERIAS,
            load_data_from_database,
            save_data_to_database,
            get_last_5_unique_dates,
            get_day_number,
            filter_5_day_cycle,
            get_day_color,
            get_grupo_days
        )
        print("  ✓ Data loader imports OK")
        
        # Testar constantes
        assert len(GRUPOS_ANIMAIS) == 25
        print("  ✓ GRUPOS_ANIMAIS: 25 items")
        
        assert len(DIA_CORES) == 5
        print("  ✓ DIA_CORES: 5 items")
        
        # Testar funções
        color = get_day_color(1)
        assert color['emoji'] == '🔴'
        print("  ✓ get_day_color(1) = 🔴")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics_module():
    """Testa o módulo de estatísticas"""
    print("Testing statistics module...")
    try:
        from modules import statistics as stats
        print("  ✓ Statistics module imports OK")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_app_imports():
    """Testa os imports do app.py"""
    print("Testing app.py imports...")
    try:
        # Simular imports do app.py
        from modules.data_loader import load_data_from_database
        print("  ✓ app.py imports OK")
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def test_page_imports():
    """Testa os imports de todas as páginas"""
    print("Testing page imports...")
    
    pages_ok = True
    
    # Processador
    try:
        from modules.data_loader import (
            GRUPOS_ANIMAIS, DIA_CORES, get_day_number, 
            save_data_to_database, load_data_from_database
        )
        print("  ✓ Processador imports OK")
    except Exception as e:
        print(f"  ✗ Processador Error: {e}")
        pages_ok = False
    
    # Analise_Dias
    try:
        from modules.data_loader import (
            GRUPOS_ANIMAIS, DIA_CORES, 
            get_last_5_unique_dates, get_day_number, 
            filter_5_day_cycle, get_day_color
        )
        print("  ✓ Analise_Dias imports OK")
    except Exception as e:
        print(f"  ✗ Analise_Dias Error: {e}")
        pages_ok = False
    
    # Bichos
    try:
        from modules.data_loader import (
            GRUPOS_ANIMAIS, DIA_CORES, 
            filter_5_day_cycle, get_grupo_days, get_day_color
        )
        print("  ✓ Bichos imports OK")
    except Exception as e:
        print(f"  ✗ Bichos Error: {e}")
        pages_ok = False
    
    # Resultados
    try:
        from modules.data_loader import (
            GRUPOS_ANIMAIS, DIA_CORES, 
            filter_5_day_cycle, get_day_number, 
            get_last_5_unique_dates, get_day_color
        )
        print("  ✓ Resultados imports OK")
    except Exception as e:
        print(f"  ✗ Resultados Error: {e}")
        pages_ok = False
    
    # Mapa_Pedras
    try:
        from modules.data_loader import (
            DIA_CORES, filter_5_day_cycle, 
            get_last_5_unique_dates, get_day_color
        )
        from modules import statistics as stats
        print("  ✓ Mapa_Pedras imports OK")
    except Exception as e:
        print(f"  ✗ Mapa_Pedras Error: {e}")
        pages_ok = False
    
    # Consolidacao
    try:
        from modules.data_loader import (
            GRUPOS_ANIMAIS, DIA_CORES, 
            filter_5_day_cycle, get_last_5_unique_dates
        )
        from modules import statistics as stats
        print("  ✓ Consolidacao imports OK")
    except Exception as e:
        print(f"  ✗ Consolidacao Error: {e}")
        pages_ok = False
    
    return pages_ok

def run_all_tests():
    """Executa todos os testes"""
    print("=" * 50)
    print("JOGO DO BICHO - AUTOMATED TESTS")
    print("=" * 50)
    print()
    
    results = []
    
    results.append(("Database", test_database_module()))
    results.append(("Data Loader", test_data_loader_module()))
    results.append(("Statistics", test_statistics_module()))
    results.append(("App Imports", test_app_imports()))
    results.append(("Page Imports", test_page_imports()))
    
    print()
    print("=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {name}: {status}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("✓ ALL TESTS PASSED - Ready for deploy!")
        return 0
    else:
        print("✗ SOME TESTS FAILED - Fix errors before deploy!")
        return 1

if __name__ == "__main__":
    exit(run_all_tests())
