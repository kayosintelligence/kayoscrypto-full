use rand::{RngCore, SeedableRng};
use rand_chacha::ChaCha20Rng;
use std::fs::File;
use std::io::Write;

fn main() {
    // Generate 1 MiB directly from ChaCha20 with no post-processing so we can
    // validate the RNG independently of the Kayos refinement pipeline.
    let mut rng = ChaCha20Rng::from_entropy();
    let size = 1024 * 1024; // 1 MiB
    let mut buffer = vec![0u8; size];

    println!("Generating pure ChaCha20 stream...");
    rng.fill_bytes(&mut buffer);

    let mut file = File::create("test_pure_chacha.bin")
        .expect("failed to create test_pure_chacha.bin");
    file.write_all(&buffer)
        .expect("failed to write ChaCha20 output");

    println!("Generated {} bytes with PURE ChaCha20", size);
    println!("File: test_pure_chacha.bin");
}
