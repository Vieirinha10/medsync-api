"""Adiciona títulos públicos neutros aos casos clínicos."""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260811_08"
down_revision = "20260802_07"
branch_labels = None
depends_on = None


PUBLIC_CASE_TITLES = {
    1: "Dor torácica progressiva em homem de 32 anos",
    2: "Cefaleia crônica em mulher de 48 anos",
    3: "Dispneia progressiva e síncope em homem de 62 anos",
    4: "Febre e dores articulares em mulher de 37 anos",
    5: "Sangramento uterino intenso em mulher de 37 anos",
    6: "Hematêmese e dor epigástrica em homem de 61 anos",
    7: "Fadiga após cirurgia bariátrica em mulher de 32 anos",
    8: "Dispneia súbita e dor torácica em mulher de 54 anos",
    9: "Dor orofaríngea e alteração facial em mulher de 78 anos",
    10: "Febre e piora de lesões cutâneas em adolescente de 16 anos",
    11: "Cefaleia e alterações visuais em mulher de 32 anos",
    12: "Ganho de peso e fraqueza em mulher de 18 anos",
    13: "Icterícia e prurido em homem de 43 anos",
    14: "Dor epigástrica intensa em mulher de 49 anos",
    15: "Sangramento menstrual e dor pélvica em mulher de 41 anos",
    16: "Amenorreia primária em mulher de 22 anos",
    17: "Dismenorreia intensa e dor pélvica em mulher de 20 anos",
    18: "Disúria e lesões vulvares em mulher de 25 anos",
    19: "Corrimento e disúria em mulher de 23 anos",
    20: "Tetraplegia súbita em homem de 52 anos",
    21: "Fraqueza facial unilateral em mulher de 32 anos",
    22: "Cefaleia pulsátil em mulher de 35 anos",
    23: "Espasmos recorrentes em lactente de 6 meses",
    24: "Cefaleia intensa com sintomas neurológicos em mulher de 25 anos",
    25: "Convulsão prolongada em mulher de 65 anos",
    26: "Déficit neurológico focal em homem de 68 anos",
    27: "Perda ponderal e sintomas digestivos em homem de 71 anos",
    28: "Diarreia e dor abdominal em criança de 10 anos",
    29: "Febre e dispneia após amigdalite em criança de 6 anos",
    30: "Cansaço e dores articulares em adolescente de 17 anos",
    31: "Crises convulsivas súbitas em lactente de 40 dias",
    32: "Regressão da linguagem em criança de 1 ano e 6 meses",
    33: "Dor precordial e perda de consciência em mulher de 61 anos",
    34: "Déficit neurológico transitório em mulher de 43 anos",
    35: "Sonolência e vômitos após queda em lactente de 6 meses",
    36: "Febre, diarreia e piora clínica em homem de 68 anos",
    37: "Desorientação e cefaleia em homem de 35 anos",
    38: "Dispneia intensa e tosse em homem de 72 anos",
    39: "Sintomas urinários progressivos em homem de 67 anos",
    40: "Febre, disúria e dor lombar em mulher de 55 anos",
}


def upgrade() -> None:
    columns = {
        column["name"] for column in inspect(op.get_bind()).get_columns("clinical_cases")
    }
    if "titulo_publico" not in columns:
        with op.batch_alter_table("clinical_cases") as batch_op:
            batch_op.add_column(sa.Column("titulo_publico", sa.String(240)))

    connection = op.get_bind()
    for case_id, title in PUBLIC_CASE_TITLES.items():
        connection.execute(
            sa.text(
                "UPDATE clinical_cases SET titulo_publico = :title WHERE id = :case_id"
            ),
            {"title": title, "case_id": case_id},
        )
    connection.execute(
        sa.text(
            "UPDATE clinical_cases SET titulo_publico = "
            "'Apresentação clínica para investigação' WHERE titulo_publico IS NULL"
        )
    )
    with op.batch_alter_table("clinical_cases") as batch_op:
        batch_op.alter_column("titulo_publico", nullable=False)


def downgrade() -> None:
    columns = {
        column["name"] for column in inspect(op.get_bind()).get_columns("clinical_cases")
    }
    if "titulo_publico" in columns:
        with op.batch_alter_table("clinical_cases") as batch_op:
            batch_op.drop_column("titulo_publico")
