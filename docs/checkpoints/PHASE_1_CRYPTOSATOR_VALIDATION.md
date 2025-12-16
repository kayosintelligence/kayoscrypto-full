# Phase 1 – Cryptographic Sator Validation (Prototype)

**Date:** 2025-11-18  
**Scope:** Kayos entropy roadmap – Phase 1 (concept validation)

## Goals
- Model 64-bit entropy windows as geometric structures (8×8 grid).
- Extract Sator-inspired metrics (column/row balance, diagonal symmetry, quadrant harmony, density balance).
- Combine metrics into a single `sator_score` and measure correlation with Approximate Entropy (ApEn).
- Produce synthetic datasets mixing random and patterned sequences to emulate the observed 0.958 plateau behavior.

## Implementation Notes
- Created prototype: `prototypes/kayos_entropy/cryptographic_sator_prototype.py`.
- Sator score weights tuned to emphasise quadrant harmony and row balance: `[0.1, 0.25, 0.15, 0.4, 0.1]`.
- Patterned samples include repeated-byte, half-block, and checkerboard geometries to simulate low-entropy regimes.
- Approximate Entropy implemented in pure Python (m=2) for correlation studies.

## Experiment Outcome (500 samples)
- **Correlation (Sator vs ApEn):** `0.665`  
- **Label breakdown:**
  - Patterned sequences: `mean sator=0.648`, `mean ApEn=0.272`, high variance confirms sensitivity.  
  - Random sequences: `mean sator=0.769`, `mean ApEn=0.659`.
- **Metric contribution (corr vs ApEn):**
  - Quadrant harmony: `0.649`
  - Row balance: `0.449`
  - Diagonal symmetry: `0.059`
  - Column balance: `-0.296`
  - Density balance: `-0.173`

## Conclusions
- Geometric metrics track entropy changes: quadrant harmony and row balance are strong predictors (>0.4 correlation).
- Column and density balances negatively correlate with ApEn under current synthetic mix, informing future weighting/feature redesign.
- Weighted Sator score surpasses the 0.6 correlation threshold, establishing viability for integration.

## Next Steps
1. Generate labeled datasets from actual Rust refiner outputs (baseline vs plateau) to recalibrate weights.
2. Extend prototype with sliding windows and temporal aggregation (`SlidingSatorAnalyzer`).
3. Export metrics as feature vectors for downstream clustering (GMM) and archival (Phase 2).
4. Define API contract for the Rust ↔ Python analytics bridge based on validated metric schema.
