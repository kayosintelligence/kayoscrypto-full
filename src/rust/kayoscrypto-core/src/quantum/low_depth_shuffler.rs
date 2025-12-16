#[derive(Clone, Debug)]
pub struct LowDepthShuffler {
    permutation_tables: [[u8; 256]; 2],
    shuffle_rounds: usize,
}

impl LowDepthShuffler {
    pub fn new() -> Self {
        let mut tables = [[0u8; 256]; 2];
        for (table_idx, table) in tables.iter_mut().enumerate() {
            for i in 0..256u32 {
                table[i as usize] = i
                    .wrapping_mul(167 + table_idx as u32)
                    .wrapping_add(113) as u8;
            }
        }
        Self {
            permutation_tables: tables,
            shuffle_rounds: 2,
        }
    }

    pub fn shuffle_matrix_data(&self, data: &[u8], row_size: usize) -> Vec<u8> {
        if row_size == 0 {
            return data.to_vec();
        }
        let mut shuffled = data.to_vec();
        for round in 0..self.shuffle_rounds {
            shuffled = self.apply_permutation_round(&shuffled, round, row_size);
        }
        shuffled
    }

    fn apply_permutation_round(&self, data: &[u8], round: usize, row_size: usize) -> Vec<u8> {
        // Preserve dados originais como fallback para posições não tocadas pela permutação
        let mut output = data.to_vec();
        let table = &self.permutation_tables[round % self.permutation_tables.len()];
        let row_size = row_size.min(data.len().max(1));

        for row_start in (0..data.len()).step_by(row_size) {
            let row_end = row_start.saturating_add(row_size).min(data.len());
            let row_len = row_end - row_start;
            for col in 0..row_len {
                let perm_index = col % table.len();
                let new_pos = (table[perm_index] as usize) % row_len;
                output[row_start + new_pos] = data[row_start + col];
            }
        }
        output
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn shuffler_is_deterministic() {
        let shuffler = LowDepthShuffler::new();
        let test_data: Vec<u8> = (0..1000).map(|i| (i % 251) as u8).collect();
        let result1 = shuffler.shuffle_matrix_data(&test_data, 100);
        let result2 = shuffler.shuffle_matrix_data(&test_data, 100);
        assert_eq!(result1, result2);
        assert_ne!(result1, test_data);
    }
}
