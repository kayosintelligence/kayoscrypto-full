use dudect_bencher::{BenchRng, Class, CtRunner};
use kayoscrypto_safe::SecureOps;
use subtle::Choice;

use dudect_bencher::rand::{Rng, RngCore};

pub const TRACE_COUNT: usize = 8_192;
const BLOCK_LEN: usize = 64;

pub fn bench_ct_select(runner: &mut CtRunner, rng: &mut BenchRng) {
    for _ in 0..TRACE_COUNT {
        let a = rng.gen::<u8>();
        let b = rng.gen::<u8>();

        runner.run_one(Class::Left, || SecureOps::ct_select(a, b, Choice::from(0u8)));
        runner.run_one(Class::Right, || SecureOps::ct_select(a, b, Choice::from(1u8)));
    }
}

pub fn bench_ct_eq_64(runner: &mut CtRunner, rng: &mut BenchRng) {
    for _ in 0..TRACE_COUNT {
        let mut base = [0u8; BLOCK_LEN];
        rng.fill_bytes(&mut base);

        let equal = base;
        let mut different = base;
        different[0] ^= 0x01;

        runner.run_one(Class::Left, || SecureOps::ct_eq(&base, &equal));
        runner.run_one(Class::Right, || SecureOps::ct_eq(&base, &different));
    }
}

pub fn bench_catalog() -> Vec<dudect_bencher::ctbench::BenchMetadata> {
    vec![
        dudect_bencher::ctbench::BenchMetadata {
            name: dudect_bencher::ctbench::BenchName("bench_ct_select"),
            seed: None,
            benchfn: bench_ct_select,
        },
        dudect_bencher::ctbench::BenchMetadata {
            name: dudect_bencher::ctbench::BenchName("bench_ct_eq_64"),
            seed: None,
            benchfn: bench_ct_eq_64,
        },
    ]
}
