use serde::Serialize;

use crate::analysis::kayos_pattern_analyzer::{PatternType, StreamDiagnosis};

/// Mirrors the KAYOS "Neurônio Espelho" regime, translating temporal observations
/// into behavioural states and concrete counter-movements.
pub struct BehaviorClassifier {
    confidence_floor: f64,
}

impl BehaviorClassifier {
    pub fn new() -> Self {
        Self {
            confidence_floor: 0.2,
        }
    }

    pub fn classify(&self, diagnosis: &StreamDiagnosis) -> BehaviorProfile {
        let mut profile = BehaviorProfile::default();

        if diagnosis.analyses.is_empty() {
            profile.state = BehaviorState::ObservationNeeded;
            profile.confidence = self.confidence_floor;
            profile
                .recommended_actions
                .push("Collect additional temporal windows to raise diagnostic confidence.".into());
            return profile;
        }

        profile.mirrored_pattern = diagnosis.primary_pattern.clone();
        profile.model_score = self.derive_model_score(diagnosis);
        profile.confidence = self.derive_confidence(diagnosis);
        profile.drivers = self.identify_drivers(diagnosis);

        let state = self.derive_state(diagnosis);
        profile.state = state;
        profile.risk_level = self.derive_risk_level(diagnosis, state);
        profile.recommended_actions = self.plan_actions(&profile);

        profile
    }

    fn derive_model_score(&self, diagnosis: &StreamDiagnosis) -> f64 {
        let stability = diagnosis.average_stability;
        let force = diagnosis.average_force_correlation.abs();
        let change_penalty = (diagnosis.change_points.len() as f64 / 10.0).min(0.3);
        let cycles = diagnosis.average_cyclical_strength;
        let cyclical_balance = 1.0 - (cycles - 0.5).abs();

        clamp_unit(
            0.35 * stability
                + 0.25 * cyclical_balance
                + 0.25 * (1.0 - force)
                + 0.15 * (1.0 - change_penalty),
        )
    }

    fn derive_confidence(&self, diagnosis: &StreamDiagnosis) -> f64 {
        let sample_ratio = (diagnosis.analyses.len() as f64 / 24.0).min(1.0);
        let dispersion = clamp_unit(diagnosis.sator_score_std.unwrap_or(0.25));
        let certainty = 1.0 - dispersion;

        clamp_unit(self.confidence_floor + 0.5 * sample_ratio + 0.3 * certainty)
    }

    fn derive_state(&self, diagnosis: &StreamDiagnosis) -> BehaviorState {
        let stability = diagnosis.average_stability;
        let cycles = diagnosis.average_cyclical_strength;
        let force = diagnosis.average_force_correlation;
        let changes = diagnosis.change_points.len();

        match diagnosis.primary_pattern {
            PatternType::ForcedTransitions => BehaviorState::CriticalDisruption,
            PatternType::DeterministicRotation => BehaviorState::StableFlow,
            PatternType::LocalizedBias => BehaviorState::EscortBias,
            PatternType::TemporalCycles => BehaviorState::AdaptiveRhythm,
            PatternType::ComplexInteraction => {
                if stability < 0.45 && changes > 6 {
                    BehaviorState::CriticalDisruption
                } else if cycles > 0.5 {
                    BehaviorState::AdaptiveRhythm
                } else if force.abs() > 0.55 {
                    BehaviorState::EscortBias
                } else {
                    BehaviorState::TransitionalPhase
                }
            }
            PatternType::InsufficientData => BehaviorState::ObservationNeeded,
        }
    }

    fn derive_risk_level(&self, diagnosis: &StreamDiagnosis, state: BehaviorState) -> RiskLevel {
        let instability = 1.0 - diagnosis.average_stability;
        let force = diagnosis.average_force_correlation.abs();
        let change_ratio = (diagnosis.change_points.len() as f64 / 12.0).min(1.0);

        let composite = (0.5 * instability) + (0.3 * force) + (0.2 * change_ratio);

        match state {
            BehaviorState::CriticalDisruption if composite > 0.55 => RiskLevel::Critical,
            BehaviorState::CriticalDisruption | BehaviorState::EscortBias if composite > 0.45 => {
                RiskLevel::High
            }
            BehaviorState::AdaptiveRhythm | BehaviorState::TransitionalPhase
                if composite > 0.35 =>
            {
                RiskLevel::Moderate
            }
            BehaviorState::ObservationNeeded => RiskLevel::Unknown,
            _ => RiskLevel::Low,
        }
    }

    fn identify_drivers(&self, diagnosis: &StreamDiagnosis) -> Vec<String> {
        let mut drivers = Vec::new();

        if diagnosis.average_stability < 0.4 {
            drivers.push("Low stability across temporal windows".into());
        }
        if diagnosis.average_force_correlation.abs() > 0.6 {
            drivers.push("Strong directional bias detected in force correlation".into());
        }
        if diagnosis.average_cyclical_strength > 0.6 {
            drivers.push("High cyclical strength suggests rhythmic behaviour".into());
        }
        if diagnosis.change_points.len() > 8 {
            drivers.push("Frequent change points indicate transition pressure".into());
        }
        if drivers.is_empty() {
            drivers.push("Stable observational regime".into());
        }

        drivers
    }

    fn plan_actions(&self, profile: &BehaviorProfile) -> Vec<String> {
        match profile.state {
            BehaviorState::StableFlow => vec![
                "Maintain current configuration; continue passive monitoring.".into(),
                "Log baseline metrics for comparison with future phases.".into(),
            ],
            BehaviorState::AdaptiveRhythm => vec![
                "Validate cyclical alignment with intended Fibonacci-Ezekiel cadence.".into(),
                "Prepare adaptive key rotation to follow detected rhythm.".into(),
            ],
            BehaviorState::EscortBias => vec![
                "Deploy targeted entropy refiner to offset localized bias.".into(),
                "Increase sampling density to confirm directional persistence.".into(),
            ],
            BehaviorState::TransitionalPhase => vec![
                "Trigger predictive simulations to forecast next transition.".into(),
                "Stage optimization module for rapid intervention.".into(),
            ],
            BehaviorState::CriticalDisruption => vec![
                "Escalate to emergency corrective protocol; freeze outbound keys.".into(),
                "Activate Sator bridge in high-frequency mode for real-time diagnostics.".into(),
            ],
            BehaviorState::ObservationNeeded => vec![
                "Extend observation window; insufficient evidence for behavior mapping.".into(),
                "Under-sample environment noise to isolate genuine signal.".into(),
            ],
        }
    }
}

impl Default for BehaviorClassifier {
    fn default() -> Self {
        Self::new()
    }
}

#[derive(Clone, Debug, Serialize)]
pub struct BehaviorProfile {
    pub state: BehaviorState,
    pub risk_level: RiskLevel,
    pub mirrored_pattern: PatternType,
    pub confidence: f64,
    pub model_score: f64,
    pub drivers: Vec<String>,
    pub recommended_actions: Vec<String>,
}

impl BehaviorProfile {
    pub fn stable() -> Self {
        Self::default()
    }
}

impl Default for BehaviorProfile {
    fn default() -> Self {
        Self {
            state: BehaviorState::ObservationNeeded,
            risk_level: RiskLevel::Unknown,
            mirrored_pattern: PatternType::InsufficientData,
            confidence: 0.0,
            model_score: 0.0,
            drivers: Vec::new(),
            recommended_actions: Vec::new(),
        }
    }
}

#[derive(Clone, Copy, Debug, Serialize, PartialEq, Eq)]
pub enum BehaviorState {
    StableFlow,
    AdaptiveRhythm,
    EscortBias,
    TransitionalPhase,
    CriticalDisruption,
    ObservationNeeded,
}

#[derive(Clone, Copy, Debug, Serialize, PartialEq, Eq)]
pub enum RiskLevel {
    Low,
    Moderate,
    High,
    Critical,
    Unknown,
}

fn clamp_unit(value: f64) -> f64 {
    value.max(0.0).min(1.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::analysis::kayos_pattern_analyzer::{StreamDiagnosis, TemporalAnalysis};

    fn build_diagnosis(
        stability: f64,
        cyclical: f64,
        force: f64,
        change_points_per_window: usize,
        score: f64,
    ) -> StreamDiagnosis {
        let mut diagnosis = StreamDiagnosis::new();
        let windows = 6usize;

        for idx in 0..windows {
            let mut change_points = Vec::new();
            if change_points_per_window > 0 {
                change_points.extend((0..change_points_per_window).map(|offset| idx * 10 + offset));
            }

            diagnosis.add_analysis(TemporalAnalysis {
                window_size: 1024,
                pattern_stability: stability,
                cyclical_strength: cyclical,
                change_points,
                force_correlation: force,
                latest_score: Some(score),
            });
        }

        diagnosis.set_scores(vec![score; windows]);
        diagnosis.finalize();
        diagnosis
    }

    #[test]
    fn classifier_identifies_stable_flow() {
        let diagnosis = build_diagnosis(0.95, 0.10, 0.10, 0, 0.60);
        let classifier = BehaviorClassifier::new();
        let profile = classifier.classify(&diagnosis);

        assert_eq!(profile.state, BehaviorState::StableFlow);
        assert_eq!(profile.risk_level, RiskLevel::Low);
        assert!(profile
            .recommended_actions
            .iter()
            .any(|action| action.contains("baseline")));
    }

    #[test]
    fn classifier_identifies_adaptive_rhythm() {
        let diagnosis = build_diagnosis(0.70, 0.80, 0.20, 2, 0.65);
        let classifier = BehaviorClassifier::new();
        let profile = classifier.classify(&diagnosis);

        assert_eq!(profile.state, BehaviorState::AdaptiveRhythm);
        assert_eq!(profile.risk_level, RiskLevel::Moderate);
        assert!(profile
            .recommended_actions
            .iter()
            .any(|action| action.contains("cyclical")));
    }

    #[test]
    fn classifier_identifies_localized_bias() {
        let diagnosis = build_diagnosis(0.60, 0.30, 0.85, 3, 0.55);
        let classifier = BehaviorClassifier::new();
        let profile = classifier.classify(&diagnosis);

        assert_eq!(profile.state, BehaviorState::EscortBias);
        assert!(matches!(
            profile.risk_level,
            RiskLevel::High | RiskLevel::Moderate
        ));
        assert!(profile
            .recommended_actions
            .iter()
            .any(|action| action.contains("entropy refiner")));
    }

    #[test]
    fn classifier_flags_critical_disruption() {
        let diagnosis = build_diagnosis(0.20, 0.10, 0.50, 3, 0.40);
        let classifier = BehaviorClassifier::new();
        let profile = classifier.classify(&diagnosis);

        assert_eq!(profile.state, BehaviorState::CriticalDisruption);
        assert_eq!(profile.risk_level, RiskLevel::Critical);
        assert!(profile
            .recommended_actions
            .iter()
            .any(|action| action.contains("emergency")));
    }
}
