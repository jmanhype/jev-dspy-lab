#!/usr/bin/env python3
"""Build the deterministic synthetic calibration fixture used by offline CI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jev_dspy_lab.replay import canonical_request_hash

OWNERS = ["api-platform", "billing", "checkout", "infra", "support-ops"]

CASES = [
    ("checkout-500", "Checkout returns HTTP 500 for 18% of sessions", "checkout", True),
    ("invoice-double", "Enterprise invoice was charged twice", "billing", False),
    ("api-latency", "API p95 latency increased from 210ms to 980ms", "api-platform", True),
    ("disk-full", "Primary node reports 98% disk utilization", "infra", True),
    ("refund-policy", "Customer requests an exception to the refund window", "support-ops", False),
    ("payment-webhook", "Payment provider webhook signature validation fails", "billing", True),
    ("search-timeout", "Search requests time out during index rebuild", "api-platform", True),
    ("checkout-tax", "Tax calculation is wrong for one EU region", "checkout", False),
    ("node-restart", "Kubernetes node restarts every nine minutes", "infra", True),
    ("sla-credit", "Customer requests an SLA credit for last week", "support-ops", False),
    ("api-auth", "OAuth token refresh intermittently returns invalid_grant", "api-platform", True),
    ("card-decline", "Valid corporate cards decline only in one region", "billing", True),
    ("cart-csv", "Cart CSV export omits discounted items", "checkout", False),
    ("db-failover", "Database failover left one replica read-only", "infra", True),
    ("priority-change", "Customer asks to change ticket priority to urgent", "support-ops", False),
    ("api-schema", "Public API schema breaks three integrations", "api-platform", True),
    ("duplicate-charge", "Subscription renewal created a duplicate charge", "billing", True),
    ("checkout-mobile", "Mobile checkout fails on one deprecated OS version", "checkout", True),
    ("cache-eviction", "Session cache evicts active users during deploys", "infra", True),
    ("refund-status", "Customer cannot see a completed refund status", "support-ops", False),
    ("api-keys", "New API key returns 401 immediately after activation", "api-platform", True),
    ("tax-report", "Monthly tax report excludes refunded invoices", "billing", False),
    ("checkout-currency", "Currency selector resets during checkout", "checkout", False),
    ("queue-backlog", "Job queue backlog grows after a failed deployment", "infra", True),
]


def build_rows() -> tuple[list[dict], list[dict]]:
    cases: list[dict] = []
    responses: list[dict] = []
    for index, (case_id, summary, expected, customer_impacting) in enumerate(CASES):
        request = {
            "document": {
                "ticket": {
                    "id": case_id,
                    "summary": summary,
                    "customer_impacting": customer_impacting,
                },
                "rubric": "Route to the team that should own the first response.",
            },
            "questions": {
                "owner": {"kind": "choice", "options": OWNERS},
            },
        }
        cases.append({"case_id": case_id, "request": request, "expected": {"owner": expected}})

        # The fixture deliberately includes correct, incorrect, high-confidence,
        # and low-confidence answers so calibration and selective-risk paths run.
        confidence = 0.57 + ((index * 17) % 43) / 100.0
        if index in {4, 9, 14, 19, 21, 22}:
            predicted = OWNERS[(OWNERS.index(expected) + 1) % len(OWNERS)]
        else:
            predicted = expected
        residual = max(0.01, round(1.0 - confidence, 4))
        probabilities = {owner: 0.01 for owner in OWNERS}
        probabilities[predicted] = confidence
        if predicted == expected:
            other_owners = [owner for owner in OWNERS if owner != predicted]
            for owner in other_owners:
                probabilities[owner] = residual / len(other_owners)
        else:
            probabilities[expected] = residual * 0.7
            unselected = [owner for owner in OWNERS if owner not in {predicted, expected}]
            for owner in unselected:
                probabilities[owner] = residual * 0.3 / len(unselected)
        responses.append(
            {
                "request_hash": canonical_request_hash(request),
                "source": "synthetic-deterministic-v1",
                "response": {
                    "answers": {
                        "owner": {
                            "choice": predicted,
                            "probabilities": probabilities,
                            "confidence": confidence,
                        }
                    },
                    "usage": {
                        "input_tokens": 680 + (index * 37) % 520,
                        "output_tokens": 18 + index % 9,
                    },
                    "latency_ms": 78.0 + (index * 29) % 180.0,
                },
            }
        )
    return cases, responses


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("fixtures"))
    args = parser.parse_args()
    cases, responses = build_rows()
    write_jsonl(args.output_dir / "tickets.jsonl", cases)
    write_jsonl(args.output_dir / "typesafe_responses.jsonl", responses)
    print(f"wrote {len(cases)} cases and {len(responses)} deterministic responses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
