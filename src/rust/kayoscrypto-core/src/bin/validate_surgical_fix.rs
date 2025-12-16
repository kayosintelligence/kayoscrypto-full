use kayoscrypto_safe::quantum::{GapMetrics, SurgicalEntropyRefiner};
use rand::Rng;

fn main() {
    println!("\u{1F52D} VALIDAÇÃO CIRÚRGICA DOS 3 GAPS CRÍTICOS");
    println!("===========================================\n");

    let test_samples = generate_test_samples(120_000);
    let baseline = baseline_scores(&test_samples);

    let mut refined_samples = test_samples.clone();
    let mut refiner = SurgicalEntropyRefiner::new(0xCAFEBABE_DEADBEEF);

    // Três passagens simulam o refinamento contínuo no pipeline real.
    let mut report = SurgicalReportSnapshot::default();
    for _ in 0..3 {
        let pass_report = refiner.refine_surgically_with_force(&mut refined_samples, 8);
        report = SurgicalReportSnapshot::from(pass_report);
    }

    let predicted_score = report.predicted_nist_score;

    println!("\u{1F4CA} RELATÓRIO CIRÚRGICO - PREVISÃO vs LINHA DE BASE");
    println!(
        "ApproximateEntropy:  {before:.3} → {after:.3} (Δ{delta:+.3})",
        before = baseline.approximate_entropy_score,
        after = report.approx_entropy_score,
        delta = report.approx_entropy_score - baseline.approximate_entropy_score,
    );
    println!(
        "BlockFrequency:      {before:.3} → {after:.3} (Δ{delta:+.3})",
        before = baseline.block_frequency_score,
        after = report.block_freq_score,
        delta = report.block_freq_score - baseline.block_frequency_score,
    );
    println!(
        "CumulativeSums:      {before:.3} → {after:.3} (Δ{delta:+.3})",
        before = baseline.cumulative_sums_score,
        after = report.cumulative_sums_score,
        delta = report.cumulative_sums_score - baseline.cumulative_sums_score,
    );

    println!(
        "\n\u{1F3AF} SCORE NIST PREDITO: {pred:.3}",
        pred = predicted_score
    );

    if predicted_score > 0.99 {
        println!("\u{2705} SUCESSO CIRÚRGICO: Todos os gaps devem estar FECHADOS!");
        println!("   Execute o teste NIST completo para confirmação final.");
    } else {
        println!("\u{26A0}\u{FE0F} AJUSTE NECESSÁRIO: Refinamento precisa de calibração.");
    }
}

fn generate_test_samples(count: usize) -> Vec<u64> {
    let mut rng = rand::thread_rng();
    (0..count)
        .map(|idx| {
            let template = match idx % 3 {
                0 => 0xFFFF_0000_FFFF_0000u64,
                1 => 0x0000_FFFF_0000_FFFFu64,
                _ => 0xF0F0_F0F0_0F0F_0F0Fu64,
            };
            let noise = (rng.gen::<u32>() as u64) << (idx % 24);
            template ^ noise
        })
        .collect()
}

fn baseline_scores(buffer: &[u64]) -> GapSnapshot {
    let mut metrics = GapMetrics::new();
    metrics.analyze_chunk(buffer);
    let report = metrics.generate_gap_report();
    GapSnapshot {
        approximate_entropy_score: report.approximate_entropy_score,
        block_frequency_score: report.block_frequency_score,
        cumulative_sums_score: report.dft_score,
    }
}

struct GapSnapshot {
    approximate_entropy_score: f64,
    block_frequency_score: f64,
    cumulative_sums_score: f64,
}

#[derive(Clone, Copy, Default)]
struct SurgicalReportSnapshot {
    approx_entropy_score: f64,
    block_freq_score: f64,
    cumulative_sums_score: f64,
    predicted_nist_score: f64,
}

impl From<kayoscrypto_safe::quantum::SurgicalReport> for SurgicalReportSnapshot {
    fn from(report: kayoscrypto_safe::quantum::SurgicalReport) -> Self {
        Self {
            approx_entropy_score: report.approx_entropy_score,
            block_freq_score: report.block_freq_score,
            cumulative_sums_score: report.cumulative_sums_score,
            predicted_nist_score: report.predicted_nist_score,
        }
    }
}
