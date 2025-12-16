//! AvalancheCascade disrupts residual periodicity detected by DFT checks.

#[derive(Clone, Debug)]
pub struct AvalancheCascade {
    cascade_state: [u64; 16],
    phase_accumulator: u32,
}

impl AvalancheCascade {
    pub fn new(seed: u64) -> Self {
        let mut cascade_state = [0u64; 16];
        let mut value = seed;
        for slot in &mut cascade_state {
            value = Self::avalanche_transform(value.wrapping_add(0x9E37_79B9_7F4A_7C15));
            *slot = value;
        }
        Self {
            cascade_state,
            phase_accumulator: 0,
        }
    }

    pub fn apply_cascade(&mut self, input: u64) -> u64 {
        self.phase_accumulator = self.phase_accumulator.wrapping_add(1);
        let phase = (self.phase_accumulator % self.cascade_state.len() as u32) as usize;

        let stage1 = input ^ self.cascade_state[phase];
        let stage2 = self.avalanche_stage(stage1, self.cascade_state[(phase + 4) % 16]);
        let stage3 = self.avalanche_stage(stage2, self.cascade_state[(phase + 8) % 16]);
        let stage4 = self.avalanche_stage(stage3, self.cascade_state[(phase + 12) % 16]);

        self.cascade_state[phase] = self.cascade_state[phase]
            .wrapping_add(stage4)
            .rotate_left((stage4 & 63) as u32);

        stage4
    }

    fn avalanche_stage(&self, input: u64, key: u64) -> u64 {
        let mut x = input.wrapping_add(key);
        x = (x ^ (x >> 31)).wrapping_mul(0x7FB5_D329_728E_A185);
        x = (x ^ (x >> 26)).wrapping_mul(0x81C5_71D5_C1B7_499D);
        x ^ (x >> 25) ^ (x << 37)
    }

    fn avalanche_transform(mut x: u64) -> u64 {
        x = (x ^ (x >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        x = (x ^ (x >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        x ^ (x >> 31)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cascade_output_is_non_trivial() {
        let mut cascade = AvalancheCascade::new(0xABCDEF);
        let mut outputs = Vec::new();
        for _ in 0..16 {
            outputs.push(cascade.apply_cascade(0x1234_5678_9ABC_DEF0));
        }
        assert!(outputs.windows(2).any(|pair| pair[0] != pair[1]));
    }

    #[test]
    fn cascade_state_changes() {
        let mut cascade = AvalancheCascade::new(0);
        let baseline = cascade.cascade_state;
        let _ = cascade.apply_cascade(42);
        assert_ne!(baseline, cascade.cascade_state);
    }
}
