# Estrutura do Pacote para Distribuição

## ⚠️ Importante: Nome do Pacote

Para que o pacote funcione corretamente quando instalado via `pip install litevectordb`, a estrutura de pastas deve ser:

```
LiteVectorDB/                    # Diretório do projeto (pode ter qualquer nome)
├── litevectordb/               # ⚠️ DEVE se chamar "litevectordb" (minúsculo)
│   ├── __init__.py
│   ├── client.py
│   ├── vector_store.py
│   ├── memory.py
│   └── embeddings.py
├── pyproject.toml
├── README.md
├── MANIFEST.in
└── setup.py
```

## 🔧 Opção 1: Reorganizar a Estrutura (Recomendado)

Se os arquivos estão diretamente em `LiteVectorDB/`, você precisa criar uma subpasta:

```bash
# Na raiz do projeto
cd LiteVectorDB
mkdir litevectordb
mv __init__.py client.py vector_store.py memory.py embeddings.py litevectordb/
```

Depois ajuste o `pyproject.toml`:

```toml
[tool.setuptools]
packages = ["litevectordb"]
```

## 🔧 Opção 2: Manter Estrutura Atual (Alternativa)

Se preferir manter os arquivos na raiz de `LiteVectorDB/`, ajuste o `pyproject.toml`:

```toml
[tool.setuptools]
packages = { find = { where = ".", include = ["*"] } }
package-dir = { "" = "." }
```

E renomeie a pasta `LiteVectorDB/` para `litevectordb/` OU ajuste os imports.

## ✅ Verificação

Após ajustar, teste:

```bash
# Instalação em modo desenvolvimento
pip install -e .

# Teste os imports
python -c "from litevectordb import LocalVectorDB; print('OK!')"

# Execute o script de teste
python test_install.py
```

## 📝 Notas

- O nome no `pyproject.toml` (`name = "litevectordb"`) deve corresponder ao nome da pasta do pacote
- Os imports nos exemplos devem usar `from litevectordb import ...`
- A pasta `api/` e `examples/` podem ficar fora do pacote (não serão instalados)

