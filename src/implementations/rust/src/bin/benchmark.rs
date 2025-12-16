//! Performance Benchmark for KayosCrypto Rust Implementation

use kayoscrypto::KayosCrypto;
use std::time::Instant;

fn main() {
    println!("{}", "=".repeat(70));
    println!("🚀 KayosCrypto Rust Performance Benchmark");
    println!("{}", "=".repeat(70));
    
    let password = "KayosCrypto-Benchmark-Key-2025";
    let sizes: Vec<(usize, &str)> = vec![
        (1024, "1 KB"),
        (10 * 1024, "10 KB"),
        (100 * 1024, "100 KB"),
        (1024 * 1024, "1 MB"),
    ];
    
    // Create cipher
    let mut cipher = KayosCrypto::new(true, true);
    
    println!("\n📊 Encryption Performance:\n");
    println!("| Size    | Time (ms) | Throughput    |");
    println!("|---------|-----------|---------------|");
    
    for (size, label) in &sizes {
        let plaintext: Vec<u8> = (0..*size).map(|i| (i % 256) as u8).collect();
        
        // Warmup
        let _ = cipher.encrypt(&plaintext, password, 3);
        
        // Benchmark
        let iterations = if *size >= 1024 * 1024 { 10 } else { 100 };
        let start = Instant::now();
        for _ in 0..iterations {
            let _ = cipher.encrypt(&plaintext, password, 3);
        }
        let elapsed = start.elapsed();
        let time_per_op = elapsed.as_secs_f64() / iterations as f64 * 1000.0;
        let throughput = *size as f64 / (elapsed.as_secs_f64() / iterations as f64);
        
        let throughput_str = if throughput > 1024.0 * 1024.0 {
            format!("{:.2} MB/s", throughput / 1024.0 / 1024.0)
        } else {
            format!("{:.2} KB/s", throughput / 1024.0)
        };
        
        println!("| {:7} | {:9.3} | {:13} |", label, time_per_op, throughput_str);
    }
    
    // Verify correctness
    println!("\n🔍 Verification:");
    let test_data = b"Hello, KayosCrypto Rust!";
    let encrypted = cipher.encrypt(test_data, password, 3).unwrap();
    let decrypted = cipher.decrypt(&encrypted, password, 3).unwrap();
    
    if decrypted == test_data.to_vec() {
        println!("  ✅ Encryption/Decryption: VERIFIED");
    } else {
        println!("  ❌ Encryption/Decryption: FAILED");
    }
    
    // Compare with Python
    println!("\n📈 Performance Comparison:");
    println!("  Python: ~308 KB/s");
    println!("  Rust:   See table above");
    println!("  Expected improvement: 50-100x");
    
    println!("\n{}", "=".repeat(70));
}
