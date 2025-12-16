use std::mem::ManuallyDrop;

use dudect_bencher::{
    ctbench::{BenchFn, BenchMetadata, BenchOpts, CtRunner},
    run_benches_console, BenchRng,
};
use dudect_bencher::rand::SeedableRng;

mod dudect_scenarios;
use dudect_scenarios::{bench_catalog, bench_ct_eq_64, bench_ct_select, TRACE_COUNT};

const MAX_ABS_T: f64 = 5.0;

fn collect_samples(bench: BenchFn, seed: u64) -> (Vec<u64>, Vec<u64>) {
    let mut runner = CtRunner::default();
    let mut rng = BenchRng::seed_from_u64(seed);
    bench(&mut runner, &mut rng);

    unsafe {
        let mut runner = ManuallyDrop::new(runner);
        let ptr = (&mut *runner) as *mut CtRunner as *mut (Vec<u64>, Vec<u64>);
        std::ptr::read(ptr)
    }
}

fn student_t(left: &[u64], right: &[u64]) -> f64 {
    assert!(left.len() > 1 && right.len() > 1, "insufficient samples for t-test");

    let n0 = left.len() as f64;
    let n1 = right.len() as f64;

    let mean0 = left.iter().map(|&v| v as f64).sum::<f64>() / n0;
    let mean1 = right.iter().map(|&v| v as f64).sum::<f64>() / n1;

    let var0 = left
        .iter()
        .map(|&v| {
            let diff = v as f64 - mean0;
            diff * diff
        })
        .sum::<f64>()
        / (n0 - 1.0);
    let var1 = right
        .iter()
        .map(|&v| {
            let diff = v as f64 - mean1;
            diff * diff
        })
        .sum::<f64>()
        / (n1 - 1.0);

    let denom = (var0 / n0 + var1 / n1).sqrt();
    if denom == 0.0 {
        0.0
    } else {
        (mean0 - mean1) / denom
    }
}

#[test]
fn constant_time_primitives_pass_t_test() {
    let benches: [(&str, BenchFn); 2] = [
        ("bench_ct_select", bench_ct_select),
        ("bench_ct_eq_64", bench_ct_eq_64),
    ];

    for (name, bench) in benches {
        let (left, right) = collect_samples(bench, 0xC0DEC0DEAF_u64);
        assert_eq!(left.len(), TRACE_COUNT, "left sample mismatch for {name}");
        assert_eq!(right.len(), TRACE_COUNT, "right sample mismatch for {name}");

        let t = student_t(&left, &right).abs();
        assert!(
            t <= MAX_ABS_T,
            "timing divergence detected for {name}: |t|={:.4} (n={})",
            t,
            left.len() + right.len()
        );
    }
}

#[test]
#[ignore = "Produces detailed Dudect console output"]
fn manual_dudect_run() -> std::io::Result<()> {
    let benches: Vec<BenchMetadata> = bench_catalog();
    let mut opts = BenchOpts::default();
    opts.filter = None;
    run_benches_console(opts, benches)
}
