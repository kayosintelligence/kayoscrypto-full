use std::str::FromStr;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum KayosMode {
    MatutoRegulatorio,
    SatorSimbiotico,
}

impl KayosMode {
    pub fn is_regulatory(self) -> bool {
        matches!(self, KayosMode::MatutoRegulatorio)
    }
}

#[derive(Clone, Copy, Debug)]
pub struct VelhoMatuto;

impl VelhoMatuto {
    pub fn decide(profile: &str) -> KayosMode {
        match profile {
            "high_risk" | "finance" | "critical" => KayosMode::MatutoRegulatorio,
            "simbiose" | "identity" | "art" => KayosMode::SatorSimbiotico,
            _ => KayosMode::MatutoRegulatorio,
        }
    }
}

impl FromStr for KayosMode {
    type Err = String;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        match value.trim().to_lowercase().as_str() {
            "matuto" | "matuto_regulatorio" | "regulatorio" => Ok(KayosMode::MatutoRegulatorio),
            "sator" | "sator_simbiotico" | "simbiotico" => Ok(KayosMode::SatorSimbiotico),
            other => Err(format!("modo desconhecido '{other}'")),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_modes() {
        assert_eq!(KayosMode::from_str("matuto").unwrap(), KayosMode::MatutoRegulatorio);
        assert_eq!(KayosMode::from_str("SATOR").unwrap(), KayosMode::SatorSimbiotico);
        assert!(KayosMode::from_str("foo").is_err());
    }
}
