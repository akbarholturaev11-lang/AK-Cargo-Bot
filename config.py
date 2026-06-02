import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get_int_list(value: str | None) -> list[int]:
    if not value:
        return []

    admin_ids: list[int] = []
    for item in value.replace(" ", ",").split(","):
        item = item.strip()
        if item:
            admin_ids.append(int(item))
    return admin_ids


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return float(value)


BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")
ADMIN_IDS = _get_int_list(os.getenv("ADMIN_IDS"))
CLIENT_CODE_PREFIX = os.getenv("CLIENT_CODE_PREFIX", "AK")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_VISION_MODEL = os.getenv("OPENAI_VISION_MODEL", "gpt-5.4-mini")

DEFAULT_KG_PRICE_TJS = _get_float("DEFAULT_KG_PRICE_TJS", 0.0)
DEFAULT_CUBE_PRICE_TJS = _get_float("DEFAULT_CUBE_PRICE_TJS", 0.0)
DEFAULT_DELIVERY_DAYS_TJ = os.getenv("DEFAULT_DELIVERY_DAYS_TJ", "10-15 рӯз")
DEFAULT_DELIVERY_DAYS_RU = os.getenv("DEFAULT_DELIVERY_DAYS_RU", "10-15 дней")
