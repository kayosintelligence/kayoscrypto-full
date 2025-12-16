use std::collections::VecDeque;
use std::env;
use std::fs::File;
use std::io::{self, BufWriter, Write};
use std::path::PathBuf;
use std::str::FromStr;

use kayoscrypto_safe::quantum::{KayosMode, SatorObservation, SatorOrchestrator, VelhoMatuto};
use rand::rngs::OsRng;
use rand::RngCore;
use rand::SeedableRng;
use rand_chacha::ChaCha20Rng;

fn parse_bytes(arg: &str) -> Result<Option<usize>, String> {
    let normalized = arg.trim().to_lowercase();
    if normalized == "infinite" || normalized == "inf" {
        return Ok(None);
    }
    let (numeric_part, multiplier) = if let Some(rest) = normalized.strip_suffix("kb") {
        (rest, 1024usize)
    } else if let Some(rest) = normalized.strip_suffix("mb") {
        (rest, 1024usize * 1024)
    } else if let Some(rest) = normalized.strip_suffix("gb") {
        (rest, 1024usize * 1024 * 1024)
    } else {
        (normalized.as_str(), 1usize)
    };

    let value = numeric_part
        .trim()
        .parse::<f64>()
        .map_err(|err| format!("invalid size '{arg}': {err}"))?;
    let bytes = (value * multiplier as f64) as usize;
    if bytes == 0 {
        Err(format!("requested size '{arg}' resolves to zero bytes"))
    } else {
        Ok(Some(bytes))
    }
}

#[derive(Debug)]
enum OutputTarget {
    File(PathBuf),
    Stdout,
}

fn parse_args() -> Result<(Option<usize>, OutputTarget, u32, u64, KayosMode, bool), String> {
    let mut args = env::args().skip(1);
    let size_arg = args
        .next()
        .ok_or_else(|| "expected <size_bytes>".to_string())?;
    let total_bytes = parse_bytes(&size_arg)?;

    let output_target = args
        .next()
        .map(|value| {
            if value == "-" {
                OutputTarget::Stdout
            } else {
                OutputTarget::File(PathBuf::from(value))
            }
        })
        .unwrap_or_else(|| OutputTarget::File(PathBuf::from("kayos_entropy_stream.bin")));

    let force_level = args
        .next()
        .map(|value| value.parse::<u32>())
        .transpose()
        .map_err(|err| format!("invalid force level: {err}"))?
        .unwrap_or(8);

    let kayos_id = args
        .next()
        .map(|value| value.parse::<u64>())
        .transpose()
        .map_err(|err| format!("invalid kayos id: {err}"))?
        .unwrap_or(0x4B_41_59_4F_53_5F_455F);

    let mode = args
        .next()
        .map(|value| KayosMode::from_str(&value))
        .transpose()
        .map_err(|err| format!("invalid mode: {err}"))?
        .unwrap_or_else(|| VelhoMatuto::decide("high_risk"));

    let mut enable_matrix_fix = false;
    for extra in args {
        match extra.as_str() {
            "--matrix-fix" => enable_matrix_fix = true,
            "--no-matrix-fix" => enable_matrix_fix = false,
            other => return Err(format!("unexpected argument '{other}'")),
        }
    }

    Ok((
        total_bytes,
        output_target,
        force_level,
        kayos_id,
        mode,
        enable_matrix_fix,
    ))
}

fn flush_pending<W: Write>(
    writer: &mut W,
    queue: &mut VecDeque<u8>,
    remaining: Option<&mut usize>,
    produced_bytes: &mut u128,
    stream_mode: bool,
) -> Result<bool, String> {
    let mut target_len = queue.len();
    if let Some(remaining_ref) = remaining.as_ref() {
        target_len = target_len.min(**remaining_ref);
    }

    if target_len == 0 {
        return Ok(true);
    }

    let chunk: Vec<u8> = queue.drain(..target_len).collect();
    if let Err(err) = writer.write_all(&chunk) {
        if stream_mode && err.kind() == io::ErrorKind::BrokenPipe {
            eprintln!(
                "[generate_entropy_stream] broken pipe detected after {} bytes written",
                produced_bytes
            );
            return Ok(false);
        }
        return Err(format!("failed to write data: {err}"));
    }

    *produced_bytes += chunk.len() as u128;
    if let Some(remaining_ref) = remaining {
        *remaining_ref -= chunk.len();
    }

    Ok(true)
}

fn main() -> Result<(), String> {
    let (total_bytes, output_target, force_level, kayos_id, mode, enable_matrix_fix) =
        parse_args()?;
    let stream_mode = matches!(output_target, OutputTarget::Stdout);

    if total_bytes.is_none() && !matches!(output_target, OutputTarget::Stdout) {
        return Err("infinite generation requires '-' output target".to_string());
    }

    let stdout_handle;
    let writer: Box<dyn Write> = match &output_target {
        OutputTarget::File(path) => {
            let file = File::create(path)
                .map_err(|err| format!("failed to create '{}': {err}", path.display()))?;
            Box::new(BufWriter::new(file))
        }
        OutputTarget::Stdout => {
            stdout_handle = io::stdout();
            Box::new(BufWriter::new(stdout_handle))
        }
    };

    let mut rng = ChaCha20Rng::from_rng(OsRng).map_err(|err| format!("rng init failed: {err}"))?;
    let mut orchestrator = SatorOrchestrator::new(mode, kayos_id);
    if enable_matrix_fix && matches!(mode, KayosMode::MatutoRegulatorio) {
        orchestrator.enable_matrix_fix();
    }
    let matrix_fix_active = orchestrator.matrix_fix_active();
    let mut writer = writer;
    let mut buffer = [0u64; 1];
    let mut blocks_generated: u64 = 0;
    let mut last_observation: Option<SatorObservation> = None;
    let mut produced_bytes: u128 = 0;
    let mut pending_output = VecDeque::new();
    let mut stream_alive = true;

    if let Some(mut remaining) = total_bytes {
        let total_target = remaining;
        while remaining > 0 && stream_alive {
            let raw = rng.next_u64();
            let (processed, observation) = orchestrator.process(raw);
            buffer[0] = processed;
            let bytes = buffer[0].to_be_bytes();
            if matrix_fix_active {
                pending_output.extend(orchestrator.post_process_block(&bytes));
            } else {
                pending_output.extend(bytes);
            }

            stream_alive = flush_pending(
                &mut writer,
                &mut pending_output,
                Some(&mut remaining),
                &mut produced_bytes,
                stream_mode,
            )?;

            blocks_generated += 1;
            last_observation = Some(observation);

            if blocks_generated % 1_000_000 == 0 {
                let produced = total_target.saturating_sub(remaining);
                eprintln!(
                    "[generate_entropy_stream] produced {} MB of {} MB (mode {:?})",
                    produced / (1024 * 1024),
                    total_target / (1024 * 1024),
                    orchestrator.mode()
                );
            }
        }

        if stream_alive {
            if matrix_fix_active {
                pending_output.extend(orchestrator.finalize_matrix_fix());
            }
            flush_pending(
                &mut writer,
                &mut pending_output,
                Some(&mut remaining),
                &mut produced_bytes,
                stream_mode,
            )?;
        }
    } else {
        while stream_alive {
            let raw = rng.next_u64();
            let (processed, observation) = orchestrator.process(raw);
            buffer[0] = processed;
            let bytes = buffer[0].to_be_bytes();
            if matrix_fix_active {
                pending_output.extend(orchestrator.post_process_block(&bytes));
            } else {
                pending_output.extend(bytes);
            }

            stream_alive = flush_pending(
                &mut writer,
                &mut pending_output,
                None,
                &mut produced_bytes,
                stream_mode,
            )?;

            blocks_generated += 1;
            last_observation = Some(observation);

            if blocks_generated % 1_000_000 == 0 {
                eprintln!(
                    "[generate_entropy_stream] produced {} MB (mode {:?})",
                    produced_bytes / ((1024 * 1024) as u128),
                    orchestrator.mode()
                );
            }
        }
    }

    if let Err(err) = writer.flush() {
        if !(stream_mode && err.kind() == io::ErrorKind::BrokenPipe) {
            return Err(format!("failed to flush output: {err}"));
        }
    }

    if let Some(observation) = last_observation {
        if stream_mode {
            eprintln!(
                "[generate_entropy_stream] mode {:?} gap {:.4} perm {:.4} weight {:.4} severity {:.3} predicted {:.1}",
                orchestrator.mode(),
                observation.summary.gap_deviation,
                observation.summary.permutation_bias,
                observation.summary.weight_bias,
                observation.forecast.severity,
                observation.forecast.predicted_failures
            );
        } else {
            println!(
                "[generate_entropy_stream] mode {:?} gap {:.4} perm {:.4} weight {:.4} severity {:.3} predicted {:.1}",
                orchestrator.mode(),
                observation.summary.gap_deviation,
                observation.summary.permutation_bias,
                observation.summary.weight_bias,
                observation.forecast.severity,
                observation.forecast.predicted_failures
            );
        }

        if let Some(audit) = observation.audit {
            if stream_mode {
                eprintln!(
                    "[generate_entropy_stream] audit sator_score {:.4} column {:.4} row {:.4}",
                    audit.sator_score,
                    audit.column_balance,
                    audit.row_balance
                );
            } else {
                println!(
                    "[generate_entropy_stream] audit sator_score {:.4} column {:.4} row {:.4}",
                    audit.sator_score,
                    audit.column_balance,
                    audit.row_balance
                );
            }
        }
    }

    if let Some(err) = orchestrator.last_audit_error() {
        eprintln!("[generate_entropy_stream] auditor fallback: {err}");
    }

    match (&output_target, total_bytes) {
        (OutputTarget::File(path), Some(total_target)) => {
            println!(
                "[generate_entropy_stream] wrote {} bytes to '{}' with force level {}",
                total_target,
                path.display(),
                force_level
            );
        }
        (OutputTarget::File(_), None) => {
            unreachable!("infinite generation with file output is disallowed");
        }
        (OutputTarget::Stdout, Some(_)) => {
            eprintln!(
                "[generate_entropy_stream] streamed up to {} bytes to stdout with force level {}",
                produced_bytes,
                force_level
            );
        }
        (OutputTarget::Stdout, None) => {
            eprintln!(
                "[generate_entropy_stream] streamed {} bytes (infinite mode) to stdout with force level {}",
                produced_bytes,
                force_level
            );
        }
    }

    Ok(())
}
