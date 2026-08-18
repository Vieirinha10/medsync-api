"""Gera comentários próprios para questões sem reutilizar material editorial externo."""

from __future__ import annotations

import json
import logging
import os

from pydantic import BaseModel, Field, model_validator

from models import ExamQuestion
from schemas import QuestionExplanation

logger = logging.getLogger(__name__)


class GeneratedAlternativeExplanation(BaseModel):
    id: str
    correta: bool
    explicacao: str = Field(min_length=8, max_length=700)


class GeneratedQuestionExplanation(BaseModel):
    resumo: str = Field(min_length=20, max_length=900)
    porque_correta: str = Field(min_length=20, max_length=1200)
    analise_alternativas: list[GeneratedAlternativeExplanation]
    ponto_chave: str = Field(min_length=10, max_length=500)
    alerta_atualizacao: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def validate_alternatives(self):
        ids = [item.id for item in self.analise_alternativas]
        if len(ids) != len(set(ids)):
            raise ValueError("A análise repetiu uma alternativa.")
        if sum(item.correta for item in self.analise_alternativas) != 1:
            raise ValueError("A análise deve preservar um único gabarito.")
        return self


def _fallback_explanation(question: ExamQuestion) -> QuestionExplanation:
    correct = next(
        item for item in question.alternativas
        if item["id"] == question.alternativa_correta_id
    )
    return QuestionExplanation(
        resumo=(
            "O gabarito validado aponta a alternativa "
            f"{question.alternativa_correta_id} como resposta esperada."
        ),
        porque_correta=(
            f"A resposta esperada é: {correct['texto']} "
            "A explicação clínica ampliada está sendo preparada pela Synapse."
        ),
        analise_alternativas=[
            {
                "id": item["id"],
                "correta": item["id"] == question.alternativa_correta_id,
                "explicacao": (
                    "Esta alternativa corresponde ao gabarito validado da questão."
                    if item["id"] == question.alternativa_correta_id
                    else "Esta alternativa não corresponde ao gabarito validado."
                ),
            }
            for item in question.alternativas
        ],
        ponto_chave=f"Resposta esperada: {correct['texto']}",
        alerta_atualizacao=(
            "Conteúdo explicativo temporário; consulte protocolos e diretrizes atuais."
        ),
        fonte="resumo_automatico",
    )


def generate_question_explanation(question: ExamQuestion) -> QuestionExplanation:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback_explanation(question)

    model = os.getenv("OPENAI_QUESTION_MODEL") or os.getenv("OPENAI_MODEL", "gpt-5.6")
    alternatives = json.dumps(question.alternativas, ensure_ascii=False)
    prompt = f"""
Você é a Synapse, tutora educacional da plataforma MedSync. Produza uma explicação
original e independente para uma questão de residência médica. Use somente o
enunciado, as alternativas, o gabarito validado e conhecimento médico consolidado.
Não copie, não tente reproduzir e não mencione comentários de cursinhos.

Regras obrigatórias:
- O gabarito validado é {question.alternativa_correta_id}; nunca o altere.
- Analise todas as alternativas exatamente uma vez e preserve seus IDs.
- Explique de forma objetiva por que a correta é adequada e por que as demais não são.
- Não invente dados ausentes no caso.
- Se a questão de {question.ano} puder envolver recomendação desatualizada, use o
  campo alerta_atualizacao; caso contrário, deixe-o nulo.
- Escreva em português do Brasil e não forneça aconselhamento para pacientes reais.

Especialidade: {question.especialidade}
Assunto: {question.assunto}
Prova: {question.cabecalho}
Enunciado: {question.enunciado}
Alternativas: {alternatives}
""".strip()

    try:
        from openai import OpenAI

        response = OpenAI(api_key=api_key, timeout=12).responses.parse(
            model=model,
            input=prompt,
            text_format=GeneratedQuestionExplanation,
        )
        generated = response.output_parsed
        expected_ids = {item["id"] for item in question.alternativas}
        received_ids = {item.id for item in generated.analise_alternativas}
        marked = next(
            item.id for item in generated.analise_alternativas if item.correta
        )
        if received_ids != expected_ids or marked != question.alternativa_correta_id:
            raise ValueError("A explicação não preservou as alternativas e o gabarito.")
        return QuestionExplanation(**generated.model_dump(), fonte="synapse")
    except Exception:
        logger.exception(
            "Falha ao gerar explicação independente da questão %s", question.id
        )
        return _fallback_explanation(question)
