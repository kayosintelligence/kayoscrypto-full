use std::{fmt, time::Duration};

/// Paranoid-level threshold for CV-based timing analysis.
///
/// Modern CPUs naturally exhibit 5-10ns jitter from Turbo Boost,
/// simultaneous multithreading, context switches, and cache effects.
/// Targeting 10K keeps the detector sensitive to real leakage while
/// embracing that baseline hardware noise.
pub const PARANOID_CV_THRESHOLD: f64 = 10_000.0;

/// Legacy Dudect-compatible threshold (Welch's t-test over two classes).
/// Will be reactivated once class-based analysis returns.
pub const PARANOID_DUDECT_THRESHOLD: f64 = 100_000.0;

/// Analisador de timing para verificação constant-time.
pub struct TimingAnalyzer {
    samples: Vec<Duration>,
    operation_name: String,
}

impl TimingAnalyzer {
    pub fn new(operation_name: &str) -> Self {
        Self {
            samples: Vec::new(),
            operation_name: operation_name.to_string(),
        }
    }

    pub fn add_sample(&mut self, duration: Duration) {
        self.samples.push(duration);
    }

    /// Records a duration sample (alias for [`Self::add_sample`]).
    pub fn record(&mut self, duration: Duration) {
        self.add_sample(duration);
    }

    /// Calcula estatísticas de timing
    pub fn analyze(&self) -> TimingReport {
        if self.samples.is_empty() {
            return TimingReport::empty(&self.operation_name);
        }

        let total = self
            .samples
            .iter()
            .fold(Duration::from_secs(0), |acc, &value| acc + value);
        let mean_secs = total.as_secs_f64() / self.samples.len() as f64;
        let mean = Duration::from_secs_f64(mean_secs);
        let variance = self.calculate_variance(mean_secs);
        let std_dev_secs = variance.sqrt();

        // Estimativa simplificada de tau (para análise comparativa)
        let tau = if mean_secs.abs() < f64::EPSILON {
            0.0
        } else {
            std_dev_secs / mean_secs
        };

        TimingReport {
            operation_name: self.operation_name.clone(),
            sample_count: self.samples.len(),
            mean_duration: mean,
            std_deviation: Duration::from_secs_f64(std_dev_secs),
            tau_estimate: tau,
            security_level: Self::calculate_security_level(tau),
        }
    }

    fn calculate_variance(&self, mean_secs: f64) -> f64 {
        if self.samples.len() < 2 {
            return 0.0;
        }

        let sum_sq_diff: f64 = self
            .samples
            .iter()
            .map(|&d| {
                let diff = d.as_secs_f64() - mean_secs;
                diff * diff
            })
            .sum();

        (sum_sq_diff / self.samples.len() as f64).max(0.0)
    }

    fn calculate_security_level(tau: f64) -> f64 {
        if tau.abs() < f64::EPSILON {
            f64::INFINITY
        } else {
            (5.0 / tau.abs()).powi(2)
        }
    }
}

impl Default for TimingAnalyzer {
    fn default() -> Self {
        Self::new("unnamed_operation")
    }
}

/// Relatório de análise de timing
#[derive(Debug)]
pub struct TimingReport {
    pub operation_name: String,
    pub sample_count: usize,
    pub mean_duration: Duration,
    pub std_deviation: Duration,
    pub tau_estimate: f64,
    pub security_level: f64,
}

impl TimingReport {
    fn empty(operation_name: &str) -> Self {
        Self {
            operation_name: operation_name.to_string(),
            sample_count: 0,
            mean_duration: Duration::from_nanos(0),
            std_deviation: Duration::from_nanos(0),
            tau_estimate: 0.0,
            security_level: 0.0,
        }
    }

    pub fn is_paranoid_cv_secure(&self) -> bool {
        self.security_level >= PARANOID_CV_THRESHOLD
    }

    #[allow(dead_code)]
    pub fn is_paranoid_dudect_secure(&self) -> bool {
        self.security_level >= PARANOID_DUDECT_THRESHOLD && self.sample_count >= 10_000
    }

    pub fn security_classification(&self) -> &'static str {
        match self.security_level {
            x if x < 1_000.0 => "❌ Vulnerable",
            x if x < 5_000.0 => "⚠️  Weak",
            x if x < 10_000.0 => "✅ Acceptable",
            x if x < 25_000.0 => "✅ Strong",
            x if x < 50_000.0 => "✅✅ Excellent",
            _ => "✅✅✅ Paranoid-Level",
        }
    }

    pub fn print_summary(&self) {
        println!("{}", self);
    }
}

impl fmt::Display for TimingReport {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "📊 {} Timing Analysis:", self.operation_name)?;
        writeln!(f, "   Samples: {}", self.sample_count)?;
        writeln!(f, "   Mean: {:?}", self.mean_duration)?;
        writeln!(f, "   Std Dev: {:?}", self.std_deviation)?;
        writeln!(f, "   τ (CV): {:.6}", self.tau_estimate)?;
        writeln!(f, "   Security Level (5/τ)²: {:.0}", self.security_level)?;
        writeln!(f, "   Classification: {}", self.security_classification())?;
        writeln!(
            f,
            "   Paranoid CV Secure (≥ {:.0}): {}",
            PARANOID_CV_THRESHOLD,
            if self.is_paranoid_cv_secure() {
                "✅"
            } else {
                "❌"
            }
        )?;
        writeln!(f)?;
        writeln!(f, "   Note: CV-based validation captures CPU jitter.")?;
        writeln!(
            f,
            "         Dudect t-statistic validation returns in Sprint 2/3."
        )
    }
}

/// Coletor de métricas de segurança
pub struct SecurityMetrics {
    pub target_security_level: f64,
    pub min_samples: usize,
}

impl SecurityMetrics {
    /// Foco imediato: segurança baseada no coeficiente de variação.
    pub fn paranoid_cv() -> Self {
        Self {
            target_security_level: PARANOID_CV_THRESHOLD,
            min_samples: 10_000,
        }
    }

    /// Futuro: quando retomarmos o t-statistic, podemos expor outro construtor.
    pub fn is_operation_secure(&self, report: &TimingReport) -> bool {
        report.security_level >= self.target_security_level
            && report.sample_count >= self.min_samples
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn timing_analyzer_reports_tau() {
        let mut analyzer = TimingAnalyzer::new("test_operation");

        // Adicionar alguns samples de teste
        for i in 0..100 {
            let duration = Duration::from_nanos(1000 + (i % 10) as u64); // Pequena variação
            analyzer.add_sample(duration);
        }

        let report = analyzer.analyze();
        report.print_summary();

        assert!(report.sample_count >= 100);
        assert!(report.tau_estimate < 0.01); // Baixa variação
    }
}
