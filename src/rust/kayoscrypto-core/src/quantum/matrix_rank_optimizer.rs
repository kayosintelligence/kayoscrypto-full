use core::convert::TryInto;

#[derive(Clone, Debug)]
pub struct MatrixRankOptimizer {
    lfsr_taps: [u64; 4],
    matrix_dim: usize,
}

impl MatrixRankOptimizer {
    pub const MATRIX_DIM: usize = 5_000;

    pub fn new() -> Self {
        Self {
            lfsr_taps: [
                0xD800_0000_0000_0000,
                0xBA00_0000_0000_0000,
                0xE100_0000_0000_0000,
                0x8E00_0000_0000_0000,
            ],
            matrix_dim: Self::MATRIX_DIM,
        }
    }

    pub fn process_matrix_blocks(&self, data: &[u8]) -> Vec<u8> {
        let matrix_bits = self.matrix_dim * self.matrix_dim;
        let matrix_bytes = (matrix_bits + 7) / 8;
        let mut output = Vec::with_capacity(data.len());
        let mut chunks = data.chunks_exact(matrix_bytes);

        for chunk in chunks.by_ref() {
            let processed = self.process_single_matrix(chunk);
            output.extend_from_slice(&processed);
        }

        let remainder = chunks.remainder();
        if !remainder.is_empty() {
            output.extend_from_slice(remainder);
        }

        output
    }

    fn process_single_matrix(&self, matrix_data: &[u8]) -> Vec<u8> {
        let mut output = matrix_data.to_vec();
        let mut lfsr_state = self.initialize_lfsrs(matrix_data);
        let mut chunks = output.chunks_exact_mut(8);

        for (index, word_bytes) in chunks.by_ref().enumerate() {
            let input_word = u64::from_le_bytes(word_bytes.try_into().unwrap());
            let lfsr_mix = self.advance_lfsrs(&mut lfsr_state);
            let mixed = input_word ^ lfsr_mix.rotate_left((index % 64) as u32);
            word_bytes.copy_from_slice(&mixed.to_le_bytes());
        }

        let remainder = chunks.into_remainder();
        if !remainder.is_empty() {
            for (i, byte) in remainder.iter_mut().enumerate() {
                let lfsr_mix = self.advance_lfsrs(&mut lfsr_state);
                *byte ^= ((lfsr_mix >> ((i % 8) * 8)) & 0xFF) as u8;
            }
        }

        output
    }

    fn initialize_lfsrs(&self, seed_data: &[u8]) -> [u64; 4] {
        let mut state = [0u64; 4];
        for (i, &byte) in seed_data.iter().enumerate().take(32) {
            state[i % 4] = state[i % 4]
                .rotate_left(8)
                ^ (byte as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15);
        }
        state
    }

    fn advance_lfsrs(&self, state: &mut [u64; 4]) -> u64 {
        let mut mix = 0u64;
        for i in 0..4 {
            let lsb = state[i] & 1;
            state[i] >>= 1;
            if lsb != 0 {
                state[i] ^= self.lfsr_taps[i];
            }
            mix = mix.rotate_left(16) ^ state[i];
        }
        mix
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn matrix_optimizer_is_deterministic() {
        let optimizer = MatrixRankOptimizer::new();
        let test_data = vec![0x42u8; 3_125_000];
        let result1 = optimizer.process_matrix_blocks(&test_data);
        let result2 = optimizer.process_matrix_blocks(&test_data);
        assert_eq!(result1, result2);
    }

    #[test]
    fn lfsr_initialization_is_repeatable() {
        let optimizer = MatrixRankOptimizer::new();
        let seed = vec![0xAAu8; 32];
        let state1 = optimizer.initialize_lfsrs(&seed);
        let state2 = optimizer.initialize_lfsrs(&seed);
        assert_eq!(state1, state2);
    }
}
