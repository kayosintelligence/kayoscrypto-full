use std::cmp::Ordering;

#[derive(Clone, Debug, Default)]
pub struct RelojoeiroSummary {
    pub gap_deviation: f64,
    pub permutation_bias: f64,
    pub weight_bias: f64,
}

pub struct Relojoeiro {
    bins: usize,
}

impl Relojoeiro {
    pub fn new(bins: usize) -> Self {
        let bins = bins.max(4);
        Self { bins }
    }

    pub fn analyze_block(&mut self, block: &[u8]) -> RelojoeiroSummary {
        if block.is_empty() {
            return RelojoeiroSummary::default();
        }

        let gap = self.compute_gap_deviation(block);
        let permutation = self.compute_permutation_bias(block);
        let weight = self.compute_weight_bias(block);

        RelojoeiroSummary {
            gap_deviation: gap,
            permutation_bias: permutation,
            weight_bias: weight,
        }
    }

    fn compute_gap_deviation(&self, block: &[u8]) -> f64 {
        let mut counts = vec![0usize; self.bins];
        for &byte in block {
            let idx = ((byte as usize) * self.bins) >> 8;
            let idx = idx.min(self.bins - 1);
            counts[idx] += 1;
        }

        let expected = block.len() as f64 / self.bins as f64;
        if expected == 0.0 {
            return 0.0;
        }

        counts
            .into_iter()
            .map(|count| ((count as f64 - expected).abs()) / expected)
            .fold(0.0f64, f64::max)
            .min(1.0)
    }

    fn compute_permutation_bias(&self, block: &[u8]) -> f64 {
        if block.len() < 4 {
            return 0.0;
        }

        let mut ascending = 0usize;
        let mut descending = 0usize;

        for window in block.windows(4) {
            let mut trend = Ordering::Equal;
            for pair in window.windows(2) {
                let cmp = pair[0].cmp(&pair[1]);
                if cmp == Ordering::Equal {
                    trend = Ordering::Equal;
                    break;
                }
                if trend == Ordering::Equal {
                    trend = cmp;
                } else if trend != cmp {
                    trend = Ordering::Equal;
                    break;
                }
            }

            match trend {
                Ordering::Less => ascending += 1,
                Ordering::Greater => descending += 1,
                Ordering::Equal => {}
            }
        }

        let total = block.len().saturating_sub(3);
        if total == 0 {
            return 0.0;
        }

        let mixed = total - (ascending + descending);

        let asc_ratio = ascending as f64 / total as f64;
        let desc_ratio = descending as f64 / total as f64;
        let flat_ratio = mixed as f64 / total as f64;

        let max_ratio = asc_ratio.max(desc_ratio).max(flat_ratio);
        let min_ratio = asc_ratio.min(desc_ratio).min(flat_ratio);
        (max_ratio - min_ratio).clamp(0.0, 1.0)
    }

    fn compute_weight_bias(&self, block: &[u8]) -> f64 {
        let ones: usize = block.iter().map(|byte| byte.count_ones() as usize).sum();
        let total_bits = block.len() * 8;
        if total_bits == 0 {
            return 0.0;
        }

        let ratio = ones as f64 / total_bits as f64;
        ((ratio - 0.5).abs() * 2.0).min(1.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn summary_bounds() {
        let mut relojoeiro = Relojoeiro::new(16);
        let summary = relojoeiro.analyze_block(&[0u8; 32]);
        assert!((0.0..=1.0).contains(&summary.gap_deviation));
        assert!((0.0..=1.0).contains(&summary.permutation_bias));
        assert!((0.0..=1.0).contains(&summary.weight_bias));
    }

    #[test]
    fn gap_detects_bias() {
        let mut relojoeiro = Relojoeiro::new(16);
        let mut block = vec![0u8; 64];
        block.extend([250u8; 64]);
        let summary = relojoeiro.analyze_block(&block);
        assert!(summary.gap_deviation > 0.2);
    }

    #[test]
    fn weight_detects_unbalance() {
        let mut relojoeiro = Relojoeiro::new(16);
        let block = vec![0xFFu8; 64];
        let summary = relojoeiro.analyze_block(&block);
        assert!(summary.weight_bias > 0.9);
    }
}
