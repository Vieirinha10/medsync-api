# Arquivo: main.py

import os
from typing import Any, Dict, List

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Progresso, User
from security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

app = FastAPI(title="API MEDSYNC", version="0.2.0")

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials="*" not in origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# --- Modelos de Dados ---
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


class CasoClinicoDetalhes(CasoClinico):
    historia_clinica: str
    exame_fisico: str
    exames_disponiveis: List[Dict[str, Any]]

class ProgressoCreate(BaseModel):
    id_caso: int = Field(gt=0)
    respostas_usuario: Dict[str, Any]
    pontuacao: int = Field(ge=0, le=100)


class ProgressoResponse(ProgressoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    id_usuario: int

# --- Banco de Dados Falso com os 40 Casos Clínicos Detalhados ---
fake_casos_db = [
    {
        "id": 1, "titulo": "Diagnóstico diferencial de dor torácica", "especialidade": "Cardiologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "JSP, 32 anos, masculino, mecânico. Queixa de dor torácica em região precordial, de início há 7 dias, em peso, de intensidade progressiva, ventilatório dependente. Melhora com ântero-flexão do tronco. Histórico de orquiectomia por seminoma há 4 anos.",
        "exame_fisico": "BEG, eupneico, hipocorado (+/4+), ansioso. Ausculta cardíaca e pulmonar sem alterações.",
        "exames_disponiveis": [{"id": "ecg", "nome": "ECG", "resultado": "Sem alterações.", "correto": True}, {"id": "raiox", "nome": "Radiografia de Tórax", "resultado": "Sem alterações.", "correto": True}, {"id": "marcadores", "nome": "Marcadores de necrose miocárdica", "resultado": "Sem alterações.", "correto": True}, {"id": "pcr", "nome": "PCR", "resultado": "25 mg/L (VR: <5 mg/L).", "correto": True}, {"id": "tc_torax", "nome": "TC de tórax", "resultado": "Imagem densa em mediastino médio.", "correto": True}]
    },
    {
        "id": 2, "titulo": "Cefaleia e Hipertensão Mascarada", "especialidade": "Cardiologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "NPS, 48 anos, feminina. Cefaleia temporal há 1 ano. Fundoscopia com sinais de retinopatia hipertensiva. Histórico de cirurgia por neurinoma hipofisário.",
        "exame_fisico": "PA no consultório: 110/70 mmHg. Ausculta cardíaca: B4 em ponta, A2 hiperfonética.",
        "exames_disponiveis": [{"id": "mapa", "nome": "MAPA (24 horas)", "resultado": "Média de 154/88 mmHg.", "correto": True}, {"id": "ecg", "nome": "ECG", "resultado": "Sobrecarga ventricular esquerda.", "correto": True}, {"id": "eco", "nome": "Ecocardiograma", "resultado": "Hipertrofia ventricular esquerda concêntrica.", "correto": True}, {"id": "lab_renal", "nome": "Função Renal e Glicemia", "resultado": "Ureia=59; Creatinina=1,54; Glicose=112.", "correto": True}]
    },
    {
        "id": 3, "titulo": "Amiloidose cardíaca e mieloma múltiplo", "especialidade": "Cardiologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Masculino, 62 anos. Dispneia progressiva há 10 meses e síncope há 1 mês. Dispneia aos mínimos esforços, edema de MMII, fraqueza, palidez, dor costal. Síndrome do túnel do carpo.",
        "exame_fisico": "Hipocorado, bulhas hipofonéticas, murmúrio vesicular diminuído em bases, turgência jugular, hepatomegalia.",
        "exames_disponiveis": [{"id": "hemo", "nome": "Hemograma", "resultado": "Hb de 6,7 g/dL, hemácias em Rouleaux.", "correto": True}, {"id": "eletroforese", "nome": "Eletroforese de proteínas", "resultado": "Pico monoclonal.", "correto": True}, {"id": "eco", "nome": "Ecocardiograma", "resultado": "Padrão restritivo, FEVE: 48%.", "correto": True}, {"id": "ecg", "nome": "ECG", "resultado": "Baixa voltagem.", "correto": True}, {"id": "biopsia_mo", "nome": "Biópsia de Medula Óssea", "resultado": "Confirmação diagnóstica.", "correto": True}]
    },
    {
        "id": 4, "titulo": "Miocardite lúpica e ICFER", "especialidade": "Cardiologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Feminino, 37 anos. Dor em mãos, cotovelos e joelhos, com febre diária há 15 dias. Rosto mais avermelhado. Mãe com doença reumatológica.",
        "exame_fisico": "Febril (38ºC), taquipneica (FR=30), eritema malar, edema em MMII. Sopro sistólico em foco aórtico e diastólico em foco mitral.",
        "exames_disponiveis": [{"id": "les", "nome": "Marcadores de LES (FAN, anti-DNA, anti-Sm)", "resultado": "Todos positivos.", "correto": True}, {"id": "eco", "nome": "Ecocardiograma", "resultado": "Derrame pericárdico, FE de 33%.", "correto": True}, {"id": "raiox", "nome": "Raio-X de tórax", "resultado": "Cardiomegalia.", "correto": True}, {"id": "hemo", "nome": "Hemograma", "resultado": "Anemia (Hb 7.9 g/dl).", "correto": True}]
    },
    {
        "id": 5, "titulo": "Sangramento uterino anormal (Leiomioma)", "especialidade": "Cirurgia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "L.M.N, 37 anos, feminina, obesa. Sangramento uterino anormal há 7 dias, grande quantidade, dor pélvica e dispareunia. Menarca precoce, G2P0A2.",
        "exame_fisico": "IMC 32 kg/m². Abdome doloroso à palpação inferior. Útero aumentado, móvel e de contorno irregular.",
        "exames_disponiveis": [{"id": "usg_tv", "nome": "Ultrassonografia Transvaginal", "resultado": "Padrão ouro para diagnóstico.", "correto": True}, {"id": "hemo", "nome": "Hemograma", "resultado": "Anemia microcítica e hipocrômica.", "correto": True}, {"id": "beta_hcg", "nome": "Beta-HCG", "resultado": "Negativo.", "correto": True}]
    },
    {
        "id": 6, "titulo": "Hematêmese (Úlcera Péptica Perfurada)", "especialidade": "Cirurgia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "V.Y.L, 61 anos, masculino. Hematêmese há 6 horas. Dor epigástrica em queimação (8/10), piora após alimentação, acorda à noite. Perda de 8 Kg no último mês.",
        "exame_fisico": "FC: 120 bpm, Tax: 38°C. Abdome com distensão, doloroso e em tábua.",
        "exames_disponiveis": [{"id": "eda", "nome": "Endoscopia Digestiva Alta", "resultado": "Padrão ouro para diagnóstico.", "correto": True}, {"id": "raiox_abdome", "nome": "Raio-X de abdome agudo", "resultado": "Presença de pneumoperitônio.", "correto": True}, {"id": "hemo", "nome": "Hemograma", "resultado": "Leucocitose.", "correto": True}]
    },
    {
        "id": 7, "titulo": "Deficiência de Ferro Pós-Bariátrica", "especialidade": "Clínica Médica", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "E.M.F.R, 32 anos, feminino. Pós-operatório de 5 meses de cirurgia bariátrica (bypass gástrico). Refere dor de cabeça, diarreia, falta de ar, tonturas, desânimo e palpitações.",
        "exame_fisico": "Palidez cutaneomucosa, queilite angular, unhas quebradiças, adinamia. PA=139x90mmHg, FC=90 bpm.",
        "exames_disponiveis": [{"id": "hemo", "nome": "Hemograma", "resultado": "HB=4g/dL, VCM=73fL, CHCM=27g/dL.", "correto": True}, {"id": "ferro", "nome": "Perfil de Ferro", "resultado": "Ferro sérico=24mg/dL, ferritina=10g/mL, TIBC=470mg/dL.", "correto": True}, {"id": "vit_b12", "nome": "Vitamina B12 e Folato", "resultado": "Níveis normais.", "correto": False}]
    },
    {
        "id": 8, "titulo": "Tromboembolismo Pulmonar", "especialidade": "Clínica Médica", "nivel_dificuldade": "Difícil",
        "historia_clinica": "C.R.O., 54 anos, feminino. Dor ventilatório dependente em pontada, de início súbito, no hemitórax direito há 9 horas. Falta de ar. DM, HAS e CA de mama.",
        "exame_fisico": "Taquipneica (FR 27 ipm), saturação de 83%. Braço esquerdo edemaciado, hiperemiado e doloroso.",
        "exames_disponiveis": [{"id": "angiotc", "nome": "AngioTC de Tórax", "resultado": "Falha de enchimento em artérias pulmonares.", "correto": True}, {"id": "dimerod", "nome": "D-dímero", "resultado": "Maior que 500 ng/dl.", "correto": True}, {"id": "doppler_mmss", "nome": "USG com Doppler de MMSS", "resultado": "Trombose em veia subclávia esquerda.", "correto": True}, {"id": "gaso", "nome": "Gasometria Arterial", "resultado": "Hipoxemia e alcalose respiratória.", "correto": True}]
    },
    {
        "id": 9, "titulo": "Síndrome de Ramsay Hunt", "especialidade": "Dermatologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "L.R.B, 78 anos, feminino. Lesões em região oral. Dor em queimação em orofaringe há 6 dias, seguida de vesículas em pavilhão auditivo esquerdo, mandíbula e couro cabeludo. Vertigem, perda auditiva e paralisia facial ipsilateral.",
        "exame_fisico": "Bolhas em base eritematosa com ardor no trajeto do nervo facial.",
        "exames_disponiveis": [{"id": "clinico", "nome": "Diagnóstico Clínico", "resultado": "O diagnóstico é primariamente clínico, baseado na tríade de otalgia, vesículas e paralisia facial.", "correto": True}]
    },
    {
        "id": 10, "titulo": "Reação hansênica", "especialidade": "Dermatologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "Masculino, 16 anos. Manchas no corpo e coceira há 1 mês. Febre, cefaleia, mal-estar. Em tratamento para hanseníase dimorfa há 2 meses.",
        "exame_fisico": "Exantema difuso com placas eritemoinfiltradas. Edema de mãos e pés. Dor à palpação dos nervos ulnar e fibular direito.",
        "exames_disponiveis": [{"id": "hemo", "nome": "Hemograma", "resultado": "Anemia moderada, leucocitose com eosinofilia.", "correto": True}, {"id": "funcao_hepatica", "nome": "Função Hepática", "resultado": "Elevação de transaminases.", "correto": True}, {"id": "baciloscopia", "nome": "Baciloscopia de linfa", "resultado": "Pode mostrar bacilos, dependendo da forma.", "correto": False}]
    },
    {
        "id": 11, "titulo": "Macroprolactinoma", "especialidade": "Endocrinologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "C.M.F, 32 anos, feminino. Cefaleia intensa e diplopia visual. Desregulação menstrual, dispareunia, redução da libido, infertilidade e galactorreia há 1 mês.",
        "exame_fisico": "Tireoide normopalpável.",
        "exames_disponiveis": [{"id": "prolactina", "nome": "Dosagem de Prolactina (PRL)", "resultado": "700 ng/ml.", "correto": True}, {"id": "rm_sela_turcica", "nome": "RM de Sela Túrcica", "resultado": "Macroadenoma (2,3x1,8x1,5cm) com compressão do quiasma óptico.", "correto": True}, {"id": "tsh_t4l", "nome": "TSH e T4 Livre", "resultado": "Dentro da normalidade.", "correto": True}]
    },
    {
        "id": 12, "titulo": "Síndrome de Cushing Iatrogênica", "especialidade": "Endocrinologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "AFP, 18 anos, feminino. Ganho de peso (22 kg em 1 ano), estrias violáceas, pêlos na face, desregulação menstrual e fraqueza. Uso crônico (5 anos) de descongestionante nasal com Betametasona.",
        "exame_fisico": "Fácies em lua cheia, giba, obesidade centrípeta, hirsutismo, pele acneica. PA 150x110mmHg.",
        "exames_disponiveis": [{"id": "cortisol_acth", "nome": "Cortisol e ACTH plasmático", "resultado": "Cortisol indosável e ACTH suprimido.", "correto": True}, {"id": "glicemia", "nome": "Glicemia de Jejum", "resultado": "Normal.", "correto": False}]
    },
    {
        "id": 13, "titulo": "Colangite Esclerosante Primária", "especialidade": "Gastroenterologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "J.H.B, 43 anos, masculino. Dor abdominal, fraqueza, tontura e prurido há 2 anos. Piora há 1 mês com icterícia, náuseas, vômitos. Febre e calafrios há 4 dias. Histórico de Retocolite Ulcerativa.",
        "exame_fisico": "Febril, ictérico. Bordo hepático palpável 4 cm abaixo do rebordo costal, duro e irregular.",
        "exames_disponiveis": [{"id": "cpre", "nome": "Colangiopancreatografia Retrógrada Endoscópica (CPRE)", "resultado": "Múltiplas estenoses e dilatações dos ductos biliares (padrão 'contas de rosário').", "correto": True}, {"id": "funcao_hepatica", "nome": "Função Hepática", "resultado": "Padrão colestático com elevação de Fosfatase Alcalina e GGT.", "correto": True}, {"id": "anticorpos", "nome": "Anticorpos (p-ANCA)", "resultado": "Positivo.", "correto": True}]
    },
    {
        "id": 14, "titulo": "Pancreatite Aguda", "especialidade": "Gastroenterologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "M.A.C, 49 anos, feminino. Dor intensa e contínua em epigástrio irradiando para dorso há 8 horas (9/10). Vômitos, náuseas, sudorese. Piora após ingestão de gordura. Diagnóstico de colelitíase há 15 dias.",
        "exame_fisico": "Taquicárdica, hipertensa. Sinal de Cullen presente. Abdome rígido e doloroso.",
        "exames_disponiveis": [{"id": "amilase_lipase", "nome": "Amilase e Lipase séricas", "resultado": "Amilase: 300 U/L, Lipase: 190 I/L (ambas elevadas > 3x o LSN).", "correto": True}, {"id": "usg_abdome", "nome": "USG de Abdome", "resultado": "Pâncreas edemaciado, presença de cálculos na vesícula biliar.", "correto": True}, {"id": "hemo", "nome": "Hemograma", "resultado": "Leucocitose (20.000).", "correto": True}]
    },
    {
        "id": 15, "titulo": "Adenomiose", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "F.C.A., 41 anos, feminino. Menorragia e hipermenorreia há 11 meses, cólicas incapacitantes e dispareunia.",
        "exame_fisico": "Ultrassonografia transvaginal mostrou útero aumentado, cistos miometriais e textura heterogênea.",
        "exames_disponiveis": [{"id": "rm_pelvica", "nome": "Ressonância Magnética Pélvica", "resultado": "Confirma espessamento da zona juncional, confirmando adenomiose.", "correto": True}, {"id": "hemo", "nome": "Hemograma", "resultado": "Anemia ferropriva (Hb: 8,7 g/dL).", "correto": True}]
    },
    {
        "id": 16, "titulo": "Síndrome de Turner", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "AMP, 22 anos, feminino. Ausência de menarca e pouco desenvolvimento de caracteres sexuais secundários.",
        "exame_fisico": "Baixa estatura (1,42m). Mamas em estágio M2 e pelos pubianos em P2.",
        "exames_disponiveis": [{"id": "cariotipo", "nome": "Cariótipo", "resultado": "45,X, confirmando o diagnóstico.", "correto": True}, {"id": "hormonios", "nome": "Dosagens Hormonais (FSH, LH)", "resultado": "FSH: 67mUI/ml, LH: 29 mUI/ml (elevados por falência ovariana).", "correto": True}]
    },
    {
        "id": 17, "titulo": "Endometriose", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "MSR, 20 anos, feminino. Piora progressiva de dismenorreia (10/10), dor pélvica crônica e dispareunia profunda. Menarca precoce, ciclos curtos.",
        "exame_fisico": "Dor à mobilização uterina, nódulos e espessamentos em fundo de saco.",
        "exames_disponiveis": [{"id": "usg_tv_preparo", "nome": "USG Transvaginal com Preparo Intestinal", "resultado": "Detecta focos de endometriose profunda.", "correto": True}, {"id": "ca125", "nome": "CA-125", "resultado": "Pode estar elevado, mas é inespecífico.", "correto": False}]
    },
    {
        "id": 18, "titulo": "Herpes Genital", "especialidade": "Infectologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "A.S.C., 25 anos, feminino. Dor e ardor intenso para urinar há 2 dias. Corrimento fétido e 'feridas' na vulva. Febre.",
        "exame_fisico": "Várias lesões ulceradas em pequenos lábios e vestíbulo, com secreção amarelada e edema.",
        "exames_disponiveis": [{"id": "raspado", "nome": "Raspado do fundo da lesão (Citologia)", "resultado": "Presença de células gigantes multinucleadas.", "correto": True}, {"id": "sorologia", "nome": "Sorologia para Herpes (HSV)", "resultado": "IgG reagente, IgM não reagente.", "correto": True}]
    },
    {
        "id": 19, "titulo": "Gonorreia", "especialidade": "Infectologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "M.S., 23 anos, feminino. Corrimento amarelado e disúria há 15 dias. Piora pós-coito e sinusorragia. Parceiro com sintomas.",
        "exame_fisico": "Colo friável, mácula rubra periorificial e secreção endocervical amarelada abundante.",
        "exames_disponiveis": [{"id": "gram", "nome": "Bacterioscopia (Gram) da secreção", "resultado": "Presença de diplococos Gram-negativos intracelulares.", "correto": True}, {"id": "pcr_clamidia", "nome": "PCR para Clamídia", "resultado": "Recomendado para co-infecção.", "correto": True}]
    },
    {
        "id": 20, "titulo": "Síndrome do Encarceramento (Locked-in)", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "J.M.F.P., 52 anos, masculino. Quadro súbito de tetraplegia, disartria. Comunica-se com movimentos oculares.",
        "exame_fisico": "Babinski bilateral, paralisia facial bilateral, perda do olhar horizontal, preservação dos movimentos oculares verticais.",
        "exames_disponiveis": [{"id": "tc_cranio", "nome": "TC de Crânio", "resultado": "Área de infarto em ponte ventral.", "correto": True}, {"id": "puncao_lombar", "nome": "Punção Lombar", "resultado": "Líquor hemorrágico.", "correto": True}, {"id": "angiografia", "nome": "Angiografia Cerebral", "resultado": "Trombose da artéria basilar.", "correto": True}]
    },
    {
        "id": 21, "titulo": "Paralisia de Bell", "especialidade": "Neurologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "J.C.S., 32 anos, feminino. Queixa de não conseguir controlar os músculos da hemiface esquerda há alguns dias.",
        "exame_fisico": "Desvio da rima bucal para direita, dificuldade em fechar o olho esquerdo e enrugar a testa do lado esquerdo.",
        "exames_disponiveis": [{"id": "eletroneuro", "nome": "Eletroneurografia", "resultado": "Avalia a gravidade da lesão do nervo facial.", "correto": True}, {"id": "rm_cranio", "nome": "RM de Crânio", "resultado": "Exclui outras causas como tumores.", "correto": True}]
    },
    {
        "id": 22, "titulo": "Migrânea sem Aura", "especialidade": "Neurologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "Feminino, 35 anos. Cefaleia há 12h, temporal esquerda, pulsátil. Piora com luz e som. Dores semelhantes na adolescência e no período menstrual.",
        "exame_fisico": "Exame neurológico normal, sem sinais de irritação meníngea.",
        "exames_disponiveis": [{"id": "clinico", "nome": "Diagnóstico Clínico", "resultado": "Baseado nos critérios do ICHD-3.", "correto": True}]
    },
    {
        "id": 23, "titulo": "Síndrome de West", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Masculino, 6 meses. Movimentos súbitos como 'sustos' (espasmos extensores) há 1 mês, mais frequentes ao despertar. Atraso no desenvolvimento.",
        "exame_fisico": "Hipotonia generalizada, letargia, não sustenta a cabeça.",
        "exames_disponiveis": [{"id": "eeg", "nome": "Eletroencefalograma (EEG)", "resultado": "Padrão de hipsarritmia.", "correto": True}, {"id": "tc_cranio", "nome": "TC de Crânio", "resultado": "Pode mostrar a etiologia (ex: esclerose tuberosa).", "correto": True}]
    },
    {
        "id": 24, "titulo": "Enxaqueca com Aura", "especialidade": "Neurologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "R.E.F.P., 25 anos, feminino. Cefaleia intensa (9/10), pulsátil, frontotemporal E, associada a náuseas, vômitos e afasia. Uso de ACO.",
        "exame_fisico": "Exame neurológico sem alterações.",
        "exames_disponiveis": [{"id": "clinico", "nome": "Diagnóstico Clínico", "resultado": "Baseado nos critérios, incluindo o déficit neurológico focal (afasia).", "correto": True}, {"id": "tc_cranio", "nome": "TC de Crânio", "resultado": "Solicitada para excluir outras causas, resultado normal.", "correto": True}]
    },
    {
        "id": 25, "titulo": "Status Epilepticus", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "N.M.D, 65 anos, feminino. Abalos motores bilaterais com perda de consciência há mais de 20 minutos. Histórico de epilepsia.",
        "exame_fisico": "FC=130 bpm, FR=28 irpm. Estado geral comprometido.",
        "exames_disponiveis": [{"id": "eeg", "nome": "Eletroencefalograma (EEG)", "resultado": "Atividade contínua de ondas e picos.", "correto": True}, {"id": "glicemia_capilar", "nome": "Glicemia Capilar", "resultado": "Essencial para descartar hipoglicemia como causa.", "correto": True}]
    },
    {
        "id": 26, "titulo": "AVC Isquêmico", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "P. F. M. P., 68 anos, masculino. Cefaleia e vômitos. Internado após convulsão. Dormência no braço esquerdo, dificuldade visual, hemiparesia facial à esquerda. HAS, DM, etilista, tabagista.",
        "exame_fisico": "Hipertenso, taquicárdico, taquipneico.",
        "exames_disponiveis": [{"id": "tc_cranio", "nome": "TC de Crânio", "resultado": "Obstrução arterial em território de cerebral posterior.", "correto": True}, {"id": "angio_tc", "nome": "AngioTC de Crânio", "resultado": "Confirma a localização da oclusão.", "correto": True}]
    },
    {
        "id": 27, "titulo": "Avaliação Nutricional (Doença de Chagas)", "especialidade": "Nutrologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "PDS, 71 anos, masculino. Doença de Chagas. Constipação, mal-estar ao se alimentar, distensão abdominal, disfagia e vômitos. Perda de >10 kg em 6 meses.",
        "exame_fisico": "Caquético (54 kg, 152 cm). Abdome escavado.",
        "exames_disponiveis": [{"id": "albumina", "nome": "Albumina Sérica", "resultado": "Avalia o estado nutricional proteico.", "correto": True}, {"id": "endoscopia", "nome": "Endoscopia Digestiva Alta", "resultado": "Avalia megaesôfago chagásico.", "correto": True}]
    },
    {
        "id": 28, "titulo": "Doença Celíaca", "especialidade": "Nutrologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "D.E.R, 10 anos, feminino. Diarreia, dor abdominal, cólicas, perda de apetite. Dieta com alto consumo de pães e cereais.",
        "exame_fisico": "Descorada, 22,7kg, 124 cm. Tórax escavado.",
        "exames_disponiveis": [{"id": "anti_ttg", "nome": "Anticorpo Anti-Transglutaminase IgA", "resultado": "Elevado, altamente sugestivo de Doença Celíaca.", "correto": True}, {"id": "biopsia_duodeno", "nome": "Biópsia de Duodeno via Endoscopia", "resultado": "Atrofia das vilosidades, confirma o diagnóstico.", "correto": True}, {"id": "hemo", "nome": "Hemograma", "resultado": "Anemia (Hemoglobina=11,2g/dL).", "correto": True}]
    },
    {
        "id": 29, "titulo": "Escarlatina", "especialidade": "Otorrinolaringologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "SNP, 6 anos. Após amigdalite, apresentou dispneia, febre e taquicardia.",
        "exame_fisico": "Edema, dores articulares, língua em framboesa.",
        "exames_disponiveis": [{"id": "teste_rapido_strepto", "nome": "Teste Rápido para Streptococcus A", "resultado": "Positivo.", "correto": True}, {"id": "cultura_orofaringe", "nome": "Cultura de Orofaringe", "resultado": "Confirma Streptococcus pyogenes.", "correto": True}]
    },
    {
        "id": 30, "titulo": "Cardite Reumática", "especialidade": "Otorrinolaringologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "Guilherme, 17 anos. Infecções de garganta recorrentes. Cansaço fácil, poliartrite migratória (inchaço em joelhos, tornozelos e punhos).",
        "exame_fisico": "PA = 140x50mmHg, estase jugular. Insuficiências aórtica e mitral ++ e estenose mitral +.",
        "exames_disponiveis": [{"id": "aslo", "nome": "Antiestreptolisina O (ASLO)", "resultado": "Título elevado, indica infecção estreptocócica recente.", "correto": True}, {"id": "eco", "nome": "Ecocardiograma", "resultado": "Confirma as valvulopatias (insuficiência e estenose).", "correto": True}, {"id": "vhs_pcr", "nome": "VHS e PCR", "resultado": "Elevados, indicando atividade inflamatória.", "correto": True}]
    },
    {
        "id": 31, "titulo": "Síndrome do Bebê Sacudido", "especialidade": "Pediatria", "nivel_dificuldade": "Difícil",
        "historia_clinica": "I.D.N, lactente de 40 dias. Crises convulsivas tônico-clônicas. Quadro iniciou-se de repente enquanto estava com o pai.",
        "exame_fisico": "Hipotônica, fundoscopia com hemorragia retiniana bilateral. Petéquias na face e hematomas pelo corpo.",
        "exames_disponiveis": [{"id": "tc_cranio", "nome": "TC de Crânio", "resultado": "Hemorragia inter-hemisférica e edema cerebral.", "correto": True}, {"id": "fundo_olho", "nome": "Fundoscopia", "resultado": "Hemorragia retiniana bilateral difusa.", "correto": True}]
    },
    {
        "id": 32, "titulo": "Transtorno do Espectro Autista (TEA)", "especialidade": "Pediatria", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "LCSD, 1 ano e 6 meses. Não mantém contato visual, não responde ao nome, entretido com movimentos repetitivos, brinca sozinho, regressão da linguagem. Pai autista.",
        "exame_fisico": "Exame dificultado por agitação da criança.",
        "exames_disponiveis": [{"id": "mchat", "nome": "Escala M-CHAT", "resultado": "Triagem para autismo, pontuação de risco.", "correto": True}, {"id": "avaliacao_neuro", "nome": "Avaliação com Neuropediatra", "resultado": "Diagnóstico clínico baseado em observação e critérios do DSM-5.", "correto": True}]
    },
    {
        "id": 33, "titulo": "Parada Cardiorrespiratória (PCR)", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico",
        "historia_clinica": "Mulher, 61 anos, HAS não controlada. Dor precordial intensa em aperto, irradiação para braço esquerdo, tontura e perda de consciência.",
        "exame_fisico": "Ausência de pulso e respiração.",
        "exames_disponiveis": [{"id": "dea", "nome": "Análise de Ritmo (DEA/Monitor)", "resultado": "Fibrilação ventricular.", "correto": True}]
    },
    {
        "id": 34, "titulo": "AIT por Cardioembolismo Paradoxal", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Mulher, 43 anos. Quadro súbito de parestesia em braço direito e hemiface direita, desvio da rima labial, com melhora em minutos. Histórico de dispneia aos esforços.",
        "exame_fisico": "TC de crânio inicial sem alterações.",
        "exames_disponiveis": [{"id": "eco_transesofagico", "nome": "Ecocardiograma Transesofágico com Microbolhas", "resultado": "Detecta Forame Oval Patente (FOP) e mixoma em átrio direito.", "correto": True}, {"id": "rm_cranio", "nome": "RM de Crânio", "resultado": "Pode mostrar pequenas áreas de isquemia não visíveis na TC.", "correto": True}]
    },
    {
        "id": 35, "titulo": "Trauma Cranioencefálico em Lactente", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Lactente, 6 meses. História de queda do berço há um dia. Ficou 'molinho', sonolento, recusando amamentação, vômitos. Histórico de fratura de fêmur. Pai etilista e agressivo.",
        "exame_fisico": "Hipoativo, hipotônico, sinais de má-higiene, lesões tipo queimadura, hematoma galeal. Fundoscopia com hemorragia retiniana.",
        "exames_disponiveis": [{"id": "tc_cranio", "nome": "TC de Crânio", "resultado": "Hemorragia inter-hemisférica.", "correto": True}, {"id": "rx_corpo", "nome": "Raio-X de esqueleto", "resultado": "Pode revelar fraturas em diferentes estágios de consolidação.", "correto": True}]
    },
    {
        "id": 36, "titulo": "Sepse de Foco Gastrointestinal", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico",
        "historia_clinica": "Francisco, 68 anos. Diarreia há 2 dias, dor abdominal, vômitos e febre (39°C). Evoluiu com sangue nas fezes e queda do estado geral.",
        "exame_fisico": "Ruim estado geral, desidratado. FC: 135 bpm, PA: 90x65mmHg. Glasgow 13.",
        "exames_disponiveis": [{"id": "lactato", "nome": "Lactato sérico", "resultado": "2,1 (elevado), indicando má perfusão.", "correto": True}, {"id": "hemoculturas", "nome": "Hemoculturas", "resultado": "Coletar 2 pares antes de iniciar antibiótico.", "correto": True}, {"id": "hemo", "nome": "Hemograma", "resultado": "Leucocitose (20.000) com desvio (Bast 4%).", "correto": True}]
    },
    {
        "id": 37, "titulo": "Encefalopatia Hipertensiva", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico",
        "historia_clinica": "Homem, 35 anos. Desorientação e agitação há um dia. Queixa de cefaleia, palpitações e sudorese após exercício há meses. Diagnosticado com HAS há uma semana.",
        "exame_fisico": "FC: 123 bpm, PA: 230/145 mmHg. Glasgow: 14.",
        "exames_disponiveis": [{"id": "fundo_olho", "nome": "Fundoscopia", "resultado": "Presença de papiledema e hemorragias retinianas.", "correto": True}, {"id": "tc_cranio", "nome": "TC de Crânio", "resultado": "Descarta AVE hemorrágico.", "correto": True}]
    },
    {
        "id": 38, "titulo": "Edema Agudo de Pulmão (EAP)", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico",
        "historia_clinica": "Masculino, 72 anos. Dispneia aos mínimos esforços e tosse com expectoração rósea há 1 hora. HAS mal controlada.",
        "exame_fisico": "FC 110 bpm, FR 32 irpm, PA 180x130 mmHg, saturação O2: 82%. Tiragem intercostal e creptações em ambos hemitoraces.",
        "exames_disponiveis": [{"id": "raiox_torax", "nome": "Raio-X de Tórax", "resultado": "Infiltrado alveloar bilateral em 'asa de borboleta', cardiomegalia.", "correto": True}, {"id": "bnp", "nome": "BNP ou pro-BNP", "resultado": "Elevado, sugere causa cardíaca.", "correto": True}, {"id": "ecg", "nome": "ECG", "resultado": "Pode mostrar isquemia ou sobrecarga ventricular.", "correto": True}]
    },
    {
        "id": 39, "titulo": "Hiperplasia Prostática Benigna (HPB)", "especialidade": "Urologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "C.S.S, 67 anos, masculino. Diminuição da força e calibre urinário, hesitação, gotejamento, polaciúria e nictúria.",
        "exame_fisico": "Jato fraco, globo vesical palpável. Toque retal: próstata aumentada, lisa, fibroelástica.",
        "exames_disponiveis": [{"id": "psa", "nome": "PSA (Antígeno Prostático Específico)", "resultado": "6,0 ng/dl (elevado).", "correto": True}, {"id": "usg_vias_urinarias", "nome": "USG de Vias Urinárias", "resultado": "Próstata de 70 g, bexiga espessada, uretéro-hidronefrose bilateral.", "correto": True}, {"id": "urina1", "nome": "Sumário de Urina", "resultado": "Descarta infecção urinária.", "correto": True}]
    },
    {
        "id": 40, "titulo": "Pielonefrite Aguda", "especialidade": "Urologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "E.L.D, 55 anos, feminino. Dor lombar à direita, febre, calafrios, disúria e polaciúria há 1 dia.",
        "exame_fisico": "Febril (38,6ºC), desidratada. FC: 104 bpm. Sinal de Giordano positivo à direita.",
        "exames_disponiveis": [{"id": "urina1", "nome": "Sumário de Urina", "resultado": "Urina turva, proteinúria, leucocitúria, nitrito positivo, cilindros leucocitários.", "correto": True}, {"id": "urocultura", "nome": "Urocultura com Antibiograma", "resultado": "Identifica o agente e a sensibilidade a antibióticos.", "correto": True}, {"id": "hemo", "nome": "Hemograma", "resultado": "Leucocitose com desvio à esquerda.", "correto": True}]
    }
]
@app.get("/health", tags=["Sistema"])
def health_check():
    return {"status": "ok"}


@app.post(
    "/usuarios/registrar",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Usuários"],
)
def registrar_usuario(user: UserCreate, db: Session = Depends(get_db)):
    new_user = User(
        nome=user.nome.strip(),
        email=str(user.email),
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado."
        )
    db.refresh(new_user)
    return new_user


@app.post("/usuarios/login", response_model=Token, tags=["Usuários"])
def login_usuario(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == str(form_data.email)))
    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos.",
        )
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@app.get("/usuarios/me", response_model=UserResponse, tags=["Usuários"])
def obter_usuario_atual(current_user: User = Depends(get_current_user)):
    return current_user


@app.get(
    "/casos-clinicos/", response_model=List[CasoClinico], tags=["Casos Clínicos"]
)
def listar_casos_clinicos(current_user: User = Depends(get_current_user)):
    return fake_casos_db


@app.get(
    "/casos-clinicos/{caso_id}",
    response_model=CasoClinicoDetalhes,
    tags=["Casos Clínicos"],
)
def obter_caso_clinico(
    caso_id: int, current_user: User = Depends(get_current_user)
):
    caso = next((c for c in fake_casos_db if c["id"] == caso_id), None)
    if caso is None:
        raise HTTPException(status_code=404, detail="Caso não encontrado")
    return caso


@app.post(
    "/progresso/registrar",
    response_model=ProgressoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Progresso do Usuário"],
)
def registrar_progresso(
    progresso: ProgressoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not any(caso["id"] == progresso.id_caso for caso in fake_casos_db):
        raise HTTPException(status_code=404, detail="Caso não encontrado.")

    entry = Progresso(
        id_usuario=current_user.id,
        **progresso.model_dump(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@app.get(
    "/progresso/meu",
    response_model=List[ProgressoResponse],
    tags=["Progresso do Usuário"],
)
def obter_meu_progresso(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.scalars(
        select(Progresso)
        .where(Progresso.id_usuario == current_user.id)
        .order_by(Progresso.id.desc())
    ).all()
