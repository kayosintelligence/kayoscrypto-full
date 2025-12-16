use std::env;

use kayoscrypto_safe::quantum::{
    sator_bridge::{SatorAnalysisSnapshot, SatorBridgeError, SatorPythonBridge},
    surgical_refiner::SurgicalEntropyRefiner,
};
use rand::Rng;
use serde::Serialize;

#[derive(Serialize)]
struct SampleRecord {
    force_level: u32,
    sample_index: usize,
    input: u64,
    output: u64,
    approx_entropy_score: f64,
    block_frequency_score: f64,
    cumulative_sums_score: f64,
    predicted_nist_score: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_score: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_score_weighted: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_column_balance: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_row_balance: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_diagonal_symmetry: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_quadrant_harmony: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_density_balance: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_suggested_strategy: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    sator_confidence: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    adjusted_force_level: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    predicted_score_with_sator: Option<f64>,
}

fn parse_args() -> Result<(u32, usize, u64), String> {
    let mut args = env::args().skip(1);
    let force_level = args
        .next()
        .ok_or_else(|| "expected <force_level>".to_string())?
        .parse::<u32>()
        .map_err(|err| format!("invalid force_level: {err}"))?;

    let sample_count = args
        .next()
        .ok_or_else(|| "expected <sample_count>".to_string())?
        .parse::<usize>()
        .map_err(|err| format!("invalid sample_count: {err}"))?;

    let kayos_id = match args.next() {
        Some(id_str) => id_str
            .parse::<u64>()
            .map_err(|err| format!("invalid kayos_id: {err}"))?,
        None => 0x6973_5341_6b61_796f, // "isSAkayo" marker for reproducibility
    };

    Ok((force_level, sample_count, kayos_id))
}

fn main() -> Result<(), String> {
    let (force_level, sample_count, kayos_id) = parse_args()?;
    let mut rng = rand::thread_rng();
    let mut refiner = SurgicalEntropyRefiner::new(kayos_id);
    let mut sator_bridge = match SatorPythonBridge::new() {
        Ok(bridge) => Some(bridge),
        Err(SatorBridgeError::ScriptMissing(path)) => {
            eprintln!(
                "[generate_refiner_samples] Sator analyzer script not found at '{}'. Skipping Sator metrics.",
                path.display()
            );
            None
        }
        Err(SatorBridgeError::PythonMissing(exec)) => {
            eprintln!(
                "[generate_refiner_samples] Python executable '{}' not available. Skipping Sator metrics.",
                exec
            );
            None
        }
        Err(err) => {
            eprintln!(
                "[generate_refiner_samples] Failed to initialize Sator bridge ({}). Skipping Sator metrics.",
                err
            );
            None
        }
    };

    for sample_index in 0..sample_count {
        let input = rng.gen::<u64>();
        let mut buffer = [input];
        let report = refiner.refine_surgically_with_force(&mut buffer, force_level);
        let output = buffer[0];

        let mut sator_snapshot: Option<SatorAnalysisSnapshot> = None;
        let mut sator_weighted_score: Option<f64> = None;
        let mut sator_suggested_strategy: Option<String> = None;
        let mut sator_confidence: Option<f64> = None;
        let mut adjusted_force_level: Option<u32> = None;
        let mut predicted_score_with_sator: Option<f64> = None;
        let mut disable_sator = false;

        if let Some(bridge) = sator_bridge.as_ref() {
            match bridge.analyze_bytes(&output.to_be_bytes()) {
                Ok(snapshot) => {
                    let weighted_from_snapshot = snapshot.sator_score_weighted;
                    match bridge.optimize_output(output, force_level) {
                        Ok(feedback) => {
                            let new_level = refiner.apply_sator_guidance(&feedback);
                            adjusted_force_level = Some(new_level);
                            sator_suggested_strategy = Some(feedback.suggested_strategy.clone());
                            sator_confidence = Some(feedback.confidence);
                            let weighted =
                                weighted_from_snapshot.unwrap_or(feedback.weighted_score);
                            sator_weighted_score = Some(weighted);
                            predicted_score_with_sator = Some(
                                (report.approx_entropy_score
                                    + report.block_freq_score
                                    + report.cumulative_sums_score
                                    + weighted)
                                    / 4.0,
                            );
                            sator_snapshot = Some(snapshot);
                        }
                        Err(err) => {
                            eprintln!(
                                "[generate_refiner_samples] Sator optimization feedback failed ({}). Disabling further attempts.",
                                err
                            );
                            disable_sator = true;
                        }
                    }
                }
                Err(err) => {
                    eprintln!(
                        "[generate_refiner_samples] Sator analysis failed ({}). Disabling further attempts.",
                        err
                    );
                    disable_sator = true;
                }
            }
        }

        if disable_sator {
            sator_bridge = None;
        }

        let record = SampleRecord {
            force_level,
            sample_index,
            input,
            output,
            approx_entropy_score: report.approx_entropy_score,
            block_frequency_score: report.block_freq_score,
            cumulative_sums_score: report.cumulative_sums_score,
            predicted_nist_score: report.predicted_nist_score,
            sator_score: sator_snapshot.as_ref().map(|snapshot| snapshot.sator_score),
            sator_score_weighted: sator_weighted_score,
            sator_column_balance: sator_snapshot
                .as_ref()
                .map(|snapshot| snapshot.column_balance),
            sator_row_balance: sator_snapshot.as_ref().map(|snapshot| snapshot.row_balance),
            sator_diagonal_symmetry: sator_snapshot
                .as_ref()
                .map(|snapshot| snapshot.diagonal_symmetry),
            sator_quadrant_harmony: sator_snapshot
                .as_ref()
                .map(|snapshot| snapshot.quadrant_harmony),
            sator_density_balance: sator_snapshot
                .as_ref()
                .map(|snapshot| snapshot.density_balance),
            sator_suggested_strategy,
            sator_confidence,
            adjusted_force_level,
            predicted_score_with_sator,
        };

        let json = serde_json::to_string(&record)
            .map_err(|err| format!("failed to serialize record: {err}"))?;
        println!("{json}");
    }

    Ok(())
}
