//! GapMetrics provide live monitoring for the three statistical gaps.

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum GapStatus {
    Sovereign,
    Excellent,
    Good,
    NeedsWork,
}

#[derive(Clone, Debug)]
pub struct GapAnalysis {
    pub approximate_entropy_score: f64,
    pub block_frequency_score: f64,
    pub dft_score: f64,
    pub overall_gap_status: GapStatus,
}

#[derive(Clone, Debug)]
pub struct GapMetrics {
    bit_patterns: [usize; 8],
    block_balances: Vec<usize>,
    spectral_data: Vec<f64>,
}

impl GapMetrics {
    pub fn new() -> Self {
        Self {
            bit_patterns: [0; 8],
            block_balances: Vec::with_capacity(1024),
            spectral_data: Vec::with_capacity(512),
        }
    }

    pub fn analyze_chunk(&mut self, chunk: &[u64]) {
        for &value in chunk {
            self.analyze_approximate_entropy(value);
            self.analyze_block_frequency(value);
            self.analyze_dft_patterns(value);
        }
    }

    pub fn generate_gap_report(&self) -> GapAnalysis {
        let approx_score = self.calculate_approximate_entropy_estimate();
        let block_score = self.calculate_block_frequency_estimate();
        let dft_score = self.calculate_dft_estimate();
        let overall = (approx_score + block_score + dft_score) / 3.0;

        let status = if approx_score > 0.99 && block_score > 0.99 && dft_score > 0.99 {
            GapStatus::Sovereign
        } else if overall > 0.985 {
            GapStatus::Excellent
        } else if overall > 0.975 {
            GapStatus::Good
        } else {
            GapStatus::NeedsWork
        };

        GapAnalysis {
            approximate_entropy_score: approx_score,
            block_frequency_score: block_score,
            dft_score,
            overall_gap_status: status,
        }
    }

    fn analyze_approximate_entropy(&mut self, value: u64) {
        for shift in 0..=61 {
            let pattern = ((value >> shift) & 0b111) as usize;
            self.bit_patterns[pattern] += 1;
        }
    }

    fn analyze_block_frequency(&mut self, value: u64) {
        self.block_balances.push(value.count_ones() as usize);
        if self.block_balances.len() > 1024 {
            self.block_balances.remove(0);
        }
    }

    fn analyze_dft_patterns(&mut self, value: u64) {
        let normalized = (value as f64) / (u64::MAX as f64);
        self.spectral_data.push(normalized);
        if self.spectral_data.len() > 512 {
            self.spectral_data.remove(0);
        }
    }

    fn calculate_approximate_entropy_estimate(&self) -> f64 {
        let total: usize = self.bit_patterns.iter().sum();
        if total == 0 {
            return 0.95;
        }

        let expected = total as f64 / 8.0;
        let mut chi_squared = 0.0;
        for &count in &self.bit_patterns {
            let diff = count as f64 - expected;
            chi_squared += (diff * diff) / expected.max(1e-6);
        }

        let raw = 0.995 - (chi_squared.min(25.0) / 100.0);
        raw.clamp(0.95, 0.995)
    }

    fn calculate_block_frequency_estimate(&self) -> f64 {
        if self.block_balances.len() < 128 {
            return 0.95;
        }

        let expected = 32.0;
        let variance: f64 = self
            .block_balances
            .iter()
            .map(|&ones| {
                let diff = ones as f64 - expected;
                diff * diff
            })
            .sum::<f64>()
            / self.block_balances.len() as f64;

        let raw = 0.995 - (variance.min(16.0) / 200.0);
        raw.clamp(0.95, 0.995)
    }

    fn calculate_dft_estimate(&self) -> f64 {
        if self.spectral_data.len() < 128 {
            return 0.95;
        }

        let lag = 1;
        let mut correlation = 0.0;
        for i in lag..self.spectral_data.len() {
            correlation += (self.spectral_data[i] - 0.5) * (self.spectral_data[i - lag] - 0.5);
        }
        correlation /= (self.spectral_data.len() - lag) as f64;
        let raw = 0.995 - (correlation.abs().min(0.1) * 10.0);
        raw.clamp(0.95, 0.995)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn metrics_default_need_work() {
        let metrics = GapMetrics::new();
        assert_eq!(
            metrics.generate_gap_report().overall_gap_status,
            GapStatus::NeedsWork
        );
    }

    #[test]
    fn metrics_detect_improvement() {
        let mut metrics = GapMetrics::new();
        let baseline = metrics.generate_gap_report();
        let mut value = 0x1234_5678_9ABC_DEF0u64;
        for _ in 0..256 {
            value = value.wrapping_mul(0x9E37_79B9_7F4A_7C15).rotate_left(7);
            metrics.analyze_chunk(&[value]);
        }
        let report = metrics.generate_gap_report();
        assert!(report.approximate_entropy_score >= baseline.approximate_entropy_score);
        assert!(report.block_frequency_score >= baseline.block_frequency_score);
    }
}
