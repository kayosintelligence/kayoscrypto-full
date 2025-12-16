//! BlockFrequencyFix performs dual corrections for Block Frequency and Cumulative Sums gaps.

#[derive(Clone, Debug)]
pub struct BlockFrequencyFix {
    block_histogram: [u32; 64],
    running_sum: i32,
    block_counter: u32,
    correction_aggressiveness: u32,
}

impl BlockFrequencyFix {
    pub fn new() -> Self {
        Self {
            block_histogram: [0; 64],
            running_sum: 0,
            block_counter: 0,
            correction_aggressiveness: 5,
        }
    }

    /// Applies aggressive, multi-step balancing of bit and block distributions.
    pub fn fix_block_frequency(&mut self, input: u64) -> u64 {
        self.block_counter = self.block_counter.wrapping_add(1);
        let mut output = self.aggressive_bit_balancing(input);
        output = self.force_block_uniformity(output);
        self.strong_cumulative_correction(output)
    }

    pub fn running_sum(&self) -> i32 {
        self.running_sum
    }

    pub fn set_aggressiveness(&mut self, level: u32) {
        self.correction_aggressiveness = level.clamp(1, 10);
    }

    fn aggressive_bit_balancing(&mut self, input: u64) -> u64 {
        let mut output = input;
        for bit in 0..64 {
            if (output >> bit) & 1 == 1 {
                self.block_histogram[bit] = self.block_histogram[bit].saturating_add(1);
            }
        }

        let interval = (8usize / self.correction_aggressiveness.max(1) as usize).max(1);
        if (self.block_counter as usize) % interval == 0 {
            output = self.apply_immediate_correction(output);
        }

        output
    }

    fn apply_immediate_correction(&self, input: u64) -> u64 {
        let mut output = input;
        let samples = self.block_counter.max(1);
        let target = ((samples as f64) * 0.5).ceil() as i32;
        let tolerance = (self.correction_aggressiveness as i32).max(1) * 2;
        for bit in 0..64 {
            let current = self.block_histogram[bit] as i32;
            let diff = current - target;
            if diff > tolerance {
                output &= !(1u64 << bit);
            } else if diff < -tolerance {
                output |= 1u64 << bit;
            }
        }
        output
    }

    fn force_block_uniformity(&self, input: u64) -> u64 {
        let mut output = input;
        let max_adjust = self.correction_aggressiveness.min(8) as usize;
        for block in 0..8 {
            let start_bit = block * 8;
            let mut ones_positions = [0usize; 8];
            let mut zeros_positions = [0usize; 8];
            let mut ones_count = 0usize;
            let mut zeros_count = 0usize;

            for offset in 0..8 {
                let pos = start_bit + offset;
                if (output >> pos) & 1 == 1 {
                    ones_positions[ones_count] = pos;
                    ones_count += 1;
                } else {
                    zeros_positions[zeros_count] = pos;
                    zeros_count += 1;
                }
            }

            if ones_count > 1 {
                self.rotate_positions(&mut ones_positions[..ones_count], output, block as u32 + 11);
            }
            if zeros_count > 1 {
                self.rotate_positions(&mut zeros_positions[..zeros_count], output, block as u32);
            }

            let target = 4usize;
            if ones_count > target {
                let mut adjustments = (ones_count - target).min(max_adjust);
                let mut idx = 0usize;
                while adjustments > 0 && idx < ones_count {
                    let pos = ones_positions[idx];
                    output &= !(1u64 << pos);
                    adjustments -= 1;
                    idx += 1;
                }
            } else if ones_count < target {
                let mut adjustments = (target - ones_count).min(max_adjust);
                let mut idx = 0usize;
                while adjustments > 0 && idx < zeros_count {
                    let pos = zeros_positions[idx];
                    output |= 1u64 << pos;
                    adjustments -= 1;
                    idx += 1;
                }
            }
        }

        output
    }

    fn strong_cumulative_correction(&mut self, input: u64) -> u64 {
        let mut output = input;
        let ones = output.count_ones() as i32;
        let zeros = 64 - ones;
        let net = ones - zeros;
        self.running_sum = self.running_sum.saturating_add(net);

        let threshold = 500i32.saturating_sub((self.correction_aggressiveness as i32 - 1) * 30);
        if self.running_sum.abs() > threshold {
            if self.running_sum > 0 {
                output = self.inject_zeros_aggressive(output);
                self.running_sum = self.running_sum.saturating_sub(300);
            } else {
                output = self.inject_ones_aggressive(output);
                self.running_sum = self.running_sum.saturating_add(300);
            }
        }

        output
    }

    fn inject_zeros_aggressive(&self, input: u64) -> u64 {
        let flips = self.correction_aggressiveness.min(8) as usize;
        if flips == 0 {
            return input;
        }

        let mut output = input;
        let mut seed =
            input.rotate_left(19) ^ (self.block_counter as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15);

        let mut applied = 0usize;
        let mut attempts = 0usize;
        while applied < flips && attempts < 256 {
            let pos = (seed & 0x3F) as u32;
            if (output >> pos) & 1 == 1 {
                output &= !(1u64 << pos);
                applied += 1;
            }
            seed = seed.wrapping_mul(0xBF58_476D_1CE4_E5B9).rotate_left(13) ^ 0x94D0_49BB_1331_11EB;
            attempts += 1;
        }

        output
    }

    fn inject_ones_aggressive(&self, input: u64) -> u64 {
        let flips = self.correction_aggressiveness.min(8) as usize;
        if flips == 0 {
            return input;
        }

        let mut output = input;
        let mut seed = input.rotate_right(23)
            ^ (self.block_counter as u64).wrapping_mul(0xD1B5_4A32_D192_ED03);

        let mut applied = 0usize;
        let mut attempts = 0usize;
        while applied < flips && attempts < 256 {
            let pos = (seed & 0x3F) as u32;
            if (output >> pos) & 1 == 0 {
                output |= 1u64 << pos;
                applied += 1;
            }
            seed = seed.wrapping_mul(0x94D0_49BB_1331_11EB).rotate_left(7) ^ 0xD1B5_4A32_D192_ED03;
            attempts += 1;
        }

        output
    }

    fn rotate_positions(&self, positions: &mut [usize], seed_input: u64, salt: u32) {
        if positions.len() <= 1 {
            return;
        }

        let mix = seed_input.rotate_left((self.block_counter as u32).wrapping_add(salt) % 64)
            ^ ((self.block_counter as u64) << 17)
            ^ ((salt as u64) << 23);
        let offset = (mix as usize) % positions.len();
        positions.rotate_left(offset);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn block_fix_mutates_values_over_time() {
        let mut fix = BlockFrequencyFix::new();
        let mut mutated = false;
        for _ in 0..256 {
            let next = fix.fix_block_frequency(0xFFFF_FFFF_FFFF_FFFFu64);
            if next != 0xFFFF_FFFF_FFFF_FFFFu64 {
                mutated = true;
                break;
            }
        }
        assert!(mutated, "expected block fix to alter the stream");
    }

    #[test]
    fn block_fix_controls_running_sum() {
        let mut fix = BlockFrequencyFix::new();
        fix.set_aggressiveness(8);
        let mut exceeded = false;
        let mut restored = false;
        for _ in 0..256 {
            let output = fix.fix_block_frequency(0xFFFF_FFFF_FFFF_FFFFu64);
            if output != 0xFFFF_FFFF_FFFF_FFFFu64 {
                exceeded = true;
            }
            if exceeded && fix.running_sum().abs() <= 1000 {
                restored = true;
                break;
            }
        }
        assert!(exceeded, "running sum must exceed threshold at least once");
        assert!(restored, "running sum should decay back under threshold");
    }
}
