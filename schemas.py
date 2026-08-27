import unicodedata
from datetime import datetime
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)


def _normalized_spoiler_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return " ".join(
        "".join(
            char for char in decomposed if unicodedata.category(char) != "Mn"
        ).split()
    )


def _validated_public_url(value: str, *, allow_placeholder: bool = False) -> str:
    normalized = value.strip()
    if allow_placeholder and normalized == "#":
        return normalized
    if normalized.startswith("/") and not normalized.startswith("//"):
        return normalized
    parsed = urlsplit(normalized)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Use uma URL HTTPS ou um caminho interno iniciado por /.")
    return normalized


class UserCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    periodo_curso: int = Field(ge=1, le=12)
    faculdade: str = Field(min_length=2, max_length=180)
    password: str = Field(min_length=8, max_length=72)
    aceite_termos: Literal[True]

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
    email_verificado: bool = False
    is_admin: bool = False
    premium_ativo: bool = False
    premium_plano: str | None = None
    premium_valido_ate: datetime | None = None
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


class EmailVerificationRequest(BaseModel):
    token: str = Field(min_length=32, max_length=200)


class EmailVerificationResend(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class PasswordResetRequest(BaseModel):
    token: str = Field(min_length=32, max_length=200)
    password: str = Field(min_length=8, max_length=72)


class MessageResponse(BaseModel):
    message: str


class PublicStatsResponse(BaseModel):
    estudantes_medsync: int


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
    sinais_vitais: list[dict[str, Any]]
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


class VisualChallengeAnswerRequest(BaseModel):
    alternativa_id: str = Field(min_length=1, max_length=40)


class VisualChallengeAnswerResponse(BaseModel):
    correta: bool
    alternativa_correta_id: str
    diagnostico_correto: str
    explicacao: str
    achados_chave: list[str]
    fonte_credito: str = "MedSync"
    fonte_licenca: str = "Uso educacional"
    fonte_url: str = "#"


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


class SpacedReviewForecast(BaseModel):
    intervalo_dias: int
    proxima_revisao_em: datetime


class SpacedReviewPlanItem(StudyErrorResponse):
    previsoes: dict[
        Literal["errei", "dificil", "bom", "facil"],
        SpacedReviewForecast,
    ]


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
    titulo_publico: str = Field(min_length=3, max_length=240)
    especialidade: str = Field(min_length=2, max_length=120)
    nivel_dificuldade: Literal["Fácil", "Médio", "Intermediário", "Difícil", "Crítico"]
    historia_clinica: str = Field(min_length=10, max_length=10000)
    exame_fisico: str = Field(min_length=5, max_length=10000)
    status: Literal["rascunho", "publicado", "arquivado"] = "rascunho"
    premium: bool = False
    exames: list[AdminClinicalExam] = Field(default_factory=list)
    rubrica: dict[str, Any] | None = None
    rubrica_status: Literal["rascunho", "revisada"] = "rascunho"

    @model_validator(mode="after")
    def prevent_public_title_spoiler(self):
        if not self.rubrica:
            return self
        public_title = _normalized_spoiler_text(self.titulo_publico)
        diagnosis = _normalized_spoiler_text(
            str(self.rubrica.get("diagnostico_referencia", ""))
        )
        accepted_terms = [
            _normalized_spoiler_text(str(term))
            for term in self.rubrica.get("diagnostico_termos", [])
        ]
        spoilers = [diagnosis, *(term for term in accepted_terms if len(term) >= 8)]
        if any(term and term in public_title for term in spoilers):
            raise ValueError(
                "O título público não pode conter o diagnóstico ou termos do gabarito."
            )
        return self


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

    @field_validator("imagem_url")
    @classmethod
    def validate_image_url(cls, value: str) -> str:
        return _validated_public_url(value)

    @field_validator("fonte_url")
    @classmethod
    def validate_source_url(cls, value: str) -> str:
        return _validated_public_url(value, allow_placeholder=True)

    @model_validator(mode="after")
    def prevent_public_metadata_spoiler(self):
        diagnosis = _normalized_spoiler_text(self.diagnostico_correto)
        if len(diagnosis) < 5:
            return self
        public_metadata = _normalized_spoiler_text(
            " ".join((self.id, self.imagem_url, self.imagem_alt, self.pergunta))
        )
        if diagnosis in public_metadata:
            raise ValueError(
                "ID, imagem, texto alternativo e pergunta não podem revelar o gabarito."
            )
        return self


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

    @field_validator("link_url")
    @classmethod
    def validate_link_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _validated_public_url(value)


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


class AdminFinancialSummary(BaseModel):
    total_pedidos: int
    pedidos_pendentes: int
    pedidos_pagos: int
    falhas_30_dias: int
    assinaturas_ativas: int
    assinaturas_recorrentes: int
    receita_bruta_centavos: int
    estornos_centavos: int
    receita_liquida_centavos: int
    receita_mes_centavos: int
    mrr_centavos: int
    ticket_medio_centavos: int
    conversao_percentual: float


class AdminFinancialOrder(BaseModel):
    id: str
    usuario_id: int
    usuario_nome: str
    usuario_email: EmailStr
    plano_id: str
    valor_centavos: int
    forma_pagamento: str
    tipo_cobranca: str
    status: str
    referencia_asaas: str | None = None
    criado_em: datetime
    atualizado_em: datetime
    pago_em: datetime | None = None


class AdminFinancialPayment(BaseModel):
    pagamento_id: str
    pedido_id: str
    usuario_nome: str
    usuario_email: EmailStr
    plano_id: str
    valor_centavos: int
    forma_pagamento: str
    confirmado_em: datetime
    origem: Literal["asaas", "checkout", "pedido"]


class AdminFinancialSubscription(BaseModel):
    usuario_id: int
    usuario_nome: str
    usuario_email: EmailStr
    plano_id: str
    status: str
    situacao: Literal["ativa", "expirada", "suspensa"]
    renovacao_automatica: bool
    valido_ate: datetime
    dias_restantes: int
    assinatura_asaas_id: str | None = None
    atualizado_em: datetime


class AdminFinancialFailure(BaseModel):
    pedido_id: str
    usuario_nome: str
    usuario_email: EmailStr
    plano_id: str
    valor_centavos: int
    forma_pagamento: str
    status: str
    referencia_asaas: str | None = None
    ocorrido_em: datetime


class AdminMonthlyRevenue(BaseModel):
    mes: str
    receita_centavos: int
    pagamentos: int


class AdminFinancialResponse(BaseModel):
    resumo: AdminFinancialSummary
    pedidos: list[AdminFinancialOrder]
    pagamentos: list[AdminFinancialPayment]
    assinaturas: list[AdminFinancialSubscription]
    falhas: list[AdminFinancialFailure]
    receita_mensal: list[AdminMonthlyRevenue]
    status_pedidos: dict[str, int]
    planos_ativos: dict[str, int]


class QuestionAlternative(BaseModel):
    id: str
    texto: str


class QuestionListItem(BaseModel):
    id: int
    ano: int
    instituicao: str
    cabecalho: str
    especialidade: str
    assunto: str
    enunciado: str
    alternativas: list[QuestionAlternative]
    explicacao_disponivel: bool = False


class QuestionFacetCount(BaseModel):
    valor: str
    total: int


class QuestionMetadataResponse(BaseModel):
    total_questoes: int
    especialidades: list[QuestionFacetCount]
    assuntos: list[QuestionFacetCount]
    anos: list[QuestionFacetCount]
    instituicoes: list[QuestionFacetCount]
    premium_ativo: bool
    limite_diario: int | None
    respondidas_hoje: int
    restantes_hoje: int | None


class QuestionAnswerRequest(BaseModel):
    alternativa_id: str = Field(min_length=1, max_length=5)
    tempo_segundos: int | None = Field(default=None, ge=0, le=3600)

    @field_validator("alternativa_id")
    @classmethod
    def normalize_alternative_id(cls, value: str) -> str:
        return value.strip().upper()


class QuestionAlternativeExplanation(BaseModel):
    id: str
    correta: bool
    explicacao: str


class QuestionExplanation(BaseModel):
    resumo: str
    porque_correta: str
    analise_alternativas: list[QuestionAlternativeExplanation]
    alerta_atualizacao: str | None = None
    fonte: Literal["synapse", "revisao_medsync", "resumo_automatico"]


class QuestionAlternativeSelectionStats(BaseModel):
    id: str
    escolhas: int
    percentual: float


class QuestionAnswerResponse(BaseModel):
    correta: bool
    alternativa_correta_id: str
    explicacao: QuestionExplanation
    distribuicao_alternativas: list[QuestionAlternativeSelectionStats]
    total_respondentes: int
    respondidas_hoje: int
    restantes_hoje: int | None


class QuestionPerformanceTopic(BaseModel):
    assunto: str
    respondidas: int
    acertos: int
    percentual: float


class QuestionPerformanceResponse(BaseModel):
    respondidas: int
    acertos: int
    percentual: float
    tempo_medio_segundos: int | None
    assuntos: list[QuestionPerformanceTopic]


class QuestionReportCreate(BaseModel):
    motivo: Literal["gabarito", "enunciado", "explicacao", "desatualizada", "outro"]
    descricao: str | None = Field(default=None, max_length=1000)


class MessageWithIdResponse(BaseModel):
    id: int
    message: str


class AdminQuestionSummary(BaseModel):
    total: int
    publicadas: int
    explicacoes_pendentes: int
    explicacoes_geradas: int
    relatos_abertos: int
    tentativas: int


class AdminQuestionItem(BaseModel):
    id: int
    cabecalho: str
    especialidade: str
    assunto: str
    enunciado: str
    alternativas: list[QuestionAlternative]
    alternativa_correta_id: str
    explicacao: QuestionExplanation | None
    explicacao_status: str
    status: str
    tentativas: int
    percentual_acerto: float
    relatos_abertos: int


class AdminQuestionReport(BaseModel):
    id: int
    questao_id: int
    questao_cabecalho: str
    usuario_nome: str
    usuario_email: EmailStr
    motivo: str
    descricao: str | None
    status: str
    created_at: datetime


class AdminQuestionsResponse(BaseModel):
    resumo: AdminQuestionSummary
    questoes: list[AdminQuestionItem]
    relatos: list[AdminQuestionReport]


class AdminQuestionUpdate(BaseModel):
    assunto: str | None = Field(default=None, min_length=2, max_length=160)
    status: Literal["publicada", "oculta", "revisao"] | None = None
    explicacao_status: Literal["pendente", "gerada", "revisada"] | None = None


class AdminQuestionReportUpdate(BaseModel):
    status: Literal["aberto", "em_analise", "resolvido"]


class CheckoutCreate(BaseModel):
    plano_id: Literal["avulso", "recorrente", "trimestral"]


class CheckoutResponse(BaseModel):
    pedido_id: str
    checkout_url: str
    status: str


class TransparentPayer(BaseModel):
    cpf_cnpj: str
    telefone: str
    cep: str
    numero_endereco: str = Field(min_length=1, max_length=20)
    complemento: str | None = Field(default=None, max_length=80)

    @field_validator("cpf_cnpj")
    @classmethod
    def validate_document(cls, value: str) -> str:
        digits = "".join(char for char in value if char.isdigit())
        if len(digits) not in {11, 14}:
            raise ValueError("Informe um CPF ou CNPJ válido.")
        return digits

    @field_validator("telefone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        digits = "".join(char for char in value if char.isdigit())
        if len(digits) not in {10, 11}:
            raise ValueError("Informe um telefone com DDD.")
        return digits

    @field_validator("cep")
    @classmethod
    def validate_postal_code(cls, value: str) -> str:
        digits = "".join(char for char in value if char.isdigit())
        if len(digits) != 8:
            raise ValueError("Informe um CEP válido.")
        return digits


class TransparentCard(BaseModel):
    titular: str = Field(min_length=3, max_length=120)
    numero: SecretStr
    mes_validade: str
    ano_validade: str
    ccv: SecretStr

    @field_validator("numero")
    @classmethod
    def validate_card_number(cls, value: SecretStr) -> SecretStr:
        digits = "".join(char for char in value.get_secret_value() if char.isdigit())
        if len(digits) < 13 or len(digits) > 19:
            raise ValueError("Número de cartão inválido.")
        return SecretStr(digits)

    @field_validator("mes_validade")
    @classmethod
    def validate_expiry_month(cls, value: str) -> str:
        digits = "".join(char for char in value if char.isdigit()).zfill(2)
        if len(digits) != 2 or not 1 <= int(digits) <= 12:
            raise ValueError("Mês de validade inválido.")
        return digits

    @field_validator("ano_validade")
    @classmethod
    def validate_expiry_year(cls, value: str) -> str:
        digits = "".join(char for char in value if char.isdigit())
        if len(digits) == 2:
            digits = f"20{digits}"
        if len(digits) != 4:
            raise ValueError("Ano de validade inválido.")
        return digits

    @field_validator("ccv")
    @classmethod
    def validate_ccv(cls, value: SecretStr) -> SecretStr:
        digits = "".join(char for char in value.get_secret_value() if char.isdigit())
        if len(digits) not in {3, 4}:
            raise ValueError("Código de segurança inválido.")
        return SecretStr(digits)


class TransparentPaymentCreate(BaseModel):
    plano_id: Literal["avulso", "recorrente", "trimestral"]
    pagador: TransparentPayer
    cartao: TransparentCard | None = None
    parcelas: int = Field(default=1, ge=1, le=3)

    @model_validator(mode="after")
    def validate_payment_method(self):
        if self.plano_id == "avulso" and self.cartao is not None:
            raise ValueError("O plano avulso deve ser pago por Pix.")
        if self.plano_id in {"recorrente", "trimestral"} and self.cartao is None:
            raise ValueError("Informe os dados do cartão.")
        if self.plano_id != "trimestral" and self.parcelas != 1:
            raise ValueError("Este plano não permite parcelamento.")
        return self


class TransparentPaymentResponse(BaseModel):
    pedido_id: str
    forma_pagamento: Literal["PIX", "CREDIT_CARD"]
    status: str
    pix_qr_code: str | None = None
    pix_copia_cola: str | None = None
    pix_expira_em: datetime | None = None


class PaymentStatusResponse(BaseModel):
    pedido_id: str
    plano_id: str
    status: str
    premium_ativo: bool
    premium_valido_ate: datetime | None = None
