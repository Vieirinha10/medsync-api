"""Extrai sinais vitais documentados sem inventar dados ausentes."""

import re


def _item(
    key: str,
    label: str,
    value: str | None,
    unit: str,
    status: str,
    reference: str,
) -> dict[str, str | None]:
    return {
        "id": key,
        "nome": label,
        "valor": value,
        "unidade": unit,
        "status": status,
        "referencia": reference,
    }


def extract_vital_signs(history: str, physical_exam: str) -> list[dict[str, str | None]]:
    text = f"{history} {physical_exam}"
    normalized = text.replace("×", "x")

    pressure = re.search(
        r"\bPA(?:\s+no\s+consult[oó]rio)?\s*[:=]?\s*(\d{2,3})\s*[x/]\s*(\d{2,3})\s*mmhg",
        normalized,
        re.IGNORECASE,
    )
    heart_rate = re.search(r"\bFC\s*[:=]?\s*(\d{2,3})\s*bpm", normalized, re.IGNORECASE)
    respiratory_rate = re.search(
        r"\bFR\s*[:=]?\s*(\d{1,2})\s*(?:i?r?pm)?",
        normalized,
        re.IGNORECASE,
    )
    saturation = re.search(
        r"(?:sat(?:ura[cç][aã]o)?(?:\s+de)?(?:\s*o2)?|spo2)\s*[:=]?\s*(\d{2,3})\s*%",
        normalized,
        re.IGNORECASE,
    )
    temperature = re.search(
        r"(?:temperatura|temp\.?|tax|t)\s*[:=]?\s*(\d{2}(?:[,.]\d)?)\s*[º°]?c",
        normalized,
        re.IGNORECASE,
    ) or re.search(
        r"febril\s*\(\s*(\d{2}(?:[,.]\d)?)\s*[º°]?c\s*\)",
        normalized,
        re.IGNORECASE,
    )

    if pressure:
        systolic, diastolic = (int(pressure.group(1)), int(pressure.group(2)))
        pressure_status = "normal" if systolic < 130 and diastolic < 85 else "alterado"
        pressure_value = f"{systolic}/{diastolic}"
    else:
        pressure_status, pressure_value = "nao_informado", None

    heart_value = int(heart_rate.group(1)) if heart_rate else None
    respiratory_value = int(respiratory_rate.group(1)) if respiratory_rate else None
    saturation_value = int(saturation.group(1)) if saturation else None
    temperature_value = (
        float(temperature.group(1).replace(",", ".")) if temperature else None
    )

    return [
        _item("pa", "Pressão arterial", pressure_value, "mmHg", pressure_status, "< 130/85 mmHg"),
        _item(
            "fc",
            "Frequência cardíaca",
            str(heart_value) if heart_value is not None else None,
            "bpm",
            "normal" if heart_value is not None and 60 <= heart_value <= 100 else "alterado" if heart_value is not None else "nao_informado",
            "60–100 bpm",
        ),
        _item(
            "fr",
            "Frequência respiratória",
            str(respiratory_value) if respiratory_value is not None else None,
            "irpm",
            "normal" if respiratory_value is not None and 12 <= respiratory_value <= 20 else "alterado" if respiratory_value is not None else "nao_informado",
            "12–20 irpm",
        ),
        _item(
            "spo2",
            "Saturação de O₂",
            str(saturation_value) if saturation_value is not None else None,
            "%",
            "normal" if saturation_value is not None and saturation_value >= 95 else "alterado" if saturation_value is not None else "nao_informado",
            "≥ 95%",
        ),
        _item(
            "temperatura",
            "Temperatura",
            f"{temperature_value:.1f}" if temperature_value is not None else None,
            "°C",
            "normal" if temperature_value is not None and 36 <= temperature_value < 37.8 else "alterado" if temperature_value is not None else "nao_informado",
            "36,0–37,7 °C",
        ),
    ]
