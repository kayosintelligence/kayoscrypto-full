use super::sator_bridge::{SatorAnalysisSnapshot, SatorPythonBridge};

pub struct SatorAuditor {
    bridge: Option<SatorPythonBridge>,
    sample_interval: usize,
    counter: usize,
    last_error: Option<String>,
}

impl SatorAuditor {
    pub fn new(sample_interval: usize) -> Self {
        let bridge = SatorPythonBridge::new().ok();
        Self {
            bridge,
            sample_interval: sample_interval.max(1),
            counter: 0,
            last_error: None,
        }
    }

    pub fn audit_if_needed(&mut self, block: &[u8]) -> Option<SatorAnalysisSnapshot> {
        let bridge = self.bridge.as_ref()?;
        self.counter = self.counter.wrapping_add(1);
        if self.counter % self.sample_interval != 0 {
            return None;
        }

        match bridge.analyze_bytes(block) {
            Ok(snapshot) => {
                self.last_error = None;
                Some(snapshot)
            }
            Err(err) => {
                self.last_error = Some(err.to_string());
                None
            }
        }
    }

    pub fn last_error(&self) -> Option<&str> {
        self.last_error.as_deref()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn auditor_handles_missing_bridge() {
        let mut auditor = SatorAuditor::new(1024);
        assert!(auditor.audit_if_needed(&[0u8; 64]).is_none());
    }
}
