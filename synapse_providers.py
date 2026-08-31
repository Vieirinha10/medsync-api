"""synapse_providers.py - Camada de Provedores Multi-LLM para a Synapse MedSync.

Suporta 5 provedores de inteligência artificial médica:
1. OpenAI (GPT-4o, GPT-4o-mini, GPT-5)
2. Anthropic (Claude 3.5 Sonnet, Claude 3.5 Haiku)
3. Google Gemini (Gemini 2.0 Flash, Gemini 1.5 Pro)
4. xAI (Grok 2, Grok Mini)
5. DeepSeek (DeepSeek-R1 Reasoning, DeepSeek-V3)
"""

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Tabela unificada de preços (USD por 1 milhão de tokens: input, cached_input, output)
PROVIDER_MODEL_PRICING: dict[str, tuple[float, float, float]] = {
    # OpenAI
    "gpt-5.6": (4.0, 0.4, 20.0),
    "gpt-5.6-sol": (4.0, 0.4, 20.0),
    "gpt-5.6-terra": (2.0, 0.2, 12.0),
    "gpt-5.6-luna": (0.2, 0.02, 1.2),
    "gpt-4o-mini": (0.15, 0.075, 0.60),
    "gpt-4o": (2.50, 1.25, 10.00),
    # Anthropic Claude
    "claude-3-5-haiku-20241022": (0.80, 0.08, 4.00),
    "claude-3-5-sonnet-20241022": (3.00, 0.30, 15.00),
    "claude-3-haiku-20240307": (0.25, 0.025, 1.25),
    # Google Gemini
    "gemini-2.0-flash": (0.10, 0.025, 0.40),
    "gemini-1.5-flash": (0.075, 0.01875, 0.30),
    "gemini-1.5-pro": (1.25, 0.3125, 5.00),
    # xAI Grok
    "grok-2-mini": (0.20, 0.10, 1.00),
    "grok-2": (2.00, 1.00, 10.00),
    "grok-beta": (5.00, 2.50, 15.00),
    # DeepSeek
    "deepseek-reasoner": (0.55, 0.14, 2.19),
    "deepseek-chat": (0.14, 0.014, 0.28),
}


class ProviderUsageMetrics(BaseModel):
    provider: str
    model: str
    input_tokens: int = Field(ge=0)
    cached_input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(ge=0)
    reasoning_tokens: int = Field(default=0, ge=0)
    total_tokens: int = Field(ge=0)
    duracao_ms: int = Field(ge=0)
    custo_estimado_usd: float | None = Field(default=None, ge=0)


def calculate_cost_usd(
    model: str,
    input_tokens: int,
    cached_tokens: int,
    output_tokens: int,
) -> float | None:
    rates = PROVIDER_MODEL_PRICING.get(model)
    if not rates:
        return None
    input_rate, cached_rate, output_rate = rates
    billable_input = max(0, input_tokens - cached_tokens)
    return round(
        (billable_input * input_rate / 1_000_000)
        + (cached_tokens * cached_rate / 1_000_000)
        + (output_tokens * output_rate / 1_000_000),
        6,
    )


class AnthropicProvider:
    name = "anthropic"

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.default_model = os.getenv(
            "SYNAPSE_ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"
        )
        self.timeout = float(os.getenv("ANTHROPIC_TIMEOUT_SECONDS", "30"))

    def is_configured(self) -> bool:
        return bool(self.api_key) and os.getenv(
            "SYNAPSE_ENABLE_ANTHROPIC", "true"
        ).lower() in ("1", "true", "yes")

    def generate_narrative(
        self,
        payload: dict[str, Any],
        instructions: str,
        max_tokens: int = 900,
        model: str | None = None,
    ) -> tuple[dict[str, Any] | None, ProviderUsageMetrics | None]:
        if not self.is_configured():
            return None, None

        chosen_model = model or self.default_model
        system_prompt = (
            f"{instructions}\n\n"
            "IMPORTANTE: Você deve responder APENAS com um objeto JSON válido no seguinte formato exato:\n"
            "{\n"
            '  "sintese_raciocinio": "...",\n'
            '  "feedback_hipotese": "...",\n'
            '  "feedback_conduta": "...",\n'
            '  "plano_pessoal_melhoria": ["..."]\n'
            "}\n"
            "Não adicione blocos markdown ```json nem texto antes ou depois."
        )

        user_content = json.dumps(payload, ensure_ascii=False)
        started_at = time.perf_counter()

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        body = {
            "model": chosen_model,
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_content}],
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=body,
                )
                res.raise_for_status()
                data = res.json()

            duracao_ms = max(0, int((time.perf_counter() - started_at) * 1000))
            usage_data = data.get("usage", {})
            input_tokens = usage_data.get("input_tokens", 0)
            output_tokens = usage_data.get("output_tokens", 0)
            cached_tokens = usage_data.get("cache_read_input_tokens", 0)

            cost = calculate_cost_usd(
                chosen_model, input_tokens, cached_tokens, output_tokens
            )
            metrics = ProviderUsageMetrics(
                provider=self.name,
                model=chosen_model,
                input_tokens=input_tokens,
                cached_input_tokens=cached_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                duracao_ms=duracao_ms,
                custo_estimado_usd=cost,
            )

            content_blocks = data.get("content", [])
            text = "".join(
                b.get("text", "") for b in content_blocks if b.get("type") == "text"
            ).strip()
            if text.startswith("```"):
                text = text.strip("`").removeprefix("json").strip()

            parsed = json.loads(text)
            return parsed, metrics
        except Exception:
            logger.exception("Falha ao consultar Anthropic Claude (%s)", chosen_model)
            return None, None


class GeminiProvider:
    name = "gemini"

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.default_model = os.getenv(
            "SYNAPSE_GEMINI_MODEL", "gemini-2.0-flash"
        )
        self.timeout = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))

    def is_configured(self) -> bool:
        return bool(self.api_key) and os.getenv(
            "SYNAPSE_ENABLE_GEMINI", "true"
        ).lower() in ("1", "true", "yes")

    def generate_narrative(
        self,
        payload: dict[str, Any],
        instructions: str,
        max_tokens: int = 900,
        model: str | None = None,
    ) -> tuple[dict[str, Any] | None, ProviderUsageMetrics | None]:
        if not self.is_configured():
            return None, None

        chosen_model = model or self.default_model
        started_at = time.perf_counter()

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{chosen_model}:generateContent?key={self.api_key}"
        body = {
            "systemInstruction": {"parts": [{"text": instructions}]},
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": json.dumps(payload, ensure_ascii=False)}],
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "maxOutputTokens": max_tokens,
                "temperature": 0.2,
            },
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, json=body)
                res.raise_for_status()
                data = res.json()

            duracao_ms = max(0, int((time.perf_counter() - started_at) * 1000))
            usage_meta = data.get("usageMetadata", {})
            input_tokens = usage_meta.get("promptTokenCount", 0)
            output_tokens = usage_meta.get("candidatesTokenCount", 0)
            cached_tokens = usage_meta.get("cachedContentTokenCount", 0)

            cost = calculate_cost_usd(
                chosen_model, input_tokens, cached_tokens, output_tokens
            )
            metrics = ProviderUsageMetrics(
                provider=self.name,
                model=chosen_model,
                input_tokens=input_tokens,
                cached_input_tokens=cached_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                duracao_ms=duracao_ms,
                custo_estimado_usd=cost,
            )

            candidates = data.get("candidates", [])
            if not candidates:
                return None, metrics

            part_text = candidates[0]["content"]["parts"][0]["text"]
            parsed = json.loads(part_text)
            return parsed, metrics
        except Exception:
            logger.exception("Falha ao consultar Google Gemini (%s)", chosen_model)
            return None, None


class XAIProvider:
    name = "xai"

    def __init__(self):
        self.api_key = os.getenv("XAI_API_KEY", "").strip()
        self.default_model = os.getenv("SYNAPSE_XAI_MODEL", "grok-2-mini")
        self.timeout = float(os.getenv("XAI_TIMEOUT_SECONDS", "30"))

    def is_configured(self) -> bool:
        return bool(self.api_key) and os.getenv(
            "SYNAPSE_ENABLE_XAI", "true"
        ).lower() in ("1", "true", "yes")

    def generate_narrative(
        self,
        payload: dict[str, Any],
        instructions: str,
        max_tokens: int = 900,
        model: str | None = None,
    ) -> tuple[dict[str, Any] | None, ProviderUsageMetrics | None]:
        if not self.is_configured():
            return None, None

        chosen_model = model or self.default_model
        system_prompt = (
            f"{instructions}\n\n"
            "Responda EXCLUSIVAMENTE em formato JSON com as chaves: "
            "sintese_raciocinio, feedback_hipotese, feedback_conduta, plano_pessoal_melhoria."
        )

        started_at = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": chosen_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json=body,
                )
                res.raise_for_status()
                data = res.json()

            duracao_ms = max(0, int((time.perf_counter() - started_at) * 1000))
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)

            cost = calculate_cost_usd(chosen_model, input_tokens, 0, output_tokens)
            metrics = ProviderUsageMetrics(
                provider=self.name,
                model=chosen_model,
                input_tokens=input_tokens,
                cached_input_tokens=0,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                duracao_ms=duracao_ms,
                custo_estimado_usd=cost,
            )

            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            return parsed, metrics
        except Exception:
            logger.exception("Falha ao consultar xAI Grok (%s)", chosen_model)
            return None, None


class DeepSeekProvider:
    name = "deepseek"

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
        self.default_model = os.getenv(
            "SYNAPSE_DEEPSEEK_MODEL", "deepseek-reasoner"
        )
        self.timeout = float(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "45"))

    def is_configured(self) -> bool:
        return bool(self.api_key) and os.getenv(
            "SYNAPSE_ENABLE_DEEPSEEK", "true"
        ).lower() in ("1", "true", "yes")

    def generate_narrative(
        self,
        payload: dict[str, Any],
        instructions: str,
        max_tokens: int = 1200,
        model: str | None = None,
    ) -> tuple[dict[str, Any] | None, ProviderUsageMetrics | None]:
        if not self.is_configured():
            return None, None

        chosen_model = model or self.default_model
        system_prompt = (
            f"{instructions}\n\n"
            "Responda EXCLUSIVAMENTE em formato JSON com as chaves: "
            "sintese_raciocinio, feedback_hipotese, feedback_conduta, plano_pessoal_melhoria."
        )

        started_at = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {
            "model": chosen_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(
                    "https://api.deepseek.com/chat/completions",
                    headers=headers,
                    json=body,
                )
                res.raise_for_status()
                data = res.json()

            duracao_ms = max(0, int((time.perf_counter() - started_at) * 1000))
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            cached_tokens = usage.get("prompt_cache_hit_tokens", 0)
            reasoning_tokens = usage.get("completion_tokens_details", {}).get(
                "reasoning_tokens", 0
            )

            cost = calculate_cost_usd(
                chosen_model, input_tokens, cached_tokens, output_tokens
            )
            metrics = ProviderUsageMetrics(
                provider=self.name,
                model=chosen_model,
                input_tokens=input_tokens,
                cached_input_tokens=cached_tokens,
                output_tokens=output_tokens,
                reasoning_tokens=reasoning_tokens,
                total_tokens=input_tokens + output_tokens,
                duracao_ms=duracao_ms,
                custo_estimado_usd=cost,
            )

            content = data["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.strip("`").removeprefix("json").strip()
            parsed = json.loads(content)
            return parsed, metrics
        except Exception:
            logger.exception("Falha ao consultar DeepSeek (%s)", chosen_model)
            return None, None


@dataclass
class ConsensusResult:
    narrative: dict[str, Any]
    source: str
    active_providers: list[str]
    metrics_by_provider: dict[str, ProviderUsageMetrics]
    total_duration_ms: int
    total_cost_usd: float


class SynapseMultiEngine:
    def __init__(self):
        self.anthropic = AnthropicProvider()
        self.gemini = GeminiProvider()
        self.xai = XAIProvider()
        self.deepseek = DeepSeekProvider()

    def get_configured_secondary_providers(self) -> list[Any]:
        providers = []
        if self.anthropic.is_configured():
            providers.append(self.anthropic)
        if self.gemini.is_configured():
            providers.append(self.gemini)
        if self.xai.is_configured():
            providers.append(self.xai)
        if self.deepseek.is_configured():
            providers.append(self.deepseek)
        return providers

    def is_multi_provider_active(self) -> bool:
        return len(self.get_configured_secondary_providers()) > 0

    def list_active_provider_names(self) -> list[str]:
        active = ["openai"] if os.getenv("OPENAI_API_KEY") else []
        for p in self.get_configured_secondary_providers():
            active.append(p.name)
        return active

    def execute_multi_provider_consensus(
        self,
        payload: dict[str, Any],
        instructions: str,
        primary_openai_narrative: dict[str, Any] | None,
        primary_openai_metrics: Any | None,
    ) -> ConsensusResult | None:
        secondary_providers = self.get_configured_secondary_providers()
        if not secondary_providers and not primary_openai_narrative:
            return None

        started_at = time.perf_counter()
        results: dict[str, dict[str, Any]] = {}
        metrics: dict[str, ProviderUsageMetrics] = {}

        if primary_openai_narrative and primary_openai_metrics:
            results["openai"] = primary_openai_narrative
            metrics["openai"] = ProviderUsageMetrics(
                provider="openai",
                model=getattr(primary_openai_metrics, "model", "openai"),
                input_tokens=primary_openai_metrics.input_tokens,
                cached_input_tokens=primary_openai_metrics.cached_input_tokens,
                output_tokens=primary_openai_metrics.output_tokens,
                reasoning_tokens=primary_openai_metrics.reasoning_tokens,
                total_tokens=primary_openai_metrics.total_tokens,
                duracao_ms=primary_openai_metrics.duracao_ms,
                custo_estimado_usd=primary_openai_metrics.custo_estimado_usd,
            )

        if secondary_providers:
            with ThreadPoolExecutor(max_workers=len(secondary_providers)) as pool:
                future_to_provider = {
                    pool.submit(
                        p.generate_narrative, payload, instructions
                    ): p
                    for p in secondary_providers
                }
                for future in as_completed(future_to_provider):
                    p = future_to_provider[future]
                    try:
                        narrative, prov_metrics = future.result()
                        if narrative:
                            results[p.name] = narrative
                        if prov_metrics:
                            metrics[p.name] = prov_metrics
                    except Exception:
                        logger.exception("Exceção no provedor %s", p.name)

        if not results:
            return None

        total_duration = int((time.perf_counter() - started_at) * 1000)
        total_cost = sum(m.custo_estimado_usd or 0.0 for m in metrics.values())

        if len(results) == 1:
            prov_name = next(iter(results.keys()))
            return ConsensusResult(
                narrative=results[prov_name],
                source=prov_name,
                active_providers=[prov_name],
                metrics_by_provider=metrics,
                total_duration_ms=total_duration,
                total_cost_usd=round(total_cost, 6),
            )

        consolidated = dict(primary_openai_narrative or next(iter(results.values())))

        if "anthropic" in results and results["anthropic"].get("sintese_raciocinio"):
            consolidated["sintese_raciocinio"] = results["anthropic"]["sintese_raciocinio"]

        if "deepseek" in results and results["deepseek"].get("feedback_hipotese"):
            consolidated["feedback_hipotese"] = results["deepseek"]["feedback_hipotese"]

        if "xai" in results and results["xai"].get("feedback_conduta"):
            consolidated["feedback_conduta"] = results["xai"]["feedback_conduta"]

        combined_priorities = []
        for prov_res in results.values():
            for item in prov_res.get("plano_pessoal_melhoria", []):
                if item and item not in combined_priorities:
                    combined_priorities.append(item)
        if combined_priorities:
            consolidated["plano_pessoal_melhoria"] = combined_priorities[:3]

        return ConsensusResult(
            narrative=consolidated,
            source="synapse_multi_llm",
            active_providers=list(results.keys()),
            metrics_by_provider=metrics,
            total_duration_ms=total_duration,
            total_cost_usd=round(total_cost, 6),
        )


multi_engine = SynapseMultiEngine()
