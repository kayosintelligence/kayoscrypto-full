use std::f64::consts::PI;

use sha3::{Digest, Sha3_256};

const SPONGE_STATE: usize = 64;
const GOLDEN_RATIO: f64 = 1.618_033_988_749_895;
const FIB_MAX_TERMS: usize = 24;

/// Result of the refinement process combining the transformed payload and updated metrics.
#[derive(Clone, Debug)]
pub struct EntropyRefinementResult {
    pub refined: Vec<u8>,
    pub intermediate: Vec<u8>,
    pub metrics: EntropyMetrics,
}

/// Coordinates all sub-components of the MRE v2.0 pipeline.
pub struct EntropyRefinementModule {
    sponge: SatorSpongeEnterprise,
    fold: FibonacciFold,
    pool: GeometricEntropyPool,
}

impl EntropyRefinementModule {
    pub fn new(seed: &[u8]) -> Self {
        let sponge = SatorSpongeEnterprise::new(seed);
        let fold = FibonacciFold::default();
        let pool = GeometricEntropyPool::new(seed);
        Self { sponge, fold, pool }
    }

    pub fn refine(&mut self, payload: &[u8]) -> EntropyRefinementResult {
        let mut staged = payload.to_vec();
        self.sponge.absorb(&staged);
        let permutation = self.sponge.permutation(staged.len());
        apply_permutation(&mut staged, &permutation);

        let folded = self.fold.apply(&staged);
        let interm = self.pool.reharmonize(&folded);

        let metrics = EntropyMetrics::analyze(&interm);

        EntropyRefinementResult {
            refined: folded,
            intermediate: interm,
            metrics,
        }
    }
}

/// Implements the Sator Sponge using reversible permutations derived from the absorbed state.
#[derive(Clone, Debug)]
struct SatorSpongeEnterprise {
    state: [u8; SPONGE_STATE],
}

impl SatorSpongeEnterprise {
    fn new(seed: &[u8]) -> Self {
        let mut hasher = Sha3_256::new();
        hasher.update(seed);
        let digest = hasher.finalize();
        let mut state = [0u8; SPONGE_STATE];
        for (idx, byte) in state.iter_mut().enumerate() {
            *byte = digest[idx % digest.len()] ^ ((idx as u8).rotate_left(3));
        }
        Self { state }
    }

    fn absorb(&mut self, data: &[u8]) {
        for (idx, chunk) in data.chunks(SPONGE_STATE).enumerate() {
            for (pos, &value) in chunk.iter().enumerate() {
                let lane = (pos + idx) % SPONGE_STATE;
                self.state[lane] = self.state[lane].rotate_left(1) ^ value;
            }
            self.rotate_state(idx as u32 + 7);
        }
    }

    fn permutation(&self, length: usize) -> Vec<usize> {
        if length == 0 {
            return Vec::new();
        }

        let mut indices: Vec<usize> = (0..length).collect();
        let mut cursor = 0usize;
        for round in 0..(length.max(1)) {
            let lane = self.state[round % SPONGE_STATE] as usize;
            cursor = (cursor + lane + round) % length;
            let swap_with = (cursor + lane) % length;
            indices.swap(cursor, swap_with);
        }
        indices
    }

    fn rotate_state(&mut self, amount: u32) {
        let rotation = (amount % SPONGE_STATE as u32) as usize;
        self.state.rotate_left(rotation);
        for idx in 0..SPONGE_STATE {
            self.state[idx] = self.state[idx]
                .rotate_left((idx as u32 % 7) + 1)
                .wrapping_add((idx as u8).rotate_right(1));
        }
    }
}

/// Applies Fibonacci-driven segment rotations that preserve length and data integrity.
#[derive(Clone, Debug)]
struct FibonacciFold {
    sequence: [usize; FIB_MAX_TERMS],
}

impl Default for FibonacciFold {
    fn default() -> Self {
        let mut sequence = [0usize; FIB_MAX_TERMS];
        sequence[0] = 1;
        sequence[1] = 1;
        for idx in 2..FIB_MAX_TERMS {
            sequence[idx] = sequence[idx - 1] + sequence[idx - 2];
        }
        Self { sequence }
    }
}

impl FibonacciFold {
    fn apply(&self, data: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return Vec::new();
        }

        let mut output = data.to_vec();
        let mut cursor = 0usize;
        for &fib in &self.sequence {
            if cursor >= output.len() {
                break;
            }
            let segment_len = fib.min(output.len() - cursor);
            if segment_len == 0 {
                break;
            }
            let offset = (fib % segment_len).max(1);
            let end = cursor + segment_len;
            output[cursor..end].rotate_left(offset);
            cursor = end;
        }
        output
    }
}

/// Maintains a deterministic pool that projects the buffer onto geometric harmonics.
#[derive(Clone, Debug)]
struct GeometricEntropyPool {
    pool: Vec<u8>,
    cursor: usize,
}

impl GeometricEntropyPool {
    fn new(seed: &[u8]) -> Self {
        let mut hasher = Sha3_256::new();
        hasher.update(seed);
        hasher.update(&seed.len().to_be_bytes());
        let digest = hasher.finalize();
        let pool = digest
            .iter()
            .copied()
            .cycle()
            .take(SPONGE_STATE * 2)
            .collect();
        Self { pool, cursor: 0 }
    }

    fn reharmonize(&mut self, data: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return Vec::new();
        }

        let mut output = Vec::with_capacity(data.len());
        for (idx, &value) in data.iter().enumerate() {
            let harmonics = self.sample_harmonics(idx);
            let shift = ((harmonics.0 as usize + harmonics.1 as usize) % 8) as u32;
            let rotated = value.rotate_left(shift);
            output.push(rotated);
            self.cursor = (self.cursor + 1) % self.pool.len();
        }
        output
    }

    fn sample_harmonics(&self, index: usize) -> (u8, u8) {
        let primary = self.pool[(self.cursor + index) % self.pool.len()];
        let secondary = self.pool[(self.cursor + index * 3 + 7) % self.pool.len()];
        (primary, secondary)
    }
}

/// Computes key entropy metrics used by the MRE pipeline.
#[derive(Clone, Debug, Default)]
pub struct EntropyMetrics {
    pub frequency_score: f64,
    pub approximate_entropy: f64,
    pub linear_complexity: f64,
    pub golden_alignment: f64,
}

impl EntropyMetrics {
    pub fn analyze(data: &[u8]) -> Self {
        if data.is_empty() {
            return Self::default();
        }

        let frequency_score = compute_frequency_score(data);
        let approximate_entropy = compute_approximate_entropy(data);
        let linear_complexity = compute_linear_complexity(data);
        let golden_alignment = compute_golden_alignment(data);

        Self {
            frequency_score,
            approximate_entropy,
            linear_complexity,
            golden_alignment,
        }
    }

    pub fn aggregate(results: &[EntropyMetrics]) -> Self {
        if results.is_empty() {
            return Self::default();
        }

        let mut aggregate = Self::default();
        for metrics in results {
            aggregate.frequency_score += metrics.frequency_score;
            aggregate.approximate_entropy += metrics.approximate_entropy;
            aggregate.linear_complexity += metrics.linear_complexity;
            aggregate.golden_alignment += metrics.golden_alignment;
        }

        let denom = results.len() as f64;
        aggregate.frequency_score /= denom;
        aggregate.approximate_entropy /= denom;
        aggregate.linear_complexity /= denom;
        aggregate.golden_alignment /= denom;
        aggregate
    }
}

fn apply_permutation(buffer: &mut [u8], permutation: &[usize]) {
    assert_eq!(buffer.len(), permutation.len());
    let mut visited = vec![false; buffer.len()];
    for start in 0..buffer.len() {
        if visited[start] {
            continue;
        }
        let mut current = start;
        let mut prev_value = buffer[start];
        loop {
            visited[current] = true;
            let next = permutation[current];
            if visited[next] {
                buffer[current] = prev_value;
                break;
            }
            let tmp = buffer[next];
            buffer[next] = prev_value;
            prev_value = tmp;
            current = next;
        }
    }
}

fn compute_frequency_score(data: &[u8]) -> f64 {
    let mut counts = [0usize; 256];
    for &byte in data {
        counts[byte as usize] += 1;
    }
    let length = data.len() as f64;
    let expected = length / 256.0;
    let mut variance = 0.0;
    for &count in &counts {
        let diff = count as f64 - expected;
        variance += diff * diff;
    }
    let chi_square = variance / expected.max(1.0);
    (1.0 / (1.0 + chi_square / length.max(1.0))).clamp(0.0, 1.0)
}

fn compute_approximate_entropy(data: &[u8]) -> f64 {
    let mut entropy = 0.0;
    for window in data.windows(2) {
        let diff = (window[0] as i16 - window[1] as i16).abs() as f64;
        entropy += (diff / 255.0).powi(2);
    }
    let norm = (data.len().saturating_sub(1)) as f64;
    if norm == 0.0 {
        return 0.0;
    }
    (entropy / norm).clamp(0.0, 1.0)
}

fn compute_linear_complexity(data: &[u8]) -> f64 {
    let mut complexity = 0.0;
    let mut register = 0u32;
    for (idx, &byte) in data.iter().enumerate() {
        let phi_based = ((idx as f64 + 1.0) * GOLDEN_RATIO).fract();
        register ^= ((byte as u32) << (idx % 8)) ^ ((phi_based * 255.0) as u32);
        complexity += register.count_ones() as f64;
    }
    let max_complexity = (data.len() * 8) as f64;
    (complexity / max_complexity).clamp(0.0, 1.0)
}

fn compute_golden_alignment(data: &[u8]) -> f64 {
    let mut alignment = 0.0;
    for (idx, &byte) in data.iter().enumerate() {
        let angle = ((idx as f64 + 1.0) / GOLDEN_RATIO) % 1.0;
        let wave = (2.0 * PI * angle).sin().abs();
        alignment += wave * (byte as f64 / 255.0);
    }
    let denom = data.len() as f64;
    if denom == 0.0 {
        return 0.0;
    }
    (alignment / denom).clamp(0.0, 1.0)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sponge_permutation_is_bijective() {
        let sponge = SatorSpongeEnterprise::new(b"seed");
        let len = 128;
        let permutation = sponge.permutation(len);
        let mut sorted = permutation.clone();
        sorted.sort_unstable();
        let expected: Vec<usize> = (0..len).collect();
        assert_eq!(sorted, expected);
    }

    #[test]
    fn fibonacci_fold_preserves_length() {
        let fold = FibonacciFold::default();
        let data: Vec<u8> = (0..64).collect();
        let folded = fold.apply(&data);
        assert_eq!(folded.len(), data.len());
        assert_ne!(folded, data);
    }

    #[test]
    fn geometric_pool_reharmonizes_deterministically() {
        let mut pool = GeometricEntropyPool::new(b"seed");
        let first = pool.reharmonize(&[1, 2, 3, 4]);
        let mut pool_again = GeometricEntropyPool::new(b"seed");
        let second = pool_again.reharmonize(&[1, 2, 3, 4]);
        assert_eq!(first, second);
    }

    #[test]
    fn metrics_within_bounds() {
        let data: Vec<u8> = (0..255).collect();
        let metrics = EntropyMetrics::analyze(&data);
        assert!((0.0..=1.0).contains(&metrics.frequency_score));
        assert!((0.0..=1.0).contains(&metrics.approximate_entropy));
        assert!((0.0..=1.0).contains(&metrics.linear_complexity));
        assert!((0.0..=1.0).contains(&metrics.golden_alignment));
    }

    #[test]
    fn refinement_module_produces_metrics() {
        let mut module = EntropyRefinementModule::new(b"kayos");
        let payload: Vec<u8> = (0..128).collect();
        let result = module.refine(&payload);
        assert_eq!(result.refined.len(), payload.len());
        assert_eq!(result.intermediate.len(), payload.len());
        assert!(result.metrics.frequency_score > 0.0);
    }
}
