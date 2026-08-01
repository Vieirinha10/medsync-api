from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr


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
