#!/bin/bash
set -euo pipefail

echo "== BUILD PARANOID 10K - FINAL CONFIGURATION =="
echo "=============================================="

# Extreme compilation settings for hardened builds
declare -r ORIGINAL_RUSTFLAGS="${RUSTFLAGS-}"
export RUSTFLAGS="-C target-cpu=native -C llvm-args=-x86-cmov-converter=false -C opt-level=3 -C debuginfo=0"
export CARGO_PROFILE_RELEASE_LTO="fat"
export CARGO_PROFILE_RELEASE_CODEGEN_UNITS=1
export CARGO_PROFILE_RELEASE_PANIC="abort"

trap 'export RUSTFLAGS="$ORIGINAL_RUSTFLAGS"' EXIT

echo "-- Compiling with hardened profile (release)"
cargo build --release

echo "-- Running core library tests (release)"
cargo test --release --lib

echo "-- Running optimized timing test harness"
cargo test --release constant_time_primitives_pass_t_test

echo "-- Running full manual timing analysis (ignored test)"
cargo test --release manual_timing_run -- --ignored

echo "== BUILD PARANOID 10K COMPLETED =="
echo "Review the timing reports above for (5/tau)^2 ≥ 10_000 compliance."
