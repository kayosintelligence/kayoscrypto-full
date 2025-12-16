//! SatorBlockWhitener balances medium-size blocks to lift Block Frequency statistics.

#[derive(Clone, Debug)]
pub struct SatorBlockWhitener {
    block_history: [u64; 8],
    block_counter: usize,
}

impl SatorBlockWhitener {
    pub fn new() -> Self {
        Self {
            block_history: [0x6A09_E667_F3BC_C908; 8],
            block_counter: 0,
        }
    }

    pub fn whiten_block(&mut self, block: &mut [u64]) {
        if block.is_empty() {
            return;
        }

        for chunk in block.chunks_mut(2) {
            let idx = self.block_counter % self.block_history.len();
            let salt_a = self.block_history[idx];
            let salt_b = self.block_history[(idx + 1) % self.block_history.len()];

            if chunk.len() == 2 {
                let (a, b) = (chunk[0], chunk[1]);
                chunk[0] = self.sator_mix(a, b, salt_a);
                chunk[1] = self.sator_mix(b, a, salt_b);
                self.update_block_state(chunk[0], chunk[1]);
            } else {
                let value = chunk[0];
                chunk[0] = self.sator_mix(value, value.rotate_left(7), salt_a);
                self.update_block_state(chunk[0], chunk[0]);
            }

            self.block_counter = self.block_counter.wrapping_add(1);
        }
    }

    fn sator_mix(&self, a: u64, b: u64, salt: u64) -> u64 {
        let mut x = a ^ b ^ salt;
        x = x.wrapping_mul(0xFF51_AFD7_ED55_8CCD);
        x ^= x.rotate_left(17) ^ x.rotate_right(29);
        x = x.wrapping_mul(0xC4CE_B9FE_1A85_EC53);
        x ^ (x >> 33) ^ (x << 17)
    }

    fn update_block_state(&mut self, a: u64, b: u64) {
        let idx = self.block_counter % self.block_history.len();
        self.block_history[idx] = a.wrapping_add(b).rotate_left(41);
        let mirror = (idx + 4) % self.block_history.len();
        self.block_history[mirror] = a ^ b.rotate_right(23);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn whitener_changes_block_values() {
        let mut whitener = SatorBlockWhitener::new();
        let mut block = [0xFFFF_FFFF_FFFF_FFFFu64; 4];
        let original = block.clone();
        whitener.whiten_block(&mut block);
        assert_ne!(original, block);
    }

    #[test]
    fn whitener_balances_bitcounts() {
        let mut whitener = SatorBlockWhitener::new();
        let mut block = [0u64; 8];
        for i in 0..4 {
            block[2 * i] = u64::MAX;
        }
        whitener.whiten_block(&mut block);
        let ones: usize = block.iter().map(|value| value.count_ones() as usize).sum();
        let zeros = block.len() * 64 - ones;
        assert!((ones as isize - zeros as isize).abs() < (block.len() * 64 / 4) as isize);
    }
}
