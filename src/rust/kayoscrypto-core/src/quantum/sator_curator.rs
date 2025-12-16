use super::relojoeiro::RelojoeiroSummary;

const MIX_A: u128 = 0x9E37_79B9_7F4A_7C15_6A09_E667_F3BC_C901;
const MIX_B: u128 = 0xC2B2_AE35_9BD3_4415_85EB_CA6B_6C3B_2E59;

pub struct SatorCurator {
    state: u128,
}

impl SatorCurator {
    pub fn new(seed: u64) -> Self {
        let seed = if seed == 0 { 0x4B_4159_4F53_4D4F44 } else { seed };
        let mut state = seed as u128;
        state ^= state.rotate_left(11);
        state = state.wrapping_mul(MIX_A);
        Self { state }
    }

    pub fn curate(&self, value: u64) -> u64 {
        let rotation = (self.state as u64 & 63) as u32;
        let tweak = ((self.state >> 64) as u64) ^ 0xA5A5_A5A5_A5A5_A5A5;
        let rotated = value.rotate_left(rotation);
        rotated ^ tweak
    }

    pub fn absorb_feedback(&mut self, summary: &RelojoeiroSummary) {
        let gap = (summary.gap_deviation * 1_000_000.0) as u128;
        let perm = (summary.permutation_bias * 1_000_000.0) as u128;
        let weight = (summary.weight_bias * 1_000_000.0) as u128;

        let mix = gap.wrapping_add(perm.rotate_left(5)).wrapping_add(weight.rotate_left(11));
        self.state ^= mix ^ MIX_B;
        self.state = self.state.rotate_left(7);
        self.state = self.state.wrapping_mul(MIX_A).wrapping_add(MIX_B);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn curator_changes_output_without_zeroing_entropy() {
        let curator = SatorCurator::new(1234);
        let value = 0x0123_4567_89AB_CDEFu64;
        let curated = curator.curate(value);
        assert_ne!(value, curated);
    }

    #[test]
    fn curator_state_moves_with_feedback() {
        let mut curator = SatorCurator::new(1);
        let before = curator.curate(0);
        let summary = RelojoeiroSummary {
            gap_deviation: 0.4,
            permutation_bias: 0.2,
            weight_bias: 0.3,
        };
        curator.absorb_feedback(&summary);
        let after = curator.curate(0);
        assert_ne!(before, after);
    }
}
