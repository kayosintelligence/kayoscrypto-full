use std::collections::HashSet;

use crate::constant_time::{ConstantTimePermutation, SecureLookup};
use crate::tables::FIBONACCI_PERMUTATIONS;

pub struct GeometricPermutations {
    fibonacci_perms: Vec<ConstantTimePermutation>,
}

impl GeometricPermutations {
    pub fn new(max_size: usize) -> Self {
        let fibonacci_perms = Self::precompute_fibonacci_permutations(max_size);
        Self { fibonacci_perms }
    }

    fn precompute_fibonacci_permutations(max_size: usize) -> Vec<ConstantTimePermutation> {
        let mut perms = Vec::with_capacity(max_size + 1);
        for n in 0..=max_size {
            if n == 0 {
                perms.push(ConstantTimePermutation::new(Vec::new()));
                continue;
            }

            let indices: Vec<usize> = if n <= 256 {
                FIBONACCI_PERMUTATIONS[n][..n]
                    .iter()
                    .map(|&value| value as usize)
                    .collect()
            } else {
                Self::compute_fibonacci_permutation(n)
            };

            debug_assert!(
                Self::is_valid_permutation(&indices),
                "Permutação inválida para n={}",
                n
            );
            perms.push(ConstantTimePermutation::new(indices));
        }
        perms
    }

    fn compute_fibonacci_permutation(n: usize) -> Vec<usize> {
        let mut fib_seq = vec![1usize, 1];
        while fib_seq.len() < n {
            let len = fib_seq.len();
            fib_seq.push(fib_seq[len - 1] + fib_seq[len - 2]);
        }

        let mut indices: Vec<usize> = (0..n).collect();
        for i in 0..n {
            let rotation = fib_seq[i] % n;
            indices[i] = (i + rotation) % n;
        }

        Self::make_bijective(&mut indices, n);
        indices
    }

    fn make_bijective(indices: &mut [usize], n: usize) {
        let mut used = HashSet::new();
        let mut available: Vec<usize> = (0..n).collect();

        for entry in indices.iter_mut() {
            if used.insert(*entry) {
                if let Some(pos) = available.iter().position(|&candidate| candidate == *entry) {
                    available.swap_remove(pos);
                }
            } else if let Some(next_free) = available.pop() {
                *entry = next_free;
                used.insert(next_free);
            }
        }
    }

    fn is_valid_permutation(indices: &[usize]) -> bool {
        let n = indices.len();
        let mut seen = vec![false; n];
        for &target in indices {
            if target >= n {
                return false;
            }
            if seen[target] {
                return false;
            }
            seen[target] = true;
        }
        true
    }

    pub fn fibonacci_spiral_permutation(&self, data: &[u8], layer: usize) -> Vec<u8> {
        let n = data.len();
        if n == 0 {
            return Vec::new();
        }

        if n <= 256 {
            let lookup = SecureLookup::new();
            let mut result = vec![0u8; n];
            for (idx, &value) in data.iter().enumerate() {
                let target = lookup.fibonacci_permutation(idx, n, layer).min(n - 1);
                result[target] = value;
            }
            return result;
        }

        if n < self.fibonacci_perms.len() {
            self.fibonacci_perms[n].apply(data)
        } else {
            ConstantTimePermutation::new(Self::compute_fibonacci_permutation(n)).apply(data)
        }
    }

    pub fn ezekiel_permutation(
        &self,
        data: &[u8],
        angles: (usize, usize),
        layer: usize,
    ) -> Vec<u8> {
        let n = data.len();
        if n == 0 {
            return Vec::new();
        }

        let indices = self.compute_ezekiel_indices(n, angles, layer);
        ConstantTimePermutation::new(indices).apply(data)
    }

    fn compute_ezekiel_indices(
        &self,
        n: usize,
        angles: (usize, usize),
        layer: usize,
    ) -> Vec<usize> {
        let mut indices: Vec<usize> = (0..n).collect();
        let (theta1, theta2) = angles;

        let lookup = SecureLookup::new();
        for j in 0..n {
            let offset = lookup.ezekiel_offset(j, n, (theta1 as i32, theta2 as i32), layer);
            indices[j] = (j + offset) % n;
        }

        Self::make_bijective(&mut indices, n);
        indices
    }

    pub fn golden_ratio_permutation(&self, data: &[u8], layer: usize) -> Vec<u8> {
        let n = data.len();
        if n == 0 {
            return Vec::new();
        }

        const GOLDEN_NUM: usize = 1618;
        const GOLDEN_DEN: usize = 1000;

        let mut indices: Vec<usize> = (0..n).collect();
        for j in 0..n {
            let gamma = (j * GOLDEN_NUM) / GOLDEN_DEN;
            let adjusted = (gamma * (1 + layer)) % n;
            indices[j] = (adjusted + j) % n;
        }

        Self::make_bijective(&mut indices, n);
        ConstantTimePermutation::new(indices).apply(data)
    }

    pub fn apply_geometric_phase(
        &self,
        data: &[u8],
        angles: (usize, usize),
        layers: usize,
    ) -> Vec<u8> {
        let mut current = data.to_vec();
        for layer in 0..layers {
            current = self.fibonacci_spiral_permutation(&current, layer);
            current = self.ezekiel_permutation(&current, angles, layer);
            current = self.golden_ratio_permutation(&current, layer);
        }
        current
    }

    pub fn reverse_geometric_phase(
        &self,
        data: &[u8],
        angles: (usize, usize),
        layers: usize,
    ) -> Vec<u8> {
        let mut current = data.to_vec();
        for layer in (0..layers).rev() {
            current = self.golden_ratio_inverse(&current, layer);
            current = self.ezekiel_inverse(&current, angles, layer);
            current = self.fibonacci_inverse(&current, layer);
        }
        current
    }

    fn fibonacci_inverse(&self, data: &[u8], _layer: usize) -> Vec<u8> {
        let n = data.len();
        if n == 0 {
            return Vec::new();
        }

        if n < self.fibonacci_perms.len() {
            self.fibonacci_perms[n].apply_inverse(data)
        } else {
            ConstantTimePermutation::new(Self::compute_fibonacci_permutation(n)).apply_inverse(data)
        }
    }

    fn ezekiel_inverse(&self, data: &[u8], angles: (usize, usize), layer: usize) -> Vec<u8> {
        let n = data.len();
        if n == 0 {
            return Vec::new();
        }
        let indices = self.compute_ezekiel_indices(n, angles, layer);
        ConstantTimePermutation::new(indices).apply_inverse(data)
    }

    fn golden_ratio_inverse(&self, data: &[u8], layer: usize) -> Vec<u8> {
        let n = data.len();
        if n == 0 {
            return Vec::new();
        }

        const GOLDEN_NUM: usize = 1618;
        const GOLDEN_DEN: usize = 1000;

        let mut indices: Vec<usize> = (0..n).collect();
        for j in 0..n {
            let gamma = (j * GOLDEN_NUM) / GOLDEN_DEN;
            let adjusted = (gamma * (1 + layer)) % n;
            indices[j] = (adjusted + j) % n;
        }

        Self::make_bijective(&mut indices, n);
        ConstantTimePermutation::new(indices).apply_inverse(data)
    }
}

impl Default for GeometricPermutations {
    fn default() -> Self {
        Self::new(256)
    }
}
