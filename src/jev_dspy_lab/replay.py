"""Canonical request hashing and deterministic TypeSafe response replay."""

from __future__ import annotations

import hashlib
import json
import threading
import time
from collections.abc import Mapping
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def canonical_request_hash(request: Mapping[str, Any]) -> str:
    """Hash a request canonically, independent of JSON object key order."""

    payload = json.dumps(
        _json_safe(request), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _json_safe(value: Any) -> Any:
    """Convert SDK structs and namespaces to stable JSON-compatible data."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]

    struct_fields = getattr(value, "__struct_fields__", None)
    if isinstance(struct_fields, tuple):
        fields = {}
        for field in struct_fields:
            field_value = getattr(value, field)
            if type(field_value).__name__ == "UnsetType":
                continue
            fields[field] = _json_safe(field_value)
        struct_type = type(value).__name__.lower()
        if struct_type in {"choice", "noul", "score"}:
            return {"type": struct_type, **fields}
        return {"__struct__": type(value).__name__, **fields}
    if isinstance(value, SimpleNamespace):
        return {
            "__namespace__": type(value).__name__,
            **{key: _json_safe(item) for key, item in vars(value).items()},
        }
    return {"__opaque__": type(value).__name__, "repr": repr(value)}


def system_one_request_hash(
    document: Mapping[str, Any],
    questions: Mapping[str, Any],
    *,
    model: str | None,
) -> str:
    """Hash a complete `system_one` request, including the selected model."""

    return canonical_request_hash({"document": document, "questions": questions, "model": model})


class ReplayClient:
    """A fail-closed `system_one` client backed by hashed JSON fixtures."""

    def __init__(self, responses_by_hash: Mapping[str, Mapping[str, Any]]) -> None:
        self._responses_by_hash = dict(responses_by_hash)

    def system_one(
        self,
        document: Mapping[str, Any],
        questions: Mapping[str, Any],
        *,
        model: str | None = None,
    ) -> Any:
        request_hash = system_one_request_hash(document, questions, model=model)
        try:
            payload = self._responses_by_hash[request_hash]
        except KeyError as exc:
            raise KeyError(
                f"No replay response for request hash {request_hash}; "
                "refusing to fabricate a decision"
            ) from exc
        return self.payload_to_namespace(payload)

    @staticmethod
    def payload_to_namespace(
        value: Any,
        *,
        root: bool = True,
        preserve_mapping: bool = False,
    ) -> Any:
        """Convert a JSON payload to the namespace shape returned by TypeSafe SDK."""

        if isinstance(value, dict) and not preserve_mapping:
            return SimpleNamespace(
                **{
                    key: ReplayClient.payload_to_namespace(
                        item,
                        root=False,
                        preserve_mapping=root and key in {"answers", "probabilities"},
                    )
                    for key, item in value.items()
                }
            )
        if isinstance(value, dict):
            return {
                key: ReplayClient.payload_to_namespace(item, root=True)
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [ReplayClient.payload_to_namespace(item) for item in value]
        return value

    @staticmethod
    def namespace_to_payload(value: Any) -> Any:
        """Serialize SDK namespace response objects into stable JSON data."""

        struct_fields = getattr(value, "__struct_fields__", None)
        if isinstance(struct_fields, tuple):
            return {
                key: ReplayClient.namespace_to_payload(item)
                for key, item in (
                    (field, getattr(value, field))
                    for field in struct_fields
                    if type(getattr(value, field)).__name__ != "UnsetType"
                )
            }
        if isinstance(value, SimpleNamespace):
            return {
                key: ReplayClient.namespace_to_payload(item)
                for key, item in vars(value).items()
                if not key.startswith("__")
            }
        if isinstance(value, list):
            return [ReplayClient.namespace_to_payload(item) for item in value]
        if isinstance(value, Mapping):
            return {key: ReplayClient.namespace_to_payload(item) for key, item in value.items()}
        return value


def load_replay_index(path: str | Path) -> dict[str, Mapping[str, Any]]:
    """Load a JSONL replay fixture and reject ambiguous duplicate hashes."""

    index: dict[str, Mapping[str, Any]] = {}
    with Path(path).open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            request_hash = row.get("request_hash")
            response = row.get("response")
            if not isinstance(request_hash, str) or not isinstance(response, dict):
                raise ValueError(f"Invalid replay row at {path}:{line_number}")
            if request_hash in index:
                raise ValueError(
                    f"Duplicate replay request hash at {path}:{line_number}: {request_hash}"
                )
            index[request_hash] = response
    return index


class RecordingClient:
    """Wrap a TypeSafe client and persist deterministic, replayable responses."""

    def __init__(self, client: Any, recording_path: str | Path | None = None) -> None:
        self._client = client
        self._recording_path = Path(recording_path) if recording_path is not None else None
        self._lock = threading.Lock()
        self._seen_hashes: set[str] = set()
        self.records: list[dict[str, Any]] = []
        if self._recording_path is not None and self._recording_path.exists():
            self._seen_hashes.update(load_replay_index(self._recording_path))

    def system_one(
        self,
        document: Mapping[str, Any],
        questions: Mapping[str, Any],
        *,
        model: str | None = None,
    ) -> Any:
        started = time.perf_counter()
        response = self._client.system_one(document, questions, model=model)
        latency_ms = (time.perf_counter() - started) * 1_000.0
        payload = ReplayClient.namespace_to_payload(response)
        if not isinstance(payload, dict):
            raise TypeError("Recorded TypeSafe response did not serialize to an object")

        request_hash = system_one_request_hash(document, questions, model=model)
        row = {
            "request_hash": request_hash,
            "source": "recorded",
            "model": model,
            "response": {**payload, "latency_ms": latency_ms},
        }
        with self._lock:
            if request_hash not in self._seen_hashes:
                self._seen_hashes.add(request_hash)
                self.records.append(row)
                if self._recording_path is not None:
                    self._recording_path.parent.mkdir(parents=True, exist_ok=True)
                    with self._recording_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(row, sort_keys=True) + "\n")
        return response
