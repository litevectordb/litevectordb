# 📦 Guia de Distribuição do LiteVectorDB

Este guia explica como preparar e distribuir o LiteVectorDB como biblioteca Python no PyPI.

## 🎯 Estrutura Necessária

Para distribuir como pacote, a estrutura deve ser:

```
LiteVectorDB/                    # Diretório do projeto
├── litevectordb/              # ⚠️ Pasta do pacote (nome deve ser "litevectordb")
│   ├── __init__.py
│   ├── client.py
│   ├── vector_store.py
│   ├── memory.py
│   └── embeddings.py
├── api/                         # Exemplos (não será instalado)
├── examples/                    # Exemplos (não será instalado)
├── pyproject.toml
├── README.md
├── MANIFEST.in
└── setup.py
```

## 🚀 Preparação Rápida (Automática)

Execute o script de preparação:

```bash
cd LiteVectorDB
./prepare_for_distribution.sh
```

Este script:
1. Cria a pasta `litevectordb/` se não existir
2. Move os arquivos do pacote para a pasta correta
3. Atualiza o `pyproject.toml`
4. Testa a instalação

## 🔧 Preparação Manual

Se preferir fazer manualmente:

### 1. Criar estrutura do pacote

```bash
mkdir litevectordb
mv __init__.py client.py vector_store.py memory.py embeddings.py litevectordb/
```

### 2. Verificar pyproject.toml

O `pyproject.toml` deve ter:

```toml
[tool.setuptools]
packages = ["litevectordb"]
```

### 3. Testar instalação local

```bash
pip install -e .
python -c "from litevectordb import LocalVectorDB; print('OK!')"
```

## 📤 Construir e Publicar

### 1. Instalar ferramentas

```bash
pip install build twine
```

### 2. Construir pacote

```bash
python -m build
```

Isso cria:
- `dist/litevectordb-0.1.0.tar.gz`
- `dist/litevectordb-0.1.0-py3-none-any.whl`

### 3. Verificar pacote

```bash
twine check dist/*
```

### 4. Publicar no Test PyPI (recomendado primeiro)

```bash
# Criar conta em https://test.pypi.org/
# Criar API token
twine upload --repository testpypi dist/*
```

### 5. Testar instalação do Test PyPI

```bash
pip install -i https://test.pypi.org/simple/ litevectordb
```

### 6. Publicar no PyPI oficial

```bash
# Criar conta em https://pypi.org/
# Criar API token
twine upload dist/*
```

## 📥 Como os Usuários Instalam

Após publicar, os usuários podem instalar com:

```bash
# Instalação básica
pip install litevectordb

# Com dependências opcionais da API
pip install litevectordb[api]
```

## ✅ Checklist Antes de Publicar

- [ ] Estrutura de pastas correta (`litevectordb/` existe)
- [ ] Versão atualizada no `pyproject.toml` e `__init__.py`
- [ ] README.md completo e atualizado
- [ ] Todos os imports testados
- [ ] `python -m build` executado com sucesso
- [ ] `twine check dist/*` sem erros
- [ ] Testado instalação do wheel gerado
- [ ] Testado no Test PyPI antes de publicar oficialmente

## 🔍 Verificação Pós-Instalação

Após instalar, teste:

```python
from litevectordb import LocalVectorDB, VectorStore, MemoryDB
from litevectordb.embeddings import fake_embed

# Teste básico
db = LocalVectorDB(path="test.db", dim=64)
db.add_texts(["Teste"])
resultados = db.similarity_search("teste")
print("✅ Funcionando!")
```

## 📝 Notas Importantes

1. **Nome do pacote**: Deve ser `litevectordb` (minúsculo, sem espaços)
2. **Versão**: Atualize antes de cada release
3. **Pasta api/**: Não será instalada (não está em `packages`)
4. **Imports**: Todos devem usar `from litevectordb import ...`

## 🐛 Troubleshooting

### Erro: "No module named 'litevectordb'"

- Verifique se a pasta `litevectordb/` existe
- Verifique se `__init__.py` está dentro de `litevectordb/`
- Execute `pip install -e .` novamente

### Erro ao construir: "package not found"

- Verifique se `packages = ["litevectordb"]` está no `pyproject.toml`
- Verifique se a pasta `litevectordb/` contém os arquivos `.py`

### Imports não funcionam após instalação

- Verifique se o `__init__.py` exporta as classes corretas
- Teste: `python -c "import litevectordb; print(litevectordb.__version__)"`

