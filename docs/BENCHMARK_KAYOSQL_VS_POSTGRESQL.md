# Benchmark Real: KayosQL vs PostgreSQL

**Data**: Dezembro 2025 
**Versão KayosQL**: 7.0.0 (Rust) 
**Versão PostgreSQL**: 16.10

---

## Resultados do Benchmark

### Escala: 1,000 registros

| Operação | KayosQL (ops/s) | PostgreSQL (ops/s) | Vencedor | Fator |
|----------|-----------------|--------------------|-----------| ------|
| INSERT | 2,434 | 1,359 | **KayosQL** | 1.8x |
| SELECT * | 2,154,359 | 3,378,935 | PostgreSQL | 1.6x |
| SELECT WHERE | 3,156 | 34,399 | PostgreSQL | 10.9x |
| UPDATE | 1,104 | 1,356 | PostgreSQL | 1.2x |

### Escala: 10,000 registros

| Operação | KayosQL (ops/s) | PostgreSQL (ops/s) | Vencedor | Fator |
|----------|-----------------|--------------------|-----------| ------|
| INSERT | 549 | 1,087 | PostgreSQL | 2.0x |
| SELECT * | 2,088,577 | 3,378,935 | PostgreSQL | 1.6x |
| SELECT WHERE | 289 | 34,399 | PostgreSQL | 119x |
| UPDATE | 133 | 1,220 | PostgreSQL | 9.2x |

---

## Análise Honesta

### Onde KayosQL é competitivo:

1. **INSERT em escala pequena (1k)** - 1.8x mais rápido
 - Auto-criação de índice B+Tree eficiente
 - WAL otimizado para poucos registros

### Onde PostgreSQL é superior:

1. **SELECT WHERE com índice** - 10-119x mais rápido
 - B-Tree do PostgreSQL tem décadas de otimização
 - Query optimizer maduro

2. **UPDATE** - 1.2-9x mais rápido
 - MVCC otimizado
 - HOT updates (Heap-Only Tuples)

3. **Escalabilidade** - PostgreSQL mantém performance, KayosQL degrada
 - KayosQL: INSERT cai de 2,434 → 549 ops/s (4.4x pior)
 - PostgreSQL: INSERT cai de 1,359 → 1,087 ops/s (1.25x pior)

---

## Limitações do Type System KayosQL

### Problema Identificado

KayosQL é **mais rígido** que PostgreSQL em tipos:

```sql
-- PostgreSQL aceita:
CREATE TABLE t (salary REAL);
INSERT INTO t VALUES (75000); -- INTEGER → REAL implícito 

-- KayosQL rejeita:
CREATE TABLE t (salary REAL);
INSERT INTO t VALUES (75000); -- AXIOMA 1 VIOLADO: Tipo incompatível
```

### Solução

Usar tipos explícitos:
```sql
-- KayosQL correto:
CREATE TABLE t (salary INTEGER); -- ou
INSERT INTO t VALUES (75000.0); -- valor como REAL explícito
```

### Tipos Suportados

| Tipo | KayosQL | PostgreSQL |
|------|---------|------------|
| INTEGER | | |
| REAL | (strict) | (coercion) |
| TEXT | | |
| BOOLEAN | | |
| TIMESTAMP | | |
| NULL | | |
| ARRAY | ️ Limitado | |
| JSON | | |
| UUID | | |

---

## Conclusões

### Afirmações Corrigidas

| Claim Original | Realidade |
|----------------|-----------|
| "1000x mais rápido" | **FALSO** - PostgreSQL é mais rápido na maioria dos casos |
| "Superior em tudo" | **FALSO** - KayosQL só é melhor em INSERT pequeno |
| "Substitui PostgreSQL" | **FALSO** - PostgreSQL é mais maduro e escalável |

### Quando usar KayosQL

 **Casos apropriados:**
- Protótipos e desenvolvimento
- Aplicações embarcadas sem servidor de banco
- Cache layer com SQL interface
- Projetos que precisam de banco proprietário

 **Casos NÃO apropriados:**
- Produção com alta carga
- Dados críticos que precisam de ACID robusto
- Queries complexas com JOINs
- Escalabilidade horizontal

---

## Metodologia do Benchmark

```
Hardware: Linux x86_64
Operações testadas:
 - INSERT: 1000/10000 registros sequenciais
 - SELECT *: 10 iterações com fetchall
 - SELECT WHERE: 100 queries com índice
 - UPDATE: 100 updates com WHERE

Ambos os bancos usaram índice no campo PRIMARY KEY.
```

---

## Arquivos de Benchmark

- `benchmarks/benchmark_simple.py` - Benchmark simplificado
- `benchmarks/benchmark_separated.py` - Versão com subprocess
- `benchmarks/benchmark_results.json` - Resultados em JSON
