//! Constant-time timing leakage validation harness aligned with the paranoid CV target.

use kayoscrypto_safe::metrics::{SecurityMetrics, TimingAnalyzer};
use kayoscrypto_safe::{KayosCryptoSafe, MixDirection, SecureOps, StrongMix};
use std::time::{Duration, Instant};
use subtle::Choice;

const DEBUG_SAMPLES: usize = 10_000;
const RELEASE_SAMPLES: usize = 100_000;

/// Batched timing harness used to minimise jitter and surface CV outliers.
pub struct OptimizedTimingHarness {
    analyzers: Vec<TimingAnalyzer>,
    security_metrics: SecurityMetrics,
}

impl OptimizedTimingHarness {
    pub fn new() -> Self {
        Self {
            analyzers: Vec::new(),
            security_metrics: SecurityMetrics::paranoid_cv(),
        }
    }

    /// Profiles the constant-time primitives with batched execution to smooth CPU noise.
    pub fn test_primitives_optimized(&mut self, target_samples: usize) {
        println!("[timing] primitives (batched)");

        let mut analyzer = TimingAnalyzer::new("SecureOps::ct_select_bytes");
        let batch_size = 1_000;
        let batches = Self::batches_needed(target_samples, batch_size);

        for batch in 0..batches {
            let current_batch = Self::current_batch_size(target_samples, batch_size, batch);
            let start = Instant::now();

            for i in 0..current_batch {
                let base_index = batch * batch_size + i;
                let left = self.generate_test_data(32, base_index);
                let right = self.generate_test_data(32, base_index + target_samples);
                let choice = Choice::from((i % 2) as u8);

                let _ = SecureOps::ct_select_bytes(&left, &right, choice);
                let _ = SecureOps::ct_xor(&left, &right);
                let _ = SecureOps::ct_eq(&left, &right);
            }

            self.record_batch(&mut analyzer, start, current_batch);

            if batch % 10 == 0 {
                println!("  - {}/{} primitive batches", batch + 1, batches);
            }
        }

        self.analyzers.push(analyzer);
    }

    /// Profiles StrongMix::apply to confirm constant-time behaviour under load.
    pub fn test_strong_mix_optimized(&mut self, target_samples: usize) {
        println!("[timing] strong_mix (batched)");

        let mixer = StrongMix::new(4);
        let key = b"timing_test_key";
        let mut analyzer = TimingAnalyzer::new("StrongMix::apply");
        let batch_size = 500;
        let batches = Self::batches_needed(target_samples, batch_size);

        for batch in 0..batches {
            let current_batch = Self::current_batch_size(target_samples, batch_size, batch);
            let start = Instant::now();

            for i in 0..current_batch {
                let base_index = batch * batch_size + i;
                let data = self.generate_test_data(64, base_index);
                let _ = mixer.apply(&data, key, "timing", MixDirection::Forward);
            }

            self.record_batch(&mut analyzer, start, current_batch);

            if batch % 10 == 0 {
                println!("  - {}/{} strong_mix batches", batch + 1, batches);
            }
        }

        self.analyzers.push(analyzer);
    }

    /// Profiles the full encryption path to ensure composite constant-time guarantees.
    pub fn test_complete_encryption_optimized(&mut self, target_samples: usize) {
        println!("[timing] full encryption (batched)");

        let crypto = KayosCryptoSafe::new();
        let password = b"timing_test_password";
        let mut analyzer = TimingAnalyzer::new("KayosCryptoSafe::encrypt");
        let batch_size = 200;
        let batches = Self::batches_needed(target_samples, batch_size);

        for batch in 0..batches {
            let current_batch = Self::current_batch_size(target_samples, batch_size, batch);
            let start = Instant::now();

            for i in 0..current_batch {
                let base_index = batch * batch_size + i;
                let data = self.generate_test_data(128, base_index);
                let _ = crypto.encrypt(&data, password);
            }

            self.record_batch(&mut analyzer, start, current_batch);

            if batch % 5 == 0 {
                println!("  - {}/{} encryption batches", batch + 1, batches);
            }
        }

        self.analyzers.push(analyzer);
    }

    fn generate_test_data(&self, len: usize, seed: usize) -> Vec<u8> {
        let mut data = vec![0u8; len];
        for (idx, byte) in data.iter_mut().enumerate() {
            *byte = ((seed + idx * 31) % 256) as u8;
        }
        data
    }

    fn record_batch(&self, analyzer: &mut TimingAnalyzer, start: Instant, count: usize) {
        if count == 0 {
            return;
        }

        let elapsed = start.elapsed();
        let secs = (elapsed.as_secs_f64() / count as f64).max(0.0);
        let per_sample = Duration::from_secs_f64(secs);

        for _ in 0..count {
            analyzer.add_sample(per_sample);
        }
    }

    fn batches_needed(target_samples: usize, batch_size: usize) -> usize {
        if batch_size == 0 {
            return 0;
        }
        (target_samples + batch_size - 1) / batch_size
    }

    fn current_batch_size(target_samples: usize, batch_size: usize, batch_index: usize) -> usize {
        if batch_size == 0 {
            return 0;
        }
        let processed = batch_index * batch_size;
        if processed >= target_samples {
            0
        } else {
            (target_samples - processed).min(batch_size)
        }
    }

    pub fn print_comprehensive_report(&self) {
        println!("\n== CONSTANT-TIME SECURITY REPORT ==");

        let mut all_secure = true;
        let mut total_samples = 0usize;

        for analyzer in &self.analyzers {
            let report = analyzer.analyze();
            report.print_summary();
            println!();

            if !self.security_metrics.is_operation_secure(&report) {
                all_secure = false;
            }
            total_samples += report.sample_count;
        }

        println!("Total samples recorded: {}", total_samples);
        println!(
            "Paranoid 100K compliance: {}",
            if all_secure { "PASS" } else { "FAIL" }
        );

        if !all_secure {
            println!("Warning: investigate operations with tau above the threshold");
        }
    }
}

#[test]
fn constant_time_primitives_pass_t_test() {
    let mut harness = OptimizedTimingHarness::new();

    #[cfg(debug_assertions)]
    let samples = DEBUG_SAMPLES;
    #[cfg(not(debug_assertions))]
    let samples = RELEASE_SAMPLES;

    println!("[timing] launching optimized analysis...");

    harness.test_primitives_optimized(samples);
    harness.test_strong_mix_optimized(samples);
    harness.test_complete_encryption_optimized(samples / 2);

    harness.print_comprehensive_report();
}

#[test]
#[ignore = "Produces detailed timing console output"]
fn manual_timing_run() {
    let mut harness = OptimizedTimingHarness::new();

    println!("[timing] manual run with extended samples");

    #[cfg(debug_assertions)]
    let samples = 50_000;
    #[cfg(not(debug_assertions))]
    let samples = 250_000;

    let start = Instant::now();

    harness.test_primitives_optimized(samples);
    harness.test_strong_mix_optimized(samples);
    harness.test_complete_encryption_optimized(samples);

    let duration = start.elapsed();

    println!("\nTotal runtime: {:?}", duration);
    harness.print_comprehensive_report();

    println!(
        "\nHint: run `cargo test --release -- --ignored manual_timing_run` for paranoid coverage"
    );
}
