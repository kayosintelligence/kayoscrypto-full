//! Timing exploration harness for KayosCrypto constant-time primitives.

use kayoscrypto_safe::metrics::{SecurityMetrics, TimingAnalyzer, PARANOID_CV_THRESHOLD};
use kayoscrypto_safe::{KayosCryptoSafe, MixDirection, SecureOps, StrongMix};
use std::time::{Duration, Instant};
use subtle::Choice;

const INNER_LOOP: usize = 256;
const TARGET_SAMPLES: usize = 10_000;

fn main() {
    let mut harness = ExampleTimingHarness::new();

    println!("🚀 Executando análise otimizada de constant-time (exemplo)...");
    harness.test_primitives(TARGET_SAMPLES);
    harness.test_strong_mix(TARGET_SAMPLES);
    harness.test_complete_encryption(TARGET_SAMPLES);
    harness.print_report();
}

struct ExampleTimingHarness {
    primitives: TimingAnalyzer,
    strong_mix: TimingAnalyzer,
    encryption: TimingAnalyzer,
    security: SecurityMetrics,
}

impl ExampleTimingHarness {
    fn new() -> Self {
        Self {
            primitives: TimingAnalyzer::new("SecureOps::ct_select_bytes"),
            strong_mix: TimingAnalyzer::new("StrongMix::apply"),
            encryption: TimingAnalyzer::new("KayosCryptoSafe::encrypt"),
            security: SecurityMetrics::paranoid_cv(),
        }
    }

    fn test_primitives(&mut self, target_samples: usize) {
        println!("🧪 Primitivas constant-time...");

        let batch = 500;
        let batches = target_samples / batch;

        for batch_idx in 0..batches {
            let start = Instant::now();

            for i in 0..batch {
                let data1 = self.generate_data(32, batch_idx * batch + i);
                let data2 = self.generate_data(32, batch_idx * batch + i + target_samples);
                let choice = Choice::from((i & 1) as u8);

                for _ in 0..INNER_LOOP {
                    let _ = SecureOps::ct_select_bytes(&data1, &data2, choice);
                    let _ = SecureOps::ct_xor(&data1, &data2);
                }
            }

            let elapsed = start.elapsed();
            let per_sample = self.per_sample_duration(elapsed, batch);
            for _ in 0..batch {
                self.primitives.add_sample(per_sample);
            }

            if batch_idx % 5 == 0 {
                println!("  • Batches concluídos: {}/{}", batch_idx + 1, batches);
            }
        }
    }

    fn test_strong_mix(&mut self, target_samples: usize) {
        println!("🧪 StrongMix constant-time...");

        let mixer = StrongMix::new(4);
        let key = b"example_timing_key";
        let batch = 250;
        let batches = target_samples / batch;

        for batch_idx in 0..batches {
            let start = Instant::now();

            for i in 0..batch {
                let data = self.generate_data(64, batch_idx * batch + i);

                for _ in 0..INNER_LOOP {
                    let _ = mixer.apply(&data, key, "example", MixDirection::Forward);
                }
            }

            let elapsed = start.elapsed();
            let per_sample = self.per_sample_duration(elapsed, batch);
            for _ in 0..batch {
                self.strong_mix.add_sample(per_sample);
            }

            if batch_idx % 5 == 0 {
                println!("  • Batches concluídos: {}/{}", batch_idx + 1, batches);
            }
        }
    }

    fn test_complete_encryption(&mut self, target_samples: usize) {
        println!("🧪 Criptografia completa constant-time...");

        let crypto = KayosCryptoSafe::new();
        let password = b"example_password";
        let batch = 100;
        let batches = target_samples / batch;

        for batch_idx in 0..batches {
            let start = Instant::now();

            for i in 0..batch {
                let data = self.generate_data(128, batch_idx * batch + i);

                for _ in 0..INNER_LOOP {
                    let _ = crypto.encrypt(&data, password);
                }
            }

            let elapsed = start.elapsed();
            let per_sample = self.per_sample_duration(elapsed, batch);
            for _ in 0..batch {
                self.encryption.add_sample(per_sample);
            }

            if batch_idx % 5 == 0 {
                println!("  • Batches concluídos: {}/{}", batch_idx + 1, batches);
            }
        }
    }

    fn print_report(&self) {
        println!("\n🎯 RELATÓRIO FINAL (exemplo)");
        println!("============================");

        let reports = [
            self.primitives.analyze(),
            self.strong_mix.analyze(),
            self.encryption.analyze(),
        ];

        let mut compliant = true;

        for report in reports.iter() {
            report.print_summary();
            let secure = self.security.is_operation_secure(report);
            println!(
                "   Cumpre objetivo Paranoid {:.0}? {}",
                PARANOID_CV_THRESHOLD,
                if secure { "✅" } else { "⚠️" }
            );
            println!();

            if !secure {
                compliant = false;
            }
        }

        if compliant {
            println!(
                "🎉 Todas as operações cumpriram o alvo Paranoid {:.0} CV security level.",
                PARANOID_CV_THRESHOLD
            );
        } else {
            println!(
                "⚠️  Investigue operações com τ acima do limiar recomendado (≥ {:.0}).",
                PARANOID_CV_THRESHOLD
            );
        }
    }

    fn generate_data(&self, len: usize, seed: usize) -> Vec<u8> {
        let mut data = vec![0u8; len];
        for (idx, byte) in data.iter_mut().enumerate() {
            *byte = ((seed + idx * 31) % 256) as u8;
        }
        data
    }

    fn per_sample_duration(&self, elapsed: Duration, batch: usize) -> Duration {
        if batch == 0 {
            return Duration::from_secs(0);
        }

        let secs = (elapsed.as_secs_f64() / batch as f64).max(0.0);
        Duration::from_secs_f64(secs)
    }
}
