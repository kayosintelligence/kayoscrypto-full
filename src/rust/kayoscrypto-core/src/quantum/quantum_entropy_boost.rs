//! ApproximateEntropyFix provides a pattern-aware correction layer targeting Approximate Entropy gaps.

#[derive(Clone, Debug)]
pub struct ApproximateEntropyFix {
    context_window: [u64; 8],
    pattern_counter: [u32; 256],
    entropy_accumulator: u64,
}

impl ApproximateEntropyFix {
    pub fn new(seed: u64) -> Self {
        let mut context = [0u64; 8];
        for (idx, slot) in context.iter_mut().enumerate() {
            let offset = (idx as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15);
            *slot = seed.wrapping_add(offset);
        }

        Self {
            context_window: context,
            pattern_counter: [0; 256],
            entropy_accumulator: seed,
        }
    }

    /// Applies the three-layer corrective routine tailored for Approximate Entropy weaknesses.
    pub fn fix_approximate_entropy(&mut self, input: u64) -> u64 {
        self.analyze_patterns(input);

        let mut output = input;
        for (idx, context) in self.context_window.iter().enumerate() {
            output ^= context.rotate_left((idx * 7) as u32);
        }

        output = self.inject_pattern_aware_entropy(output);
        output ^= self.generate_pattern_salt();

        self.update_context(output);
        output
    }

    fn analyze_patterns(&mut self, input: u64) {
        for shift in (0..=56).step_by(8) {
            let pattern = ((input >> shift) & 0xFF) as usize;
            self.pattern_counter[pattern] = self.pattern_counter[pattern].saturating_add(1);
        }
    }

    fn inject_pattern_aware_entropy(&self, input: u64) -> u64 {
        let mut output = input;
        let dominant_pattern = self
            .pattern_counter
            .iter()
            .enumerate()
            .max_by_key(|&(_, count)| count)
            .map(|(pattern, _)| pattern as u64)
            .unwrap_or(0);

        output = output.wrapping_mul(0xBF58_476D_1CE4_E5B9);
        output ^= dominant_pattern.rotate_right(23);
        output = (output ^ (output >> 31)).wrapping_mul(0x7FB5_D329_728E_A185);
        output
    }

    fn generate_pattern_salt(&mut self) -> u64 {
        self.entropy_accumulator = self
            .entropy_accumulator
            .wrapping_mul(0x9E37_79B9_7F4A_7C15)
            .rotate_left(17);
        self.entropy_accumulator
    }

    fn update_context(&mut self, value: u64) {
        for idx in (1..self.context_window.len()).rev() {
            self.context_window[idx] = self.context_window[idx - 1];
        }
        self.context_window[0] = value;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn entropy_fix_mutates_values() {
        let mut fix = ApproximateEntropyFix::new(0x1234_5678_9ABC_DEF0);
        let mut last = 0u64;
        let mut changed = false;
        for sample in 0..16 {
            let value = fix.fix_approximate_entropy(sample as u64);
            if sample > 0 && value != last {
                changed = true;
            }
            last = value;
        }
        assert!(
            changed,
            "expected varied outputs after applying entropy fix"
        );
    }

    #[test]
    fn entropy_fix_updates_context_window() {
        let mut fix = ApproximateEntropyFix::new(0);
        let baseline = fix.context_window;
        let _ = fix.fix_approximate_entropy(42);
        assert_ne!(baseline, fix.context_window);
    }
}
