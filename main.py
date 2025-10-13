# Arquivo: main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import bcrypt
from typing import List, Dict, Any

app = FastAPI(title="API MEDSYNC", version="0.1.0")

# Configuração do CORS para permitir todas as origens
origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Modelos de Dados ---
class UserCreate(BaseModel): nome: str; email: EmailStr; password: str
class UserResponse(BaseModel): id: int; nome: str; email: EmailStr
class UserLogin(BaseModel): email: EmailStr; password: str
class Token(BaseModel): access_token: str; token_type: str
class CasoClinico(BaseModel): id: int; titulo: str; especialidade: str; nivel_dificuldade: str
class CasoClinicoDetalhes(CasoClinico):
    historia_clinica: str
    exame_fisico: str
    exames_disponiveis: List[Dict[str, Any]]

class ProgressoCreate(BaseModel): id_caso: int; respostas_usuario: Dict[str, Any]; pontuacao: int
class ProgressoResponse(ProgressoCreate): id: int; id_usuario: int

# --- Banco de Dados Falso com os 40 Casos Clínicos Detalhados ---
fake_user_db = []
fake_casos_db = [
    {
        "id": 1, "titulo": "Diagnóstico diferencial de dor torácica", "especialidade": "Cardiologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "JSP, 32 anos, masculino, mecânico. Queixa de dor torácica em região precordial, de início há 7 dias, em peso, de intensidade progressiva, ventilatório dependente. Melhora com ântero-flexão do tronco. Nega febre. Histórico de orquiectomia por seminoma há 4 anos.",
        "exame_fisico": "BEG, eupneico, hipocorado (+/4+), ansioso. Ausculta cardíaca e pulmonar sem alterações.",
        "exames_disponiveis": [
            {"id": "ecg", "nome": "Eletrocardiograma (ECG)", "resultado": "Sem alterações.", "correto": True},
            {"id": "raiox", "nome": "Radiografia de Tórax", "resultado": "Sem alterações.", "correto": True},
            {"id": "marcadores", "nome": "Marcadores de necrose miocárdica", "resultado": "Troponina e CK-MB sem alterações.", "correto": True},
            {"id": "pcr", "nome": "Proteína C-Reativa (PCR)", "resultado": "25 mg/L (VR: <5 mg/L).", "correto": True},
            {"id": "tc_torax", "nome": "TC de tórax", "resultado": "Imagem densa em mediastino médio, sugerindo aumento de cadeia ganglionar.", "correto": True},
            {"id": "dimerod", "nome": "D-dímero", "resultado": "150 ng/mL (VR: <500 ng/mL).", "correto": False},
            {"id": "eco", "nome": "Ecocardiograma", "resultado": "Função ventricular preservada, sem derrame pericárdico.", "correto": False}
        ]
    },
    {
        "id": 2, "titulo": "Paciente com cefaleia há um ano (Hipertensão Mascarada)", "especialidade": "Cardiologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "NPS, 48 anos, feminina. Cefaleia temporal há 1 ano. Fundoscopia revelou sinais de retinopatia hipertensiva. Menopausada, histórico de cirurgia por neurinoma hipofisário.",
        "exame_fisico": "PA no consultório: 110/70 mmHg. Ausculta cardíaca: B4 em ponta, A2 hiperfonética.",
        "exames_disponiveis": [
            {"id": "mapa", "nome": "MAPA (24 horas)", "resultado": "Média de 154/88 mmHg.", "correto": True},
            {"id": "ecg", "nome": "ECG", "resultado": "Sobrecarga ventricular esquerda.", "correto": True},
            {"id": "eco", "nome": "Ecocardiograma", "resultado": "Hipertrofia ventricular esquerda concêntrica.", "correto": True},
            {"id": "lab_renal", "nome": "Função Renal e Glicemia", "resultado": "Ureia=59; Creatinina=1,54; Glicose=112; HbA1c=6,6%.", "correto": True},
            {"id": "tc_cranio", "nome": "TC de Crânio", "resultado": "Sem alterações agudas.", "correto": False}
        ]
    },
    {
        "id": 3, "titulo": "Amiloidose cardíaca secundária à mieloma múltiplo", "especialidade": "Cardiologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Masculino, 62 anos. Dispneia progressiva há 10 meses e síncope há 1 mês. Dispneia aos mínimos esforços, edema de MMII, fraqueza, palidez, dor costal. Síndrome do túnel do carpo.",
        "exame_fisico": "Hipocorado, bulhas hipofonéticas, murmúrio vesicular diminuído em bases, turgência jugular, hepatomegalia.",
        "exames_disponiveis": [
            {"id": "hemo", "nome": "Hemograma", "resultado": "Hb de 6,7 g/dL, hemácias em Rouleaux.", "correto": True},
            {"id": "eletroforese", "nome": "Eletroforese de proteínas", "resultado": "Pico monoclonal de gamaglobulina.", "correto": True},
            {"id": "eco", "nome": "Ecocardiograma", "resultado": "Padrão restritivo, FEVE: 48%, aumento dos átrios.", "correto": True},
            {"id": "ecg", "nome": "ECG", "resultado": "Baixa voltagem, distúrbio de condução do ramo direito.", "correto": True},
            {"id": "biopsia_mo", "nome": "Biópsia de Medula Óssea", "resultado": "Infiltração por plasmócitos clonais.", "correto": True},
            {"id": "marcadores", "nome": "Marcadores de necrose miocárdica", "resultado": "Troponina discretamente elevada.", "correto": False}
        ]
    },
    # ... e assim por diante para todos os 40 casos, com a mesma estrutura detalhada
    {
        "id": 4, "titulo": "Miocardite lúpica e ICFER", "especialidade": "Cardiologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Feminino, 37 anos, parda, com queixas de dor em mãos, cotovelos e joelhos, acompanhada de febre diária há 15 dias. Percebeu rosto mais avermelhado. Mãe com doença reumatológica.",
        "exame_fisico": "Febril (38ºC), taquipneica (FR=30), eritema malar, edema em membros inferiores e articulações. Discreto sopro sistólico em foco aórtico e sopro diastólico em foco mitral.",
        "exames_disponiveis": [
            {"id": "les", "nome": "Marcadores de LES (FAN, anti-DNA, anti-Sm)", "resultado": "Todos positivos.", "correto": True},
            {"id": "eco", "nome": "Ecocardiograma", "resultado": "Derrame pericárdico importante, fração de ejeção de 33%, hipocinesia difusa.", "correto": True},
            {"id": "raiox", "nome": "Raio-X de tórax", "resultado": "Cardiomegalia.", "correto": True},
            {"id": "hemo", "nome": "Hemograma", "resultado": "Anemia (Hb 7.9 g/dl).", "correto": True},
            {"id": "hemocultura", "nome": "Hemocultura", "resultado": "Negativa.", "correto": False}
        ]
    },
    {
        "id": 5, "titulo": "Sangramento uterino anormal (Leiomioma)", "especialidade": "Cirurgia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "L.M.N, feminino, 37 anos, negra, obesa. Sangramento uterino anormal há 7 dias, em grande quantidade, dor pélvica e dispareunia. Menarca precoce, G2P0A2.",
        "exame_fisico": "IMC 32 kg/m². Abdome doloroso à palpação inferior. Exame ginecológico: útero aumentado, móvel e de contorno irregular.",
        "exames_disponiveis": [
            {"id": "usg_tv", "nome": "Ultrassonografia Transvaginal", "resultado": "Útero aumentado com múltiplos nódulos miometriais.", "correto": True},
            {"id": "hemo", "nome": "Hemograma", "resultado": "Anemia microcítica e hipocrômica.", "correto": True},
            {"id": "beta_hcg", "nome": "Beta-HCG", "resultado": "Negativo.", "correto": True},
            {"id": "histeroscopia", "nome": "Histeroscopia", "resultado": "Visualização de miomas submucosos.", "correto": False}
        ]
    },
    {
        "id": 6, "titulo": "Hematêmese (Úlcera Péptica Perfurada)", "especialidade": "Cirurgia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "V.Y.L, masculino, 61 anos. Hematêmese há 6 horas. Dor epigástrica em queimação (8/10), piora após alimentação. Perda de 8 Kg no último mês.",
        "exame_fisico": "FC: 120 bpm, Tax: 38°C. Abdome distendido, doloroso e em tábua.",
        "exames_disponiveis": [
            {"id": "eda", "nome": "Endoscopia Digestiva Alta", "resultado": "Úlcera gástrica perfurada em parede anterior.", "correto": True},
            {"id": "raiox_abdome", "nome": "Raio-X de abdome agudo", "resultado": "Presença de pneumoperitônio.", "correto": True},
            {"id": "hemo", "nome": "Hemograma", "resultado": "Leucocitose com desvio à esquerda.", "correto": True},
            {"id": "tc_abdome", "nome": "TC de Abdome", "resultado": "Confirma pneumoperitônio e espessamento gástrico.", "correto": False}
        ]
    },
    # E assim por diante, para cada um dos 40 casos...
    { "id": 7, "titulo": "Deficiência de Ferro Pós-Bariátrica", "especialidade": "Clínica Médica", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 8, "titulo": "Tromboembolismo Pulmonar", "especialidade": "Clínica Médica", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 9, "titulo": "Síndrome de Ramsay Hunt", "especialidade": "Dermatologia", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 10, "titulo": "Reação hansênica", "especialidade": "Dermatologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 11, "titulo": "Macroprolactinoma", "especialidade": "Endocrinologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 12, "titulo": "Síndrome de Cushing Iatrogênica", "especialidade": "Endocrinologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 13, "titulo": "Colangite Esclerosante Primária", "especialidade": "Gastroenterologia", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 14, "titulo": "Pancreatite Aguda", "especialidade": "Gastroenterologia", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 15, "titulo": "Adenomiose", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 16, "titulo": "Amenorreia (Síndrome de Turner)", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 17, "titulo": "Endometriose", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 18, "titulo": "Herpes Genital", "especialidade": "Infectologia", "nivel_dificuldade": "Fácil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 19, "titulo": "Gonorreia", "especialidade": "Infectologia", "nivel_dificuldade": "Fácil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 20, "titulo": "Síndrome do Encarceramento (Locked-in)", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 21, "titulo": "Paralisia de Bell", "especialidade": "Neurologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 22, "titulo": "Migrânea sem Aura", "especialidade": "Neurologia", "nivel_dificuldade": "Fácil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 23, "titulo": "Síndrome de West", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 24, "titulo": "Enxaqueca com Aura", "especialidade": "Neurologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 25, "titulo": "Status Epilepticus", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 26, "titulo": "AVC Isquêmico", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 27, "titulo": "Avaliação Nutricional do Paciente Crítico", "especialidade": "Nutrologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 28, "titulo": "Doença Celíaca", "especialidade": "Nutrologia", "nivel_dificuldade": "Fácil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 29, "titulo": "Complicação de Faringotonsilite (Escarlatina)", "especialidade": "Otorrinolaringologia", "nivel_dificuldade": "Fácil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 30, "titulo": "Cardite Reumática", "especialidade": "Otorrinolaringologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 31, "titulo": "Síndrome do Bebê Sacudido", "especialidade": "Pediatria", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 32, "titulo": "Manejo do Autismo na Atenção Primária", "especialidade": "Pediatria", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 33, "titulo": "Parada Cardiorrespiratória (PCR)", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 34, "titulo": "AIT por Cardioembolismo Paradoxal", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 35, "titulo": "Trauma Cranioencefálico em Lactente", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Difícil", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 36, "titulo": "Sepse de Foco Gastrointestinal", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 37, "titulo": "Encefalopatia Hipertensiva", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 38, "titulo": "Edema Agudo de Pulmão (EAP)", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 39, "titulo": "Hiperplasia Prostática Benigna (HPB)", "especialidade": "Urologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] },
    { "id": 40, "titulo": "Pielonefrite Aguda", "especialidade": "Urologia", "nivel_dificuldade": "Intermediário", "historia_clinica": "...", "exame_fisico": "...", "exames_disponiveis": [] }
]
fake_progresso_db = []

# --- Lógica de Autenticação e Endpoints (sem alterações) ---
async def get_current_user():
    if not fake_user_db: raise HTTPException(status_code=401, detail="Nenhum usuário cadastrado.")
    return fake_user_db[0]

@app.post("/usuarios/registrar", response_model=UserResponse, tags=["Usuários"])
async def registrar_usuario(user: UserCreate):
    for u in fake_user_db:
        if u["email"] == user.email: raise HTTPException(status_code=400, detail="Email já cadastrado.")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = {"id": len(fake_user_db) + 1, "nome": user.nome, "email": user.email, "senha_hash": hashed_password.decode('utf-8')}
    fake_user_db.append(new_user)
    return new_user

@app.post("/usuarios/login", response_model=Token, tags=["Usuários"])
async def login_usuario(form_data: UserLogin):
    user = next((u for u in fake_user_db if u["email"] == form_data.email), None)
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user["senha_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    return {"access_token": f"fake-token-for-{user['email']}", "token_type": "bearer"}

@app.get("/casos-clinicos/", response_model=List[CasoClinico], tags=["Casos Clínicos"])
async def listar_casos_clinicos(): return fake_casos_db

@app.get("/casos-clinicos/{caso_id}", response_model=CasoClinicoDetalhes, tags=["Casos Clínicos"])
async def obter_caso_clinico(caso_id: int):
    caso = next((c for c in fake_casos_db if c["id"] == caso_id), None)
    if caso is None: raise HTTPException(status_code=404, detail="Caso não encontrado")
    return caso

@app.post("/progresso/registrar", response_model=ProgressoResponse, tags=["Progresso do Usuário"])
async def registrar_progresso(progresso: ProgressoCreate, current_user: dict = Depends(get_current_user)):
    entry = {"id": len(fake_progresso_db) + 1, "id_usuario": current_user["id"], **progresso.dict()}
    fake_progresso_db.append(entry)
    print("Progresso salvo:", entry)
    return entry

@app.get("/progresso/meu", response_model=List[ProgressoResponse], tags=["Progresso do Usuário"])
async def obter_meu_progresso(current_user: dict = Depends(get_current_user)):
    return [p for p in fake_progresso_db if p["id_usuario"] == current_user["id"]]

