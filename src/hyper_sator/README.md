# Kayos Hyper-SATOR 6D (POC)

Este diretório contém uma prova de conceito do hipercubo SATOR em 6 dimensões.

Arquivos:
- `hyper_sator_6d.py`: implementação POC do hipercubo, extração de diagonais
  e checagens palindrômicas em projeções 2D selecionadas.
- `README.md`: este arquivo.

Como usar:

1. Rode o demo:

```bash
# a partir da raiz do repositório
.venv/bin/python scripts/hyper_sator_demo.py
```

O demo imprime a diagonal principal, a anti-diagonal e mostra três
projeções 5x5 (pares de eixos (0,1), (2,3), (4,5)), bem como se cada projeção
passa na checagem palindrômica (linhas/colunas/diagonais).

Observação: isto é uma prova de conceito com decisões pragmáticas para
verificação rápida. Podemos sofisticar a construção do hipercubo para
garantir propriedades adicionais (todas as projeções 2D SATOR, alinhamentos
entre faces, mapeamentos de verso/anverso, etc.) se você pedir.
