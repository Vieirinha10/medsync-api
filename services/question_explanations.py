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
    explicacao: str = Field(min_length=80, max_length=1400)


class GeneratedQuestionExplanation(BaseModel):
    resumo: str = Field(min_length=20, max_length=900)
    porque_correta: str = Field(min_length=180, max_length=3000)
    analise_alternativas: list[GeneratedAlternativeExplanation]
    alerta_atualizacao: str | None = Field(default=None, max_length=700)

    @model_validator(mode="after")
    def validate_alternatives(self):
        ids = [item.id for item in self.analise_alternativas]
        if len(ids) != len(set(ids)):
            raise ValueError("A análise repetiu uma alternativa.")
        if sum(item.correta for item in self.analise_alternativas) != 1:
            raise ValueError("A análise deve preservar um único gabarito.")
        return self


def _fallback_explanation(question: ExamQuestion) -> QuestionExplanation:
    return QuestionExplanation(
        resumo=(
            "O gabarito validado aponta a alternativa "
            f"{question.alternativa_correta_id} como resposta esperada."
        ),
        porque_correta=(
            "A explicação clínica detalhada não ficou pronta. "
            "Para não apresentar uma justificativa genérica ou potencialmente "
            "enganosa, a análise deve ser solicitada novamente."
        ),
        analise_alternativas=[],
        alerta_atualizacao=(
            "A explicação clínica detalhada não pôde ser preparada agora. "
            "O gabarito foi preservado, mas este resumo não substitui a análise da Synapse."
        ),
        fonte="resumo_automatico",
    )


def generate_question_explanation(question: ExamQuestion) -> QuestionExplanation:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning(
            "OPENAI_API_KEY ausente ao gerar explicação da questão %s", question.id
        )
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
- Em porque_correta, escreva uma explicação clínica sólida em 2 a 4 parágrafos:
  identifique os dados decisivos do enunciado, conecte-os ao mecanismo, diagnóstico
  ou conduta cobrada e conclua por que a alternativa correta é a melhor resposta.
- Na análise, dedique de 2 a 4 frases específicas a cada alternativa. Na correta,
  explique por que ela atende ao comando. Em cada distrator, identifique precisamente
  o erro e diga em que cenário ele poderia ser adequado, quando isso for pertinente.
- Nunca use justificativas circulares ou genéricas como "é o gabarito", "não corresponde
  ao gabarito", "está correta" ou "está errada" sem explicar o raciocínio médico.
- Evite repetir em analise_alternativas o mesmo texto de porque_correta.
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

        response = OpenAI(api_key=api_key, timeout=45, max_retries=2).responses.parse(
            model=model,
            input=prompt,
            text_format=GeneratedQuestionExplanation,
            max_output_tokens=4200,
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
