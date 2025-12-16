# KayosCryptoSuite v2

Sistema modular de licenciamento e validação criptográfica.

## Estrutura
- `core/`: Criptografia, assinatura e licenças
- `infrastructure/`: Banco de dados, modelos, logging
- `sync/`: Comunicação remota e heartbeat
- `vigil_api/`: API REST
- `tests/`: Testes unitários

## Rodando localmente

```bash
docker-compose up --build
