# Task 9.0 – Paranoid 100K Timing Snapshot (2025-11-17)

## Overview
- **Context**: Captured release-mode timing harness output to document the current constant-time behaviour.
- **Commands Executed**:
  1. `cargo test --release constant_time_primitives_pass_t_test -- --nocapture`
  2. `cargo test --release manual_timing_run -- --ignored --nocapture`
- **Raw Logs**: Stored in `docs/checkpoints/logs/paranoid_100k_test_2025-11-17.txt` and `docs/checkpoints/logs/paranoid_100k_manual_2025-11-17.txt`.

## Key Metrics (Release Timing Harness)
| Operation | Samples | Mean | Std Dev | τ | (5/τ)² | Paranoid 100K |
|-----------|---------|------|---------|---|--------|----------------|
| SecureOps::ct_select_bytes | 100,000 | 31 ns | 4 ns | 0.137116 | 1,330 |  |
| StrongMix::apply | 100,000 | 1.488 us | 302 ns | 0.203210 | 605 |  |
| KayosCryptoSafe::encrypt | 50,000 | 55.714 us | 2.866 us | 0.051443 | 9,447 |  |
| **Total** | **250,000** | — | — | — | — | **FAIL** |

## Key Metrics (Manual Extended Run)
| Operation | Samples | Mean | Std Dev | τ | (5/τ)² | Paranoid 100K |
|-----------|---------|------|---------|---|--------|----------------|
| SecureOps::ct_select_bytes | 250,000 | 39 ns | 8 ns | 0.199934 | 625 |  |
| StrongMix::apply | 250,000 | 1.489 us | 273 ns | 0.183275 | 744 |  |
| KayosCryptoSafe::encrypt | 250,000 | 55.249 us | 2.896 us | 0.052414 | 9,100 |  |
| **Total** | **750,000** | — | — | — | — | **FAIL** |

## Observations
- All measured stages remain deterministic, but τ values are above the Paranoid 100K threshold (≤0.0001), yielding FAIL verdicts despite high sample volume.
- Encryption stage variance is low compared to primitives, yet still short of the 100K security level.
- Batch processing completed without runtime errors; harness integration is stable in release mode.

## Next Focus
1. Investigate variance reduction strategies for `SecureOps::ct_select_bytes` and `StrongMix::apply` (e.g., tighten buffer alignment or instruction-level balancing).
2. Consider increasing batch granularity or introducing jitter smoothing to push τ below the Paranoid target.
3. Re-run the captured commands after adjustments and append new logs to maintain longitudinal traceability.
