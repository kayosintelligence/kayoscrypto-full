//! KayosCrypto - Geometric Cryptographic System
//!
//! This is the Rust implementation of KayosCrypto v5.0.1 ULTIMATE.
//!
//! # Architecture: Fishbone (Spine + 3 Ribs)
//! - Rib 1: Fibonacci Direction
//! - Rib 2: Multi-layer Rotation (Ezekiel Concentric)
//! - Rib 3: Core System (Geometric Permutation + Feistel)
//!
//! # Patents
//! - BR 10 2025 026228-2
//! - BR 10 2025 026547-8
//!
//! # Trademark
//! - BR 51 2025 003443-1 (KAYOS)
//!
//! Author: KAYOS Quantum Research Lab
//! Date: December 2, 2025

use sha2::{Sha256, Digest};
use std::f64::consts::PI;

/// Golden ratio
pub const PHI: f64 = 1.618033988749895;

/// Inverse of golden ratio
pub const PHI_INV: f64 = 0.618033988749895;

/// Generate Fibonacci sequence up to n terms
pub fn fibonacci_sequence(n: usize) -> Vec<u64> {
    if n == 0 {
        return vec![];
    }
    if n == 1 {
        return vec![1];
    }
    
    let mut fib = vec![1u64; n];
    for i in 2..n {
        fib[i] = fib[i-1].saturating_add(fib[i-2]);
    }
    
    fib
}

/// Derive a key from password using SHA-256
pub fn derive_key(password: &str, length: usize) -> Vec<u8> {
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    let mut key: Vec<u8> = hasher.finalize().to_vec();
    
    // Extend if needed
    while key.len() < length {
        let mut hasher = Sha256::new();
        hasher.update(&key);
        key.extend_from_slice(&hasher.finalize());
    }
    
    key.truncate(length);
    key
}

/// Perform circular shift on a byte slice
pub fn circular_shift(data: &[u8], shift: i64) -> Vec<u8> {
    let n = data.len();
    if n == 0 {
        return vec![];
    }
    
    // Normalize shift to positive value within range
    let shift = ((shift % n as i64) + n as i64) as usize % n;
    
    let mut result = vec![0u8; n];
    for i in 0..n {
        let new_index = (i + shift) % n;
        result[new_index] = data[i];
    }
    
    result
}

/// Reverse circular shift
pub fn circular_shift_reverse(data: &[u8], shift: i64) -> Vec<u8> {
    circular_shift(data, -shift)
}

// =====================================
// RIB 1: Fibonacci Direction
// =====================================

/// Fibonacci-based direction transformation
pub struct FibonacciDirection {
    fib_sequence: Vec<u64>,
    mode: usize,
}

impl FibonacciDirection {
    /// Create a new FibonacciDirection instance
    pub fn new(sequence_length: usize) -> Self {
        FibonacciDirection {
            fib_sequence: fibonacci_sequence(sequence_length),
            mode: 0,
        }
    }
    
    /// Determine transformation mode from key
    pub fn determine_mode(&mut self, key: &[u8]) -> usize {
        if key.is_empty() || self.fib_sequence.is_empty() {
            self.mode = 0;
            return 0;
        }
        
        let sum: usize = key.iter().map(|&b| b as usize).sum();
        self.mode = sum % self.fib_sequence.len();
        self.mode
    }
    
    /// Apply Fibonacci direction transformation
    pub fn apply(&mut self, data: &[u8], key: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return vec![];
        }
        
        self.determine_mode(key);
        let mut result = data.to_vec();
        
        for (i, &fib_val) in self.fib_sequence.iter().enumerate() {
            if i >= result.len() {
                break;
            }
            
            let direction: i64 = if self.mode % 2 == 0 { -1 } else { 1 };
            let shift = (fib_val as i64) * direction;
            result = circular_shift(&result, shift);
        }
        
        result
    }
    
    /// Reverse Fibonacci direction transformation
    pub fn reverse(&mut self, data: &[u8], key: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return vec![];
        }
        
        self.determine_mode(key);
        let mut result = data.to_vec();
        
        // Reverse order
        for i in (0..self.fib_sequence.len()).rev() {
            if i >= result.len() {
                continue;
            }
            
            let fib_val = self.fib_sequence[i];
            let direction: i64 = if self.mode % 2 == 0 { -1 } else { 1 };
            let shift = (fib_val as i64) * direction;
            result = circular_shift_reverse(&result, shift);
        }
        
        result
    }
}

// =====================================
// RIB 2: Ezekiel Concentric Engine
// =====================================

/// Single rotation wheel
struct EzekielWheel {
    #[allow(dead_code)]
    name: String,
    ratio: f64,
    position: f64,
}

impl EzekielWheel {
    fn new(name: &str, ratio: f64) -> Self {
        EzekielWheel {
            name: name.to_string(),
            ratio,
            position: 0.0,
        }
    }
    
    fn compute_rotation(&mut self, input: f64) -> f64 {
        self.position += input * self.ratio;
        self.position % (2.0 * PI)
    }
    
    fn reset(&mut self) {
        self.position = 0.0;
    }
}

/// Multi-layer rotation system
pub struct EzekielConcentric {
    main_wheel: EzekielWheel,
    alpha_wheel: EzekielWheel,
    beta_wheel: EzekielWheel,
}

impl EzekielConcentric {
    /// Create a new EzekielConcentric engine
    pub fn new() -> Self {
        EzekielConcentric {
            main_wheel: EzekielWheel::new("Main", PHI),
            alpha_wheel: EzekielWheel::new("Alpha", PHI_INV),
            beta_wheel: EzekielWheel::new("Beta", PI / PHI),
        }
    }
    
    /// Reset all wheels
    pub fn reset(&mut self) {
        self.main_wheel.reset();
        self.alpha_wheel.reset();
        self.beta_wheel.reset();
    }
    
    /// Apply multi-layer rotation transformation
    pub fn apply(&mut self, data: &[u8], key: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return vec![];
        }
        
        self.reset();
        
        // Derive rotation seed from key
        let key_sum: f64 = key.iter().map(|&b| b as f64).sum::<f64>() / 256.0;
        
        // Compute rotations
        let main_rot = self.main_wheel.compute_rotation(key_sum);
        let alpha_rot = self.alpha_wheel.compute_rotation(key_sum * PHI);
        let beta_rot = self.beta_wheel.compute_rotation(key_sum * PHI_INV);
        
        // Convert to shifts
        let n = data.len() as f64;
        let main_shift = (main_rot * n / (2.0 * PI)) as i64;
        let alpha_shift = (alpha_rot * n / (2.0 * PI)) as i64;
        let beta_shift = (beta_rot * n / (2.0 * PI)) as i64;
        
        // Apply shifts
        let mut result = circular_shift(data, main_shift);
        result = circular_shift(&result, alpha_shift);
        result = circular_shift(&result, beta_shift);
        
        result
    }
    
    /// Reverse multi-layer rotation transformation
    pub fn reverse(&mut self, data: &[u8], key: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return vec![];
        }
        
        self.reset();
        
        // Same computation as apply
        let key_sum: f64 = key.iter().map(|&b| b as f64).sum::<f64>() / 256.0;
        
        let main_rot = self.main_wheel.compute_rotation(key_sum);
        let alpha_rot = self.alpha_wheel.compute_rotation(key_sum * PHI);
        let beta_rot = self.beta_wheel.compute_rotation(key_sum * PHI_INV);
        
        let n = data.len() as f64;
        let main_shift = (main_rot * n / (2.0 * PI)) as i64;
        let alpha_shift = (alpha_rot * n / (2.0 * PI)) as i64;
        let beta_shift = (beta_rot * n / (2.0 * PI)) as i64;
        
        // Reverse order
        let mut result = circular_shift_reverse(data, beta_shift);
        result = circular_shift_reverse(&result, alpha_shift);
        result = circular_shift_reverse(&result, main_shift);
        
        result
    }
}

impl Default for EzekielConcentric {
    fn default() -> Self {
        Self::new()
    }
}

// =====================================
// RIB 3: Core System
// =====================================

/// Geometric permutation engine
pub struct GeometricPermutation {
    #[allow(dead_code)]
    block_size: usize,
}

impl GeometricPermutation {
    /// Create a new GeometricPermutation engine
    pub fn new(block_size: usize) -> Self {
        GeometricPermutation {
            block_size: if block_size == 0 { 16 } else { block_size },
        }
    }
    
    /// Generate permutation based on key
    fn generate_permutation(&self, key: &[u8], size: usize) -> Vec<usize> {
        let mut perm: Vec<usize> = (0..size).collect();
        
        // Fisher-Yates shuffle seeded by key
        let mut key_index = 0;
        for i in (1..size).rev() {
            let j = (key[key_index % key.len()] as usize) % (i + 1);
            perm.swap(i, j);
            key_index += 1;
        }
        
        perm
    }
    
    /// Compute inverse permutation
    fn inverse_permutation(&self, perm: &[usize]) -> Vec<usize> {
        let mut inverse = vec![0; perm.len()];
        for (i, &v) in perm.iter().enumerate() {
            inverse[v] = i;
        }
        inverse
    }
    
    /// Apply geometric permutation
    pub fn apply(&self, data: &[u8], key: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return vec![];
        }
        
        let perm = self.generate_permutation(key, data.len());
        let mut result = vec![0u8; data.len()];
        
        for (i, &p) in perm.iter().enumerate() {
            result[p] = data[i];
        }
        
        result
    }
    
    /// Reverse geometric permutation
    pub fn reverse(&self, data: &[u8], key: &[u8]) -> Vec<u8> {
        if data.is_empty() {
            return vec![];
        }
        
        let perm = self.generate_permutation(key, data.len());
        let inverse = self.inverse_permutation(&perm);
        let mut result = vec![0u8; data.len()];
        
        for (i, &p) in inverse.iter().enumerate() {
            result[p] = data[i];
        }
        
        result
    }
}

/// Feistel cipher network
pub struct FeistelNetwork {
    rounds: usize,
}

impl FeistelNetwork {
    /// Create a new FeistelNetwork
    pub fn new(rounds: usize) -> Self {
        FeistelNetwork {
            rounds: if rounds == 0 { 4 } else { rounds },
        }
    }
    
    /// Round function
    fn round_function(&self, data: &[u8], round_key: &[u8]) -> Vec<u8> {
        data.iter()
            .enumerate()
            .map(|(i, &b)| b ^ round_key[i % round_key.len()])
            .collect()
    }
    
    /// Apply Feistel network encryption
    pub fn apply(&self, data: &[u8], key: &[u8]) -> Vec<u8> {
        if data.len() < 2 {
            return data.to_vec();
        }
        
        let mid = data.len() / 2;
        let mut left = data[..mid].to_vec();
        let mut right = data[mid..].to_vec();
        
        for round in 0..self.rounds {
            // Derive round key
            let round_key = derive_key(&format!("{}{}", String::from_utf8_lossy(key), round), right.len());
            
            // Feistel operation
            let new_left = right.clone();
            let f = self.round_function(&right, &round_key);
            let new_right: Vec<u8> = left.iter()
                .enumerate()
                .map(|(i, &b)| b ^ f[i % f.len()])
                .collect();
            
            left = new_left;
            right = new_right;
        }
        
        // Combine
        let mut result = left;
        result.extend(right);
        result
    }
    
    /// Reverse Feistel network encryption
    pub fn reverse(&self, data: &[u8], key: &[u8]) -> Vec<u8> {
        if data.len() < 2 {
            return data.to_vec();
        }
        
        let mid = data.len() / 2;
        let mut left = data[..mid].to_vec();
        let mut right = data[mid..].to_vec();
        
        // Reverse rounds
        for round in (0..self.rounds).rev() {
            let round_key = derive_key(&format!("{}{}", String::from_utf8_lossy(key), round), left.len());
            
            // Reverse Feistel operation
            let new_right = left.clone();
            let f = self.round_function(&left, &round_key);
            let new_left: Vec<u8> = right.iter()
                .enumerate()
                .map(|(i, &b)| b ^ f[i % f.len()])
                .collect();
            
            left = new_left;
            right = new_right;
        }
        
        let mut result = left;
        result.extend(right);
        result
    }
}

// =====================================
// MAIN: KayosCrypto Ultimate
// =====================================

/// Main KayosCrypto encryption engine
pub struct KayosCrypto {
    fib_direction: FibonacciDirection,
    ezekiel_engine: EzekielConcentric,
    geometric_perm: GeometricPermutation,
    feistel_network: FeistelNetwork,
    use_concentric: bool,
    use_direction: bool,
}

impl KayosCrypto {
    /// Create a new KayosCrypto instance
    pub fn new(use_concentric: bool, use_direction: bool) -> Self {
        KayosCrypto {
            fib_direction: FibonacciDirection::new(20),
            ezekiel_engine: EzekielConcentric::new(),
            geometric_perm: GeometricPermutation::new(16),
            feistel_network: FeistelNetwork::new(4),
            use_concentric,
            use_direction,
        }
    }
    
    /// Encrypt data with the given password
    pub fn encrypt(&mut self, plaintext: &[u8], password: &str, level: u8) -> Result<Vec<u8>, &'static str> {
        if plaintext.is_empty() {
            return Err("empty plaintext");
        }
        if password.is_empty() {
            return Err("empty password");
        }
        
        let level = level.clamp(1, 3);
        let key = derive_key(password, 32);
        let mut result = plaintext.to_vec();
        
        // Phase 1: Fibonacci Direction (if enabled)
        if self.use_direction && level >= 1 {
            result = self.fib_direction.apply(&result, &key);
        }
        
        // Phase 2: Multi-layer Rotation (if enabled)
        if self.use_concentric && level >= 2 {
            result = self.ezekiel_engine.apply(&result, &key);
        }
        
        // Phase 3: Core System (always applied)
        if level >= 3 {
            result = self.geometric_perm.apply(&result, &key);
            result = self.feistel_network.apply(&result, &key);
        }
        
        Ok(result)
    }
    
    /// Decrypt data with the given password
    pub fn decrypt(&mut self, ciphertext: &[u8], password: &str, level: u8) -> Result<Vec<u8>, &'static str> {
        if ciphertext.is_empty() {
            return Err("empty ciphertext");
        }
        if password.is_empty() {
            return Err("empty password");
        }
        
        let level = level.clamp(1, 3);
        let key = derive_key(password, 32);
        let mut result = ciphertext.to_vec();
        
        // Reverse order: Phase 3 → Phase 2 → Phase 1
        
        // Phase 3: Core System (always applied)
        if level >= 3 {
            result = self.feistel_network.reverse(&result, &key);
            result = self.geometric_perm.reverse(&result, &key);
        }
        
        // Phase 2: Multi-layer Rotation (if enabled)
        if self.use_concentric && level >= 2 {
            result = self.ezekiel_engine.reverse(&result, &key);
        }
        
        // Phase 1: Fibonacci Direction (if enabled)
        if self.use_direction && level >= 1 {
            result = self.fib_direction.reverse(&result, &key);
        }
        
        Ok(result)
    }
}

impl Default for KayosCrypto {
    fn default() -> Self {
        Self::new(true, true)
    }
}

/// Returns the version string
pub fn version() -> &'static str {
    "KayosCrypto Rust v5.0.1 ULTIMATE"
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_fibonacci_sequence() {
        assert_eq!(fibonacci_sequence(0), vec![]);
        assert_eq!(fibonacci_sequence(1), vec![1]);
        assert_eq!(fibonacci_sequence(5), vec![1, 1, 2, 3, 5]);
        assert_eq!(fibonacci_sequence(10), vec![1, 1, 2, 3, 5, 8, 13, 21, 34, 55]);
    }
    
    #[test]
    fn test_derive_key_determinism() {
        let key1 = derive_key("password123", 32);
        let key2 = derive_key("password123", 32);
        assert_eq!(key1, key2);
    }
    
    #[test]
    fn test_derive_key_length() {
        for length in [16, 32, 64, 128] {
            let key = derive_key("test", length);
            assert_eq!(key.len(), length);
        }
    }
    
    #[test]
    fn test_circular_shift_reversibility() {
        let data = vec![1, 2, 3, 4, 5];
        let shifted = circular_shift(&data, 2);
        let restored = circular_shift_reverse(&shifted, 2);
        assert_eq!(restored, data);
    }
    
    #[test]
    fn test_fibonacci_direction_reversibility() {
        let mut fd = FibonacciDirection::new(20);
        let data = b"Hello, KayosCrypto!".to_vec();
        let key = b"test_key".to_vec();
        
        let transformed = fd.apply(&data, &key);
        assert_ne!(transformed, data);
        
        let mut fd2 = FibonacciDirection::new(20);
        let restored = fd2.reverse(&transformed, &key);
        assert_eq!(restored, data);
    }
    
    #[test]
    fn test_ezekiel_concentric_reversibility() {
        let mut ec = EzekielConcentric::new();
        let data = b"Ezekiel Multi-layer Test!".to_vec();
        let key = b"ezekiel_key".to_vec();
        
        let transformed = ec.apply(&data, &key);
        
        let mut ec2 = EzekielConcentric::new();
        let restored = ec2.reverse(&transformed, &key);
        assert_eq!(restored, data);
    }
    
    #[test]
    fn test_geometric_permutation_reversibility() {
        let gp = GeometricPermutation::new(16);
        let data = b"Geometric Permutation!".to_vec();
        let key = b"perm_key".to_vec();
        
        let transformed = gp.apply(&data, &key);
        let restored = gp.reverse(&transformed, &key);
        assert_eq!(restored, data);
    }
    
    #[test]
    fn test_feistel_network_reversibility() {
        let fn_net = FeistelNetwork::new(4);
        let data = b"Feistel Network Test!".to_vec();
        let key = b"feistel_key".to_vec();
        
        let transformed = fn_net.apply(&data, &key);
        let restored = fn_net.reverse(&transformed, &key);
        assert_eq!(restored, data);
    }
    
    #[test]
    fn test_kayoscrypto_encrypt_decrypt() {
        let mut kc = KayosCrypto::new(true, true);
        let plaintext = b"KayosCrypto v5.0.1 ULTIMATE Test!".to_vec();
        let password = "secure_password";
        
        let ciphertext = kc.encrypt(&plaintext, password, 3).unwrap();
        assert_ne!(ciphertext, plaintext);
        
        let decrypted = kc.decrypt(&ciphertext, password, 3).unwrap();
        assert_eq!(decrypted, plaintext);
    }
    
    #[test]
    fn test_kayoscrypto_determinism() {
        let mut kc1 = KayosCrypto::new(true, true);
        let mut kc2 = KayosCrypto::new(true, true);
        let plaintext = b"Determinism test".to_vec();
        let password = "same_password";
        
        let cipher1 = kc1.encrypt(&plaintext, password, 3).unwrap();
        let cipher2 = kc2.encrypt(&plaintext, password, 3).unwrap();
        
        assert_eq!(cipher1, cipher2);
    }
    
    #[test]
    fn test_kayoscrypto_key_sensitivity() {
        let mut kc = KayosCrypto::new(true, true);
        let plaintext = b"Key sensitivity test".to_vec();
        
        let cipher1 = kc.encrypt(&plaintext, "password1", 3).unwrap();
        let cipher2 = kc.encrypt(&plaintext, "password2", 3).unwrap();
        
        assert_ne!(cipher1, cipher2);
    }
    
    #[test]
    fn test_kayoscrypto_wrong_password() {
        let mut kc = KayosCrypto::new(true, true);
        let plaintext = b"Secret message".to_vec();
        
        let ciphertext = kc.encrypt(&plaintext, "correct_password", 3).unwrap();
        let decrypted = kc.decrypt(&ciphertext, "wrong_password", 3).unwrap();
        
        assert_ne!(decrypted, plaintext);
    }
    
    #[test]
    fn test_version() {
        assert_eq!(version(), "KayosCrypto Rust v5.0.1 ULTIMATE");
    }
}
