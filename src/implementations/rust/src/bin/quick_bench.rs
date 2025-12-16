//! Quick Performance Benchmark for KayosCrypto Rust

use kayoscrypto::KayosCrypto;
use std::time::Instant;

fn main() {
    println!("🚀 KayosCrypto Rust Quick Benchmark\n");
    
    let password = "KayosCrypto-Benchmark-Key-2025";
    let mut cipher = KayosCrypto::new(true, true);
    
    // Test sizes
    let sizes = vec![(1024, "1 KB"), (10 * 1024, "10 KB"), (50 * 1024, "50 KB")];
    
    println!("| Size  | Time (ms) | Throughput  | vs Python 308 KB/s |");
    println!("|-------|-----------|-------------|-------------------|");
    
    for (size, label) in sizes {
        let plaintext: Vec<u8> = (0..size).map(|i| (i % 256) as u8).collect();
        
        // Warmup
        let _ = cipher.encrypt(&plaintext, password, 3);
        
        // Benchmark (10 iterations)
        let start = Instant::now();
        for _ in 0..10 {
            let _ = cipher.encrypt(&plaintext, password, 3);
        }
        let elapsed = start.elapsed();
        let time_per_op = elapsed.as_secs_f64() / 10.0 * 1000.0;
        let throughput_kbs = size as f64 / (elapsed.as_secs_f64() / 10.0) / 1024.0;
        let speedup = throughput_kbs / 308.0;
        
        println!("| {:5} | {:9.2} | {:8.0} KB/s | {:5.1}x faster     |", 
                 label, time_per_op, throughput_kbs, speedup);
    }
    
    // Verify
    println!("\n✅ Verification:");
    let test = b"KayosCrypto Rust Test";
    let enc = cipher.encrypt(test, password, 3).unwrap();
    let dec = cipher.decrypt(&enc, password, 3).unwrap();
    println!("   Encrypt/Decrypt: {}", if dec == test.to_vec() { "PASSED" } else { "FAILED" });
}
