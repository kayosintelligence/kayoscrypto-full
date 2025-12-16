use kayoscrypto_safe::analysis::kayos_pattern_analyzer::KayosStreamAnalyzer;
use kayoscrypto_safe::analysis::kayos_pattern_analyzer::StreamDiagnosis;
use kayoscrypto_safe::behavior::{BehaviorClassifier, BehaviorProfile};
use serde::Serialize;
use std::env;
use std::error::Error;
use std::fs;

fn main() -> Result<(), Box<dyn Error>> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("usage: {} <binary_stream_file>", args[0]);
        std::process::exit(1);
    }

    let path = &args[1];
    let data = fs::read(path)?;

    let mut analyzer = KayosStreamAnalyzer::new();
    let diagnosis = analyzer.analyze_stream_pattern(&data);

    let classifier = BehaviorClassifier::new();
    let behavior = classifier.classify(&diagnosis);

    let report = AnalyzerReport {
        diagnosis,
        behavior,
    };
    println!("{}", serde_json::to_string_pretty(&report)?);

    Ok(())
}

#[derive(Serialize)]
struct AnalyzerReport {
    #[serde(flatten)]
    diagnosis: StreamDiagnosis,
    behavior: BehaviorProfile,
}
