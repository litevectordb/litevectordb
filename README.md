# LiteVectorDB

> **Banco de dados vetorial local, leve e simples. Sem servidor, sem complicação.**

## 🎯 Slogan e Descrição

**Slogan:** *"Vector Search, Zero Fuss"*

**Descrição curta:** LiteVectorDB é um banco de dados vetorial local construído sobre SQLite e NumPy. Perfeito para prototipagem rápida, aplicações desktop, e sistemas que precisam de busca semântica sem a complexidade de soluções enterprise.

---

## 📖 Por Que Existe / Missão do Projeto

### O Problema

A busca vetorial e bancos de dados semânticos estão se tornando essenciais para aplicações modernas de IA. No entanto, as soluções existentes frequentemente apresentam barreiras significativas:

- **Complexidade de setup**: Soluções como Chroma, Pinecone ou Weaviate requerem servidores dedicados, configuração de infraestrutura e dependências pesadas
- **Overhead desnecessário**: Para projetos pequenos, protótipos ou aplicações desktop, você não precisa de toda a infraestrutura de um banco vetorial distribuído
- **Dependências externas**: Muitas soluções dependem de serviços em nuvem ou APIs externas, limitando a portabilidade e privacidade
- **Curva de aprendizado**: Configuração e uso podem ser intimidantes para desenvolvedores que só querem adicionar busca semântica rapidamente

### A Missão

LiteVectorDB existe para democratizar o acesso à busca vetorial, oferecendo:

1. **Simplicidade**: Uma biblioteca Python que você instala e usa imediatamente, sem configuração complexa
2. **Portabilidade**: Um único arquivo SQLite que contém tudo - perfeito para distribuir com sua aplicação
3. **Privacidade**: Tudo roda localmente, sem necessidade de conexões externas ou serviços em nuvem
4. **Leveza**: Dependências mínimas (SQLite + NumPy), sem overhead de servidores ou infraestrutura
5. **Flexibilidade**: Interface simples para uso direto, mas também APIs de baixo nível para casos avançados

### Para Quem?

- **Desenvolvedores de protótipos** que precisam de busca semântica rápida sem setup complexo
- **Aplicações desktop** que precisam de memória vetorial local
- **Projetos educacionais** que querem entender como funciona busca vetorial na prática
- **Sistemas embarcados** ou edge computing que precisam de busca vetorial offline
- **Desenvolvedores que valorizam simplicidade** sobre features enterprise

---

## 🏗️ Arquitetura do Banco

### Visão Geral

LiteVectorDB utiliza uma arquitetura em camadas, construída sobre SQLite para persistência e NumPy para operações vetoriais:

```
┌────────────────────────────────────────────────────────┐
│                    Camada de Aplicação                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ LocalVectorDB│  │  MemoryDB    │  │  FastAPI     │  │
│  │  (Interface  │  │  (Memória    │  │  (API REST)  │  │
│  │   Simples)   │  │   de Sessão) │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
└─────────┼─────────────────┼─────────────────┼──────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────┐
│              Camada de Armazenamento                     │
│                    VectorStore                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │  • Gerenciamento de conexão SQLite               │    │
│  │  • Encode/Decode de vetores (BLOB)               │    │
│  │  • Operações CRUD (add, get, delete, upsert)     │    │
│  │  • Busca por similaridade de cosseno             │    │
│  └──────────────────────────────────────────────────┘    │
└───────────────────────────┬──────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│              Camada de Persistência                     │
│                    SQLite Database                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Tabela: documents                               │   │
│  │  ┌────┬─────┬─────────┬──────────┬───────┬─────┐ │   │
│  │  │ id │ key │ content │ metadata │ vector│ dim │ │   │
│  │  └────┴─────┴─────────┴──────────┴───────┴─────┘ │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Estrutura do Banco de Dados

A tabela `documents` armazena todos os dados vetoriais:

```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,              -- Chave opcional para upsert
    content TEXT,                 -- Texto original do documento
    metadata TEXT,                -- JSON com metadados adicionais
    vector BLOB NOT NULL,         -- Vetor de embedding (float32[])
    dim INTEGER NOT NULL,         -- Dimensão do vetor
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Componentes Principais

#### 1. **VectorStore** (`vector_store.py`)
- **Responsabilidade**: Camada de baixo nível para operações vetoriais
- **Funcionalidades**:
  - Armazenamento de vetores como BLOB no SQLite
  - Busca por similaridade de cosseno (em memória)
  - Operações CRUD completas (add, get, delete, upsert)
  - Gerenciamento de conexão SQLite com WAL mode

#### 2. **LocalVectorDB** (`client.py`)
- **Responsabilidade**: Interface de alto nível simplificada
- **Funcionalidades**:
  - Adicionar textos com geração automática de embeddings
  - Busca semântica com resultados tipados
  - Gerenciamento automático de metadados

#### 3. **MemoryDB** (`memory.py`)
- **Responsabilidade**: Sistema de memória por sessão
- **Funcionalidades**:
  - Armazenamento de memórias por `session_id`
  - Recuperação contextual de memórias relevantes
  - Filtragem automática por sessão

#### 4. **Embeddings** (`embeddings.py`)
- **Responsabilidade**: Geração de embeddings
- **Nota**: Inclui função `fake_embed` para testes. Em produção, substitua por OpenAI, Ollama, ou outro provedor.

### Algoritmo de Busca

A busca vetorial utiliza **similaridade de cosseno**:

1. **Normalização**: Cada vetor é normalizado (L2 norm)
2. **Cálculo de Similaridade**: `score = dot(query, vector) / (||query|| * ||vector||)`
3. **Filtragem**: Apenas resultados com `score >= min_score` são retornados
4. **Ordenação**: Resultados ordenados por score (decrescente)
5. **Top-K**: Retorna apenas os `top_k` melhores resultados

**Nota**: A busca atual é linear (O(n)) e funciona bem para até alguns milhares de vetores. Para datasets maiores, considere implementar índices como HNSW ou IVF.

---

## 🚀 Instalação

```bash
pip install litevectordb
```

Ou instale a partir do código:

```bash
git clone https://github.com/seuuser/litevectordb
cd litevectordb
pip install -e .
```

### Dependências

- Python >= 3.9
- numpy >= 1.21
- sqlite3 (incluído no Python padrão)

---

## 💻 Exemplos de Uso

### Exemplo 1: Uso Básico com LocalVectorDB

```python
from litevectordb import LocalVectorDB

# Inicializa o banco (cria arquivo litevectordb.db)
db = LocalVectorDB(path="meu_banco.db", dim=64)

# Adiciona documentos
textos = [
    "Python é uma linguagem de programação popular",
    "Machine Learning usa algoritmos para aprender padrões",
    "FastAPI é um framework web moderno para Python",
    "SQLite é um banco de dados embutido e leve"
]

ids = db.add_texts(
    texts=textos,
    metadatas=[
        {"categoria": "linguagem"},
        {"categoria": "IA"},
        {"categoria": "web"},
        {"categoria": "banco_dados"}
    ]
)

print(f"Documentos adicionados: {ids}")

# Busca semântica
query = "Quero aprender sobre desenvolvimento web"
resultados = db.similarity_search(query, top_k=2)

print("\nResultados da busca:")
for resultado in resultados:
    print(f"Score: {resultado.score:.4f}")
    print(f"Texto: {resultado.text}")
    print(f"Metadata: {resultado.metadata}")
    print("---")
```

### Exemplo 2: Uso Avançado com VectorStore

```python
from litevectordb.vector_store import VectorStore
from litevectordb.embeddings import fake_embed
import numpy as np

# Cria o store
store = VectorStore("avancado.db", dim=128)

# Adiciona documento com chave customizada
texto = "Este é um documento importante"
vetor = fake_embed(texto, dim=128)

doc_id = store.add(
    vector=vetor,
    content=texto,
    metadata={"autor": "João", "data": "2024-01-15"},
    key="doc_importante_001"
)

print(f"Documento inserido com ID: {doc_id}")

# Busca por chave
doc = store.get_by_key("doc_importante_001")
print(f"Documento encontrado: {doc['content']}")

# Upsert (atualiza se existe, cria se não existe)
novo_vetor = fake_embed("Texto atualizado", dim=128)
store.upsert(
    vector=novo_vetor,
    content="Texto atualizado",
    metadata={"autor": "João", "versao": 2},
    key="doc_importante_001"
)

# Busca vetorial
query_vec = fake_embed("documento importante", dim=128)
resultados = store.search(
    query_vector=query_vec,
    top_k=5,
    min_score=0.3
)

print(f"\nTotal de documentos: {store.count()}")

# Limpeza
store.close()
```

### Exemplo 3: Sistema de Memória por Sessão

```python
from litevectordb.memory import MemoryDB

# Inicializa o sistema de memória
memory = MemoryDB("memorias.db", dim=64)

# Armazena memórias de uma conversa
session_id = "chat_001"

memory.store_memory(
    session_id=session_id,
    role="user",
    content="Eu gosto de programar em Python e estudar IA"
)

memory.store_memory(
    session_id=session_id,
    role="assistant",
    content="Ótimo! Python é excelente para IA. Quer dicas sobre frameworks?"
)

memory.store_memory(
    session_id=session_id,
    role="user",
    content="Sim, me fale sobre FastAPI e PyTorch"
)

# Recupera memórias relevantes
query = "O que o usuário gosta de fazer?"
memorias = memory.retrieve_memory(
    session_id=session_id,
    query=query,
    top_k=3,
    min_score=0.2
)

print("Memórias relevantes:")
for mem in memorias:
    print(f"[{mem['metadata']['role']}] {mem['content']}")
    print(f"Score: {mem['score']:.4f}\n")

memory.close()
```

### Exemplo 4: Integração com Embeddings Reais

```python
from litevectordb import LocalVectorDB
import openai  # ou outro provedor

# Função customizada de embedding
def gerar_embedding(texto: str, dim: int = 1536) -> np.ndarray:
    response = openai.Embedding.create(
        input=texto,
        model="text-embedding-ada-002"
    )
    return np.array(response['data'][0]['embedding'], dtype=np.float32)

# Modifica o client para usar embeddings reais
class LocalVectorDBReal(LocalVectorDB):
    def add_texts(self, texts, metadatas=None, ids=None):
        metadatas = metadatas or [{} for _ in texts]
        inserted_ids = []
        
        for i, text in enumerate(texts):
            vec = gerar_embedding(text, dim=self.dim)
            doc_id = self._store.add(
                vector=vec,
                content=text,
                metadata=metadatas[i],
                key=ids[i] if ids else None
            )
            inserted_ids.append(doc_id)
        return inserted_ids
    
    def similarity_search(self, query, top_k=5, min_score=0.2):
        q_vec = gerar_embedding(query, dim=self.dim)
        raw_results = self._store.search(
            query_vector=q_vec,
            top_k=top_k,
            min_score=min_score
        )
        return [
            DocumentResult(
                id=r["id"],
                text=r["content"],
                metadata=r["metadata"],
                score=r["score"]
            )
            for r in raw_results
        ]

# Uso
db = LocalVectorDBReal(path="real_embeddings.db", dim=1536)
db.add_texts(["Exemplo com embeddings reais"])
resultados = db.similarity_search("busca semântica")
```

### Exemplo 5: API REST com FastAPI

```python
# Veja api/main.py para implementação completa
# Inicia o servidor:
# uvicorn api.main:app --reload

# Exemplo de uso da API:

import requests

BASE_URL = "http://localhost:8000"

# Armazenar memória
response = requests.post(f"{BASE_URL}/memory/store", json={
    "session_id": "sessao_001",
    "role": "user",
    "content": "Eu preciso aprender sobre vetores",
    "metadata": {"topico": "matematica"}
})

# Buscar memórias
response = requests.post(f"{BASE_URL}/memory/query", json={
    "session_id": "sessao_001",
    "query": "O que eu quero aprender?",
    "top_k": 3
})

print(response.json())

# Estatísticas
response = requests.get(f"{BASE_URL}/stats")
print(response.json())
```

### Exemplo 6: Sistema de Recomendação Simples

```python
from litevectordb import LocalVectorDB
import numpy as np

db = LocalVectorDB("recomendacoes.db", dim=64)

# Adiciona produtos
produtos = [
    "Notebook Dell com 16GB RAM e SSD 512GB",
    "Mouse sem fio Logitech MX Master 3",
    "Teclado mecânico RGB com switches Cherry",
    "Monitor 4K 27 polegadas para design",
    "Webcam Full HD para streaming"
]

db.add_texts(
    texts=produtos,
    metadatas=[
        {"tipo": "computador", "preco": 3500},
        {"tipo": "periferico", "preco": 450},
        {"tipo": "periferico", "preco": 600},
        {"tipo": "monitor", "preco": 2000},
        {"tipo": "periferico", "preco": 300}
    ]
)

# Busca produtos similares
query = "Preciso de um mouse bom para trabalho"
resultados = db.similarity_search(query, top_k=3)

print("Produtos recomendados:")
for r in resultados:
    print(f"{r.text} (R$ {r.metadata['preco']}) - Score: {r.score:.3f}")
```

---

## 📊 Limitações e Considerações

### Performance

- **Busca Linear**: A busca atual é O(n) e funciona bem para até ~10.000 documentos
- **Em Memória**: Todos os vetores são carregados em memória durante a busca
- **Sem Índices**: Não há índices vetoriais (HNSW, IVF) para otimização

### Escalabilidade

Para datasets maiores (>50k documentos), considere:
- Implementar índices vetoriais (HNSW via `hnswlib`)
- Usar busca aproximada (ANN)
- Particionar dados em múltiplos bancos

### Embeddings

- A função `fake_embed` é apenas para testes/demos
- Em produção, use embeddings reais (OpenAI, Sentence Transformers, etc.)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Abrir issues para bugs ou sugestões
2. Fazer fork e criar pull requests
3. Melhorar a documentação
4. Adicionar novos exemplos

---

## 📝 Licença

MIT License - veja o arquivo LICENSE para detalhes.

---

## 🔗 Links Úteis

- [Documentação SQLite](https://www.sqlite.org/docs.html)
- [NumPy Documentation](https://numpy.org/doc/)
- [Vector Search Concepts](https://www.pinecone.io/learn/vector-database/)

---

**Desenvolvido com ❤️ para a comunidade Python**

