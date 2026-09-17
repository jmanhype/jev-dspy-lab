from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from jev_dspy_lab.replay import (
    RecordingClient,
    ReplayClient,
    canonical_request_hash,
    load_replay_index,
    system_one_request_hash,
)


def test_canonical_request_hash_is_stable_regardless_of_key_order(tmp_path):
    first = {"document": {"ticket": "checkout down", "priority": 2}, "questions": ["noul"]}
    second = {"questions": ["noul"], "document": {"priority": 2, "ticket": "checkout down"}}

    assert canonical_request_hash(first) == canonical_request_hash(second)
    assert len(canonical_request_hash(first)) == 64


def test_canonical_request_hash_serializes_sdk_struct_questions():
    class FakeChoice:
        __struct_fields__ = ("criteria", "instructions")

        def __init__(self):
            self.criteria = {"option_0": "infra", "option_1": "billing"}
            self.instructions = "Route the ticket"

    first = {"document": {"ticket": "down"}, "questions": {"owner": FakeChoice()}}
    second = {"document": {"ticket": "down"}, "questions": {"owner": FakeChoice()}}

    assert canonical_request_hash(first) == canonical_request_hash(second)


def test_canonical_request_hash_matches_sdk_struct_and_raw_question():
    class Choice:
        __struct_fields__ = ("criteria", "instructions")

        def __init__(self):
            self.criteria = {"infra": None, "billing": None}
            self.instructions = "Which team owns this ticket?"

    raw_request = {
        "document": {"ticket": "Checkout is unavailable"},
        "questions": {
            "owner": {
                "type": "choice",
                "criteria": {"infra": None, "billing": None},
                "instructions": "Which team owns this ticket?",
            }
        },
    }
    sdk_request = {
        "document": {"ticket": "Checkout is unavailable"},
        "questions": {"owner": Choice()},
    }

    assert canonical_request_hash(raw_request) == canonical_request_hash(sdk_request)


def test_replay_client_returns_response_for_exact_request():
    request = {"document": {"ticket": "checkout down"}, "questions": {"impact": "noul"}}
    response = {
        "answers": {"impact": {"noul": 0.91}},
        "usage": {"input_tokens": 11, "output_tokens": 3},
    }
    client = ReplayClient(
        {
            system_one_request_hash(
                request["document"], request["questions"], model="speed_latest"
            ): response
        }
    )

    result = client.system_one(request["document"], request["questions"], model="speed_latest")

    assert result.answers["impact"].noul == 0.91
    assert result.usage.input_tokens == 11


def test_replay_client_rejects_the_same_request_for_a_different_model():
    document = {"ticket": "checkout down"}
    questions = {"impact": "noul"}
    response = {
        "answers": {"impact": {"noul": 0.91}},
        "usage": {"input_tokens": 11, "output_tokens": 3},
    }
    client = ReplayClient(
        {system_one_request_hash(document, questions, model="speed_latest"): response}
    )

    with pytest.raises(KeyError, match="No replay response"):
        client.system_one(document, questions, model="other-model")


def test_replay_client_fails_closed_on_missing_request():
    client = ReplayClient({})

    with pytest.raises(KeyError, match="No replay response"):
        client.system_one({"ticket": "unseen"}, {}, model="speed_latest")


def test_load_replay_index_rejects_duplicate_hash(tmp_path):
    request = {"document": {"ticket": "same"}, "questions": {}}
    digest = canonical_request_hash(request)
    path = tmp_path / "responses.jsonl"
    path.write_text(
        f'{{"request_hash": "{digest}", "response": {{}}}}\n'
        f'{{"request_hash": "{digest}", "response": {{}}}}\n'
    )

    with pytest.raises(ValueError, match="Duplicate replay request hash"):
        load_replay_index(path)


def test_recorded_namespace_round_trips(tmp_path):
    payload = {
        "answers": {"impact": {"noul": 0.8}},
        "usage": {"input_tokens": 1, "output_tokens": 2},
    }
    namespace = SimpleNamespace(
        answers={"impact": SimpleNamespace(noul=0.8)},
        usage=SimpleNamespace(input_tokens=1, output_tokens=2),
    )

    serialized = ReplayClient.namespace_to_payload(namespace)
    restored = ReplayClient.payload_to_namespace(serialized)

    assert serialized == payload
    assert restored.answers["impact"].noul == 0.8


def test_recording_client_records_hash_and_latency_without_changing_response(tmp_path):
    request = {"document": {"ticket": "API down"}, "questions": {"impact": "noul"}}
    response = SimpleNamespace(
        answers={"impact": SimpleNamespace(noul=0.9)},
        usage=SimpleNamespace(input_tokens=9, output_tokens=2),
    )

    class InnerClient:
        def system_one(self, document, questions, *, model=None):
            return response

    path = tmp_path / "recorded.jsonl"
    recorder = RecordingClient(InnerClient(), recording_path=path)
    returned = recorder.system_one(request["document"], request["questions"], model="speed_latest")

    assert returned is response
    assert len(recorder.records) == 1
    assert recorder.records[0]["request_hash"] == system_one_request_hash(
        request["document"], request["questions"], model="speed_latest"
    )
    assert recorder.records[0]["response"]["answers"]["impact"]["noul"] == 0.9
    assert recorder.records[0]["response"]["latency_ms"] >= 0.0
    assert path.read_text().count("\n") == 1


def test_recording_client_does_not_append_an_already_recorded_request(tmp_path):
    request = {"document": {"ticket": "API down"}, "questions": {"impact": "noul"}}
    response = SimpleNamespace(
        answers={"impact": SimpleNamespace(noul=0.9)},
        usage=SimpleNamespace(input_tokens=9, output_tokens=2),
    )

    class InnerClient:
        def system_one(self, document, questions, *, model=None):
            return response

    path = tmp_path / "recorded.jsonl"
    digest = system_one_request_hash(
        request["document"], request["questions"], model="speed_latest"
    )
    path.write_text(
        json.dumps(
            {
                "request_hash": digest,
                "source": "recorded",
                "model": "speed_latest",
                "response": {},
            }
        )
        + "\n"
    )
    recorder = RecordingClient(InnerClient(), recording_path=path)
    recorder.system_one(request["document"], request["questions"], model="speed_latest")

    assert recorder.records == []
    assert path.read_text().count("\n") == 1


def test_recording_client_serializes_sdk_struct_responses(tmp_path):
    class ChoiceAnswer:
        __struct_fields__ = ("choice", "confidence", "probabilities")

        def __init__(self):
            self.choice = "infra"
            self.confidence = 0.91
            self.probabilities = {"infra": 0.91, "billing": 0.09}

    class Usage:
        __struct_fields__ = ("billing_units", "input_tokens", "output_tokens")

        def __init__(self):
            self.billing_units = 42
            self.input_tokens = 41
            self.output_tokens = 7

    class SystemOneResponse:
        __struct_fields__ = ("model", "usage", "answers")

        def __init__(self):
            self.model = "jev-1.13.0"
            self.usage = Usage()
            self.answers = {"owner": ChoiceAnswer()}

    class InnerClient:
        def system_one(self, document, questions, *, model=None):
            return SystemOneResponse()

    path = tmp_path / "sdk-recording.jsonl"
    recorder = RecordingClient(InnerClient(), recording_path=path)
    recorder.system_one({"ticket": "down"}, {"owner": "choice"}, model="jev-latest")

    row = recorder.records[0]
    assert row["response"]["model"] == "jev-1.13.0"
    assert row["response"]["usage"] == {
        "billing_units": 42,
        "input_tokens": 41,
        "output_tokens": 7,
    }
    assert row["response"]["answers"]["owner"]["choice"] == "infra"
