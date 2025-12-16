pub mod analysis;
pub mod behavior;
mod constant_time;
pub mod metrics;
mod permutations;
pub mod quantum;
mod strong_mix;
mod tables;

pub use behavior::{BehaviorClassifier, BehaviorProfile, BehaviorState, RiskLevel};
pub use constant_time::{ConstantTimePermutation, SecureOps};
pub use metrics::{SecurityMetrics, TimingAnalyzer, TimingReport};
pub use permutations::GeometricPermutations;
pub use quantum::{QuantumResistanceManager, QuantumResistanceReport};
pub use strong_mix::{MixDirection, StrongMix};

use sha3::{Digest, Sha3_256};

const FEISTEL_ROUNDS: usize = 6;

/// Rust implementation of KayosCrypto with constant-time oriented primitives.
pub struct KayosCryptoSafe {
    geometric: GeometricPermutations,
    strong_mix: StrongMix,
}

/// Breakdown of the KayosCrypto pipeline for detailed analysis.
#[derive(Clone, Debug)]
pub struct PipelineBreakdown {
    pub stage_fibonacci: Vec<u8>,
    pub stage_concentric: Vec<u8>,
    pub stage_final: Vec<u8>,
}

impl PipelineBreakdown {
    pub fn empty() -> Self {
        Self {
            stage_fibonacci: Vec::new(),
            stage_concentric: Vec::new(),
            stage_final: Vec::new(),
        }
    }

    pub fn stage_slices(&self) -> [&[u8]; 3] {
        [
            self.stage_fibonacci.as_slice(),
            self.stage_concentric.as_slice(),
            self.stage_final.as_slice(),
        ]
    }

    pub fn into_final(self) -> Vec<u8> {
        self.stage_final
    }
}

impl KayosCryptoSafe {
    pub fn new() -> Self {
        Self {
            geometric: GeometricPermutations::new(256),
            strong_mix: StrongMix::new(4),
        }
    }

    pub fn encrypt(&self, data: &[u8], password: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return Vec::new();
        }

        let key = self.derive_key(password, data.len());
        let angles = self.derive_angles(&key);

        let stage_fibonacci = self.geometric.apply_geometric_phase(data, angles, 5);
        let stage_concentric = self.feistel_geometric_process(&stage_fibonacci, &key, false);
        self.strong_mix
            .apply(&stage_concentric, &key, "final", MixDirection::Forward)
    }

    /// Provides intermediate stage outputs without altering the encryption path.
    pub fn pipeline_breakdown(&self, data: &[u8], password: &[u8]) -> PipelineBreakdown {
        if data.is_empty() {
            return PipelineBreakdown::empty();
        }

        let key = self.derive_key(password, data.len());
        let angles = self.derive_angles(&key);

        let stage_fibonacci = self.geometric.apply_geometric_phase(data, angles, 5);
        let stage_concentric = self.feistel_geometric_process(&stage_fibonacci, &key, false);
        let stage_final =
            self.strong_mix
                .apply(&stage_concentric, &key, "final", MixDirection::Forward);

        PipelineBreakdown {
            stage_fibonacci,
            stage_concentric,
            stage_final,
        }
    }

    pub fn decrypt(&self, data: &[u8], password: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return Vec::new();
        }

        let key = self.derive_key(password, data.len());
        let angles = self.derive_angles(&key);

        let stage_concentric = self
            .strong_mix
            .apply(data, &key, "final", MixDirection::Inverse);
        let stage_fibonacci = self.feistel_geometric_process(&stage_concentric, &key, true);
        self.geometric
            .reverse_geometric_phase(&stage_fibonacci, angles, 5)
    }

    fn derive_key(&self, password: &[u8], length: usize) -> Vec<u8> {
        let target_len = length.max(32);
        let mut material = Vec::with_capacity(target_len);
        let mut counter: u32 = 0;

        while material.len() < target_len {
            let mut hasher = Sha3_256::new();
            hasher.update(password);
            hasher.update(counter.to_be_bytes());
            material.extend_from_slice(&hasher.finalize());
            counter = counter.wrapping_add(1);
        }

        material.truncate(target_len);
        material
    }

    fn derive_angles(&self, key: &[u8]) -> (usize, usize) {
        if key.is_empty() {
            return (0, 180);
        }

        let mut hasher = Sha3_256::new();
        hasher.update(key);
        let digest = hasher.finalize();

        let alpha = digest[0] as usize % 360;
        let beta = digest[13] as usize % 360;
        (alpha, beta)
    }

    fn feistel_geometric_process(&self, data: &[u8], key: &[u8], inverse: bool) -> Vec<u8> {
        if data.len() <= 1 {
            return data.to_vec();
        }

        let mut state = data.to_vec();
        if inverse {
            for round in (0..FEISTEL_ROUNDS).rev() {
                state = self.feistel_round_inverse(&state, key, round);
            }
        } else {
            for round in 0..FEISTEL_ROUNDS {
                state = self.feistel_round_forward(&state, key, round);
            }
        }
        state
    }

    fn feistel_round_forward(&self, state: &[u8], key: &[u8], round: usize) -> Vec<u8> {
        let mid = (state.len() + 1) / 2;
        let (left, right) = state.split_at(mid);
        let f_out = self.round_function(right, key, round, left.len());

        let mut new_right = Vec::with_capacity(left.len());
        for (idx, value) in left.iter().enumerate() {
            new_right.push(value ^ f_out[idx]);
        }

        let mut result = Vec::with_capacity(state.len());
        result.extend_from_slice(right);
        result.extend_from_slice(&new_right);
        result
    }

    fn feistel_round_inverse(&self, state: &[u8], key: &[u8], round: usize) -> Vec<u8> {
        let mid = (state.len() + 1) / 2;
        let right_len = state.len() - mid;
        let (left_prime, right_prime) = state.split_at(right_len);

        let right_before = left_prime;
        let f_out = self.round_function(right_before, key, round, right_prime.len());

        let mut left_before = Vec::with_capacity(right_prime.len());
        for (idx, value) in right_prime.iter().enumerate() {
            left_before.push(value ^ f_out[idx]);
        }

        let mut result = Vec::with_capacity(state.len());
        result.extend_from_slice(&left_before);
        result.extend_from_slice(right_before);
        result
    }

    fn round_function(
        &self,
        source: &[u8],
        key: &[u8],
        round: usize,
        output_len: usize,
    ) -> Vec<u8> {
        if output_len == 0 {
            return Vec::new();
        }

        let guard = source.len().max(1);
        let mut output = Vec::with_capacity(output_len);
        for idx in 0..output_len {
            let key_len = key.len().max(1);
            let key_idx = (idx + round * 19 + 7) % key_len;
            let key_byte = key.get(key_idx).copied().unwrap_or(0);

            let src_idx = (idx + round * 3) % guard;
            let src_val = source.get(src_idx).copied().unwrap_or(0);
            let neigh_idx = (idx + guard + round * 5 + 1) % guard;
            let neigh_val = source.get(neigh_idx).copied().unwrap_or(0);

            let rotated = src_val.rotate_left(((round + idx) % 7 + 1) as u32);
            let blended = neigh_val.rotate_right(((round + idx) % 5 + 1) as u32);
            let mixed = key_byte ^ rotated.wrapping_add(blended);
            output.push(mixed);
        }
        output
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn count_different_bits(a: &[u8], b: &[u8]) -> usize {
        a.iter()
            .zip(b.iter())
            .map(|(&x, &y)| (x ^ y).count_ones() as usize)
            .sum()
    }

    #[test]
    fn timing_analyzer_is_exported() {
        let analyzer = TimingAnalyzer::new("export_check");
        let report = analyzer.analyze();
        assert_eq!(report.sample_count, 0);
    }

    #[test]
    fn test_complete_encryption_decryption() {
        let crypto = KayosCryptoSafe::new();
        let password = b"test_password_123";

        let test_cases = [
            b"short".as_ref(),
            b"medium_length_data".as_ref(),
            b"very_long_data_sequence_that_exceeds_typical_block_sizes".as_ref(),
        ];

        for &data in &test_cases {
            let encrypted = crypto.encrypt(data, password);
            let decrypted = crypto.decrypt(&encrypted, password);
            assert_eq!(
                data,
                decrypted.as_slice(),
                "Failed for data length {}",
                data.len()
            );
        }
    }

    #[test]
    fn test_avalanche_complete() {
        let crypto = KayosCryptoSafe::new();
        let password = b"avalanche_test";

        let original = vec![0u8; 128];
        let mut modified = original.clone();
        modified[0] = 1;

        let enc_orig = crypto.encrypt(&original, password);
        let enc_mod = crypto.encrypt(&modified, password);

        let diff_bits = count_different_bits(&enc_orig, &enc_mod);
        let total_bits = enc_orig.len() * 8;
        let diff_percentage = (diff_bits as f64) / (total_bits as f64) * 100.0;

        assert!(
            diff_percentage > 45.0,
            "Weak avalanche: {:.2}%",
            diff_percentage
        );
    }
}
