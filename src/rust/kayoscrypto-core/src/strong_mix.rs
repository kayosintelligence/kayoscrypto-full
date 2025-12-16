use sha3::{Digest, Sha3_256};

/// Direction of the StrongMix operation.
#[derive(Copy, Clone, Debug, Eq, PartialEq)]
pub enum MixDirection {
    Forward,
    Inverse,
}

/// StrongMix implementation with constant-time style access patterns.
///
/// The mixer applies a keyed Feistel network where each round relies on
/// sequential memory access only. The same construction can be run in the
/// inverse direction to recover the original buffer.
pub struct StrongMix {
    rounds: usize,
}

impl StrongMix {
    pub fn new(rounds: usize) -> Self {
        Self {
            rounds: rounds.max(1),
        }
    }

    pub fn apply(
        &self,
        data: &[u8],
        key: &[u8],
        context: &str,
        direction: MixDirection,
    ) -> Vec<u8> {
        if data.is_empty() {
            return Vec::new();
        }

        let material = self.extend_key(key, context, data.len());
        match direction {
            MixDirection::Forward => self.process(data, &material, false),
            MixDirection::Inverse => self.process(data, &material, true),
        }
    }

    fn process(&self, data: &[u8], round_key: &[u8], inverse: bool) -> Vec<u8> {
        let mut state = data.to_vec();
        if inverse {
            for round in (0..self.rounds).rev() {
                state = self.inverse_round(&state, round_key, round);
            }
        } else {
            for round in 0..self.rounds {
                state = self.forward_round(&state, round_key, round);
            }
        }
        state
    }

    fn forward_round(&self, state: &[u8], round_key: &[u8], round: usize) -> Vec<u8> {
        if state.len() <= 1 {
            return state.to_vec();
        }

        let mid = (state.len() + 1) / 2;
        let (left, right) = state.split_at(mid);
        let f_output = self.round_function(right, round_key, round, left.len());

        let mut new_right = Vec::with_capacity(left.len());
        for (idx, value) in left.iter().enumerate() {
            new_right.push(value ^ f_output[idx]);
        }

        let mut new_left = Vec::with_capacity(right.len());
        new_left.extend_from_slice(right);

        let mut result = Vec::with_capacity(state.len());
        result.extend_from_slice(&new_left);
        result.extend_from_slice(&new_right);
        result
    }

    fn inverse_round(&self, state: &[u8], round_key: &[u8], round: usize) -> Vec<u8> {
        if state.len() <= 1 {
            return state.to_vec();
        }

        let mid = (state.len() + 1) / 2;
        let right_len = state.len() - mid;
        let (left_prime, right_prime) = state.split_at(right_len);

        let right_before = left_prime;
        let f_output = self.round_function(right_before, round_key, round, right_prime.len());

        let mut left_before = Vec::with_capacity(right_prime.len());
        for (idx, value) in right_prime.iter().enumerate() {
            left_before.push(value ^ f_output[idx]);
        }

        let mut result = Vec::with_capacity(state.len());
        result.extend_from_slice(&left_before);
        result.extend_from_slice(right_before);
        result
    }

    fn round_function(
        &self,
        source: &[u8],
        round_key: &[u8],
        round: usize,
        output_len: usize,
    ) -> Vec<u8> {
        if output_len == 0 {
            return Vec::new();
        }

        let guard = source.len().max(1);
        let agg_sum: u16 = source
            .iter()
            .fold(0u16, |acc, &val| acc.wrapping_add(val as u16));
        let agg_xor: u8 = source.iter().enumerate().fold(0u8, |acc, (idx, &val)| {
            acc ^ val.rotate_left(((idx + round) % 8) as u32)
        });

        let mut output = Vec::with_capacity(output_len);
        for idx in 0..output_len {
            let key_idx = (idx + round * 13) % round_key.len();
            let key_byte = round_key[key_idx];

            let src_idx = (idx + round) % guard;
            let src_val = source.get(src_idx).copied().unwrap_or(0);
            let neigh_idx = (idx + round * 7 + 3) % guard;
            let neigh_val = source.get(neigh_idx).copied().unwrap_or(0);

            let combined = src_val
                .wrapping_add(neigh_val)
                .wrapping_add(agg_sum.rotate_right(((idx + round) % 4) as u32) as u8);
            let rotated = combined.rotate_left(((round + idx) % 7 + 1) as u32);
            let blended = agg_xor.rotate_right(((round + idx) % 5 + 1) as u32);
            let mixed = key_byte
                ^ rotated
                ^ blended
                ^ (agg_sum as u8)
                    .wrapping_add((idx as u8).wrapping_mul((round as u8).wrapping_add(1)));
            output.push(mixed);
        }
        output
    }

    fn extend_key(&self, key: &[u8], context: &str, data_len: usize) -> Vec<u8> {
        let target_len = data_len.max(32);
        let mut material = Vec::with_capacity(target_len);
        let mut counter: u32 = 0;

        while material.len() < target_len {
            let mut hasher = Sha3_256::new();
            hasher.update(key);
            hasher.update(context.as_bytes());
            hasher.update(counter.to_be_bytes());
            material.extend_from_slice(&hasher.finalize());
            counter = counter.wrapping_add(1);
        }

        material.truncate(target_len);
        material
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
    fn test_strong_mix_roundtrip() {
        let mixer = StrongMix::new(4);
        let data = b"test_data_for_strong_mix";
        let key = b"test_key";

        let mixed = mixer.apply(data, key, "test", MixDirection::Forward);
        let restored = mixer.apply(&mixed, key, "test", MixDirection::Inverse);

        assert_eq!(data.to_vec(), restored);
    }

    #[test]
    fn test_strong_mix_avalanche() {
        let mixer = StrongMix::new(4);
        let key = b"avalanche_test_key";

        let original = vec![0u8; 128];
        let mut modified = original.clone();
        modified[0] = 1;

        let mixed_orig = mixer.apply(&original, key, "avalanche", MixDirection::Forward);
        let mixed_mod = mixer.apply(&modified, key, "avalanche", MixDirection::Forward);

        let diff_bits = count_different_bits(&mixed_orig, &mixed_mod);
        let total_bits = mixed_orig.len() * 8;
        let diff_percentage = (diff_bits as f64) / (total_bits as f64) * 100.0;

        assert!(
            diff_percentage > 40.0,
            "Insufficient avalanche: {:.2}%",
            diff_percentage
        );
    }
}
