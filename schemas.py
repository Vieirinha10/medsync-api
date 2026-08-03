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
    premium: bool = False


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


class SpacedReviewCreate(BaseModel):
    avaliacao: Literal["errei", "dificil", "bom", "facil"]


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
    revisoes_realizadas: int
    sequencia_acertos: int
    intervalo_dias: int
    fator_facilidade: float
    ultima_revisao_em: datetime | None
    proxima_revisao_em: datetime


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


class AdminClinicalExam(BaseModel):
    codigo: str = Field(min_length=1, max_length=80)
    nome: str = Field(min_length=2, max_length=240)
    resultado: str = Field(min_length=2, max_length=5000)
    referencia_adequada: bool = True


class AdminClinicalCaseUpsert(BaseModel):
    titulo: str = Field(min_length=3, max_length=200)
    especialidade: str = Field(min_length=2, max_length=120)
    nivel_dificuldade: Literal["Fácil", "Médio", "Intermediário", "Difícil", "Crítico"]
    historia_clinica: str = Field(min_length=10, max_length=10000)
    exame_fisico: str = Field(min_length=5, max_length=10000)
    status: Literal["rascunho", "publicado", "arquivado"] = "rascunho"
    premium: bool = False
    exames: list[AdminClinicalExam] = Field(default_factory=list)
    rubrica: dict[str, Any] | None = None


class AdminClinicalCaseResponse(AdminClinicalCaseUpsert):
    id: int
    versao_conteudo: int
    avaliacao_2_disponivel: bool
    updated_at: datetime


class AdminVisualChallengeUpsert(BaseModel):
    id: str = Field(pattern=r"^[a-z0-9-]+$", min_length=3, max_length=120)
    titulo: str = Field(min_length=3, max_length=240)
    especialidade: str = Field(min_length=2, max_length=120)
    dificuldade: Literal["Fácil", "Médio", "Difícil"]
    modalidade: str = Field(min_length=2, max_length=80)
    pergunta: str = Field(min_length=5, max_length=2000)
    imagem_url: str = Field(min_length=3, max_length=1000)
    imagem_alt: str = Field(min_length=3, max_length=500)
    alternativas: list[str] = Field(min_length=4, max_length=4)
    alternativa_correta: int = Field(ge=0, le=3)
    diagnostico_correto: str = Field(min_length=2, max_length=500)
    explicacao: str = Field(min_length=10, max_length=5000)
    achados_chave: list[str] = Field(default_factory=list, max_length=10)
    fonte_credito: str = Field(default="MedSync", max_length=240)
    fonte_licenca: str = Field(default="Uso educacional", max_length=120)
    fonte_url: str = Field(default="#", max_length=1000)
    status: Literal["rascunho", "publicado", "arquivado"] = "rascunho"


class AdminVisualChallengeResponse(AdminVisualChallengeUpsert):
    created_at: datetime
    updated_at: datetime


class AnnouncementUpsert(BaseModel):
    titulo: str = Field(min_length=3, max_length=180)
    mensagem: str = Field(min_length=5, max_length=3000)
    tom: Literal["informativo", "sucesso", "atencao", "urgente"] = "informativo"
    link_texto: str | None = Field(default=None, max_length=100)
    link_url: str | None = Field(default=None, max_length=500)
    ativo: bool = True
    inicia_em: datetime | None = None
    termina_em: datetime | None = None


class AnnouncementResponse(AnnouncementUpsert):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AdminContentMetric(BaseModel):
    tipo: Literal["caso_clinico", "desafio_visual"]
    id: str
    titulo: str
    acessos: int
    conclusoes: int


class AdminDailyMetric(BaseModel):
    data: str
    usuarios: int
    eventos: int


class AdminOverviewResponse(BaseModel):
    total_usuarios: int
    ativos_7_dias: int
    ativos_30_dias: int
    novos_30_dias: int
    taxa_conclusao: float
    retencao_7_dias: float
    casos_publicados: int
    desafios_publicados: int
    avisos_ativos: int
    conteudos_populares: list[AdminContentMetric]
    atividade_diaria: list[AdminDailyMetric]
