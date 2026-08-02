from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    periodo_curso: int = Field(ge=1, le=12)
    faculdade: str = Field(min_length=2, max_length=180)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("nome", "faculdade")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        normalized = " ".join(value.strip().split())
        if len(normalized) < 2:
            raise ValueError("O campo deve ter pelo menos 2 caracteres.")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    periodo_curso: int | None
    faculdade: str | None
    is_admin: bool = False
    created_at: datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class Token(BaseModel):
    access_token: str
    token_type: str


class AcademicPeriodMetric(BaseModel):
    periodo: int
    total: int
    percentual: float


class AcademicInstitutionMetric(BaseModel):
    faculdade: str
    total: int
    percentual: float


class AcademicAnalyticsResponse(BaseModel):
    total_usuarios: int
    perfis_academicos_preenchidos: int
    cobertura_percentual: float
    novos_ultimos_30_dias: int
    periodos: list[AcademicPeriodMetric]
    faculdades: list[AcademicInstitutionMetric]


class CasoClinico(BaseModel):
    id: int
    titulo: str
    especialidade: str
    nivel_dificuldade: str
    avaliacao_2_disponivel: bool = False


class CasoClinicoDetalhes(CasoClinico):
    historia_clinica: str
    exame_fisico: str
    exames_disponiveis: list[dict[str, Any]]


class ProgressoCreate(BaseModel):
    id_caso: int = Field(gt=0)
    respostas_usuario: dict[str, Any]
    pontuacao: int = Field(ge=0, le=100)


class ProgressoResponse(ProgressoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_usuario: int
    created_at: datetime


class ProgressoResetResponse(BaseModel):
    registros_removidos: int
    message: str


class VisualChallengeAttempt(BaseModel):
    desafio_id: str = Field(min_length=1, max_length=120)
    titulo: str = Field(min_length=2, max_length=240)
    especialidade: str = Field(min_length=2, max_length=120)
    dificuldade: str = Field(min_length=2, max_length=40)
    pergunta: str = Field(min_length=2, max_length=1000)
    resposta_usuario: str = Field(min_length=1, max_length=500)
    resposta_correta: str = Field(min_length=1, max_length=500)
    explicacao: str = Field(min_length=2, max_length=3000)
    imagem: str | None = Field(default=None, max_length=500)


class StudyErrorStatusUpdate(BaseModel):
    status: Literal["pendente", "revisando", "dominado"]


class StudyErrorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_origem: Literal["desafio_visual", "caso_clinico"]
    id_origem: str
    titulo: str
    especialidade: str
    dificuldade: str | None
    pergunta: str
    resposta_usuario: str
    resposta_correta: str
    explicacao: str
    detalhes: dict[str, Any]
    status: Literal["pendente", "revisando", "dominado"]
    quantidade_erros: int
    visto_primeiro_em: datetime
    visto_ultimo_em: datetime
    dominado_em: datetime | None


class LearningPathCompletion(BaseModel):
    pontuacao: int = Field(ge=0, le=100)


class LearningPathProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trilha_id: str
    atividade_id: str
    tipo_atividade: Literal["desafio_visual", "caso_clinico"]
    tentativas: int
    melhor_pontuacao: int
    concluido_em: datetime
    ultima_tentativa_em: datetime
