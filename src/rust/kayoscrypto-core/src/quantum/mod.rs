pub mod avalanche_cascade;
pub mod block_uniformizer;
pub mod entropy_refiner;
pub mod gap_metrics;
pub mod galois_matrix_processor;
pub mod low_depth_shuffler;
pub mod matrix_rank_optimizer;
pub mod orchestrator;
pub mod quantum_entropy_boost;
pub mod quantum_xor_fold;
pub mod relojoeiro;
pub mod sator_auditor;
pub mod sator_block_whitener;
pub mod sator_bridge;
pub mod sator_curator;
pub mod spectral_analyzer;
pub mod surgical_refiner;
pub mod targeted_entropy_refiner;
pub mod velho_matuto;
pub mod vidente;

pub use avalanche_cascade::AvalancheCascade;
pub use block_uniformizer::BlockFrequencyFix;
pub use gap_metrics::{GapAnalysis, GapMetrics, GapStatus};
pub use galois_matrix_processor::GaloisMatrixProcessor;
pub use low_depth_shuffler::LowDepthShuffler;
pub use matrix_rank_optimizer::MatrixRankOptimizer;
pub use orchestrator::{SatorObservation, SatorOrchestrator};
pub use quantum_entropy_boost::ApproximateEntropyFix;
pub use quantum_xor_fold::QuantumXORFold;
pub use relojoeiro::{Relojoeiro, RelojoeiroSummary};
pub use sator_auditor::SatorAuditor;
pub use sator_block_whitener::SatorBlockWhitener;
pub use sator_bridge::{SatorAnalysisSnapshot, SatorOptimizationFeedback, SatorPythonBridge};
pub use sator_curator::SatorCurator;
pub use spectral_analyzer::SpectralAnalyzer;
pub use surgical_refiner::{SurgicalEntropyRefiner, SurgicalReport};
pub use targeted_entropy_refiner::TargetedEntropyRefiner;
pub use velho_matuto::{KayosMode, VelhoMatuto};
pub use vidente::{Vidente, VidenteForecast};

use std::{array, fmt};

use sha3::{Digest, Sha3_256};

use crate::KayosCryptoSafe;

const DEFAULT_SAMPLE_SIZE: usize = 128;
const MESSAGE_LEN: usize = 256;
const ENTROPY_PER_BYTE: f64 = 8.0;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum QuantumStageStatus {
    Green,
    Yellow,
    Red,
}

impl QuantumStageStatus {
    pub fn label(&self) -> &'static str {
        match self {
            Self::Green => "🟢 Stable",
            Self::Yellow => "🟡 Monitor",
            Self::Red => "🔴 Critical",
        }
    }

    pub fn is_green(&self) -> bool {
        matches!(self, Self::Green)
    }
}

impl fmt::Display for QuantumStageStatus {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(self.label())
    }
}

#[derive(Clone, Debug)]
pub struct QuantumStageAssessment {
    pub name: &'static str,
    pub entropy_bits: f64,
    pub entropy_ratio: f64,
    pub avalanche: f64,
    pub status: QuantumStageStatus,
}

impl QuantumStageAssessment {
    fn new(name: &'static str, entropy_bits: f64, avalanche: f64) -> Self {
        let entropy_ratio = (entropy_bits / ENTROPY_PER_BYTE).clamp(0.0, 1.0);
        let status = classify_stage(entropy_ratio, avalanche);
        Self {
            name,
            entropy_bits,
            entropy_ratio,
            avalanche,
            status,
        }
    }
}

impl fmt::Display for QuantumStageAssessment {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "{} | entropy {:.2} bits ({:.1}%) | avalanche {:.2}% | {}",
            self.name,
            self.entropy_bits,
            self.entropy_ratio * 100.0,
            self.avalanche * 100.0,
            self.status
        )
    }
}

/// Aggregated measurements that describe the pipeline's readiness against quantum adversaries.
#[derive(Clone, Debug)]
pub struct QuantumResistanceReport {
    pub stages: [QuantumStageAssessment; 3],
    pub stage1_entropy: f64,
    pub stage2_entropy: f64,
    pub stage3_entropy: f64,
    pub average_avalanche: f64,
    pub average_stage_avalanche: f64,
    pub average_entropy_ratio: f64,
    pub grover_resilience: f64,
    pub shor_resilience: f64,
    pub composite_score: f64,
    pub entropy_floor: f64,
    pub entropy_spread: f64,
    pub surgical_prediction: SurgicalReport,
}

impl QuantumResistanceReport {
    pub fn entropic_score(&self) -> f64 {
        self.average_entropy_ratio
    }

    pub fn readiness(&self) -> &'static str {
        match self.composite_score {
            score if score >= 85.0 => "🟢 High-Risk Ready",
            score if score >= 70.0 => "🟡 Near Ready",
            _ => "🔴 Gap Analysis Required",
        }
    }

    pub fn recommendations(&self) -> Vec<String> {
        let mut notes = Vec::new();

        if self.entropy_floor < 0.90 {
            notes.push(format!(
                "Entropy floor at {:.2}% — rebalance Fibonacci directionals to reach ≥ 90%.",
                self.entropy_floor * 100.0
            ));
        }

        if self
            .stages
            .iter()
            .any(|stage| matches!(stage.status, QuantumStageStatus::Red))
        {
            notes.push(
                "Execute Ezekiel concentric alignment calibration to eliminate critical hotspots."
                    .to_string(),
            );
        }

        if self.average_stage_avalanche < 0.40 {
            notes.push(
                "Increase Feistel diffusion or add micro-rotations to push stage avalanche ≥ 40%."
                    .to_string(),
            );
        }

        if self.grover_resilience < 0.95 {
            notes.push(
                "Double logical key length or integrate the geometric entropy pool to counter Grover.".to_string(),
            );
        }

        let high_risk_blockers = self.high_risk_blockers();
        if !high_risk_blockers.is_empty() {
            for blocker in high_risk_blockers {
                notes.push(format!("High-risk blocker: {}", blocker));
            }
        }

        if notes.is_empty() {
            notes.push(
                "Maintain configuration; schedule quarterly quantum telemetry audit.".to_string(),
            );
        }

        notes
    }

    pub fn high_risk_blockers(&self) -> Vec<String> {
        let mut blockers = Vec::new();

        if self.entropy_floor < 0.90 {
            blockers.push(format!(
                "Entropy floor {:.2}% (target ≥ 90%)",
                self.entropy_floor * 100.0
            ));
        }

        if self.average_entropy_ratio < 0.92 {
            blockers.push(format!(
                "Average stage entropy {:.2}% (target ≥ 92%)",
                self.average_entropy_ratio * 100.0
            ));
        }

        if self.average_stage_avalanche < 0.45 {
            blockers.push(format!(
                "Stage avalanche {:.2}% (target ≥ 45%)",
                self.average_stage_avalanche * 100.0
            ));
        }

        if self.average_avalanche < 0.48 {
            blockers.push(format!(
                "Final stage avalanche {:.2}% (target ≥ 48%)",
                self.average_avalanche * 100.0
            ));
        }

        if self.grover_resilience < 0.95 {
            blockers.push(format!(
                "Grover resilience {:.2}% (target ≥ 95%)",
                self.grover_resilience * 100.0
            ));
        }

        if self.shor_resilience < 0.85 {
            blockers.push(format!(
                "Shor resilience {:.2}% (target ≥ 85%)",
                self.shor_resilience * 100.0
            ));
        }

        for stage in &self.stages {
            if !stage.status.is_green() {
                blockers.push(format!("Stage '{}' status {}", stage.name, stage.status));
            }
        }

        blockers
    }

    pub fn is_high_risk_ready(&self) -> bool {
        self.high_risk_blockers().is_empty()
    }
}

impl fmt::Display for QuantumResistanceReport {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "🛰️ Quantum Resistance Report")?;
        writeln!(f, "   Composite score: {:.2}%", self.composite_score)?;
        writeln!(f, "   Readiness: {}", self.readiness())?;
        let high_risk_blockers = self.high_risk_blockers();
        let high_risk_ready = high_risk_blockers.is_empty();
        writeln!(
            f,
            "   High-risk compliance: {}",
            if high_risk_ready {
                "✅ Ready"
            } else {
                "⚠️ Blockers present"
            }
        )?;
        writeln!(
            f,
            "   Grover resilience: {:.2}%",
            self.grover_resilience * 100.0
        )?;
        writeln!(
            f,
            "   Shor resilience: {:.2}%",
            self.shor_resilience * 100.0
        )?;
        writeln!(f, "   Entropy floor: {:.2}%", self.entropy_floor * 100.0)?;
        writeln!(f, "   Entropy spread: {:.2}%", self.entropy_spread * 100.0)?;
        writeln!(f, "   Stage breakdown:")?;
        for (idx, stage) in self.stages.iter().enumerate() {
            writeln!(f, "     [{}] {}", idx + 1, stage)?;
        }

        writeln!(
            f,
            "   Surgical prediction: approx {:.3}, block {:.3}, cumulative {:.3}, composite {:.3}",
            self.surgical_prediction.approx_entropy_score,
            self.surgical_prediction.block_freq_score,
            self.surgical_prediction.cumulative_sums_score,
            self.surgical_prediction.predicted_nist_score,
        )?;

        if !high_risk_ready {
            writeln!(f, "   High-risk blockers:")?;
            for blocker in &high_risk_blockers {
                writeln!(f, "     - {}", blocker)?;
            }
        }

        let recommendations = self.recommendations();
        if !recommendations.is_empty() {
            writeln!(f, "   Recommendations:")?;
            for item in recommendations {
                writeln!(f, "     - {}", item)?;
            }
        }

        Ok(())
    }
}

/// Manager responsible for deriving deterministic quantum resistance metrics.
pub struct QuantumResistanceManager {
    sample_size: usize,
    crypto: KayosCryptoSafe,
}

impl QuantumResistanceManager {
    pub fn new(sample_size: usize) -> Self {
        let size = sample_size.max(16);
        Self {
            sample_size: size,
            crypto: KayosCryptoSafe::new(),
        }
    }

    pub fn default() -> Self {
        Self::new(DEFAULT_SAMPLE_SIZE)
    }

    pub fn assess(&self, password: &[u8]) -> QuantumResistanceReport {
        let mut entropy_scores: [Vec<f64>; 3] =
            array::from_fn(|_| Vec::with_capacity(self.sample_size));
        let mut avalanche_scores: [Vec<f64>; 3] =
            array::from_fn(|_| Vec::with_capacity(self.sample_size));

        let kayos_id = derive_kayos_id(password);
        let mut surgical_refiner = SurgicalEntropyRefiner::new(kayos_id);
        let mut surgical_totals = (0.0f64, 0.0f64, 0.0f64, 0.0f64);
        let mut surgical_samples = 0u32;

        for index in 0..self.sample_size {
            let plaintext = self.generate_plaintext(index);
            let pipeline = self.crypto.pipeline_breakdown(&plaintext, password);

            let mut mutated_plaintext = plaintext.clone();
            mutated_plaintext[0] ^= 0x01;
            let mutated_pipeline = self.crypto.pipeline_breakdown(&mutated_plaintext, password);

            let stages = [
                (&pipeline.stage_fibonacci, &mutated_pipeline.stage_fibonacci),
                (
                    &pipeline.stage_concentric,
                    &mutated_pipeline.stage_concentric,
                ),
                (&pipeline.stage_final, &mutated_pipeline.stage_final),
            ];

            for (stage_idx, (baseline, mutated)) in stages.into_iter().enumerate() {
                entropy_scores[stage_idx].push(calculate_entropy(baseline));
                avalanche_scores[stage_idx].push(calculate_avalanche_ratio(baseline, mutated));
            }

            let mut surgical_buffer = bytes_to_u64_buffer(&pipeline.stage_final);
            if !surgical_buffer.is_empty() {
                let report = surgical_refiner.refine_surgically(&mut surgical_buffer);
                surgical_totals.0 += report.approx_entropy_score;
                surgical_totals.1 += report.block_freq_score;
                surgical_totals.2 += report.cumulative_sums_score;
                surgical_totals.3 += report.predicted_nist_score;
                surgical_samples = surgical_samples.saturating_add(1);
            }
        }

        let stage_entropy_means = entropy_scores.map(|scores| mean(&scores));
        let stage_avalanche_means = avalanche_scores.map(|scores| mean(&scores));

        let surgical_prediction = if surgical_samples > 0 {
            let count = surgical_samples as f64;
            SurgicalReport {
                approx_entropy_score: surgical_totals.0 / count,
                block_freq_score: surgical_totals.1 / count,
                cumulative_sums_score: surgical_totals.2 / count,
                predicted_nist_score: surgical_totals.3 / count,
            }
        } else {
            SurgicalReport::new()
        };

        let stages = [
            QuantumStageAssessment::new(
                "Fibonacci Direction",
                stage_entropy_means[0],
                stage_avalanche_means[0],
            ),
            QuantumStageAssessment::new(
                "Ezekiel Concentric",
                stage_entropy_means[1],
                stage_avalanche_means[1],
            ),
            QuantumStageAssessment::new(
                "Core System",
                stage_entropy_means[2],
                stage_avalanche_means[2],
            ),
        ];

        let stage1_entropy = stages[0].entropy_bits;
        let stage2_entropy = stages[1].entropy_bits;
        let stage3_entropy = stages[2].entropy_bits;

        let average_avalanche = stages[2].avalanche;
        let average_stage_avalanche =
            stages.iter().map(|stage| stage.avalanche).sum::<f64>() / stages.len() as f64;
        let average_entropy_ratio =
            stages.iter().map(|stage| stage.entropy_ratio).sum::<f64>() / stages.len() as f64;
        let entropy_floor = stages
            .iter()
            .map(|stage| stage.entropy_ratio)
            .fold(1.0, f64::min);
        let entropy_peak = stages
            .iter()
            .map(|stage| stage.entropy_ratio)
            .fold(0.0, f64::max);
        let entropy_spread = (entropy_peak - entropy_floor).max(0.0);

        let grover_resilience = (entropy_floor * 2.0).min(1.0);
        let shor_resilience = (0.6 * average_entropy_ratio) + (0.4 * stages[1].avalanche);

        let composite_score = (entropy_floor * 100.0 * 0.30)
            + (average_entropy_ratio * 100.0 * 0.20)
            + (average_stage_avalanche * 100.0 * 0.20)
            + (average_avalanche * 100.0 * 0.10)
            + (grover_resilience * 100.0 * 0.10)
            + (shor_resilience * 100.0 * 0.10);

        QuantumResistanceReport {
            stages,
            stage1_entropy,
            stage2_entropy,
            stage3_entropy,
            average_avalanche,
            average_stage_avalanche,
            average_entropy_ratio,
            grover_resilience,
            shor_resilience,
            composite_score,
            entropy_floor,
            entropy_spread,
            surgical_prediction,
        }
    }

    fn generate_plaintext(&self, index: usize) -> Vec<u8> {
        let mut hasher = Sha3_256::new();
        hasher.update(index.to_be_bytes());
        let digest = hasher.finalize();
        digest.iter().copied().cycle().take(MESSAGE_LEN).collect()
    }
}

fn calculate_entropy(data: &[u8]) -> f64 {
    if data.is_empty() {
        return 0.0;
    }

    let mut counts = [0usize; 256];
    for &byte in data {
        counts[byte as usize] += 1;
    }

    let len = data.len() as f64;
    counts
        .iter()
        .filter(|&&count| count > 0)
        .map(|&count| {
            let probability = count as f64 / len;
            -probability * probability.log2()
        })
        .sum()
}

fn calculate_avalanche_ratio(a: &[u8], b: &[u8]) -> f64 {
    let compared = a.len().min(b.len());
    if compared == 0 {
        return 0.0;
    }

    let differing = count_different_bits(&a[..compared], &b[..compared]);
    differing as f64 / (compared as f64 * ENTROPY_PER_BYTE)
}

fn mean(values: &[f64]) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    values.iter().sum::<f64>() / values.len() as f64
}

fn count_different_bits(a: &[u8], b: &[u8]) -> usize {
    a.iter()
        .zip(b.iter())
        .map(|(&x, &y)| (x ^ y).count_ones() as usize)
        .sum()
}

fn classify_stage(entropy_ratio: f64, avalanche: f64) -> QuantumStageStatus {
    if entropy_ratio >= 0.95 && avalanche >= 0.45 {
        QuantumStageStatus::Green
    } else if entropy_ratio >= 0.85 && avalanche >= 0.35 {
        QuantumStageStatus::Yellow
    } else {
        QuantumStageStatus::Red
    }
}

fn derive_kayos_id(password: &[u8]) -> u64 {
    if password.is_empty() {
        return 0;
    }

    let mut hasher = Sha3_256::new();
    hasher.update(password);
    let digest = hasher.finalize();
    let mut id_bytes = [0u8; 8];
    id_bytes.copy_from_slice(&digest[..8]);
    u64::from_be_bytes(id_bytes)
}

fn bytes_to_u64_buffer(data: &[u8]) -> Vec<u64> {
    data.chunks(8)
        .map(|chunk| {
            let mut padded = [0u8; 8];
            let len = chunk.len();
            padded[..len].copy_from_slice(chunk);
            u64::from_le_bytes(padded)
        })
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn report_with_score(score: f64) -> QuantumResistanceReport {
        let stages = [
            QuantumStageAssessment::new("Stage 1", 4.0, 0.30),
            QuantumStageAssessment::new("Stage 2", 4.2, 0.32),
            QuantumStageAssessment::new("Stage 3", 4.4, 0.35),
        ];

        let average_stage_avalanche =
            stages.iter().map(|stage| stage.avalanche).sum::<f64>() / stages.len() as f64;
        let average_entropy_ratio =
            stages.iter().map(|stage| stage.entropy_ratio).sum::<f64>() / stages.len() as f64;
        let entropy_floor = stages
            .iter()
            .map(|stage| stage.entropy_ratio)
            .fold(1.0, f64::min);
        let entropy_peak = stages
            .iter()
            .map(|stage| stage.entropy_ratio)
            .fold(0.0, f64::max);
        let stage1_entropy = stages[0].entropy_bits;
        let stage2_entropy = stages[1].entropy_bits;
        let stage3_entropy = stages[2].entropy_bits;
        let average_avalanche = stages[2].avalanche;
        let entropy_spread = entropy_peak - entropy_floor;

        QuantumResistanceReport {
            stages,
            stage1_entropy,
            stage2_entropy,
            stage3_entropy,
            average_avalanche,
            average_stage_avalanche,
            average_entropy_ratio,
            grover_resilience: 0.3,
            shor_resilience: 0.92,
            composite_score: score,
            entropy_floor,
            entropy_spread,
            surgical_prediction: SurgicalReport::new(),
        }
    }

    #[test]
    fn quantum_manager_produces_reasonable_scores() {
        let manager = QuantumResistanceManager::new(32);
        let report = manager.assess(b"quantum_password");

        assert!(
            report.stage1_entropy >= 4.5 && report.stage1_entropy <= 8.0,
            "stage1={:.3} stage2={:.3} stage3={:.3} floor={:.3}",
            report.stage1_entropy,
            report.stage2_entropy,
            report.stage3_entropy,
            report.entropy_floor
        );
        assert!(
            report.stage2_entropy >= 6.0 && report.stage2_entropy <= 8.0,
            "stage1={:.3} stage2={:.3} stage3={:.3}",
            report.stage1_entropy,
            report.stage2_entropy,
            report.stage3_entropy
        );
        assert!(
            report.stage3_entropy >= 6.0 && report.stage3_entropy <= 8.0,
            "stage1={:.3} stage2={:.3} stage3={:.3}",
            report.stage1_entropy,
            report.stage2_entropy,
            report.stage3_entropy
        );
        assert!(
            report.entropy_floor >= 0.55,
            "entropy_floor={:.3}",
            report.entropy_floor
        );
        assert!(
            report.average_avalanche > 0.45 && report.average_avalanche <= 1.0,
            "avg_avalanche={:.3}",
            report.average_avalanche
        );
        assert!(
            report.composite_score > 55.0,
            "composite={:.3}",
            report.composite_score
        );
        assert!(!report.recommendations().is_empty());
    }

    #[test]
    fn readiness_labels_follow_score() {
        let baseline = report_with_score(55.0);
        let medium = report_with_score(80.0);
        let high = report_with_score(93.0);

        assert_eq!(baseline.readiness(), "🔴 Gap Analysis Required");
        assert_eq!(medium.readiness(), "🟡 Near Ready");
        assert_eq!(high.readiness(), "🟢 High-Risk Ready");
    }
}
