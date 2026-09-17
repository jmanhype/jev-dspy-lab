"""Command-line entry point for the offline benchmark."""

from __future__ import annotations

import argparse
from pathlib import Path

from jev_dspy_lab.benchmark import run_benchmark


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="jev-dspy-benchmark",
        description="Evaluate replayed Jev/TypeSafe decisions without an API key.",
    )
    parser.add_argument(
        "--dataset", required=True, type=Path, help="JSONL cases and expected outputs"
    )
    parser.add_argument(
        "--responses", required=True, type=Path, help="JSONL hashed response fixtures"
    )
    parser.add_argument("--output", required=True, type=Path, help="output directory")
    parser.add_argument("--field", required=True, help="output field to evaluate")
    parser.add_argument("--threshold", type=float, default=0.8, help="confidence gate threshold")
    parser.add_argument("--bootstrap-samples", type=int, default=1_000)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    report = run_benchmark(
        dataset=args.dataset,
        responses=args.responses,
        output_dir=args.output,
        field=args.field,
        threshold=args.threshold,
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
    )
    metrics = report.metrics
    print(
        f"answered={metrics.answered}/{metrics.total} "
        f"accuracy={metrics.accuracy:.3f} risk={metrics.selective_risk:.3f} "
        f"ece={metrics.ece:.4f} report={report.output_dir / 'benchmark.md'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
