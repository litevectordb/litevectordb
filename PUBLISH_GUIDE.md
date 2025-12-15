# 🚀 Guia de Publicação no PyPI

## ✅ Status Atual

- ✅ Pacote construído com sucesso
- ✅ Arquivos verificados e validados
- ✅ Pronto para publicação

**Arquivos gerados:**
- `dist/litevectordb-0.1.0-py3-none-any.whl` (12KB)
- `dist/litevectordb-0.1.0.tar.gz` (16KB)

---

## 📋 Passo a Passo para Publicar

### 1️⃣ Preparação (Já feito ✅)

```bash
# Instalar ferramentas (já feito)
pip install --upgrade build twine

# Construir pacote (já feito)
python -m build

# Verificar pacote (já feito)
python -m twine check dist/*
```

---

### 2️⃣ Testar no Test PyPI (RECOMENDADO)

Antes de publicar no PyPI real, teste no Test PyPI:

#### 2.1. Criar conta no Test PyPI
1. Acesse: https://test.pypi.org/account/register/
2. Crie uma conta (pode ser diferente do PyPI real)
3. Verifique seu email

#### 2.2. Criar API Token
1. Vá em: https://test.pypi.org/manage/account/#api-tokens
2. Crie um token com escopo "Entire account"
3. Copie o token (formato: `pypi-xxxxx`)

#### 2.3. Configurar credenciais (uma das opções)

**Opção A: Arquivo ~/.pypirc**
```bash
# Criar/editar ~/.pypirc
nano ~/.pypirc
```

Adicione:
```ini
[pypi]
username = __token__
password = pypi-SEU_TOKEN_AQUI

[testpypi]
username = __token__
password = pypi-SEU_TOKEN_TEST_AQUI
```

**Opção B: Variáveis de ambiente**
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-SEU_TOKEN_AQUI
```

**Opção C: Passar no comando (menos seguro)**
```bash
python -m twine upload --repository testpypi dist/* \
  --username __token__ \
  --password pypi-SEU_TOKEN_AQUI
```

#### 2.4. Upload no Test PyPI
```bash
python -m twine upload --repository testpypi dist/*
```

#### 2.5. Testar instalação do Test PyPI
```bash
pip install --index-url https://test.pypi.org/simple/ litevectordb
```

---

### 3️⃣ Publicar no PyPI Real

Depois de testar, publique no PyPI real:

#### 3.1. Criar conta no PyPI (se ainda não tem)
1. Acesse: https://pypi.org/account/register/
2. Crie uma conta
3. Verifique seu email

#### 3.2. Criar API Token
1. Vá em: https://pypi.org/manage/account/#api-tokens
2. Crie um token com escopo "Entire account"
3. Copie o token

#### 3.3. Upload no PyPI
```bash
# Se configurou ~/.pypirc:
python -m twine upload dist/*

# Ou especifique credenciais:
python -m twine upload dist/* \
  --username __token__ \
  --password pypi-SEU_TOKEN_AQUI
```

---

### 4️⃣ Verificar Publicação

Após o upload:

1. Verifique a página do pacote:
   - Test PyPI: https://test.pypi.org/project/litevectordb/
   - PyPI Real: https://pypi.org/project/litevectordb/

2. Teste a instalação:
   ```bash
   pip install litevectordb
   ```

3. Teste os imports:
   ```python
   from litevectordb import LocalVectorDB
   print("✅ Instalado com sucesso!")
   ```

---

## ⚠️ Comandos Rápidos (Copy & Paste)

### Testar no Test PyPI:
```bash
python -m twine upload --repository testpypi dist/* --username __token__ --password pypi-SEU_TOKEN_AQUI
```

### Publicar no PyPI Real:
```bash
python -m twine upload dist/* --username __token__ --password pypi-SEU_TOKEN_AQUI
```

---

## 🔄 Para Atualizar uma Versão

1. Atualize a versão em `pyproject.toml`:
   ```toml
   version = "0.1.1"
   ```

2. Atualize a versão em `litevectordb/__init__.py`:
   ```python
   __version__ = "0.1.1"
   ```

3. Reconstrua e publique:
   ```bash
   rm -rf dist build *.egg-info
   python -m build
   python -m twine check dist/*
   python -m twine upload dist/*
   ```

---

## 📝 Checklist Antes de Publicar

- [x] Estrutura do pacote correta (`litevectordb/` subdiretório)
- [x] Arquivo LICENSE criado
- [x] `pyproject.toml` configurado corretamente
- [x] README.md completo e formatado
- [x] Versão definida corretamente
- [x] Dependências listadas
- [x] Build executado com sucesso
- [x] Verificação com twine passou
- [ ] Conta no PyPI/Test PyPI criada
- [ ] Token de API criado
- [ ] Teste no Test PyPI feito (recomendado)

---

## 🆘 Troubleshooting

### Erro: "Package already exists"
- Versão já existe no PyPI
- Solução: Atualize a versão no `pyproject.toml`

### Erro: "Invalid credentials"
- Token incorreto ou expirado
- Solução: Crie um novo token

### Erro: "File already exists"
- Arquivo já foi enviado
- Solução: Remova `dist/` e reconstrua com nova versão

---

## 🎉 Pronto!

Após publicar, seu pacote estará disponível em:
- `pip install litevectordb`
- `https://pypi.org/project/litevectordb/`

