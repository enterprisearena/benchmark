import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
import time

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.schemas import ResponsesObject, ResponsesRequest
from config_loader import ConfigLoader, ConfigLoaderError
from api.main import create_app


DATASET_PATH = Path(__file__).with_name("enterprise-arena-multi-turn-queries.json")
LOG_PATH = Path(__file__).with_name("enterprise_arena_multi_turn_results_20.json")

REQUIRED_KEY_CANDIDATES = (
    "AZURE_OPENAI_API_KEY",
    "OPENAI_API_KEY",
)


_API_AUTH_HEADERS = {"Authorization": "Bearer benchmark-token"}


def _load_dataset() -> Sequence[Mapping[str, Any]]:
    if not DATASET_PATH.exists():
        pytest.skip(f"Multi-turn benchmark skipped: dataset file {DATASET_PATH} is missing.")
    try:
        payload = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        pytest.skip(f"Multi-turn benchmark skipped: dataset file is not valid JSON ({exc}).")
    if not isinstance(payload, Sequence):
        pytest.skip("Multi-turn benchmark skipped: dataset must be a JSON array.")
    entries: List[Mapping[str, Any]] = [
        entry for entry in payload if isinstance(entry, Mapping)
    ]
    if not entries:
        pytest.skip("Multi-turn benchmark skipped: dataset is empty or has invalid entries.")
    return entries


def _hydrate_environment(config: Mapping[str, Any]) -> None:
    for key, value in config.items():
        if value is None:
            continue
        if isinstance(value, (Mapping, Sequence)) and not isinstance(value, (str, bytes)):
            continue
        os.environ.setdefault(str(key), str(value))


def _require_credentials(config: Mapping[str, Any]) -> None:
    _hydrate_environment(config)
    if not any(os.getenv(candidate) for candidate in REQUIRED_KEY_CANDIDATES):
        pytest.skip(
            "Real-model benchmark skipped: missing OpenAI or Azure OpenAI credentials. "
            "Set AZURE_OPENAI_API_KEY or OPENAI_API_KEY in config.json or environment."
        )
    if not os.getenv("MODEL_NAME") and not config.get("MODEL_NAME"):
        pytest.skip(
            "Real-model benchmark skipped: MODEL_NAME is not configured for the MOTA pipeline."
        )


def _load_config() -> Mapping[str, Any]:
    loader = ConfigLoader()
    try:
        config = loader.load()
    except ConfigLoaderError as exc:
        pytest.skip(f"Cannot load configuration required for real-model benchmark: {exc}")
    if not config:
        pytest.skip("Real-model benchmark skipped: configuration is empty.")
    return config


def _resolve_max_samples(total: int) -> int:
    env_value = os.getenv("BENCHMARK_MAX_SAMPLES") or os.getenv("MULTITURN_MAX_SAMPLES")
    if not env_value:
        return total
    try:
        limit = int(env_value)
    except ValueError:
        return total
    if limit <= 0:
        return total
    return min(limit, total)


def _invoke_api(client: TestClient, request: ResponsesRequest) -> ResponsesObject:
    payload = request.dict(exclude_none=True)
    response = client.post("/v1/responses", json=payload, headers=_API_AUTH_HEADERS)
    if response.status_code != 200:
        raise RuntimeError(
            f"MOTA API returned {response.status_code}: {response.text}"
        )
    data = response.json()
    try:
        return ResponsesObject.model_validate(data)  # type: ignore[attr-defined]
    except AttributeError:
        return ResponsesObject.parse_obj(data)


def _build_system_preamble(entry: Mapping[str, Any]) -> str:
    parts: List[str] = []
    persona = entry.get("persona")
    if persona:
        parts.append(str(persona).strip())
    metadata = entry.get("metadata") or {}
    required = metadata.get("required")
    optional = metadata.get("optional")
    if required:
        parts.append(str(required).strip())
    if optional:
        parts.append(str(optional).strip())
    return "\n\n".join(part for part in parts if part)


def _build_prompt(
    entry: Mapping[str, Any],
    transcript: Sequence[Tuple[str, str]],
    current_turn: Optional[str],
) -> str:
    parts: List[str] = []
    preamble = _build_system_preamble(entry)
    if preamble:
        parts.append(preamble)

    if transcript:
        history_lines = [f"{speaker}: {utterance}" for speaker, utterance in transcript if utterance]
        if history_lines:
            parts.append("Conversation so far:\n" + "\n".join(history_lines))

    if current_turn:
        parts.append(f"User: {current_turn.strip()}")
    else:
        query = entry.get("query")
        if query:
            parts.append(str(query).strip())

    return "\n\n".join(part for part in parts if part)


def _expected_strings(entry: Mapping[str, Any]) -> Iterable[str]:
    answers = entry.get("answer") or []
    for answer in answers:
        if answer:
            yield str(answer).strip()


def _serialise_result(
    entry: Mapping[str, Any],
    prompt: str,
    response: ResponsesObject,
    *,
    turn_records: Sequence[Mapping[str, Any]] | None = None,
) -> Dict[str, Any]:
    output_text = str(response.output_text or "")
    metadata = dict(response.metadata or {})
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "idx": entry.get("idx"),
        "task": entry.get("task"),
        "prompt": prompt,
        "model": response.model,
        "response_id": response.id,
        "status": response.status,
        "output_text": output_text,
        "expected_fragments": list(_expected_strings(entry)),
        "metadata": metadata,
        "variables": metadata.get("variables"),
        "turns": list(turn_records or []),
    }


@pytest.mark.integration
@pytest.mark.slow
def test_crmarena_real_model_benchmark_multi_turn() -> None:
    """
    Run the multi-turn benchmark dataset against the live model pipeline.

    Prompts are routed through ``adapters.mota_adapter.run_non_streaming`` to exercise the full
    MOTA planning + execution stack. Results are written to ``enterprise_arena_multi_turn_results.json``
    for inspection.
    """
    config = _load_config()
    _require_credentials(config)

    model_name = config.get("MODEL_NAME") or os.getenv("MODEL_NAME")
    if not model_name:
        pytest.skip("Real-model benchmark skipped: unable to resolve a model name for the gateway.")

    entries = _load_dataset()
    results: List[Dict[str, Any]] = []
    max_samples = _resolve_max_samples(len(entries))

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    failures: List[str] = []

    app = create_app()

    with TestClient(app) as client:
        try:
            for entry in entries[:max_samples]:
                time.sleep(5)
                turns = [str(turn).strip() for turn in entry.get("turns") or [] if str(turn).strip()]
                transcript: List[Tuple[str, str]] = []
                turn_logs: List[Dict[str, Any]] = []
                last_response: Optional[ResponsesObject] = None
                last_prompt: str = ""

                session_id = f"benchmark-{entry.get('idx')}-{int(time.time() * 1000)}"
                base_metadata = {
                    "dataset": "benchmark_multi_turn",
                    "task": entry.get("task"),
                    "idx": entry.get("idx"),
                    "benchmark": "EnterpriseArena Multi-Turn",
                    "session_id": session_id,
                }

                if not turns:
                    prompt = _build_prompt(entry, transcript, None)
                    request = ResponsesRequest(
                        model=model_name,
                        input=prompt,
                        metadata=base_metadata,
                    )
                    response = _invoke_api(client, request)
                    last_response = response
                    last_prompt = prompt
                    turn_logs.append(
                        {
                            "turn_index": 0,
                            "user": entry.get("query"),
                            "prompt": prompt,
                            "response_status": response.status,
                            "response_text": response.output_text,
                        }
                    )
                else:
                    for turn_index, user_turn in enumerate(turns):
                        prompt = _build_prompt(entry, transcript, user_turn)
                        metadata = dict(base_metadata)
                        metadata["turn_index"] = turn_index
                        request = ResponsesRequest(
                            model=model_name,
                            input=prompt,
                            metadata=metadata,
                        )
                        response = _invoke_api(client, request)
                        last_response = response
                        last_prompt = prompt

                        turn_logs.append(
                            {
                                "turn_index": turn_index,
                                "user": user_turn,
                                "prompt": prompt,
                                "response_status": response.status,
                                "response_text": response.output_text,
                            }
                        )

                        transcript.append(("User", user_turn))
                        transcript.append(("Assistant", str(response.output_text or "").strip()))

                        if response.status != "completed":
                            break

                if not last_response:
                    failures.append(f"idx={entry.get('idx')} produced no response")
                    results.append(
                        {
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "idx": entry.get("idx"),
                            "task": entry.get("task"),
                            "prompt": "",
                            "model": model_name,
                            "response_id": None,
                            "status": "failed",
                            "output_text": "",
                            "expected_fragments": list(_expected_strings(entry)),
                            "metadata": base_metadata,
                            "variables": None,
                            "turns": list(turn_logs),
                            "validation_status": "pipeline_error",
                            "validation_message": "Pipeline produced no response for this entry.",
                        }
                    )
                    continue

                record = _serialise_result(
                    entry,
                    last_prompt,
                    last_response,
                    turn_records=turn_logs,
                )

                output_text = record.get("output_text", "")
                output_text_lower = output_text.lower()
                matched_fragments = [
                    fragment for fragment in _expected_strings(entry) if fragment.lower() in output_text_lower
                ]
                record["matched_fragments"] = matched_fragments

                if last_response.status != "completed" or not output_text.strip():
                    record["validation_status"] = "pipeline_error"
                    record["validation_message"] = (
                        f"Pipeline returned status '{last_response.status}' with empty output."
                    )
                    failures.append(
                        f"idx={entry.get('idx')} pipeline status '{last_response.status}'"
                    )
                elif matched_fragments:
                    record["validation_status"] = "passed"
                else:
                    record["validation_status"] = "missing_expected_fragments"
                    failures.append(
                        f"idx={entry.get('idx')} missing expected fragments"
                    )

                results.append(record)
        finally:
            LOG_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")

    if failures:
        pytest.xfail(
            "One or more multi-turn benchmarks did not meet success criteria: "
            + "; ".join(failures)
        )
