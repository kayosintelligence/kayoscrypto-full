# KayosQL - Banco de Dados Proprietário

## Visão Geral

**KayosQL** é o banco de dados **100% proprietário** do ecossistema KAYOS. Foi projetado para ser uma alternativa sem dependências externas (SQLite, PostgreSQL, MongoDB) para casos de uso específicos dentro do KayosCrypto.

### Características Principais

- **100% Proprietário** - Zero dependências de bancos externos
- **API Simples** - Interface Python intuitiva
- **Geo-espacial Nativo** - Indexação por coordenadas geográficas
- **Quantum Tunnels** - Acesso remoto via túneis quânticos
- **Thread-safe** - Operações concorrentes seguras
- **Integração KayosCrypto** - Funciona nativamente no ecossistema

### ️ Limitações (seja honesto)

- Sem SQL complexo (JOINs, subqueries)
- ACID parcial (não equivalente a PostgreSQL)
- Escala limitada (otimizado para < 100K registros)
- Persistência via JSON (I/O não otimizado)

### Quando Usar

| Use KayosQL | Use PostgreSQL |
|-------------|----------------|
| Projetos pequenos/médios | Dados críticos |
| Zero dependências é prioridade | SQL complexo necessário |
| Cache/dados temporários | Alta concorrência |
| Integração KayosCrypto | Compliance/auditoria |

## Instalação

O KayosQL já está incluído no KayosCrypto. Não requer instalação adicional.

```python
from src.database.kayosql import KayosQL
```

## Uso Básico

### Inicialização

```python
from src.database.kayosql import KayosQL

# Instância padrão (singleton)
db = KayosQL()

# Ou com configurações personalizadas
db = KayosQL(
 data_path="meus_dados/kayosql",
 enable_quantum_tunnels=True,
 enable_geo_spatial=True
)
```

### Operações CRUD

```python
# CREATE (Store)
db.store('user:123', {
 'nome': 'João Silva',
 'email': 'joao@exemplo.com',
 'idade': 30
})

# READ (Retrieve)
user = db.retrieve('user:123')
print(user) # {'nome': 'João Silva', 'email': 'joao@exemplo.com', 'idade': 30}

# UPDATE (Store com mesma chave)
db.store('user:123', {
 'nome': 'João Silva',
 'email': 'joao.novo@exemplo.com', # Atualizado
 'idade': 31 # Atualizado
})

# DELETE
db.delete('user:123')

# EXISTS
if db.exists('user:123'):
 print("Usuário existe")
```

### Operações em Batch

```python
# Store múltiplos itens
items = [
 ('produto:1', {'nome': 'Laptop', 'preco': 2500}),
 ('produto:2', {'nome': 'Mouse', 'preco': 150}),
 ('produto:3', {'nome': 'Teclado', 'preco': 300}),
]
results = db.store_batch(items)
print(results) # {'produto:1': True, 'produto:2': True, 'produto:3': True}

# Retrieve múltiplos itens
dados = db.retrieve_batch(['produto:1', 'produto:2', 'produto:3'])
print(dados)
```

### Funções de Conveniência

```python
from src.database.kayosql import quick_store, quick_retrieve, get_kayosql

# Armazenamento rápido
quick_store('config:app', {'debug': True, 'version': '1.0'})

# Recuperação rápida
config = quick_retrieve('config:app')

# Acesso à instância singleton
db = get_kayosql()
```

## Recursos Avançados

### Armazenamento Geo-espacial

```python
# Armazenar com coordenadas
db.store_at_coordinates(
 'sensor:temp:001',
 {'temperatura': 25.5, 'umidade': 60},
 lat=-23.5505, # São Paulo
 lon=-46.6333,
 alt=760.0 # metros
)

# Buscar por proximidade
sensores_proximos = db.query_by_coordinates(
 lat=-23.5505,
 lon=-46.6333,
 radius_km=10.0 # 10km de raio
)
```

### Quantum Tunnels

```python
# Criar túnel quântico para acesso remoto
db.create_tunnel(
 'tunnel:servidor-remoto',
 'api.servidor.com',
 {'encryption': 'quantum', 'latency': 'zero'}
)

# Acessar dados via túnel
dados = db.access_via_tunnel('tunnel:servidor-remoto', 'dados:importantes')
```

### Estatísticas

```python
stats = db.get_stats()
print(f"Total de stores: {stats['total_stores']}")
print(f"Total de retrieves: {stats['total_retrieves']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Sistema: {stats['system']['type']}") # KayosQL Proprietário
print(f"Dependências: {stats['system']['dependencies']}") # ZERO
```

## Tipos de Dados Suportados

O KayosQL suporta automaticamente:

| Tipo | Exemplo | Armazenamento |
|------|---------|---------------|
| `dict` | `{'key': 'value'}` | JSON automático |
| `str` | `"texto"` | UTF-8 |
| `bytes` | `b'\x00\x01'` | Binário direto |
| `int` | `42` | Via dict |
| `float` | `3.14` | Via dict |
| `list` | `[1, 2, 3]` | Via dict |

## Arquitetura Interna

```
KayosQL (API Unificada)
 │
 ├── KayosQLNativeStorage
 │ └── Armazenamento .kdb (JSON otimizado)
 │
 ├── KayosQLStorageBackend 
 │ └── Indexação geo-espacial
 │
 └── OptimizedQuantumTunnelManager
 └── Túneis quânticos para acesso remoto
```

## Performance (Dados Reais)

️ **Nota:** Benchmarks dependem muito do cenário. Estes são dados reais do ambiente de desenvolvimento.

### KayosQL (Python + JSON I/O)

| Operação | Tempo/Op | Ops/Segundo |
|----------|----------|-------------|
| INSERT | ~3.5 ms | ~288 ops/s |
| SELECT | ~7.4 ms | ~135 ops/s |

### Contexto Importante

- KayosQL persiste em JSON a cada operação (impacto de I/O)
- In-memory puro seria muito mais rápido (~2M ops/s)
- PostgreSQL é otimizado para I/O com WAL e buffers
- Comparação "justa" requer mesmo tipo de persistência

### Quando KayosQL é Mais Rápido

- Operações 100% in-memory (sem persistir)
- Datasets pequenos (< 10K registros)
- Queries simples por chave

### Quando PostgreSQL é Mais Rápido

- Datasets grandes (> 100K registros)
- Queries SQL complexas
- Alta concorrência
- Persistência otimizada

**Veja:** `docs/KAYOSQL_HONEST_ANALYSIS.md` para análise completa.

## Integração com KayosCrypto

```python
from src.core.kayoscrypto_ultimate import KayosCryptoUltimate
from src.database.kayosql import KayosQL

# Inicializar sistemas
crypto = KayosCryptoUltimate()
db = KayosQL()

# Criptografar e armazenar
dados_sensiveis = {'cpf': '123.456.789-00', 'senha': 'super_secreta'}
dados_json = json.dumps(dados_sensiveis).encode()
encrypted = crypto.encrypt(dados_json, 'minha_senha_mestre')

# Armazenar dados criptografados
db.store('usuario:dados_sensiveis', encrypted)

# Recuperar e descriptografar
encrypted_retrieved = db.retrieve('usuario:dados_sensiveis')
decrypted = crypto.decrypt(encrypted_retrieved, 'minha_senha_mestre')
dados_originais = json.loads(decrypted)
```

## Migração de Outros Bancos

### De SQLite

```python
import sqlite3
from src.database.kayosql import KayosQL

# Ler do SQLite
conn = sqlite3.connect('antigo.db')
cursor = conn.execute('SELECT id, data FROM tabela')

# Migrar para KayosQL
db = KayosQL()
for row in cursor:
 db.store(f'migrado:{row[0]}', row[1])
```

### De PostgreSQL

```python
import psycopg2
from src.database.kayosql import KayosQL

# Ler do PostgreSQL
conn = psycopg2.connect('postgresql://...')
cursor = conn.cursor()
cursor.execute('SELECT id, data FROM tabela')

# Migrar para KayosQL
db = KayosQL()
for row in cursor.fetchall():
 db.store(f'migrado:{row[0]}', row[1])
```

## Troubleshooting

### Erro: "KayosQL não disponível"

```python
from src.database.kayosql import KAYOSQL_AVAILABLE

if not KAYOSQL_AVAILABLE:
 print("Verifique se os módulos estão no path correto")
```

### Dados não persistindo

```python
# Verifique se o diretório existe
db = KayosQL(data_path="/caminho/existente/kayosql")
```

### Performance lenta

```python
# Use batch para operações em massa
db.store_batch([(f'key:{i}', data) for i in range(1000)])
```

## Arquivos

- `api.py` - API unificada principal
- `native_storage.py` - Storage nativo .kdb
- `storage_backend.py` - Backend geo-espacial
- `quantum_tunnels.py` - Túneis quânticos
- `enterprise_integration.py` - Integração enterprise

## Licença

KayosQL é parte do ecossistema KAYOS e está sob a mesma licença do KayosCrypto.

---

**KayosQL - Alternativa Proprietária para o Ecossistema KAYOS** 

*Para análise técnica completa, consulte: `docs/KAYOSQL_HONEST_ANALYSIS.md`*
