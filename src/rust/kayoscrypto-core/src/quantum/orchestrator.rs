use std::collections::{HashSet, VecDeque};

use super::galois_matrix_processor::GaloisMatrixProcessor;
use super::low_depth_shuffler::LowDepthShuffler;
use super::matrix_rank_optimizer::MatrixRankOptimizer;
use super::relojoeiro::{Relojoeiro, RelojoeiroSummary};
use super::sator_auditor::SatorAuditor;
use super::sator_bridge::SatorAnalysisSnapshot;
use super::sator_curator::SatorCurator;
use super::velho_matuto::KayosMode;
use super::vidente::{Vidente, VidenteForecast};

#[derive(Clone, Debug)]
pub struct SatorObservation {
    pub summary: RelojoeiroSummary,
    pub forecast: VidenteForecast,
    pub audit: Option<SatorAnalysisSnapshot>,
}

pub struct SatorOrchestrator {
    mode: KayosMode,
    auditor: SatorAuditor,
    relojoeiro: Relojoeiro,
    vidente: Vidente,
    curator: Option<SatorCurator>,
    matrix_optimizer: Option<MatrixRankOptimizer>,
    matrix_shuffler: Option<LowDepthShuffler>,
    galois_processor: Option<GaloisMatrixProcessor>,
    matrix_buffer: Vec<u8>,
    matrix_ready: VecDeque<u8>,
    matrix_bytes: usize,
    matrix_fix_enabled: bool,
}

impl SatorOrchestrator {
    pub fn new(mode: KayosMode, kayos_id: u64) -> Self {
        let auditor = SatorAuditor::new(16_384);
        let relojoeiro = Relojoeiro::new(16);
        let vidente = Vidente::new(64);
        let curator = if matches!(mode, KayosMode::SatorSimbiotico) {
            Some(SatorCurator::new(kayos_id))
        } else {
            None
        };
        let matrix_dim = MatrixRankOptimizer::MATRIX_DIM;
        let matrix_bits = matrix_dim * matrix_dim;
        let matrix_bytes = (matrix_bits + 7) / 8;

        Self {
            mode,
            auditor,
            relojoeiro,
            vidente,
            curator,
            matrix_optimizer: None,
            matrix_shuffler: None,
            galois_processor: None,
            matrix_buffer: Vec::with_capacity(matrix_bytes),
            matrix_ready: VecDeque::with_capacity(matrix_bytes),
            matrix_bytes,
            matrix_fix_enabled: false,
        }
    }

    pub fn process(&mut self, value: u64) -> (u64, SatorObservation) {
        let bytes = value.to_le_bytes();
        let summary = self.relojoeiro.analyze_block(&bytes);
        let forecast = self.vidente.update(summary.clone());
        let audit = self.auditor.audit_if_needed(&bytes);

        let output = match self.curator.as_mut() {
            Some(curator) => {
                let curated = curator.curate(value);
                curator.absorb_feedback(&summary);
                curated
            }
            None => value,
        };

        (
            output,
            SatorObservation {
                summary,
                forecast,
                audit,
            },
        )
    }

    pub fn mode(&self) -> KayosMode {
        self.mode
    }

    pub fn last_audit_error(&self) -> Option<&str> {
        self.auditor.last_error()
    }

    pub fn enable_matrix_fix(&mut self) {
        if self.matrix_fix_enabled {
            return;
        }
        self.matrix_optimizer = Some(MatrixRankOptimizer::new());
        self.matrix_shuffler = Some(LowDepthShuffler::new());
        self.galois_processor = Some(GaloisMatrixProcessor::new());
        self.matrix_fix_enabled = true;
    }

    pub fn matrix_fix_active(&self) -> bool {
        self.matrix_fix_enabled
    }

    pub fn post_process_block(&mut self, block: &[u8]) -> Vec<u8> {
        if !self.matrix_fix_enabled || block.is_empty() {
            return block.to_vec();
        }

        self.matrix_buffer.extend_from_slice(block);
        while self.matrix_buffer.len() >= self.matrix_bytes {
            let chunk: Vec<u8> = self
                .matrix_buffer
                .drain(..self.matrix_bytes)
                .collect();
            let processed = self.run_matrix_pipeline(&chunk);
            self.matrix_ready.extend(processed);
        }

        self.matrix_ready.drain(..).collect()
    }

    pub fn finalize_matrix_fix(&mut self) -> Vec<u8> {
        if !self.matrix_fix_enabled {
            return Vec::new();
        }

        if !self.matrix_buffer.is_empty() {
            let remainder: Vec<u8> = self.matrix_buffer.drain(..).collect();
            let processed = self.run_matrix_pipeline(&remainder);
            self.matrix_ready.extend(processed);
        }

        self.matrix_ready.drain(..).collect()
    }

    fn run_matrix_pipeline(&self, chunk: &[u8]) -> Vec<u8> {
        let debug = std::env::var_os("KAYOS_MATRIX_DEBUG").is_some();
        if debug {
            Self::log_matrix_stats("input", chunk);
        }

        let mut processed = chunk.to_vec();
        if let Some(optimizer) = &self.matrix_optimizer {
            processed = optimizer.process_matrix_blocks(&processed);
            if debug {
                Self::log_matrix_stats("after_optimizer", &processed);
            }
        }
        if let Some(shuffler) = &self.matrix_shuffler {
            processed = shuffler.shuffle_matrix_data(
                &processed,
                MatrixRankOptimizer::MATRIX_DIM,
            );
            if debug {
                Self::log_matrix_stats("after_shuffler", &processed);
            }
        }
        if let Some(galois) = &self.galois_processor {
            processed = galois.apply_galois_folding(&processed);
            if debug {
                Self::log_matrix_stats("after_galois", &processed);
            }
        }
        processed
    }

    fn log_matrix_stats(stage: &str, data: &[u8]) {
        let zeros = data.iter().filter(|&&byte| byte == 0).count();
        let unique = data.iter().copied().collect::<HashSet<_>>().len();
        eprintln!(
            "[matrix_fix::{stage}] bytes={} zeros={} unique={}",
            data.len(),
            zeros,
            unique
        );
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn orchestration_runs_in_both_modes() {
        let mut regulator = SatorOrchestrator::new(KayosMode::MatutoRegulatorio, 1);
        let (value, observation) = regulator.process(42);
        assert_eq!(value, 42);
        assert!(observation.forecast.severity >= 0.0);

        let mut simb = SatorOrchestrator::new(KayosMode::SatorSimbiotico, 99);
        let (value2, observation2) = simb.process(42);
        assert_ne!(value2, 0);
        assert!(observation2.forecast.severity >= 0.0);
    }
}
