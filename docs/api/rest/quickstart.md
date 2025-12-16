# KayosCrypto REST API Quickstart

1. **Authenticate**
   - Obtain an API token via the enterprise console.
2. **Health Check**
   - `GET /v1/entropy/health` → expect `{ "status": "ok" }`.
3. **Request Entropy**
   - `POST /v1/entropy/stream` with payload `{ "bytes": 1024 }` (endpoint TBD).
4. **Validate Response**
   - Verify response metadata includes SATOR telemetry snapshot.

> _Nota:_ Documento inicial; atualizar após definir contratos definitivos.
