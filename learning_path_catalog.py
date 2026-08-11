LEARNING_PATHS = [
    {
        "id": "emergencias-essenciais",
        "titulo": "Emergências essenciais",
        "subtitulo": "Reconheça ameaças imediatas e organize prioridades clínicas.",
        "descricao": (
            "Uma trilha prática para treinar identificação rápida, estabilização inicial "
            "e decisões que não podem esperar."
        ),
        "especialidade": "Urgência e Emergência",
        "nivel": "Intermediário",
        "cor": "laranja",
        "duracao_minutos": 55,
        "objetivos": [
            "Reconhecer sinais de instabilidade",
            "Priorizar hipóteses potencialmente fatais",
            "Relacionar imagem, diagnóstico e conduta inicial",
        ],
        "modulos": [
            {
                "id": "ameacas-toracicas",
                "titulo": "Ameaças torácicas",
                "descricao": "Diferencie rapidamente condições cardiopulmonares graves.",
                "atividades": [
                    {
                        "id": "emergencias-pneumotorax",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-001",
                        "titulo": "Interpretação de radiografia torácica",
                        "especialidade": "Radiologia",
                        "minutos": 6,
                    },
                    {
                        "id": "emergencias-tep",
                        "tipo": "caso_clinico",
                        "referencia_id": "8",
                        "titulo": "Dispneia súbita e dor torácica",
                        "especialidade": "Clínica Médica",
                        "minutos": 25,
                    },
                ],
            },
            {
                "id": "neurocirurgicas-abdominais",
                "titulo": "Emergências neurocirúrgicas e abdominais",
                "descricao": "Identifique achados de imagem que exigem ação rápida.",
                "atividades": [
                    {
                        "id": "emergencias-hematoma",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-003",
                        "titulo": "Interpretação de tomografia de crânio",
                        "especialidade": "Neurologia",
                        "minutos": 7,
                    },
                    {
                        "id": "emergencias-apendicite",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-008",
                        "titulo": "Interpretação de ultrassonografia abdominal",
                        "especialidade": "Cirurgia Geral",
                        "minutos": 7,
                    },
                ],
            },
        ],
    },
    {
        "id": "cardiopulmonar-na-pratica",
        "titulo": "Cardiopulmonar na prática",
        "subtitulo": "Integre ritmo, radiografia e raciocínio clínico.",
        "descricao": (
            "Do reconhecimento de padrões ao caso clínico completo, fortaleça a leitura "
            "dos principais problemas cardiovasculares e respiratórios."
        ),
        "especialidade": "Cardiologia e Pneumologia",
        "nivel": "Intermediário",
        "cor": "azul",
        "duracao_minutos": 48,
        "objetivos": [
            "Interpretar padrões básicos de ECG",
            "Reconhecer alterações radiográficas pulmonares",
            "Construir investigação e conduta para tromboembolismo pulmonar",
        ],
        "modulos": [
            {
                "id": "ritmo-e-torax",
                "titulo": "Ritmo e tórax",
                "descricao": "Comece pelos padrões visuais mais frequentes.",
                "atividades": [
                    {
                        "id": "cardiopulmonar-fa",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-002",
                        "titulo": "Interpretação de ritmo no ECG",
                        "especialidade": "Cardiologia",
                        "minutos": 6,
                    },
                    {
                        "id": "cardiopulmonar-pneumonia",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-007",
                        "titulo": "Interpretação de radiografia pulmonar",
                        "especialidade": "Pneumologia",
                        "minutos": 6,
                    },
                    {
                        "id": "cardiopulmonar-pneumotorax",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-001",
                        "titulo": "Interpretação de radiografia torácica",
                        "especialidade": "Radiologia",
                        "minutos": 6,
                    },
                ],
            },
            {
                "id": "raciocinio-integrado",
                "titulo": "Raciocínio integrado",
                "descricao": "Aplique os achados em uma simulação clínica completa.",
                "atividades": [
                    {
                        "id": "cardiopulmonar-tep",
                        "tipo": "caso_clinico",
                        "referencia_id": "8",
                        "titulo": "Dispneia súbita e dor torácica",
                        "especialidade": "Clínica Médica",
                        "minutos": 30,
                    },
                ],
            },
        ],
    },
    {
        "id": "diagnostico-por-imagem",
        "titulo": "Diagnóstico por imagem",
        "subtitulo": "Treine o olhar clínico em diferentes modalidades.",
        "descricao": (
            "Uma sequência visual progressiva com radiografia, tomografia, ultrassonografia, "
            "fundoscopia e fotografia clínica."
        ),
        "especialidade": "Imagem e diagnóstico",
        "nivel": "Progressivo",
        "cor": "violeta",
        "duracao_minutos": 62,
        "objetivos": [
            "Reconhecer achados-chave antes de formular hipóteses",
            "Diferenciar padrões semelhantes",
            "Ganhar velocidade em interpretação visual",
        ],
        "modulos": [
            {
                "id": "radiografia-e-tomografia",
                "titulo": "Radiografia e tomografia",
                "descricao": "Consolide padrões torácicos, neurológicos e urológicos.",
                "atividades": [
                    {
                        "id": "imagem-pneumonia",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-007",
                        "titulo": "Interpretação de radiografia pulmonar",
                        "especialidade": "Pneumologia",
                        "minutos": 6,
                    },
                    {
                        "id": "imagem-pneumotorax",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-001",
                        "titulo": "Interpretação de radiografia torácica",
                        "especialidade": "Radiologia",
                        "minutos": 6,
                    },
                    {
                        "id": "imagem-hematoma",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-003",
                        "titulo": "Interpretação de tomografia de crânio",
                        "especialidade": "Neurologia",
                        "minutos": 7,
                    },
                    {
                        "id": "imagem-calculo",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-009",
                        "titulo": "Interpretação de tomografia abdominal",
                        "especialidade": "Urologia",
                        "minutos": 7,
                    },
                ],
            },
            {
                "id": "imagem-clinica",
                "titulo": "Imagem clínica e métodos especiais",
                "descricao": "Explore pele, retina, ultrassonografia e hematologia.",
                "atividades": [
                    {
                        "id": "imagem-apendicite",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-008",
                        "titulo": "Interpretação de ultrassonografia abdominal",
                        "especialidade": "Cirurgia Geral",
                        "minutos": 7,
                    },
                    {
                        "id": "imagem-retinopatia",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-005",
                        "titulo": "Interpretação de fundoscopia",
                        "especialidade": "Oftalmologia",
                        "minutos": 7,
                    },
                    {
                        "id": "imagem-psoriase",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-004",
                        "titulo": "Interpretação de lesão dermatológica",
                        "especialidade": "Dermatologia",
                        "minutos": 6,
                    },
                    {
                        "id": "imagem-melanoma",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-010",
                        "titulo": "Avaliação de lesão pigmentada",
                        "especialidade": "Dermatologia",
                        "minutos": 8,
                    },
                    {
                        "id": "imagem-falciforme",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-006",
                        "titulo": "Interpretação de esfregaço sanguíneo",
                        "especialidade": "Hematologia",
                        "minutos": 8,
                    },
                ],
            },
        ],
    },
    {
        "id": "fundamentos-diagnosticos",
        "titulo": "Fundamentos diagnósticos",
        "subtitulo": "Construa repertório antes de avançar para casos complexos.",
        "descricao": (
            "Percurso introdutório para reconhecer padrões clássicos em diferentes áreas "
            "e ganhar segurança na formulação diagnóstica."
        ),
        "especialidade": "Clínica integrada",
        "nivel": "Básico",
        "cor": "verde",
        "duracao_minutos": 42,
        "objetivos": [
            "Reconhecer sinais visuais clássicos",
            "Relacionar achados e diagnóstico provável",
            "Construir uma base multidisciplinar",
        ],
        "modulos": [
            {
                "id": "padroes-basicos",
                "titulo": "Padrões essenciais",
                "descricao": "Comece com diagnósticos de alta relevância e sinais típicos.",
                "atividades": [
                    {
                        "id": "fundamentos-fa",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-002",
                        "titulo": "Interpretação de ritmo no ECG",
                        "especialidade": "Cardiologia",
                        "minutos": 6,
                    },
                    {
                        "id": "fundamentos-pneumonia",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-007",
                        "titulo": "Interpretação de radiografia pulmonar",
                        "especialidade": "Pneumologia",
                        "minutos": 6,
                    },
                    {
                        "id": "fundamentos-psoriase",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-004",
                        "titulo": "Interpretação de lesão dermatológica",
                        "especialidade": "Dermatologia",
                        "minutos": 6,
                    },
                    {
                        "id": "fundamentos-falciforme",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-006",
                        "titulo": "Interpretação de esfregaço sanguíneo",
                        "especialidade": "Hematologia",
                        "minutos": 7,
                    },
                ],
            },
            {
                "id": "ampliando-repertorio",
                "titulo": "Ampliando o repertório",
                "descricao": "Avance para métodos e áreas com maior especificidade.",
                "atividades": [
                    {
                        "id": "fundamentos-retinopatia",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-005",
                        "titulo": "Interpretação de fundoscopia",
                        "especialidade": "Oftalmologia",
                        "minutos": 7,
                    },
                    {
                        "id": "fundamentos-calculo",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-009",
                        "titulo": "Interpretação de tomografia abdominal",
                        "especialidade": "Urologia",
                        "minutos": 7,
                    },
                    {
                        "id": "fundamentos-apendicite",
                        "tipo": "desafio_visual",
                        "referencia_id": "desafio-visual-008",
                        "titulo": "Interpretação de ultrassonografia abdominal",
                        "especialidade": "Cirurgia Geral",
                        "minutos": 7,
                    },
                ],
            },
        ],
    },
]


def get_learning_path(path_id: str) -> dict | None:
    return next((path for path in LEARNING_PATHS if path["id"] == path_id), None)


def get_learning_activity(path: dict, activity_id: str) -> dict | None:
    for module in path["modulos"]:
        activity = next(
            (item for item in module["atividades"] if item["id"] == activity_id),
            None,
        )
        if activity is not None:
            return activity
    return None
