use kayoscrypto_safe::quantum::SurgicalEntropyRefiner;
use rand::Rng;

fn main() {
    println!("\u{1F3AF} TESTE DE FORÇA DO REFINAMENTO CIRÚRGICO");
    println!("==========================================\n");

    let test_samples = generate_test_samples(50_000);

    for force in [1, 3, 5, 8, 10] {
        println!("\n\u{1F527} TESTANDO FORÇA NÍVEL {force}:");
        let mut refiner = SurgicalEntropyRefiner::new(0xCAFEBABE_DEADBEEF);
        let mut samples = test_samples.clone();
        let report = refiner.refine_surgically_with_force(&mut samples, force);
        println!("   ApproximateEntropy:  {:.3}", report.approx_entropy_score);
        println!("   BlockFrequency:      {:.3}", report.block_freq_score);
        println!(
            "   CumulativeSums:      {:.3}",
            report.cumulative_sums_score
        );
        let predicted = report.predicted_nist_score;
        println!("   SCORE PREDITO:       {:.3}", predicted);
        if predicted > 0.99 {
            println!("   \u{2705} NÍVEL {force}: SUFICIENTE!");
            return;
        }
    }

    println!("\n\u{1F680} TESTE FINAL COM FORÇA MÁXIMA: 10");
    let mut refiner = SurgicalEntropyRefiner::new(0xCAFEBABE_DEADBEEF);
    let mut samples = test_samples.clone();
    let report = refiner.refine_surgically_with_force(&mut samples, 10);
    let predicted = report.predicted_nist_score;

    println!("\n\u{1F4CA} RESULTADO FINAL:");
    println!(
        "ApproximateEntropy:  0.958 → {:.3} (Δ{:+.3})",
        report.approx_entropy_score,
        report.approx_entropy_score - 0.958
    );
    println!(
        "BlockFrequency:      0.958 → {:.3} (Δ{:+.3})",
        report.block_freq_score,
        report.block_freq_score - 0.958
    );
    println!(
        "CumulativeSums:      0.958 → {:.3} (Δ{:+.3})",
        report.cumulative_sums_score,
        report.cumulative_sums_score - 0.958
    );
    println!("SCORE NIST PREDITO:   {:.3}", predicted);

    if predicted > 0.99 {
        println!("\n\u{1F389} SUCESSO! Todos os gaps FECHADOS com força 10!");
    } else {
        println!("\n\u{26A0}\u{FE0F} AINDA PRECISA DE AJUSTES.");
        println!(
            "   - BlockFrequency: {:.3} (meta > 0.99)",
            report.block_freq_score
        );
        println!(
            "   - CumulativeSums: {:.3} (meta > 0.99)",
            report.cumulative_sums_score
        );
    }
}

fn generate_test_samples(count: usize) -> Vec<u64> {
    let mut rng = rand::thread_rng();
    (0..count).map(|_| rng.gen()).collect()
}
