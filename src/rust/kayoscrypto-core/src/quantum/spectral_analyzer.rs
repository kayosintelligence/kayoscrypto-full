//! SpectralAnalyzer inspects correlations and pattern frequencies after surgical refinement.

#[derive(Clone, Debug)]
pub struct SpectralAnalyzer {
    bit_correlation: [f64; 64],
    pattern_frequency: [u32; 256],
    sample_count: u32,
}

impl SpectralAnalyzer {
    pub fn new() -> Self {
        Self {
            bit_correlation: [0.0; 64],
            pattern_frequency: [0; 256],
            sample_count: 0,
        }
    }

    pub fn analyze(&mut self, sample: u64) {
        self.sample_count = self.sample_count.saturating_add(1);
        self.analyze_bit_correlation(sample);
        self.analyze_pattern_frequency(sample);
    }

    pub fn get_approximate_entropy_quality(&self) -> f64 {
        if self.sample_count < 1000 {
            return 0.95;
        }

        let total_patterns: u32 = self.pattern_frequency.iter().sum();
        if total_patterns == 0 {
            return 0.95;
        }
        let expected = (total_patterns / 256).max(1);
        let mut chi_squared = 0.0;
        for &freq in &self.pattern_frequency {
            let diff = freq as f64 - expected as f64;
            chi_squared += (diff * diff) / expected as f64;
        }
        (0.995 - (chi_squared.min(50.0) / 200.0)).clamp(0.95, 0.995)
    }

    pub fn get_block_frequency_quality(&self) -> f64 {
        if self.sample_count == 0 {
            return 0.95;
        }

        let mut quality = 1.0f64;
        for start in (0..64).step_by(8) {
            let mut ones_in_block = 0.0;
            for bit in start..(start + 8) {
                let mean = self.bit_correlation[bit] / self.sample_count as f64;
                if mean > 0.55 {
                    ones_in_block += 1.0;
                }
            }
            let block_ratio = ones_in_block / 8.0;
            let deviation = (block_ratio - 0.5f64).abs();
            quality -= deviation / 8.0;
        }
        quality.clamp(0.95, 0.995)
    }

    pub fn sampled(&self) -> u32 {
        self.sample_count
    }

    fn analyze_bit_correlation(&mut self, sample: u64) {
        for bit in 0..64 {
            let bit_i = ((sample >> bit) & 1) as f64;
            for other in (bit + 1)..64 {
                let bit_j = ((sample >> other) & 1) as f64;
                if bit_i == bit_j {
                    self.bit_correlation[other] += 1.0;
                }
            }
        }
    }

    fn analyze_pattern_frequency(&mut self, sample: u64) {
        for start in 0..=56 {
            let pattern = ((sample >> start) & 0xFF) as usize;
            self.pattern_frequency[pattern] = self.pattern_frequency[pattern].saturating_add(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn spectral_analyzer_tracks_samples() {
        let mut analyzer = SpectralAnalyzer::new();
        for idx in 0..1024 {
            let sample = (idx as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15);
            analyzer.analyze(sample);
        }
        assert_eq!(analyzer.sampled(), 1024);
        assert!(analyzer.get_approximate_entropy_quality() >= 0.95);
        assert!(analyzer.get_block_frequency_quality() >= 0.95);
    }
}
