use arrayvec::ArrayVec;
use subtle::{Choice, ConditionallySelectable, ConstantTimeEq};

/// Operações constant-time seguras com APIs modernas.
#[allow(dead_code)]
pub struct SecureOps;

impl SecureOps {
    /// Seleciona entre dois bytes em tempo constante.
    pub fn ct_select(a: u8, b: u8, choice: Choice) -> u8 {
        CtBool::from_choice(choice).select(&a, &b)
    }

    /// Seleciona entre dois slices em tempo constante, retornando sempre `a.len()` elementos.
    pub fn ct_select_bytes(a: &[u8], b: &[u8], choice: Choice) -> ArrayVec<u8, 256> {
        let len = a.len().min(b.len());
        let mut result = ArrayVec::<u8, 256>::new();

        for i in 0..len {
            result.push(u8::conditional_select(&a[i], &b[i], choice));
        }

        while result.len() < a.len() {
            result.push(0);
        }

        result
    }

    /// XOR byte a byte com comprimento fixo, preenchendo o restante com zeros.
    pub fn ct_xor(a: &[u8], b: &[u8]) -> ArrayVec<u8, 256> {
        let len = a.len().min(b.len());
        let mut result = ArrayVec::<u8, 256>::new();

        for i in 0..len {
            result.push(a[i] ^ b[i]);
        }

        while result.len() < a.len() {
            result.push(0);
        }

        result
    }

    /// Compara dois slices e retorna [`Choice`] indicando igualdade.
    pub fn ct_eq(a: &[u8], b: &[u8]) -> Choice {
        a.ct_eq(b)
    }

    /// Acesso constant-time a uma tabela arbitrária.
    pub fn ct_lookup(table: &[u8], index: usize) -> u8 {
        let mut result = 0u8;
        for (i, &value) in table.iter().enumerate() {
            let select = Choice::from((i == index) as u8);
            result = u8::conditional_select(&result, &value, select);
        }
        result
    }

    /// Acesso constant-time a uma S-Box completa (256 entradas).
    pub fn ct_sbox_lookup(sbox: &[u8; 256], input: u8) -> u8 {
        Self::ct_lookup(sbox, input as usize)
    }

    /// Lookup constant-time para permutações precomputadas.
    pub fn ct_permutation_lookup(perm: &[u16], index: usize, len: usize) -> usize {
        let mut result = 0usize;
        let limit = len.min(perm.len());
        for i in 0..limit {
            let select = Choice::from((i == index) as u8);
            let value = perm[i] as usize;
            result = select_usize(result, value, select);
        }
        result
    }
}

/// Estrutura de permutação que tenta manter acessos previsíveis.
pub struct ConstantTimePermutation {
    indices: Vec<usize>,
}

impl ConstantTimePermutation {
    pub fn new(indices: Vec<usize>) -> Self {
        Self { indices }
    }

    pub fn apply(&self, data: &[u8]) -> Vec<u8> {
        let mut result = vec![0u8; data.len()];
        for (i, &value) in data.iter().enumerate() {
            let target = self.indices.get(i).copied().unwrap_or(i);
            if target < result.len() {
                result[target] = value;
            }
        }
        result
    }

    pub fn apply_inverse(&self, data: &[u8]) -> Vec<u8> {
        let mut result = vec![0u8; data.len()];
        for (i, &target) in self.indices.iter().enumerate() {
            if target < data.len() && i < result.len() {
                result[i] = data[target];
            }
        }
        result
    }
}

fn select_usize(a: usize, b: usize, choice: Choice) -> usize {
    let mask = 0usize.wrapping_sub(choice.unwrap_u8() as usize);
    (a & !mask) | (b & mask)
}

/// Wrapper para operações de lookup seguras com semântica de alto nível.
pub struct SecureLookup;

impl SecureLookup {
    pub const fn new() -> Self {
        SecureLookup
    }

    /// Fibonacci permutation lookup constant-time
    pub fn fibonacci_permutation(&self, index: usize, length: usize, _layer: usize) -> usize {
        use crate::tables::FIBONACCI_PERMUTATIONS;

        if length == 0 || length > 256 {
            return index;
        }

        let row = &FIBONACCI_PERMUTATIONS[length];
        SecureOps::ct_permutation_lookup(row, index, length)
    }

    /// Ezekiel offset calculation constant-time
    pub fn ezekiel_offset(
        &self,
        position: usize,
        length: usize,
        angles: (i32, i32),
        layer: usize,
    ) -> usize {
        use crate::tables::SIN_TABLE;

        if length == 0 {
            return 0;
        }

        let (theta1, theta2) = angles;
        let sin1_idx = ((theta1 as isize + position as isize).rem_euclid(360)) as usize;
        let sin2_idx = ((theta2 as isize + (position as isize * 2)).rem_euclid(360)) as usize;

        let sin1 = SIN_TABLE[sin1_idx] as isize;
        let sin2 = SIN_TABLE[sin2_idx] as isize;

        let rho = sin1.wrapping_add(sin2);
        let offset = rho.wrapping_mul((layer + 1) as isize).abs() as usize % length;

        offset
    }
}

#[derive(Copy, Clone)]
pub struct CtBool(Choice);

impl CtBool {
    pub fn from_choice(choice: Choice) -> Self {
        Self(choice)
    }

    pub fn from_bool(b: bool) -> Self {
        Self(Choice::from(b as u8))
    }

    pub fn select<T: ConditionallySelectable>(self, a: &T, b: &T) -> T {
        T::conditional_select(a, b, self.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_ct_select_bytes() {
        let a = [1u8, 2, 3, 4];
        let b = [5u8, 6, 7, 8];

        let selected_a = SecureOps::ct_select_bytes(&a, &b, Choice::from(0));
        let selected_b = SecureOps::ct_select_bytes(&a, &b, Choice::from(1));

        assert_eq!(a, selected_a.as_slice());
        assert_eq!(b, selected_b.as_slice());
    }

    #[test]
    fn test_ct_sbox_lookup() {
        let sbox: [u8; 256] = core::array::from_fn(|i| i as u8);

        for i in 0..256 {
            let result = SecureOps::ct_sbox_lookup(&sbox, i as u8);
            assert_eq!(result, i as u8);
        }
    }

    #[test]
    fn secure_lookup_helpers_cover_permutation_and_offsets() {
        let lookup = SecureLookup::new();

        let fib_index = lookup.fibonacci_permutation(3, 16, 0);
        assert!(fib_index < 16);

        let offset = lookup.ezekiel_offset(5, 32, (45, 90), 1);
        assert!(offset < 32);

        std::mem::drop(lookup);
    }

    #[test]
    fn ct_bool_wraps_choice_selection() {
        let ct_true = CtBool::from_bool(true);
        let ct_false = CtBool::from_bool(false);

        let select_true: u8 = ct_true.select(&10, &42);
        let select_false: u8 = ct_false.select(&10, &42);

        assert_eq!(select_true, 42);
        assert_eq!(select_false, 10);
    }
}
