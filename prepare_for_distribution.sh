#!/bin/bash
# Script para preparar o projeto para distribuição
# Este script reorganiza a estrutura para que funcione como pacote instalável

set -e

echo "🔧 Preparando LiteVectorDB para distribuição..."

# Verifica se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Erro: Execute este script na raiz do projeto (onde está pyproject.toml)"
    exit 1
fi

# Cria a pasta do pacote se não existir
if [ ! -d "litevectordb" ]; then
    echo "📁 Criando pasta litevectordb/..."
    mkdir -p litevectordb
    
    # Move os arquivos do pacote
    echo "📦 Movendo arquivos do pacote..."
    [ -f "__init__.py" ] && mv __init__.py litevectordb/
    [ -f "client.py" ] && mv client.py litevectordb/
    [ -f "vector_store.py" ] && mv vector_store.py litevectordb/
    [ -f "memory.py" ] && mv memory.py litevectordb/
    [ -f "embeddings.py" ] && mv embeddings.py litevectordb/
    
    echo "✅ Estrutura reorganizada!"
else
    echo "⚠️  Pasta litevectordb/ já existe. Pulando reorganização."
fi

# Atualiza o pyproject.toml
echo "📝 Atualizando pyproject.toml..."
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "litevectordb"
version = "0.1.0"
description = "Banco de dados vetorial local, leve e simples. Sem servidor, sem complicação."
readme = "README.md"
requires-python = ">=3.9"
authors = [
    { name = "Seu Nome", email = "seuemail@example.com" }
]
license = { text = "MIT" }
keywords = ["vector", "database", "embeddings", "semantic-search", "sqlite", "chroma"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Database",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]

dependencies = [
    "numpy>=1.21.0",
]

[project.optional-dependencies]
api = [
    "fastapi>=0.100.0",
    "uvicorn[standard]>=0.23.0",
    "pydantic>=2.0.0",
]

[project.urls]
Homepage = "https://github.com/seuuser/litevectordb"
Documentation = "https://github.com/seuuser/litevectordb#readme"
Repository = "https://github.com/seuuser/litevectordb"
Issues = "https://github.com/seuuser/litevectordb/issues"

[tool.setuptools]
packages = ["litevectordb"]

[tool.setuptools.package-data]
litevectordb = ["py.typed"]
EOF

echo "✅ pyproject.toml atualizado!"

# Testa a instalação
echo ""
echo "🧪 Testando instalação..."
pip install -e . > /dev/null 2>&1 || {
    echo "⚠️  Instalação em modo desenvolvimento falhou. Verifique os erros acima."
    exit 1
}

echo "✅ Instalação OK!"

# Testa os imports
echo "🧪 Testando imports..."
python -c "from litevectordb import LocalVectorDB; print('✅ Imports OK!')" || {
    echo "❌ Erro nos imports!"
    exit 1
}

echo ""
echo "🎉 Projeto pronto para distribuição!"
echo ""
echo "Próximos passos:"
echo "  1. python -m build"
echo "  2. twine check dist/*"
echo "  3. twine upload dist/*"
echo ""

