use std::{env, path::PathBuf, process::Command};

use serde::Deserialize;

#[derive(Debug, thiserror::Error)]
pub enum SatorBridgeError {
    #[error("python executable '{0}' not found or not executable")]
    PythonMissing(String),
    #[error("sator analyzer script not found at {0}")]
    ScriptMissing(PathBuf),
    #[error("failed to spawn python process: {0}")]
    Spawn(#[from] std::io::Error),
    #[error("sator analyzer returned non-zero exit status: {0}")]
    NonZeroStatus(String),
    #[error("failed to parse sator analyzer response: {0}")]
    Json(#[from] serde_json::Error),
}

#[derive(Clone, Debug, Deserialize)]
pub struct SatorAnalysisSnapshot {
    pub column_balance: f64,
    pub row_balance: f64,
    pub diagonal_symmetry: f64,
    pub quadrant_harmony: f64,
    pub density_balance: f64,
    pub sator_score: f64,
    #[serde(default)]
    pub sator_score_weighted: Option<f64>,
    #[serde(default)]
    pub segments_analyzed: Option<u32>,
    #[serde(default)]
    pub padding_bytes: Option<u32>,
    #[serde(default)]
    pub segment_quality_scores: Option<Vec<f64>>,
    #[serde(default)]
    pub aggregation_efficiency: Option<f64>,
}

#[derive(Clone, Debug, Deserialize)]
pub struct SatorOptimizationFeedback {
    pub force_level: u32,
    pub worst_metric: String,
    pub current_score: f64,
    pub target_score: f64,
    pub suggested_strategy: String,
    pub weighted_score: f64,
    pub confidence: f64,
}

#[derive(Clone, Debug)]
pub struct SatorPythonBridge {
    python_executable: String,
    script_path: PathBuf,
}

impl SatorPythonBridge {
    pub fn new() -> Result<Self, SatorBridgeError> {
        let python_executable = env::var("KAYOS_PYTHON_EXECUTABLE")
            .ok()
            .filter(|value| !value.trim().is_empty())
            .unwrap_or_else(|| "python3".to_string());

        let script_path = env::var("KAYOS_SATOR_SCRIPT")
            .ok()
            .map(PathBuf::from)
            .filter(|path| path.exists())
            .unwrap_or_else(|| {
                let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
                let repo_root = manifest_dir
                    .parent()
                    .and_then(|path| path.parent())
                    .map(PathBuf::from)
                    .unwrap_or(manifest_dir.clone());
                repo_root
                    .join("prototypes")
                    .join("kayos_entropy")
                    .join("sator_analyzer.py")
            });

        if !script_path.exists() {
            return Err(SatorBridgeError::ScriptMissing(script_path));
        }

        Ok(Self {
            python_executable,
            script_path,
        })
    }

    pub fn analyze_bytes(&self, data: &[u8]) -> Result<SatorAnalysisSnapshot, SatorBridgeError> {
        let payload = serde_json::to_string(data)?;
        let output = Command::new(&self.python_executable)
            .arg(&self.script_path)
            .arg("analyze")
            .arg(payload)
            .output();

        let output = match output {
            Ok(out) => out,
            Err(err) => {
                if err.kind() == std::io::ErrorKind::NotFound {
                    return Err(SatorBridgeError::PythonMissing(
                        self.python_executable.clone(),
                    ));
                }
                return Err(SatorBridgeError::Spawn(err));
            }
        };

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr).into_owned();
            return Err(SatorBridgeError::NonZeroStatus(stderr));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        let snapshot = serde_json::from_str(stdout.trim())?;
        Ok(snapshot)
    }

    pub fn optimize_output(
        &self,
        output: u64,
        force_level: u32,
    ) -> Result<SatorOptimizationFeedback, SatorBridgeError> {
        let payload = serde_json::json!({
            "output": output,
            "force_level": force_level,
        })
        .to_string();

        let output = Command::new(&self.python_executable)
            .arg(&self.script_path)
            .arg("optimize")
            .arg(payload)
            .output();

        let output = match output {
            Ok(out) => out,
            Err(err) => {
                if err.kind() == std::io::ErrorKind::NotFound {
                    return Err(SatorBridgeError::PythonMissing(
                        self.python_executable.clone(),
                    ));
                }
                return Err(SatorBridgeError::Spawn(err));
            }
        };

        if !output.status.success() {
            let stderr = String::from_utf8_lossy(&output.stderr).into_owned();
            return Err(SatorBridgeError::NonZeroStatus(stderr));
        }

        let stdout = String::from_utf8_lossy(&output.stdout);
        let feedback = serde_json::from_str(stdout.trim())?;
        Ok(feedback)
    }

    pub fn script_path(&self) -> &PathBuf {
        &self.script_path
    }

    pub fn python_executable(&self) -> &str {
        &self.python_executable
    }
}
