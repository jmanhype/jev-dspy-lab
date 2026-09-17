#!/usr/bin/env python3
"""Collect a live TypeSafe benchmark and immediately replay it offline."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from jev_dspy_lab.live import run_live_benchmark


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--responses", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--field", required=True)
    parser.add_argument("--threshold", type=float, default=0.7)
    parser.add_argument("--bootstrap-samples", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--model", default=None)
    parser.add_argument("--timeout-seconds", type=float, default=60.0)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    dataset = args.dataset
    if args.limit is None:
        report = run_live_benchmark(
            dataset=dataset,
            responses=args.responses,
            output_dir=args.output,
            field=args.field,
            threshold=args.threshold,
            bootstrap_samples=args.bootstrap_samples,
            seed=args.seed,
            model_override=args.model,
            timeout_seconds=args.timeout_seconds,
        )
    else:
        if args.limit < 1:
            parser.error("--limit must be positive")
        with (
            dataset.open("r", encoding="utf-8") as source,
            tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".jsonl") as temporary,
        ):
            selected = 0
            for line in source:
                if not line.strip():
                    continue
                temporary.write(line)
                selected += 1
                if selected >= args.limit:
                    break
            temporary.flush()
            report = run_live_benchmark(
                dataset=Path(temporary.name),
                responses=args.responses,
                output_dir=args.output,
                field=args.field,
                threshold=args.threshold,
                bootstrap_samples=args.bootstrap_samples,
                seed=args.seed,
                model_override=args.model,
                timeout_seconds=args.timeout_seconds,
            )

    metrics = report.metrics
    print(
        f"live_collection=complete answered={metrics.answered}/{metrics.total} "
        f"accuracy={metrics.accuracy:.3f} risk={metrics.selective_risk:.3f} "
        f"ece={metrics.ece:.4f} report={report.output_dir / 'benchmark.md'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
