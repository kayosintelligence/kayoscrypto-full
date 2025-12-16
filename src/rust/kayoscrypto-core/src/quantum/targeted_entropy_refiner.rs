//! TargetedEntropyRefiner stitches the three corrective transforms together.

use super::{AvalancheCascade, GapAnalysis, GapMetrics, QuantumXORFold, SatorBlockWhitener};

#[derive(Clone, Debug)]
pub struct TargetedEntropyRefiner {
    quantum_fold: QuantumXORFold,
    block_whitener: SatorBlockWhitener,
    dft_cascade: AvalancheCascade,
    metrics: GapMetrics,
}

impl TargetedEntropyRefiner {
    pub fn new(kayos_id: u64) -> Self {
        Self {
            quantum_fold: QuantumXORFold::new(kayos_id),
            block_whitener: SatorBlockWhitener::new(),
            dft_cascade: AvalancheCascade::new(kayos_id),
            metrics: GapMetrics::new(),
        }
    }

    pub fn refine_targeted(&mut self, buffer: &mut [u64]) {
        if buffer.is_empty() {
            return;
        }

        for chunk in buffer.chunks_mut(4) {
            for value in chunk.iter_mut() {
                *value = self.quantum_fold.apply_entropy_fix(*value);
                *value = self.dft_cascade.apply_cascade(*value);
            }
            self.block_whitener.whiten_block(chunk);
            self.metrics.analyze_chunk(chunk);
        }
    }

    pub fn get_gap_metrics(&self) -> GapAnalysis {
        self.metrics.generate_gap_report()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::quantum::GapStatus;

    #[test]
    fn targeted_refiner_mutates_buffer_and_metrics() {
        let mut refiner = TargetedEntropyRefiner::new(0xDEAD_BEEF);
        let baseline = refiner.get_gap_metrics();
        let mut buffer = [0u64; 16];
        refiner.refine_targeted(&mut buffer);
        assert!(buffer.iter().any(|&value| value != 0));
        let report = refiner.get_gap_metrics();
        assert!(report.approximate_entropy_score >= baseline.approximate_entropy_score);
    }

    #[test]
    fn targeted_refiner_handles_empty_buffer() {
        let mut refiner = TargetedEntropyRefiner::new(1);
        let mut buffer: [u64; 0] = [];
        refiner.refine_targeted(&mut buffer);
        let report = refiner.get_gap_metrics();
        assert_eq!(report.overall_gap_status, GapStatus::NeedsWork);
    }
}
