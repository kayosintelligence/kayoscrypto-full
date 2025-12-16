# TASK 10.4 – Statistical Battery Progress (22 Nov 2025)

##  Scope
- Consolidate all entropy-quality work completed today (PractRand ≥32 GB, Dieharder full battery, BigCrush pipeline kick-off) using the ChaCha20-whitened stream derived from `kayos_entropy_stream.bin`.
- Record commands, artefacts, and interpretation of every WEAK classification to comply with GLASSÉ Safety/Security audit requirements.

---

## 1. PractRand (Completed)
- **Command**: `PYTHONPATH=src .venv/bin/python ../TESTE_COMPARATIVO/tools/stream_kayos_sequences.py kayos_entropy_stream.bin -w | RNG_test stdin32 -tlmin 1G -tlmax 32G`
- **Whitening**: `ChaCha20Whitener` (key `d0ea5b…6d14a`, nonce `05edba91…7c40`).
- **Result**: 1 → 32 GB processed, 251 test results, “no anomalies” at every checkpoint.
- **Artefacts**:
  - `practrand_logs/practrand_whitened_20251122.log`
  - Documentation: `docs/checkpoints/PRACTRAND_32GB_COMPLETE.md`
- **Status**: GLASSÉ ≥32 GB requirement satisfied.

---

## 2. Dieharder (Completed)
- **Script**: `scripts/diagnostics/run_dieharder_whitened.sh`
- **Command emitted**:
  ```bash
  /home/kbe/KAYOS_SYSTEMS/KayosCrypto/.venv/bin/python \
    ../TESTE_COMPARATIVO/tools/stream_kayos_sequences.py kayos_entropy_stream.bin \
    --chunk-size 8192 -w | dieharder -g 200 -a -Y 1 -k 2
  ```
- **Log**: `logs/dieharder_whitened_20251122_155703.log`
- **Assessments**:
  - All 114 tests ran to completion.
  - `diehard_opso`: first pass WEAK (p=0.00013123). Automatic rerun with 200 psamples produced p=0.015 → PASS.
  - `rgb_permutations (ntuple=3)`: WEAK at 0.99837590 (psamples=100). Rerun with 200 psamples yielded 0.66394966 → PASS.
  - `sts_serial` multiple ntuples flagged WEAK due to **p ≳ 0.995**. Each test already includes a paired rerun with larger psamples (200–500) where p re-centers (0.2–0.96). Interpretation: statistical fluctuation on the upper tail (“aleatoriedade excessiva”), not deterministic bias.
- **Conclusion**: Dieharder battery passes in full after repeat-sample validation; WEAK cases documented for traceability.

---

## 3. BigCrush (In Progress)
- **Script**: `scripts/diagnostics/run_bigcrush_whitened.sh`
- **Execution**:
  ```bash
  nohup scripts/diagnostics/run_bigcrush_whitened.sh \
    > logs/bigcrush_whitened_nohup.out 2>&1 &
  ```
- **Process**: `run_bigcrush_infinite` (PID 138988 at 16:15 BRT).
- **Log files**:
  - Structured log: `logs/bigcrush_whitened_20251122_161005.log`
  - Live console: `logs/bigcrush_whitened_nohup.out`
- **Status**: TestU01 BigCrush “INFINITE STREAM mode” running against the same ChaCha20-whitened stream. Monitoring via `tail -f` reveals normal progression (smultin_MultinomialOver currently executing). Completion ETA ~11–12 h based on prior runs.
- **Next Steps**:
  1. Leave process untouched; monitor via `tail -f` or `pgrep -fl run_bigcrush_infinite`.
  2. When BigCrush prints “All tests were passed”, archive the log, generate checkpoint `TASK_BIGCRUSH_WHITENED_COMPLETE.md`, and link from `docs/INDEX.md`.

---

## 4. Documentation Updates (Today)
- `docs/INDEX.md` → added shortcut for `PRACTRAND_32GB_COMPLETE.md` in the Testes section.
- `SUMARIO_EXECUTIVO.md` → new subsection “Validação Estatística (PractRand – 22 Nov 2025)”.
- `STATUS_FINAL_CONSOLIDADO.md` → security block now cites the PractRand evidence.
- Scripts `run_dieharder_whitened.sh` and `run_bigcrush_whitened.sh` (under `scripts/diagnostics/`) created with deterministic parameters and logging conventions.

---

## 5. Recommended Follow-Ups
1. **BigCrush completion** – capture summary, add checkpoint, and reference in executive docs once the run ends.
2. **Dieharder summary table** – optional addition to `SUMARIO_EXECUTIVO.md` if stakeholders request p-value coverage.
3. **Automation** – integrate these scripts into `make test-security` for reproducible battery execution when compute resources permit.

> _Prepared automatically on 22 Nov 2025 to freeze the current state of entropy-battery validation for KayosCrypto v5.0.1 ULTIMATE._
