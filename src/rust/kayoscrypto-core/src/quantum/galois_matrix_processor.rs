use core::convert::TryInto;

#[derive(Clone, Debug)]
pub struct GaloisMatrixProcessor {
    mixing_rounds: usize,
}

impl GaloisMatrixProcessor {
    pub fn new() -> Self {
        Self { mixing_rounds: 2 }
    }

    pub fn apply_galois_folding(&self, data: &[u8]) -> Vec<u8> {
        let mut processed = data.to_vec();
        let chunk_size = 64; // 8x8 bytes
        for chunk in processed.chunks_mut(chunk_size) {
            if chunk.len() == chunk_size {
                self.process_block(chunk);
            }
        }
        processed
    }

    fn process_block(&self, block: &mut [u8]) {
        let mut words = [0u64; 8];
        for (i, word) in words.iter_mut().enumerate() {
            let start = i * 8;
            let slice = &block[start..start + 8];
            *word = u64::from_le_bytes(slice.try_into().unwrap());
        }

        for _ in 0..self.mixing_rounds {
            self.mix_words(&mut words);
        }

        for (i, word) in words.iter().enumerate() {
            let start = i * 8;
            block[start..start + 8].copy_from_slice(&word.to_le_bytes());
        }
    }

    fn mix_words(&self, words: &mut [u64; 8]) {
        for word in words.iter_mut() {
            *word = word.wrapping_mul(0x9E37_79B9_7F4A_7C15);
            *word ^= *word >> 32;
        }
        for i in 0..8 {
            let next = words[(i + 1) % 8];
            words[i] ^= next.rotate_left(17);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn galois_folding_is_deterministic() {
        let processor = GaloisMatrixProcessor::new();
        let test_data = vec![0x5Au8; 64];
        let result1 = processor.apply_galois_folding(&test_data);
        let result2 = processor.apply_galois_folding(&test_data);
        assert_eq!(result1, result2);
        assert_ne!(result1, test_data);
    }
}
