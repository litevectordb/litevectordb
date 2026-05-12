# LiteVectorDB Smoke Test Project

Projeto minimo para validar a versao `0.3.0` do LiteVectorDB usando o pacote local.

## Rodar

Na raiz do repositorio:

```bash
PYTHONPATH=. python3 sample_projects/litevectordb_smoke_test/run_demo.py
```

O script cria um banco temporario, adiciona documentos, executa busca com filtro por metadata, faz upsert por chave e valida memoria por sessao com `MemoryDB`.
