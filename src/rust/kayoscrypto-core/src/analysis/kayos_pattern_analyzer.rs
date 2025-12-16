use std::collections::BTreeSet;

use serde::Serialize;

use crate::quantum::sator_bridge::{SatorAnalysisSnapshot, SatorPythonBridge};

/// Implements the "Observação Profunda" stage from the KAYOS philosophy.
///
/// The analyzer watches full temporal windows of the stream, using Sator
/// metrics when available and graceful fallbacks otherwise. Results feed the
/// higher-level behaviour classification (Neurônios Espelho) and optimization
/// stages.
pub struct KayosStreamAnalyzer {
    sator_bridge: Option<SatorPythonBridge>,
    temporal_window: Vec<Vec<u8>>,
    pattern_evolution: Vec<f64>,
    window_limit: usize,
}

impl KayosStreamAnalyzer {
    pub fn new() -> Self {
        let sator_bridge = SatorPythonBridge::new().ok();
        Self {
            sator_bridge,
            temporal_window: Vec::with_capacity(100),
            pattern_evolution: Vec::new(),
            window_limit: 100,
        }
    }

    /// Analyse an entire stream by sliding over blocks and extracting temporal
    /// patterns. Partial blocks are ignored to keep statistics consistent.
    pub fn analyze_stream_pattern(&mut self, stream: &[u8]) -> StreamDiagnosis {
        let block_size = 1024usize;
        let mut diagnosis = StreamDiagnosis::new();

        for chunk in stream.chunks(block_size) {
            if chunk.len() != block_size {
                break;
            }

            self.temporal_window.push(chunk.to_vec());
            if self.temporal_window.len() > self.window_limit {
                self.temporal_window.remove(0);
            }

            let score = self.evaluate_block(chunk, &mut diagnosis);
            self.pattern_evolution.push(score);

            let analysis = self.analyze_temporal_pattern();
            diagnosis.add_analysis(analysis);
        }

        diagnosis.set_scores(self.pattern_evolution.clone());
        diagnosis.finalize();
        diagnosis
    }

    fn evaluate_block(&mut self, chunk: &[u8], diagnosis: &mut StreamDiagnosis) -> f64 {
        if let Some(bridge) = self.sator_bridge.as_ref() {
            match bridge.analyze_bytes(chunk) {
                Ok(snapshot) => {
                    diagnosis.record_sator_snapshot(&snapshot);
                    return snapshot
                        .sator_score_weighted
                        .unwrap_or(snapshot.sator_score);
                }
                Err(err) => {
                    diagnosis
                        .sator_failures
                        .push(format!("sator bridge failure: {err}"));
                    self.sator_bridge = None;
                }
            }
        }

        // Fallback heuristic: favour balanced bit density around 0.5.
        let score = fallback_block_score(chunk);
        diagnosis.record_fallback_segment();
        score
    }

    fn analyze_temporal_pattern(&self) -> TemporalAnalysis {
        let stability = self.calculate_pattern_stability();
        let cyclical = self.detect_cyclical_patterns();
        let change_points = self.detect_change_points();
        let force_correlation = self.analyze_force_correlation();
        let latest_score = self.pattern_evolution.last().copied();

        TemporalAnalysis {
            window_size: self.temporal_window.len(),
            pattern_stability: stability,
            cyclical_strength: cyclical,
            change_points,
            force_correlation,
            latest_score,
        }
    }

    fn calculate_pattern_stability(&self) -> f64 {
        if self.pattern_evolution.len() < 2 {
            return 1.0;
        }

        let diffs: f64 = self
            .pattern_evolution
            .windows(2)
            .map(|pair| (pair[1] - pair[0]).abs())
            .sum();
        let avg = diffs / (self.pattern_evolution.len() - 1) as f64;
        (1.0 - avg.min(1.0)).clamp(0.0, 1.0)
    }

    fn detect_cyclical_patterns(&self) -> f64 {
        let len = self.pattern_evolution.len();
        if len < 6 {
            return 0.0;
        }
        let lag = len.min(24).max(2) / 2;
        let mean = self.pattern_evolution.iter().copied().sum::<f64>() / len as f64;
        let numerator: f64 = (lag..len)
            .map(|idx| {
                (self.pattern_evolution[idx] - mean) * (self.pattern_evolution[idx - lag] - mean)
            })
            .sum();
        let denominator: f64 = self
            .pattern_evolution
            .iter()
            .map(|value| (value - mean).powi(2))
            .sum();
        if denominator.abs() < f64::EPSILON {
            0.0
        } else {
            (numerator / denominator).abs().clamp(0.0, 1.0)
        }
    }

    fn detect_change_points(&self) -> Vec<usize> {
        if self.pattern_evolution.len() < 3 {
            return Vec::new();
        }
        let mut changes = Vec::new();
        for (idx, window) in self.pattern_evolution.windows(3).enumerate() {
            let left = window[0];
            let middle = window[1];
            let right = window[2];
            if (middle - left).abs() > 0.12 && (right - middle).abs() > 0.12 {
                changes.push(idx + 1);
            }
        }
        changes
    }

    fn analyze_force_correlation(&self) -> f64 {
        let len = self.pattern_evolution.len();
        if len < 3 {
            return 0.0;
        }
        let mean_score = self.pattern_evolution.iter().copied().sum::<f64>() / len as f64;
        let mean_index = (len - 1) as f64 / 2.0;

        let mut cov = 0.0;
        let mut var_index = 0.0;
        let mut var_score = 0.0;
        for (idx, score) in self.pattern_evolution.iter().enumerate() {
            let idx_val = idx as f64;
            cov += (idx_val - mean_index) * (score - mean_score);
            var_index += (idx_val - mean_index).powi(2);
            var_score += (score - mean_score).powi(2);
        }
        if var_index.abs() < f64::EPSILON || var_score.abs() < f64::EPSILON {
            0.0
        } else {
            (cov / (var_index.sqrt() * var_score.sqrt())).clamp(-1.0, 1.0)
        }
    }
}

fn fallback_block_score(chunk: &[u8]) -> f64 {
    if chunk.is_empty() {
        return 0.5;
    }
    let ones = chunk
        .iter()
        .map(|byte| byte.count_ones() as usize)
        .sum::<usize>() as f64;
    let bits = (chunk.len() * 8) as f64;
    let balance = (ones / bits) - 0.5;
    (1.0 - (balance.abs() * 2.0)).clamp(0.0, 1.0)
}

#[derive(Debug, Clone, Serialize)]
pub struct TemporalAnalysis {
    pub window_size: usize,
    pub pattern_stability: f64,
    pub cyclical_strength: f64,
    pub change_points: Vec<usize>,
    pub force_correlation: f64,
    pub latest_score: Option<f64>,
}

impl TemporalAnalysis {
    pub fn new() -> Self {
        Self {
            window_size: 0,
            pattern_stability: 1.0,
            cyclical_strength: 0.0,
            change_points: Vec::new(),
            force_correlation: 0.0,
            latest_score: None,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
pub enum PatternType {
    ForcedTransitions,
    DeterministicRotation,
    LocalizedBias,
    TemporalCycles,
    ComplexInteraction,
    InsufficientData,
}

impl Default for PatternType {
    fn default() -> Self {
        PatternType::InsufficientData
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct StreamDiagnosis {
    pub analyses: Vec<TemporalAnalysis>,
    pub average_stability: f64,
    pub average_cyclical_strength: f64,
    pub average_force_correlation: f64,
    pub change_points: Vec<usize>,
    pub sator_scores: Vec<f64>,
    pub sator_score_mean: Option<f64>,
    pub sator_score_std: Option<f64>,
    pub sator_failures: Vec<String>,
    pub primary_pattern: PatternType,
    pub total_segments_analyzed: u32,
    pub total_padding_bytes: u32,
    pub segment_quality_scores: Vec<f64>,
    #[serde(skip_serializing)]
    aggregation_efficiency_samples: Vec<f64>,
    pub aggregation_efficiency: Option<f64>,
}

impl StreamDiagnosis {
    pub fn new() -> Self {
        Self {
            analyses: Vec::new(),
            average_stability: 0.0,
            average_cyclical_strength: 0.0,
            average_force_correlation: 0.0,
            change_points: Vec::new(),
            sator_scores: Vec::new(),
            sator_score_mean: None,
            sator_score_std: None,
            sator_failures: Vec::new(),
            primary_pattern: PatternType::InsufficientData,
            total_segments_analyzed: 0,
            total_padding_bytes: 0,
            segment_quality_scores: Vec::new(),
            aggregation_efficiency_samples: Vec::new(),
            aggregation_efficiency: None,
        }
    }

    pub fn add_analysis(&mut self, analysis: TemporalAnalysis) {
        self.analyses.push(analysis);
    }

    pub fn set_scores(&mut self, scores: Vec<f64>) {
        self.sator_scores = scores;
    }

    pub fn record_sator_snapshot(&mut self, snapshot: &SatorAnalysisSnapshot) {
        let segments = snapshot.segments_analyzed.unwrap_or(1);
        self.total_segments_analyzed = self.total_segments_analyzed.saturating_add(segments);
        if let Some(padding) = snapshot.padding_bytes {
            self.total_padding_bytes = self.total_padding_bytes.saturating_add(padding);
        }
        if let Some(scores) = snapshot.segment_quality_scores.as_ref() {
            self.segment_quality_scores.extend(scores.iter().copied());
        }
        if let Some(efficiency) = snapshot.aggregation_efficiency {
            self.aggregation_efficiency_samples.push(efficiency);
        }
    }

    pub fn record_fallback_segment(&mut self) {
        self.total_segments_analyzed = self.total_segments_analyzed.saturating_add(1);
    }

    pub fn finalize(&mut self) {
        if self.analyses.is_empty() {
            return;
        }

        let count = self.analyses.len() as f64;
        self.average_stability = self
            .analyses
            .iter()
            .map(|a| a.pattern_stability)
            .sum::<f64>()
            / count;
        self.average_cyclical_strength = self
            .analyses
            .iter()
            .map(|a| a.cyclical_strength)
            .sum::<f64>()
            / count;
        self.average_force_correlation = self
            .analyses
            .iter()
            .map(|a| a.force_correlation)
            .sum::<f64>()
            / count;

        let mut change_set = BTreeSet::new();
        for analysis in &self.analyses {
            change_set.extend(analysis.change_points.iter().copied());
        }
        self.change_points = change_set.into_iter().collect();

        if !self.sator_scores.is_empty() {
            let mean =
                self.sator_scores.iter().copied().sum::<f64>() / self.sator_scores.len() as f64;
            let variance = self
                .sator_scores
                .iter()
                .map(|score| (score - mean).powi(2))
                .sum::<f64>()
                / self.sator_scores.len() as f64;
            self.sator_score_mean = Some(mean);
            self.sator_score_std = Some(variance.sqrt());
        }

        if !self.aggregation_efficiency_samples.is_empty() {
            let sum = self
                .aggregation_efficiency_samples
                .iter()
                .copied()
                .sum::<f64>();
            let mean = sum / self.aggregation_efficiency_samples.len() as f64;
            self.aggregation_efficiency = Some(mean.clamp(0.0, 1.0));
        }

        self.primary_pattern = self.infer_pattern_type();
    }

    fn infer_pattern_type(&self) -> PatternType {
        if self.analyses.len() < 5 {
            return PatternType::InsufficientData;
        }

        if self.average_stability < 0.35 && self.average_cyclical_strength < 0.2 {
            PatternType::ForcedTransitions
        } else if self.average_stability > 0.9 && self.change_points.len() <= 2 {
            PatternType::DeterministicRotation
        } else if self.average_force_correlation.abs() > 0.7 {
            PatternType::LocalizedBias
        } else if self.average_cyclical_strength > 0.55 {
            PatternType::TemporalCycles
        } else {
            PatternType::ComplexInteraction
        }
    }
}

impl Default for StreamDiagnosis {
    fn default() -> Self {
        Self::new()
    }
}

impl Default for KayosStreamAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::quantum::sator_bridge::SatorPythonBridge;

    #[test]
    fn fallback_scores_balance_bits() {
        let balanced = vec![0b1010_1010u8; 32];
        let all_ones = vec![0xFFu8; 32];
        let balanced_score = fallback_block_score(&balanced);
        let ones_score = fallback_block_score(&all_ones);
        assert!(balanced_score > ones_score);
    }

    #[test]
    fn diagnosis_handles_small_stream() {
        let mut analyzer = KayosStreamAnalyzer::default();
        let stream = vec![0u8; 4096];
        let diagnosis = analyzer.analyze_stream_pattern(&stream);
        assert!(diagnosis.analyses.len() >= 3);
    }

    #[test]
    fn sator_multi_segment_resilience() {
        let bridge = match SatorPythonBridge::new() {
            Ok(bridge) => bridge,
            Err(err) => {
                eprintln!("skipping sator_multi_segment_resilience: {err}");
                return;
            }
        };
        let test_cases = vec![
            (vec![1u8; 7], "7_bytes_padding"),
            (vec![1u8; 8], "8_bytes_exact"),
            (vec![1u8; 15], "15_bytes_padding"),
            (vec![1u8; 1024], "enterprise_scale"),
        ];

        for (input, label) in test_cases {
            let snapshot = bridge
                .analyze_bytes(&input)
                .unwrap_or_else(|err| panic!("{label} failed: {err}"));

            let segments = snapshot.segments_analyzed.unwrap_or(1);
            assert!(segments >= 1, "{label} produced invalid segment count");
            assert!(
                snapshot.sator_score >= 0.0 && snapshot.sator_score <= 1.0,
                "{label} score out of bounds"
            );

            if input.len() >= 8 {
                let telemetry_present = snapshot
                    .segment_quality_scores
                    .as_ref()
                    .map(|scores| !scores.is_empty())
                    .unwrap_or(false);
                assert!(telemetry_present, "{label} missing segment telemetry");
            }
        }
    }
}
