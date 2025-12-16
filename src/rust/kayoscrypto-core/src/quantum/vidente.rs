use super::relojoeiro::RelojoeiroSummary;

#[derive(Clone, Debug, Default)]
pub struct VidenteForecast {
    pub severity: f64,
    pub predicted_failures: f64,
    pub p_value_window: (f64, f64),
}

pub struct Vidente {
    lookback: usize,
    history: Vec<RelojoeiroSummary>,
}

impl Vidente {
    pub fn new(lookback: usize) -> Self {
        let lookback = lookback.max(1);
        Self {
            lookback,
            history: Vec::with_capacity(lookback),
        }
    }

    pub fn update(&mut self, summary: RelojoeiroSummary) -> VidenteForecast {
        if self.history.len() == self.lookback {
            self.history.remove(0);
        }
        self.history.push(summary.clone());

        let averaged = self.average_summary();
        let severity_current = self.compute_severity(&summary);
        let severity_avg = self.compute_severity(&averaged);
        let severity = severity_current.max(severity_avg);
        let failures = (severity * 16.0).clamp(0.0, 16.0);
        let window = self.estimate_window(severity);

        VidenteForecast {
            severity,
            predicted_failures: failures,
            p_value_window: window,
        }
    }

    fn average_summary(&self) -> RelojoeiroSummary {
        if self.history.is_empty() {
            return RelojoeiroSummary::default();
        }

        let mut acc = RelojoeiroSummary::default();
        for item in &self.history {
            acc.gap_deviation += item.gap_deviation;
            acc.permutation_bias += item.permutation_bias;
            acc.weight_bias += item.weight_bias;
        }

        let denom = self.history.len() as f64;
        acc.gap_deviation /= denom;
        acc.permutation_bias /= denom;
        acc.weight_bias /= denom;
        acc
    }

    fn compute_severity(&self, summary: &RelojoeiroSummary) -> f64 {
        let weighted = (summary.gap_deviation * 0.4)
            + (summary.permutation_bias * 0.35)
            + (summary.weight_bias * 0.25);
        weighted.min(1.0)
    }

    fn estimate_window(&self, severity: f64) -> (f64, f64) {
        let spread = (severity * 0.4).min(0.4);
        let center = 0.5;
        let low = (center - spread).clamp(0.0, 1.0);
        let high = (center + spread).clamp(0.0, 1.0);
        (low, high)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn severity_tracks_bias() {
        let mut vidente = Vidente::new(4);
        let mut summary = RelojoeiroSummary::default();
        assert!(vidente.update(summary.clone()).severity <= 0.01);

        summary.gap_deviation = 0.8;
        summary.permutation_bias = 0.6;
        summary.weight_bias = 0.4;
        let forecast = vidente.update(summary);
        assert!(forecast.severity > 0.4);
        assert!(forecast.p_value_window.0 < 0.4);
        assert!(forecast.p_value_window.1 > 0.6);
    }
}
