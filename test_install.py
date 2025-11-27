#!/usr/bin/env python3
"""
Script de teste para validar a instalação do pacote.
Execute após instalar: pip install -e .
"""

def test_imports():
    """Testa se todos os imports principais funcionam"""
    print("🧪 Testando imports...")
    
    try:
        from litevectordb import LocalVectorDB, VectorStore, MemoryDB, DocumentResult
        print("✅ Imports principais OK")
    except ImportError as e:
        print(f"❌ Erro nos imports principais: {e}")
        return False
    
    try:
        from litevectordb.embeddings import fake_embed
        print("✅ Import de embeddings OK")
    except ImportError as e:
        print(f"❌ Erro no import de embeddings: {e}")
        return False
    
    try:
        from litevectordb import __version__
        print(f"✅ Versão: {__version__}")
    except ImportError:
        print("⚠️  Versão não encontrada (opcional)")
    
    return True


def test_basic_functionality():
    """Testa funcionalidade básica"""
    print("\n🧪 Testando funcionalidade básica...")
    
    try:
        import os
        from litevectordb import LocalVectorDB
        
        # Remove banco de teste se existir
        test_db = "test_install.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        # Cria banco
        db = LocalVectorDB(path=test_db, dim=64)
        print("✅ LocalVectorDB criado")
        
        # Adiciona textos
        ids = db.add_texts(["Teste 1", "Teste 2"])
        print(f"✅ Textos adicionados: {ids}")
        
        # Busca
        resultados = db.similarity_search("teste", top_k=2)
        print(f"✅ Busca realizada: {len(resultados)} resultados")
        
        # Limpeza
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✅ Funcionalidade básica OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro na funcionalidade básica: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """Testa VectorStore diretamente"""
    print("\n🧪 Testando VectorStore...")
    
    try:
        import os
        import numpy as np
        from litevectordb import VectorStore
        from litevectordb.embeddings import fake_embed
        
        test_db = "test_vectorstore.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        store = VectorStore(test_db, dim=64)
        print("✅ VectorStore criado")
        
        vec = fake_embed("teste", dim=64)
        doc_id = store.add(vector=vec, content="teste")
        print(f"✅ Documento adicionado: {doc_id}")
        
        count = store.count()
        print(f"✅ Contagem: {count}")
        
        store.close()
        
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print("✅ VectorStore OK")
        return True
        
    except Exception as e:
        print(f"❌ Erro no VectorStore: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("="*50)
    print("Teste de Instalação do LiteVectorDB")
    print("="*50)
    
    all_ok = True
    
    all_ok &= test_imports()
    all_ok &= test_basic_functionality()
    all_ok &= test_vector_store()
    
    print("\n" + "="*50)
    if all_ok:
        print("✅ Todos os testes passaram!")
        print("🎉 O pacote está pronto para distribuição!")
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
    print("="*50)

