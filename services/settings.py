from typing import Any

from sqlalchemy import select

from database.db import async_session
from database.models import Setting


BRAND_NAME = "Akcorgo"
LEGACY_BRAND_NAMES = (
    "Akbarshoy bot",
    "AK Cargo",
    "Wasit Cargo",
    "wasit_cargo",
    "Tajway_cargo",
    "Tajway Cargo",
)
BRAND_SYNC_SETTING_KEYS = {"cargo_name", "welcome_text_tj", "welcome_text_ru"}

DEFAULT_SETTINGS = {
    "cargo_name": BRAND_NAME,
    "cargo_region": "Истаравшан",
    "client_code_prefix": "AK",
    "price_per_kg_tjs": "25",
    "price_per_cube_tjs": "3500",
    "delivery_days_tj": "18–25 рӯз",
    "delivery_days_ru": "18–25 дней",
    "delivery_enabled": "false",
    "delivery_inside_city_tj": "Дохили шаҳр: 15 сомонӣ",
    "delivery_outside_city_tj": (
        "Берун аз шаҳр: ба таксӣ равон мекунем, "
        "ҳаққи таксӣ алоҳида ҳисоб мешавад."
    ),
    "delivery_inside_city_ru": "По городу: 15 сомонӣ",
    "delivery_outside_city_ru": (
        "За город: отправляем на такси, "
        "стоимость такси оплачивается отдельно."
    ),
    "require_channel_join": "false",
    "channel_username": "",
    "operator_username": "",
    "operator_phone": "",
    "operator_whatsapp": "",
    "operator_work_time": "09:00–18:00",
    "welcome_image_file_id": "",
    "welcome_text_tj": (
        "🚚 <b>Хуш омадед ба Akcorgo!</b>\n\n"
        "Борҳои худро аз Чин то Тоҷикистон осон ва ором пайгирӣ кунед.\n"
        "Лутфан забонро интихоб кунед:"
    ),
    "welcome_text_ru": (
        "🚚 <b>Добро пожаловать в Akcorgo!</b>" + chr(10) + chr(10) +
        "<blockquote>" +
        "Ваш карго-сервис из Китая в Таджикистан." + chr(10) +
        "Выберите язык, чтобы продолжить." +
        "</blockquote>"
    ),
    "calculator_image_file_id": "",
    "prices_image_file_id": "",
    "status_image_file_id": "",
    "prices_text_tj": (
        "💰 Нархҳо\n\n"
        "🇨🇳 Чин → Тоҷикистон\n\n"
        "📦 1 кг: {price_per_kg_tjs} сомонӣ\n"
        "📐 1 куб: {price_per_cube_tjs} сомонӣ\n"
        "🚚 Муддати тахминӣ: {delivery_days_tj}\n\n"
        "⚠️ Вазн ва маблағи аниқ баъди расидани бор маълум мешавад."
    ),
    "prices_text_ru": (
        "💰 Цены\n\n"
        "🇨🇳 Китай → Таджикистан\n\n"
        "📦 1 кг: {price_per_kg_tjs} сомонӣ\n"
        "📐 1 куб: {price_per_cube_tjs} сомонӣ\n"
        "🚚 Примерный срок: {delivery_days_ru}\n\n"
        "⚠️ Точный вес и сумма будут известны после прибытия груза."
    ),
}


def _replace_legacy_brand(value: str) -> str:
    updated = value
    for old_name in LEGACY_BRAND_NAMES:
        updated = updated.replace(old_name, BRAND_NAME)
    return updated


def _stringify_setting_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


async def get_setting(key: str, default: str | None = None) -> str | None:
    async with async_session() as session:
        result = await session.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if setting is None:
            return default
        return setting.value


async def set_setting(key: str, value: Any) -> str:
    value_as_text = _stringify_setting_value(value)
    async with async_session() as session:
        result = await session.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if setting is None:
            session.add(Setting(key=key, value=value_as_text))
        else:
            setting.value = value_as_text
        await session.commit()
    return value_as_text


async def get_many_settings(defaults: dict[str, str]) -> dict[str, str]:
    async with async_session() as session:
        result = await session.execute(
            select(Setting).where(Setting.key.in_(defaults)),
        )
        settings = {setting.key: setting.value for setting in result.scalars().all()}

    return {
        key: settings.get(key, default)
        for key, default in defaults.items()
    }


async def get_bool_setting(key: str, default: bool = False) -> bool:
    value = await get_setting(key)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


async def get_int_setting(key: str, default: int = 0) -> int:
    value = await get_setting(key)
    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


async def get_float_setting(key: str, default: float = 0.0) -> float:
    value = await get_setting(key)
    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        return default


async def toggle_bool_setting(key: str, default: bool = False) -> bool:
    new_value = not await get_bool_setting(key, default)
    await set_setting(key, new_value)
    return new_value


async def seed_default_settings() -> None:
    async with async_session() as session:
        result = await session.execute(
            select(Setting.key).where(Setting.key.in_(DEFAULT_SETTINGS)),
        )
        existing_keys = set(result.scalars().all())

        for key, value in DEFAULT_SETTINGS.items():
            if key not in existing_keys:
                session.add(Setting(key=key, value=value))

        brand_result = await session.execute(
            select(Setting).where(Setting.key.in_(BRAND_SYNC_SETTING_KEYS)),
        )
        for setting in brand_result.scalars().all():
            setting.value = _replace_legacy_brand(setting.value)

        await session.commit()
