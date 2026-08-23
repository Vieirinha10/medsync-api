from types import SimpleNamespace

import pytest

from evaluation import _usage_metrics


def test_openai_usage_metrics_include_cache_reasoning_duration_and_cost(monkeypatch):
    monkeypatch.setattr("evaluation.time.perf_counter", lambda: 11.25)
    response = SimpleNamespace(
        id="resp_synapse_123",
        usage=SimpleNamespace(
            input_tokens=1000,
            input_tokens_details=SimpleNamespace(cached_tokens=200),
            output_tokens=500,
            output_tokens_details=SimpleNamespace(reasoning_tokens=300),
            total_tokens=1500,
        ),
    )

    metrics = _usage_metrics(response, "gpt-5.6", 10.0)

    assert metrics.input_tokens == 1000
    assert metrics.cached_input_tokens == 200
    assert metrics.output_tokens == 500
    assert metrics.reasoning_tokens == 300
    assert metrics.total_tokens == 1500
    assert metrics.duracao_ms == 1250
    assert metrics.custo_estimado_usd == pytest.approx(0.01328)
    assert metrics.response_id == "resp_synapse_123"
