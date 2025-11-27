# Como Instalar e Distribuir o LiteVectorDB

## 📦 Instalação Local (Desenvolvimento)

Para instalar o pacote localmente em modo de desenvolvimento:

```bash
# Na raiz do projeto
pip install -e .
```

Isso permite que você edite o código e as mudanças sejam refletidas imediatamente.

## 🚀 Construir o Pacote para Distribuição

### 1. Instalar ferramentas de build

```bash
pip install build twine
```

### 2. Construir os arquivos de distribuição

```bash
# Na raiz do projeto (onde está o pyproject.toml)
python -m build
```

Isso criará:
- `dist/litevectordb-0.1.0.tar.gz` (source distribution)
- `dist/litevectordb-0.1.0-py3-none-any.whl` (wheel)

### 3. Verificar o pacote

```bash
# Verifica se o pacote está correto
twine check dist/*
```

## 📤 Publicar no PyPI

### Test PyPI (recomendado primeiro)

```bash
# 1. Criar conta em https://test.pypi.org/account/register/
# 2. Criar API token em https://test.pypi.org/manage/account/token/

# 3. Fazer upload
twine upload --repository testpypi dist/*
```

### PyPI Oficial

```bash
# 1. Criar conta em https://pypi.org/account/register/
# 2. Criar API token em https://pypi.org/manage/account/token/

# 3. Fazer upload
twine upload dist/*
```

## 📥 Instalação pelos Usuários

Após publicar, os usuários podem instalar com:

```bash
# Instalação básica
pip install litevectordb

# Com dependências opcionais da API
pip install litevectordb[api]
```

## 🔧 Estrutura do Projeto

```
LiteVectorDB/
├── litevectordb/          # Pacote principal (deve ter este nome)
│   ├── __init__.py         # Exports principais
│   ├── client.py           # LocalVectorDB
│   ├── vector_store.py     # VectorStore
│   ├── memory.py           # MemoryDB
│   └── embeddings.py       # fake_embed
├── pyproject.toml          # Configuração do pacote
├── README.md               # Documentação
├── MANIFEST.in             # Arquivos a incluir
└── setup.py                # Compatibilidade (opcional)
```

## ⚠️ Importante

1. **Nome do pacote**: O nome no `pyproject.toml` (`litevectordb`) deve corresponder ao nome da pasta do pacote
2. **Versão**: Atualize a versão no `pyproject.toml` e `__init__.py` antes de cada release
3. **Testes**: Teste a instalação localmente antes de publicar:
   ```bash
   pip install dist/litevectordb-0.1.0-py3-none-any.whl
   python -c "from litevectordb import LocalVectorDB; print('OK!')"
   ```

## 📝 Checklist antes de publicar

- [ ] Versão atualizada no `pyproject.toml` e `__init__.py`
- [ ] README.md completo e atualizado
- [ ] Todos os imports funcionando
- [ ] Testes básicos passando
- [ ] `python -m build` executado com sucesso
- [ ] `twine check dist/*` sem erros
- [ ] Testado instalação local do wheel gerado

