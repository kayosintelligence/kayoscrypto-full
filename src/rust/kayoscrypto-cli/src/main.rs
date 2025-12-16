use anyhow::Result;
use clap::{Parser, Subcommand};
use kayoscrypto_safe::KayosCryptoSafe;

#[derive(Parser)]
#[command(version, about = "KayosCrypto command-line toolkit", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Encrypt input data using the KayosCrypto pipeline
    Encrypt { data: String, password: String },
    /// Decrypt input data using the KayosCrypto pipeline
    Decrypt { data: String, password: String },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let engine = KayosCryptoSafe::new();

    match cli.command {
        Commands::Encrypt { data, password } => {
            let ciphertext = engine.encrypt(data.as_bytes(), password.as_bytes());
            println!("{}", base64::encode(ciphertext));
        }
        Commands::Decrypt { data, password } => {
            let bytes = base64::decode(data)?;
            let plaintext = engine.decrypt(&bytes, password.as_bytes());
            println!("{}", String::from_utf8_lossy(&plaintext));
        }
    }

    Ok(())
}
