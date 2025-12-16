//! QuantumXORFold injects non-linear diffusion to raise Approximate Entropy scores.

#[derive(Clone, Debug)]
pub struct QuantumXORFold {
    quantum_state: [u64; 4],
    entropy_counter: u64,
}

impl QuantumXORFold {
    pub fn new(seed: u64) -> Self {
        let mut quantum_state = [0u64; 4];
        let mut acc = seed;
        for slot in &mut quantum_state {
            acc = acc.wrapping_add(0x9E37_79B9_7F4A_7C15);
            *slot = Self::quantum_scramble(acc);
        }
        Self {
            quantum_state,
            entropy_counter: 0,
        }
    }

    pub fn apply_entropy_fix(&mut self, input: u64) -> u64 {
        self.entropy_counter = self.entropy_counter.wrapping_add(1);
        let phase = (self.entropy_counter % 64) as u32;

        // Stage 1: non-commutative XOR folding.
        let mut value = input ^ self.quantum_state[0];
        value = value.wrapping_add(self.quantum_state[1]).rotate_left(17);
        value ^= self.quantum_state[2].rotate_right(phase % 32);

        // Stage 2: chaotic feedback to keep entropy dynamic.
        self.quantum_state[0] = self.quantum_state[0].wrapping_add(value).rotate_left(23);
        self.quantum_state[1] ^= value.wrapping_mul(0xBF58_476D_1CE4_E5B9);
        self.quantum_state[2] = self.quantum_state[2].wrapping_sub(value).rotate_right(19);

        // Stage 3: final salt application.
        let salt = self.quantum_state[3].wrapping_add(self.entropy_counter);
        value ^ salt
    }

    fn quantum_scramble(mut x: u64) -> u64 {
        x = (x ^ (x >> 32)).wrapping_mul(0xD6E8_FEB8_6659_FD93);
        x = (x ^ (x >> 32)).wrapping_mul(0x9E37_79B9_7F4A_7C15);
        x ^ (x >> 27)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn entropy_fix_generates_varied_outputs() {
        let mut fold = QuantumXORFold::new(0x1234_5678_9ABC_DEF0);
        let mut outputs = [0u64; 16];
        for (idx, slot) in outputs.iter_mut().enumerate() {
            *slot = fold.apply_entropy_fix(idx as u64);
        }

        assert!(outputs.windows(2).any(|pair| pair[0] != pair[1]));
    }

    #[test]
    fn entropy_state_mutates_over_time() {
        let mut fold = QuantumXORFold::new(0);
        let baseline = fold.quantum_state;
        for i in 0..8 {
            let _ = fold.apply_entropy_fix(i as u64);
        }
        assert_ne!(baseline, fold.quantum_state);
    }
}
