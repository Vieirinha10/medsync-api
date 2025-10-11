# Arquivo: main.py

# --- 1. Importações e Configuração Inicial ---
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import bcrypt
from typing import List, Dict, Any

app = FastAPI(
    title="API MEDSYNC",
    description="API para a plataforma de aprendizado médico MEDSYNC.",
    version="0.1.0"
)

# --- Configuração do CORS Corrigida ---
# Adiciona a URL do seu site na Vercel à lista de origens permitidas.
origins = [
    "http://localhost:5173",
    "https://medsync-frontend-three.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 2. Modelos de Dados (Schemas com Pydantic) ---

# Modelos de Usuário
class UserCreate(BaseModel): nome: str; email: EmailStr; password: str
class UserResponse(BaseModel): id: int; nome: str; email: EmailStr
class UserLogin(BaseModel): email: EmailStr; password: str
class Token(BaseModel): access_token: str; token_type: str

# Modelos de Casos Clínicos
class CasoClinico(BaseModel): id: int; titulo: str; especialidade: str; nivel_dificuldade: str
class CasoClinicoDetalhes(CasoClinico):
    historia_clinica: str
    exame_fisico: str
    exames_disponiveis: List[Dict[str, Any]]

# Modelos para o Progresso do Usuário
class ProgressoCreate(BaseModel): id_caso: int; respostas_usuario: Dict[str, Any]; pontuacao: int
class ProgressoResponse(ProgressoCreate): id: int; id_usuario: int


# --- 3. "Bancos de Dados" Falsos com os 40 Casos Clínicos Corrigidos ---
fake_user_db = []
fake_casos_db = [
    {
        "id": 1, "titulo": "Diagnóstico diferencial de dor torácica", "especialidade": "Cardiologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "JSP, 32 anos, masculino, branco, mecânico. Queixa de dor torácica em região precordial, de início há 7 dias, em peso, de intensidade progressiva, ventilatório dependente, sem relação com o esforço, sem irradiações. Posição sentada em ântero-flexão do tronco como fator de melhora. Nega febre, tabagismo, etilismo e antecedentes de cardiopatia. Referiu cirurgia de orquiectomia esquerda por seminoma há 4 anos.",
        "exame_fisico": "BEG, eupneico, acianótico, anictérico, hipocorado (+/4+), ansioso. Aparelho respiratório: tórax atípico, murmúrio vesicular fisiológico presente. Aparelho cardiovascular: ritmo cardíaco regular em 2 tempos, bulhas normofonéticas, sem sopros. Abdome e membros inferiores sem alterações.",
        "exames_disponiveis": [
            {"id": "ecg", "nome": "ECG", "resultado": "Sem alterações."},
            {"id": "raiox", "nome": "Radiografia de tórax", "resultado": "Sem alterações."},
            {"id": "hemo", "nome": "Hemograma", "resultado": "Hb=10 g/dL (VR: 13 a 16,5 g/dL)."},
            {"id": "marcadores", "nome": "Marcadores de necrose miocárdica", "resultado": "Sem alterações."},
            {"id": "pcr", "nome": "PCR", "resultado": "25 mg/L (VR: <5 mg/L)."}
        ]
    },
    {
        "id": 2, "titulo": "Paciente com cefaleia há um ano", "especialidade": "Cardiologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "NPS, 48 anos, feminina, branca, queixa-se de cefaleia temporal há 1 ano. Encaminhada pelo oftalmologista após fundoscopia revelar sinais de retinopatia hipertensiva. Menopausada há 2 anos, cirurgia há 8 meses por neurinoma hipofisário. Pai hipertenso.",
        "exame_fisico": "FC: 96 bpm, PA: 110/70 mmHg. Ausculta cardíaca: ritmo regular em 3 tempos (presença de B4 em ponta), A2 hiperfonética.",
        "exames_disponiveis": [
            {"id": "ecg", "nome": "ECG", "resultado": "Sobrecarga ventricular esquerda."},
            {"id": "eco", "nome": "Ecocardiograma", "resultado": "Hipertrofia ventricular esquerda concêntrica e FEVE = 69,34%."},
            {"id": "mapa", "nome": "MAPA (24 horas)", "resultado": "Média de 154/88 mmHg."},
            {"id": "lab", "nome": "Exames laboratoriais", "resultado": "Ureia=59 mg/dL; Creatinina=1,54 mg/dL; Glicose=112 mg/dL; HbA1c=6,6%."}
        ]
    },
    {
        "id": 3, "titulo": "Amiloidose cardíaca secundária à mieloma múltiplo", "especialidade": "Cardiologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Masculino, 62 anos, pardo, aposentado, hipertenso, obeso. Apresentou dispneia progressiva há dez meses e síncope há 1 mês. Dispneia aos mínimos esforços (tomar banho), associado a edema de membros inferiores, fraqueza, palidez e dor em região costal. Diagnosticado com síndrome do túnel do carpo.",
        "exame_fisico": "Hipocorado, ausculta cardíaca com bulhas hipofonéticas, ausculta respiratória com murmúrio vesicular diminuído em bases, turgência jugular e fígado a 4cm do rebordo costal.",
        "exames_disponiveis": [
            {"id": "hemo", "nome": "Hemograma", "resultado": "Hb de 6,7 g/dL, hematócrito de 20,7%, hemácias em Rouleaux."},
            {"id": "lab", "nome": "Bioquímica", "resultado": "Creatinina = 2 mg/dL."},
            {"id": "raiox", "nome": "Radiografia de tórax", "resultado": "Área cardíaca normal, derrame pleural bilateral."},
            {"id": "ecg", "nome": "Eletrocardiograma", "resultado": "Ritmo sinusal, de baixa amplitude, com distúrbio de condução do ramo direito."},
            {"id": "eco", "nome": "Ecocardiograma", "resultado": "Aumento discreto dos átrios, FEVE: 48%, disfunção diastólica tipo III (padrão restritivo)."}
        ]
    },
    {
        "id": 4, "titulo": "Miocardite lúpica e ICFER", "especialidade": "Cardiologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Feminino, 37 anos, parda, com queixas de dor em mãos, cotovelos e joelhos, acompanhada de febre diária há 15 dias. Percebeu rosto mais avermelhado. Mãe com doença reumatológica.",
        "exame_fisico": "Febril (38ºC), taquipneica (FR=30), eritema malar, edema em membros inferiores e articulações. Discreto sopro sistólico em foco aórtico e sopro diastólico em foco mitral.",
        "exames_disponiveis": [
            {"id": "les", "nome": "Marcadores de LES", "resultado": "FAN, anti-DNA e anti-Sm positivos."},
            {"id": "eco", "nome": "Ecocardiograma (após 2 meses)", "resultado": "Derrame pericárdico importante, fração de ejeção de 33%, hipocinesia difusa."}
        ]
    },
    {
        "id": 5, "titulo": "Sangramento uterino anormal há 7 dias", "especialidade": "Cirurgia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "L.M.N, feminino, 37 anos, negra, obesa. Queixa-se de sangramento uterino anormal há 7 dias, em grande quantidade, associado a dor pélvica de baixa intensidade e dispareunia. Menarca precoce (9 anos), G2P0A2. Nega uso de contraceptivos. Uso abusivo de álcool, HAS e câncer de colo uterino na família.",
        "exame_fisico": "IMC 32 kg/m². Abdome globoso e doloroso à palpação nos quadrantes inferiores. Exame ginecológico: útero aumentado, móvel e de contorno irregular.",
        "exames_disponiveis": [{"id": "usg", "nome": "Ultrassonografia Transvaginal", "resultado": "Considerado padrão ouro para diagnóstico de Leiomioma Uterino."}]
    },
    {
        "id": 6, "titulo": "Hematêmese há 6h", "especialidade": "Cirurgia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "V.Y.L, masculino, 61 anos. Deu entrada na UPA com um episódio de hematêmese há 6 horas. Relata dor epigástrica em queimação (8/10), com piora após alimentação, que o faz acordar durante a noite. Perda ponderal de 8 Kg no último mês. Náuseas, febre e sudorese.",
        "exame_fisico": "FC: 120 bpm, Tax: 38°C. Abdome com distensão, RHA presentes, loja hepática timpânica e abdome doloroso e em tábua.",
        "exames_disponiveis": [{"id": "eda", "nome": "Endoscopia Digestiva Alta", "resultado": "Padrão ouro para diagnóstico de lesões ulcerativas."}]
    },
    {
        "id": 7, "titulo": "Deficiência de Ferro Devido a Gastrectomia", "especialidade": "Clínica Médica", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "E.M.F.R, feminino, 32 anos. Há 5 meses submetida à cirurgia bariátrica (bypass gástrico). Refere dor de cabeça, diarreia, falta de ar e tonturas frequentes. Desânimo, dificuldade para dormir, palpitações. Diabética e hipertensa.",
        "exame_fisico": "Palidez cutaneomucosa, queilite angular, unhas quebradiças, adinamia. PA=139x90mmHg, FC=90 bpm, FR=30 ipm.",
        "exames_disponiveis": [
            {"id": "hemo", "nome": "Hemograma", "resultado": "HB=4g/dL, VCM=73fL, CHCM=27g/dL, RDW=19%, plaquetas=580.000/mm³."},
            {"id": "ferro", "nome": "Perfil de Ferro", "resultado": "Ferro sérico=24mg/dL, ferritina sérica=10g/mL, TIBC=470mg/dL."}
        ]
    },
    {
        "id": 8, "titulo": "Tromboembolismo Pulmonar", "especialidade": "Clínica Médica", "nivel_dificuldade": "Difícil",
        "historia_clinica": "C.R.O., 54 anos, feminino. Queixa de dor ventilatório dependente contínua, em pontada, de início súbito, na região infraaxilar do hemitórax direito há 9 horas. Piora com movimento, tosse e respiração. Sentiu falta de ar. Diabética, hipertensa e histórico de câncer de mama.",
        "exame_fisico": "IMC 30,2 kg/m², taquipneica (FR 27 ipm), saturação de 83% em ar ambiente, FC 105 bpm. Braço esquerdo edemaciado, hiperemiado e doloroso a palpação.",
        "exames_disponiveis": [
            {"id": "ecg", "nome": "ECG", "resultado": "Apenas taquicardia sinusal."},
            {"id": "enzimas", "nome": "Enzimas cardíacas", "resultado": "Normais."},
            {"id": "dimerod", "nome": "D-dímero", "resultado": "Maior que 500 ng/dl."},
            {"id": "raiox", "nome": "Raio-X de tórax", "resultado": "Normal."}
        ]
    },
    {
        "id": 9, "titulo": "Herpes-Zóster e Síndrome de Ramsay Hunt", "especialidade": "Dermatologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "L.R.B, feminino, 78 anos. Queixa de lesões em região oral. Há 5-6 dias iniciou quadro de dor tipo queimação em orofaringe, após 2 dias surgiram vesículas. Aparição de lesões vesiculadas no pavilhão auditivo esquerdo, região mandibular e couro cabeludo. Adinamia, perda ponderal, vertigem, perda auditiva e paralisia facial ipsilateral. Diabética.",
        "exame_fisico": "Lesões na forma de bolhas em base eritematosa com ardor associado.",
        "exames_disponiveis": []
    },
    {
        "id": 10, "titulo": "Reação hansênica", "especialidade": "Dermatologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "Masculino, 16 anos. Queixa de manchas no corpo e coceira há 1 mês. Febre, cefaleia, mal-estar geral e náuseas há 7 dias. Em tratamento para hanseníase dimorfa há 2 meses.",
        "exame_fisico": "Exantema difuso associado a placas eritemoinfiltradas. Edema de mãos e pés e dor à palpação dos nervos ulnar e fibular direito.",
        "exames_disponiveis": [
            {"id": "hemo", "nome": "Hemograma", "resultado": "Anemia moderada (Hb 8,5g/dL), leucocitose com eosinofilia."},
            {"id": "transaminases", "nome": "Transaminases", "resultado": "Elevação em 4 vezes o limite superior de normalidade."}
        ]
    },
    {
        "id": 11, "titulo": "Macroprolactinoma", "especialidade": "Endocrinologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "C.M.F, 32 anos, feminino, casada. Queixas de cefaleia intensa e diplopia visual. Relata desregulação menstrual, dispareunia, ressecamento vaginal, redução da libido, infertilidade e galactorreia há 1 mês, com caráter progressivo.",
        "exame_fisico": "Tireoide normopalpável. Exames laboratoriais com PRL = 700ng/ml. Função renal, hepática, TSH e T4L normais. Gravidez afastada.",
        "exames_disponiveis": [{"id": "rm", "nome": "Ressonância Magnética de sela túrcica", "resultado": "Evidenciou macroadenoma (2,3x1,8x1,5cm) a direita da hipófise."}]
    },
    {
        "id": 12, "titulo": "Síndrome de Cushing Iatrogênica", "especialidade": "Endocrinologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "AFP, 18 anos, feminino. Queixa-se de ganho de peso e aparecimento de estrias há um ano, e surgimento de pêlos na face há um mês. Aumento do apetite, ganho de 22 kg, estrias violáceas, crescimento anormal de pêlos na mandíbula, desregulação menstrual e fraqueza muscular. Faz uso há 5 anos de descongestionante nasal a base de Betametasona.",
        "exame_fisico": "Padrão adiposo centrípeto, fácies em lua cheia, hirsutismo, giba, pele delgada, oleosa e acneica, estrias vermelho-arroxeadas. PA 150x110mmHg, IMC: 31,2kg/m².",
        "exames_disponiveis": [{"id": "lab", "nome": "Exames laboratoriais", "resultado": "Supressão do ACTH plasmático e cortisol indosável."}]
    },
    {
        "id": 13, "titulo": "Colangite Esclerosante Primária", "especialidade": "Gastroenterologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "J.H.B, masculino, 43 anos. Queixa de dor abdominal moderada, fraqueza, tontura e prurido há 2 anos. Piora há 1 mês com icterícia, náuseas, vômitos, abdome distendido e constipação. Febre (>38,5ºC) com calafrios há 4 dias. Colúria. Diagnosticado com Retocolite Ulcerativa sem acompanhamento.",
        "exame_fisico": "REG, febril, ictérico. Bordo hepático palpável 4 cm abaixo do rebordo costal direito, consistência dura e superfície irregular. Dor à palpação profunda do hipocôndrio e flanco direitos.",
        "exames_disponiveis": [{"id": "lab", "nome": "Exames laboratoriais", "resultado": "Leucocitose (15.000), Plaquetopenia (120.000), ALT/TGP: 168, AST/TGO: 173, Hiperbilirrubinemia total: 2,8 mg/dl (direta: 2,4 mg/dl)."}]
    },
    {
        "id": 14, "titulo": "Pancreatite Aguda", "especialidade": "Gastroenterologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "M.A.C, feminino, 49 anos. Dor intensa e contínua na região epigástrica irradiando para região retroesternal há 8 horas (9/10). 2 episódios de vômito, náuseas e sudorese. Piora após ingestão de alimentos gordurosos. HAS, hipercolesterolemia, hipertrigliceridemia. Diagnóstico de colelitíase há 15 dias.",
        "exame_fisico": "REG, taquicárdico (FC 120 bpm), taquipneico (FR 25 ipm), hipertenso (TA 176x102). Presença do sinal de Cullen. Abdome levemente rígido e doloroso difusamente à palpação profunda.",
        "exames_disponiveis": [{"id": "lab", "nome": "Exames laboratoriais", "resultado": "Leucograma: 20.000, Amilase: 300 U/L, Lipase: 190 I/L."}]
    },
    {
        "id": 15, "titulo": "Adenomiose", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "F.C.A., feminino, 41 anos. Relatou menorragia e hipermenorreia há 11 meses, cólicas incapacitantes no período menstrual e dor durante relação sexual.",
        "exame_fisico": "Exame de ultrassonografia transvaginal encontrou um aumento no volume uterino, cistos miometriais e textura miometrial heterogênea.",
        "exames_disponiveis": [{"id": "hemo", "nome": "Hemograma", "resultado": "Hb: 8,7 g/dL, VCM: 65 fL, HCM: 19 g/dL (Anemia ferropriva)."}]
    },
    {
        "id": 16, "titulo": "Amenorreia (Síndrome de Turner)", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "AMP, feminino, 22 anos. Paciente hígida, chega ao consultório referindo ausência de menarca. Pouco ou nenhum desenvolvimento dos caracteres sexuais secundários.",
        "exame_fisico": "Altura: 1,42m. Mamas em estágio M2 e pelos pubianos em P2.",
        "exames_disponiveis": [{"id": "hormonios", "nome": "Exames hormonais", "resultado": "FSH: 67 mUI/ml, LH: 29 mUI/ml."}]
    },
    {
        "id": 17, "titulo": "Endometriose", "especialidade": "Ginecologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "MSR, feminino, 20 anos. Queixa de piora progressiva de dismenorreia, de forte intensidade (10/10). Surgimento, há 5 meses, de dor em baixo ventre fora do período menstrual. Refere dispareunia profunda. Menarca precoce (10 anos), ciclos curtos (23 dias) com fluxo intenso.",
        "exame_fisico": "Ao exame ginecológico apresenta dor à mobilização uterina e nódulos e espessamentos em fundo de saco.",
        "exames_disponiveis": [{"id": "usg", "nome": "Ultrassonografia pélvica transvaginal", "resultado": "Primeiro exame de imagem a ser solicitado na suspeita."}]
    },
    {
        "id": 18, "titulo": "Herpes Genital", "especialidade": "Infectologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "A.S.C., 25 anos, feminino. Dor e ardor intenso para urinar há 2 dias. Disúria no início da micção. Corrimento fétido e 'feridas' na vulva. Teve febre há 3 dias.",
        "exame_fisico": "Várias lesões ulceradas (erosões) comprometendo principalmente a face interna dos pequenos lábios e vestíbulo. Secreção tipo fibrina amarelada com odor fétido. Edema de pequenos lábios.",
        "exames_disponiveis": [{"id": "raspado", "nome": "Raspado do fundo da lesão", "resultado": "Presença de células gigantes multinucleadas."}]
    },
    {
        "id": 19, "titulo": "Gonorreia", "especialidade": "Infectologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "M.S., 23 anos, feminino. Corrimento amarelado e disúria há 15 dias. Piora pós-coito e sangramento discreto durante o mesmo (sinusorragia). Namorado refere disúria e secreção amarela pela uretra.",
        "exame_fisico": "Exame especular: Colo friável, presença de mácula rubra periorificial e secreção endocervical branca amarelada abundante.",
        "exames_disponiveis": [{"id": "gram", "nome": "Gram da secreção endocervical", "resultado": "Presença de diplococo intracelular Gram-negativo."}]
    },
    {
        "id": 20, "titulo": "Síndrome do Encarceramento (Locked-in)", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "J.M.F.P., 52 anos, masculino. Quadro súbito de tetraplegia, disartria e perda da consciência. Familiar identificou que o paciente tentava realizar movimentos oculares como resposta.",
        "exame_fisico": "Babinski bilateral, paralisia facial bilateral, perda do olhar horizontal e preservação de movimentos oculares verticais. Sensibilidade dolorosa global preservada.",
        "exames_disponiveis": [{"id": "puncao", "nome": "Punção Lombar", "resultado": "Líquido cefalorraquidiano hemorrágico."}]
    },
    {
        "id": 21, "titulo": "Paralisia de Bell", "especialidade": "Neurologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "J.C.S., feminino, 32 anos. Queixa de não conseguir controlar os músculos da hemiface esquerda. Perda da força muscular na área há alguns dias.",
        "exame_fisico": "Desvio da rima bucal para direita, dificuldade no fechar dos olhos e no enrugamento da testa do lado esquerdo.",
        "exames_disponiveis": []
    },
    {
        "id": 22, "titulo": "Migrânea sem Aura", "especialidade": "Neurologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "Feminino, 35 anos. Cefaleia há 12h em região temporal esquerda, pulsátil. Piora com luminosidade e ruídos. Notou que dores mais fortes acontecem no período menstrual. Mãe possuía cefaleia semelhante.",
        "exame_fisico": "Bom estado geral, sem sinais de irritação meníngea. Sem déficits motores ou sensitivos.",
        "exames_disponiveis": []
    },
    {
        "id": 23, "titulo": "Síndrome de West", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Masculino, 6 meses. Mãe relata movimentos como se estivesse se assustando há 1 mês. Espasmos extensores, duram fração de segundos, intermitentes. Acontecem com mais frequência ao despertar. Parto pré-termo (32 semanas).",
        "exame_fisico": "Hipotonia generalizada, letargia nos movimentos, não acompanha objetos, não sustenta a cabeça.",
        "exames_disponiveis": [{"id": "eeg", "nome": "Eletroencefalograma (EEG)", "resultado": "Padrão esperado de hipsarritmia."}]
    },
    {
        "id": 24, "titulo": "Enxaqueca com Aura", "especialidade": "Neurologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "R.E.F.P., 25 anos, feminino. Cefaleia intensa em região frontotemporal E há mais de 4 anos. Dor 9/10, pulsátil, interfere nas atividades. Associada a náuseas, vômitos e afasia durante os episódios. Piora na fase pré-menstrual e com consumo de chocolate. Uso de ACO.",
        "exame_fisico": "Exame neurológico sem alterações e não há sinais de meningismo.",
        "exames_disponiveis": [{"id": "tc", "nome": "TC de crânio sem contraste", "resultado": "Sem achados de anormalidade."}]
    },
    {
        "id": 25, "titulo": "Status Epilepticus", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "N.M.D, 65 anos, feminino. Deu entrada em emergência com quadro de abalos motores bilaterais e com perda da consciência, quadro que já dura mais de 20 minutos. Filha refere que a mãe possui epilepsia desde a adolescência. Uso regular de valproato. Diagnóstico de Alzheimer há 1 ano.",
        "exame_fisico": "FC=130 bpm, PA=120x90 mmHg, FR=28 irpm. Estado geral comprometido.",
        "exames_disponiveis": [{"id": "eeg", "nome": "Eletroencefalograma", "resultado": "Mostra atividade contínua de ondas e picos."}]
    },
    {
        "id": 26, "titulo": "AVC Isquêmico", "especialidade": "Neurologia", "nivel_dificuldade": "Difícil",
        "historia_clinica": "P. F. M. P., masculino, 68 anos. Deu entrada com cefaleia e vômitos recorrentes. Histórico de HAS, DM tipo II, sedentarismo, etilista e tabagista. No dia seguinte foi internado após quadro convulsivante. Queixava de dormência do braço esquerdo e dificuldade visual, com notória hemiparesia facial à esquerda.",
        "exame_fisico": "Hipertenso, hipocorado, taquicárdico e taquipneico.",
        "exames_disponiveis": [{"id": "tc", "nome": "TC do crânio", "resultado": "Observado uma obstrução arterial, ao nível superior do tronco encefálico."}]
    },
    {
        "id": 27, "titulo": "Avaliação Nutricional do Paciente Crítico", "especialidade": "Nutrologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "PDS, 71 anos, masculino. Portador de Doença de Chagas. Há 60 dias, constipação, mal-estar ao se alimentar e distensão abdominal. Disfagia piorou, com episódios persistentes de vômitos. Perda de mais de 10 kg em seis meses, fraqueza em MMII.",
        "exame_fisico": "REG, caquético, 54 kg, 152 cm. Abdome escavado, flácido.",
        "exames_disponiveis": [{"id": "lab", "nome": "Bioquímica", "resultado": "Ureia=66 mg/dL, Fósforo=0,7 mmol/L."}]
    },
    {
        "id": 28, "titulo": "Doença Celíaca", "especialidade": "Nutrologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "D.E.R, feminino, 10 anos. Diarreia (1-2 evacuações líquidas/dia), dor abdominal, cólicas e perda de apetite. Consumo preferencial de pães e cereais.",
        "exame_fisico": "REG, descorada ++/4+, 22,7kg, 124 cm. Tórax escavado.",
        "exames_disponiveis": [{"id": "lab", "nome": "Laboratório", "resultado": "Hemoglobina=11,2g/dL, Albumina sérica=3,4 g/dL."}]
    },
    {
        "id": 29, "titulo": "Complicação de Faringotonsilite (Escarlatina)", "especialidade": "Otorrinolaringologia", "nivel_dificuldade": "Fácil",
        "historia_clinica": "SNP, 6 anos. Após recuperar de uma amigdalite, apresentou dispneia, febre, e taquicardia (período de 14 dias).",
        "exame_fisico": "Edema 1+/4+, taquipneico, dores em articulações, língua em cor bem avermelhada, em aspecto de framboesa.",
        "exames_disponiveis": []
    },
    {
        "id": 30, "titulo": "Cardite Reumática", "especialidade": "Otorrinolaringologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "Guilherme, 17 anos. Infecção de garganta atual, com outros episódios no passado. Cansaço fácil, inchaço em joelhos, tornozelos e punhos que 'pulam' de uma junta para outra sempre que tem infecção na garganta.",
        "exame_fisico": "PA = 140x50mmHg e estase jugular a 45º. Ausculta cardíaca mostrou insuficiências aórtica e mitral ++ e estenose mitral +.",
        "exames_disponiveis": []
    },
    {
        "id": 31, "titulo": "Síndrome do Bebê Sacudido", "especialidade": "Pediatria", "nivel_dificuldade": "Difícil",
        "historia_clinica": "I.D.N, lactente de 40 dias. Deu entrada com crises convulsivas tônico-clônicas generalizadas. Mãe relata que a criança chora muito e o quadro se iniciou de repente enquanto estava com o pai.",
        "exame_fisico": "Hipotônica e fundoscopia com hemorragia retiniana bilateral difusa. Petéquias na face, mancha arroxeada na coxa direita e um hematoma em resolução em panturrilha esquerda.",
        "exames_disponiveis": [{"id": "tc", "nome": "TC de crânio", "resultado": "Hemorragia inter-hemisférica na região de seio longitudinal superior e edema cerebral."}]
    },
    {
        "id": 32, "titulo": "Manejo do Autismo na Atenção Primária", "especialidade": "Pediatria", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "LCSD, 1 ano e 6 meses. Mãe percebeu há 6 meses alteração no desenvolvimento. Não mantém contato visual, não responde ao nome, entretido com movimentos repetitivos, brinca sozinho. Teve regressão da linguagem. Pai autista.",
        "exame_fisico": "Exame dificultado por agitação da criança.",
        "exames_disponiveis": []
    },
    {
        "id": 33, "titulo": "Parada Cardiorrespiratória (PCR)", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico",
        "historia_clinica": "Mulher, 61 anos, com HAS não controlada. Sentiu intensa dor precordial em aperto, com irradiação para braço esquerdo, tontura e evoluindo para perda de consciência. Transeuntes constataram parada cardiorrespiratória.",
        "exame_fisico": "Parada cardiorrespiratória.",
        "exames_disponiveis": [{"id": "dea", "nome": "DEA", "resultado": "Identificou-se fibrilação ventricular, indicando-se a desfibrilação."}]
    },
    {
        "id": 34, "titulo": "AIT por Cardioembolismo Paradoxal", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Mulher, 43 anos. Subitamente, quadro com parestesia no braço direito e lado direito da face, desvio da rima labial, que melhorou após alguns minutos. Dispneia aos esforços moderados e dores fortes em pontada no peito.",
        "exame_fisico": "TC de crânio sem alterações.",
        "exames_disponiveis": [{"id": "eco", "nome": "Ecocardiograma", "resultado": "Detectado um mixoma em átrio direito e Forame Oval Patente."}]
    },
    {
        "id": 35, "titulo": "Trauma Cranioencefálico em Lactente", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Difícil",
        "historia_clinica": "Lactente, 6 meses, masculino. História de queda do berço há um dia. Avó relata que o lactente ficou 'molinho', desinteressado, recusando amamentação e sonolento. Dois episódios de vômito. Histórico de fratura de fêmur à esquerda. Pai etilista e agressivo.",
        "exame_fisico": "Hipoativo e hipotônico, sinais de má-higiene, lesões com aspecto de queimadura térmica. Hematoma em região temporal direita. Fundoscopia com hemorragia retiniana difusa.",
        "exames_disponiveis": [{"id": "tc", "nome": "TC de crânio", "resultado": "Hemorragia inter-hemisférica na região de seio longitudinal superior."}]
    },
    {
        "id": 36, "titulo": "Sepse de Foco Gastrointestinal", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico",
        "historia_clinica": "Francisco, 68 anos. Diarreia há 2 dias (6 episódios/dia), dor abdominal, vômitos e febre (39°C). Há 24h evoluiu com sangue nas fezes e queda do estado geral.",
        "exame_fisico": "Ruim estado geral, sudoreico, desidratado. FC: 135 bpm, FR: 23 ipm, PA: 90x65mmHg. Glasgow 13. Pulsos periféricos com amplitude diminuída.",
        "exames_disponiveis": [{"id": "lab", "nome": "Laboratório", "resultado": "Leuco 20.000; Bast 4%; Lactato 2,1."}]
    },
    {
        "id": 37, "titulo": "Encefalopatia Hipertensiva", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico",
        "historia_clinica": "Homem, 35 anos. Evoluindo há um dia com desorientação e agitação. Há 4-5 meses, queixa de cefaleia intermitente, palpitações e mal estar com sudorese após exercício. Diagnosticado com HAS há uma semana, indicado atenolol.",
        "exame_fisico": "Afebril, hidratado. FC: 123 bpm, FR: 22 irpm, SaO2: 98%, PA: 230/145 mmHg. Glasgow: 14.",
        "exames_disponiveis": [{"id": "fundo_olho", "nome": "Avaliação de fundo de olho", "resultado": "Obrigatório para o diagnóstico, esperando papiledema e hemorragias."}]
    },
    {
        "id": 38, "titulo": "Edema Agudo de Pulmão (EAP)", "especialidade": "Urgência e Emergência", "nivel_dificuldade": "Crítico",
        "historia_clinica": "Masculino, 72 anos. Dispneia aos mínimos esforços associada a tosse com expectoração rósea há 1 hora. Resfriado há uma semana. HAS mal controlada.",
        "exame_fisico": "Corado, hidratado. FC 110 bpm, FR 32 irpm, PA 180x130 mmHg, saturação O2: 82%. Tiragem intercostal e presença de creptações em ambos hemitoraces. Edema de MMII 2+/4+.",
        "exames_disponiveis": []
    },
    {
        "id": 39, "titulo": "Hiperplasia Prostática Benigna (HPB)", "especialidade": "Urologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "C.S.S, 67 anos, masculino. Queixa de diminuição da força e do calibre urinário há alguns meses. Hesitação para iniciar a micção, sensação de esvaziamento incompleto, gotejamento pós-miccional, polaciúria e nictúria. HAS, tabagista.",
        "exame_fisico": "Jato fraco à micção, globo vesical palpável. Toque retal: próstata aumentada, lisa, fibroelástica e sem nodulações.",
        "exames_disponiveis": [{"id": "usg", "nome": "Ultrassonografia de vias urinárias", "resultado": "Próstata de 70 g, paredes da bexiga espessadas, uretéro-hidronefrose bilateral. PSA: 6,0 ng/dl."}]
    },
    {
        "id": 40, "titulo": "Pielonefrite Aguda", "especialidade": "Urologia", "nivel_dificuldade": "Intermediário",
        "historia_clinica": "E.L.D, 55 anos, feminino. Há 1 dia iniciou quadro de dor lombar à direita associada a febre, calafrios, disúria e polaciúria. Náuseas e anorexia.",
        "exame_fisico": "Febril (Tax: 38,6ºC), desidratada 2+/4+. PA: 130 x 80 mmHg, FC: 104 bpm. Sinal de Giordano positivo à direita.",
        "exames_disponiveis": [{"id": "urina", "nome": "Sumário de urina", "resultado": "Urina turva, proteínas ++, esterase leucocitária positivo, nitrito positivo, leucócitos: 482.000/ml, cilindros leucocitários."}]
    }
]
fake_progresso_db = []


# --- 4. SIMULAÇÃO DE AUTENTICAÇÃO ---
async def get_current_user():
    if not fake_user_db:
        raise HTTPException(status_code=401, detail="Nenhum usuário cadastrado para simular login.")
    return fake_user_db[0]


# --- 5. Endpoints de Usuários ---
@app.post("/usuarios/registrar", response_model=UserResponse, tags=["Usuários"])
async def registrar_usuario(user: UserCreate):
    for existing_user in fake_user_db:
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Este email já está cadastrado.")
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = {"id": len(fake_user_db) + 1, "nome": user.nome, "email": user.email, "senha_hash": hashed_password.decode('utf-8')}
    fake_user_db.append(new_user)
    return new_user

@app.post("/usuarios/login", response_model=Token, tags=["Usuários"])
async def login_usuario(form_data: UserLogin):
    user = next((db_user for db_user in fake_user_db if db_user["email"] == form_data.email), None)
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user["senha_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")
    access_token = f"fake-token-for-{user['email']}"
    return {"access_token": access_token, "token_type": "bearer"}


# --- 6. Endpoints dos Casos Clínicos ---
@app.get("/casos-clinicos/", response_model=List[CasoClinico], tags=["Casos Clínicos"])
async def listar_casos_clinicos():
    return fake_casos_db

@app.get("/casos-clinicos/{caso_id}", response_model=CasoClinicoDetalhes, tags=["Casos Clínicos"])
async def obter_caso_clinico(caso_id: int):
    caso = next((c for c in fake_casos_db if c["id"] == caso_id), None)
    if caso is None:
        raise HTTPException(status_code=404, detail="Caso clínico não encontrado")
    return caso


# --- 7. Endpoints de Progresso do Usuário ---
@app.post("/progresso/registrar", response_model=ProgressoResponse, tags=["Progresso do Usuário"])
async def registrar_progresso(progresso: ProgressoCreate, current_user: dict = Depends(get_current_user)):
    new_progress_entry = {
        "id": len(fake_progresso_db) + 1,
        "id_usuario": current_user["id"],
        "id_caso": progresso.id_caso,
        "respostas_usuario": progresso.respostas_usuario,
        "pontuacao": progresso.pontuacao
    }
    fake_progresso_db.append(new_progress_entry)
    print("Progresso salvo:", new_progress_entry)
    return new_progress_entry

@app.get("/progresso/meu", response_model=List[ProgressoResponse], tags=["Progresso do Usuário"])
async def obter_meu_progresso(current_user: dict = Depends(get_current_user)):
    meu_progresso = [p for p in fake_progresso_db if p["id_usuario"] == current_user["id"]]
    return meu_progresso

