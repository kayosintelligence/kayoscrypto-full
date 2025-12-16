use kayoscrypto_safe::GeometricPermutations;

fn is_bijective(original: &[u8], permuted: &[u8]) -> bool {
    let mut a = original.to_vec();
    let mut b = permuted.to_vec();
    a.sort_unstable();
    b.sort_unstable();
    a == b
}

#[test]
fn test_permutation_bijectivity() {
    let geometric = GeometricPermutations::new(256);
    let samples = [8, 16, 32, 64, 128, 256];
    for &size in &samples {
        let data: Vec<u8> = (0..size).map(|index| (index & 0xFF) as u8).collect();
        let angles = (30usize, 60usize);

        let fib = geometric.fibonacci_spiral_permutation(&data, 1);
        assert_eq!(fib.len(), size);
        assert!(
            is_bijective(&data, &fib),
            "Fibonacci permutation failed for n={size}"
        );

        let ezekiel = geometric.ezekiel_permutation(&data, angles, 1);
        assert_eq!(ezekiel.len(), size);
        assert!(
            is_bijective(&data, &ezekiel),
            "Ezekiel permutation failed for n={size}"
        );

        assert_ne!(fib, ezekiel, "Permutations identical at size {size}");
    }
}

#[test]
fn test_permutation_determinism() {
    let geometric = GeometricPermutations::new(64);
    let data = vec![1, 2, 3, 4, 5, 6, 7, 8];
    let angles = (45usize, 90usize);

    let first = geometric.fibonacci_spiral_permutation(&data, 1);
    let second = geometric.fibonacci_spiral_permutation(&data, 1);
    assert_eq!(first, second);

    let first_ezekiel = geometric.ezekiel_permutation(&data, angles, 1);
    let second_ezekiel = geometric.ezekiel_permutation(&data, angles, 1);
    assert_eq!(first_ezekiel, second_ezekiel);
}
