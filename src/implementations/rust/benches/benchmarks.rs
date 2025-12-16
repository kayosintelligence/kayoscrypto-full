use criterion::{black_box, criterion_group, criterion_main, Criterion};
use kayoscrypto::KayosCrypto;

fn benchmark_encrypt(c: &mut Criterion) {
    let mut kc = KayosCrypto::new(true, true);
    let plaintext: Vec<u8> = (0..1024).map(|i| (i % 256) as u8).collect();
    let password = "benchmark_password";
    
    c.bench_function("encrypt_1kb", |b| {
        b.iter(|| {
            kc.encrypt(black_box(&plaintext), black_box(password), 3).unwrap()
        })
    });
}

fn benchmark_decrypt(c: &mut Criterion) {
    let mut kc = KayosCrypto::new(true, true);
    let plaintext: Vec<u8> = (0..1024).map(|i| (i % 256) as u8).collect();
    let password = "benchmark_password";
    let ciphertext = kc.encrypt(&plaintext, password, 3).unwrap();
    
    c.bench_function("decrypt_1kb", |b| {
        b.iter(|| {
            kc.decrypt(black_box(&ciphertext), black_box(password), 3).unwrap()
        })
    });
}

criterion_group!(benches, benchmark_encrypt, benchmark_decrypt);
criterion_main!(benches);
