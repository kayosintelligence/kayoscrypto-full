# KayosCrypto × a16z — Playbook da Reunião (45 min)

**Data alvo:** 26-30/nov/2025  
**Objetivo:** Conduzir walkthrough técnico/comercial e alinhar próximos passos de due diligence com o time American Dynamism (liderado por Katherine Boyle).

---

## 0‑10 min — Tese & Diferencial
- Ancorar em `docs/business/EXECUTIVE_SUMMARY_A16Z.md` (seções 1, 3 e 6).
- Mensagem-chave: *randomness soberana totalmente em software*, Fishbone Architecture (Fibonacci → Ezekiel → Core) + MPC-N.
- Destaques rápidos: 1 TB/dia, 47,80% avalanche, 100% reversível, compatível com finalistas NIST PQC.

## 10‑25 min — Validação Técnica
- Guiar usando `reports/TECHNICAL_SUMMARY.md` + logs `practrand_logs/*.log`.
- Mostrar timeline do PractRand (64G→1T) e como o MPC-N rastreou interrupções (DIAGNOSTICS_MPCN_GUARD...).
- Explicar garantias: reversibilidade, ausência de hardware proprietário, integração com KayosCryptoUltimate.
- Se necessário, abrir `docs/cc/THREAT_MODEL_FISHBONE.md` para STRIDE + mitigação.

## 25‑35 min — Roadmap Comercial & TAM
- Referenciar seção 4 do executive summary (Milestones) e `ROADMAP_ALTO_RISCO.md`.
- Cobrir:
  - Certification Sprint (ISO/FIPS)
  - Quantum Resistance Manager (Rib 4)
  - Pilotos enterprise (firmware, supply chain)
  - TAM inicial (defesa/espacial + fed)
- Articular pedidas: apoio certificações + GTM defense-first.

## 35‑45 min — Q&A & Próximos Passos
- Reforçar pacote entregue: `artifacts/outbound/a16z/...` (tar.gz + sha + assinatura).
- Alinhar follow-ups:
  1. Envio oficial do bundle e confirmação de recebimento.
  2. Deep dive PQC (10 dias após call).
  3. Planejamento de pilotos (cliente âncora) pré-Series Seed.

---

## Materiais na mesa
| Item | Caminho | Uso |
|------|---------|-----|
| Pitch | `docs/business/EXECUTIVE_SUMMARY_A16Z.md` | Narrativa principal |
| Validação | `reports/TECHNICAL_SUMMARY.md` | Snapshot 1TB + compliance |
| Logs | `practrand_logs/*` | Prova bruta (raw + whitened) |
| Políticas | `docs/policies/*.md` | Governança/ISO |
| Bundle | `artifacts/outbound/a16z/...` | Arquivos enviados |
| Demo | `src/kayoscrypto/core/emulator.py` | Entropia ao vivo |

---

## Checklist de Operação
- [x] Bundle assinado pronto (tar + sha + signature).
- [x] Evento MPC-N `packaging.bundle:dispatched` registrado.
- [ ] Slides/whiteboard com Fishbone & MPC-N (opcional).
- [ ] Conferir disponibilidade dos participantes (incluir especialista PQC a16z?).
- [ ] Testar comando da demo 5 min antes da call.

> *Obs.:* Para anexar slides ou screenshots, utilize a pasta `docs/business/meeting-assets/` (a criar) e referencie aqui.
