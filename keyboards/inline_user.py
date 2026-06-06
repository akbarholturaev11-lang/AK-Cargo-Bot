from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.builders import build_inline_keyboard
from utils.constants import (
    CITY_BOKHTAR,
    CITY_DUSHANBE,
    CITY_ISTARAVSHAN,
    CITY_KHUJAND,
    CITY_KULOB,
    CITY_NAMES,
    LANG_RU,
    LANG_TJ,
)


CITY_ROWS = (
    (CITY_ISTARAVSHAN, CITY_DUSHANBE),
    (CITY_KHUJAND, CITY_BOKHTAR),
    (CITY_KULOB,),
)


def language_keyboard() -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        (
            (("🇹🇯 Тоҷикӣ", "lang:tj"), ("🇷🇺 Русский", "lang:ru")),
        ),
    )


def auth_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = ((("📝 Регистрация", "auth:register"), ("🔐 Войти", "auth:login")),)
    else:
        rows = ((("📝 Бақайдгирӣ", "auth:register"), ("🔐 Ворид шудан", "auth:login")),)
    return build_inline_keyboard(rows)


def cities_keyboard(lang: str, include_back: bool = False) -> InlineKeyboardMarkup:
    rows = tuple(
        tuple(
            (
                CITY_NAMES[city_key].get(lang, CITY_NAMES[city_key][LANG_TJ]),
                f"city:{city_key}",
            )
            for city_key in row
        )
        for row in CITY_ROWS
    )
    if include_back:
        back_label = "⬅️ Назад" if lang == LANG_RU else "⬅️ Бозгашт"
        rows = rows + (((back_label, "auth:back"),),)
    return build_inline_keyboard(rows)


def profile_edit_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = (
            (("🧑 Изменить имя", "profile:edit_name"), ("📞 Изменить телефон", "profile:edit_phone")),
            (("🏙 Изменить город", "profile:edit_city"), ("🌐 Изменить язык", "profile:edit_language")),
            (("⬅️ Назад", "profile:back"),),
        )
    else:
        rows = (
            (("🧑 Иваз кардани ном", "profile:edit_name"), ("📞 Иваз кардани телефон", "profile:edit_phone")),
            (("🏙 Иваз кардани шаҳр", "profile:edit_city"), ("🌐 Иваз кардани забон", "profile:edit_language")),
            (("⬅️ Бозгашт", "profile:back"),),
        )
    return build_inline_keyboard(rows)


def profile_city_keyboard(lang: str) -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        tuple(
            tuple(
                (
                    CITY_NAMES[city_key].get(lang, CITY_NAMES[city_key][LANG_TJ]),
                    f"profile:city:{city_key}",
                )
                for city_key in row
            )
            for row in CITY_ROWS
        ),
    )


def profile_language_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = (
            (("Тоҷикӣ", "profile:language:tj"),),
            (("Русский", "profile:language:ru"),),
            (("⬅️ Назад", "profile:show"),),
        )
    else:
        rows = (
            (("Тоҷикӣ", "profile:language:tj"),),
            (("Русский", "profile:language:ru"),),
            (("⬅️ Бозгашт", "profile:show"),),
        )
    return build_inline_keyboard(rows)


def calculator_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = (
            (("⚖️ Рассчитать по кг", "calc:kg"),),
            (("📐 Рассчитать по кубу", "calc:cube"),),
        )
    else:
        rows = (
            (("⚖️ Бо кг ҳисоб кардан", "calc:kg"),),
            (("📐 Бо куб ҳисоб кардан", "calc:cube"),),
        )
    return build_inline_keyboard(rows)


def warehouse_city_keyboard(lang: str) -> InlineKeyboardMarkup:
    return build_inline_keyboard(
        tuple(
            tuple(
                (
                    CITY_NAMES[city_key][LANG_TJ],
                    f"warehouse:city:{city_key}",
                )
                for city_key in row
            )
            for row in CITY_ROWS
        ),
    )


def delivery_keyboard(lang: str, parcel_id: int | None = None) -> InlineKeyboardMarkup:
    delivery_callback = (
        f"delivery:request:{parcel_id}"
        if parcel_id is not None
        else "delivery:request"
    )
    warehouse_callback = (
        f"warehouse:arrival:{parcel_id}"
        if parcel_id is not None
        else "warehouse:choose"
    )
    if lang == LANG_RU:
        rows = (
            (("🚚 Доставка", delivery_callback),),
            (("📍 Адрес получения 🇹🇯", warehouse_callback),),
        )
    else:
        rows = (
            (("🚚 Доставка", delivery_callback),),
            (("📍 Адреси гирифтани бор 🇹🇯", warehouse_callback),),
        )
    return build_inline_keyboard(rows)


def user_parcel_actions_keyboard(
    lang: str,
    parcel_id: int | None,
    *,
    include_delivery_actions: bool = True,
) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = [
            [("🔍 Искать снова", "parcel_search:again")],
            [("📦 Мои грузы", "user_parcel:page:0")],
        ]
        if include_delivery_actions and parcel_id is not None:
            rows.extend(
                [
                    [("🚚 Доставка", f"delivery:request:{parcel_id}")],
                    [("📍 Адрес получения", f"warehouse:arrival:{parcel_id}")],
                ],
            )
        rows.append([("☎️ Оператор", "operator:show")])
    else:
        rows = [
            [("🔍 Боз ҷустуҷӯ", "parcel_search:again")],
            [("📦 Борҳои ман", "user_parcel:page:0")],
        ]
        if include_delivery_actions and parcel_id is not None:
            rows.extend(
                [
                    [("🚚 Доставка", f"delivery:request:{parcel_id}")],
                    [("📍 Адреси гирифтани бор", f"warehouse:arrival:{parcel_id}")],
                ],
            )
        rows.append([("☎️ Оператор", "operator:show")])

    return build_inline_keyboard(tuple(tuple(row) for row in rows))


def parcel_not_found_keyboard(lang: str) -> InlineKeyboardMarkup:
    if lang == LANG_RU:
        rows = (
            (("🔍 Искать снова", "parcel_search:again"),),
            (("☎️ Оператор", "operator:show"),),
        )
    else:
        rows = (
            (("🔍 Боз ҷустуҷӯ", "parcel_search:again"),),
            (("☎️ Оператор", "operator:show"),),
        )
    return build_inline_keyboard(rows)


def user_parcels_page_keyboard(
    parcels,
    lang: str,
    *,
    page: int,
    page_size: int,
    total: int | None = None,
) -> InlineKeyboardMarkup:
    rows = []
    start = page * page_size

    for index, parcel in enumerate(parcels, start=start + 1):
        label = f"{index}. {parcel.track_code}"
        rows.append(((label, f"user_parcel:view:{parcel.id}"),))

    nav = []
    if page > 0:
        nav.append(("⬅️", f"user_parcel:page:{page - 1}"))
    if total is None:
        has_next = len(parcels) == page_size
    else:
        has_next = (page + 1) * page_size < total
    if has_next:
        nav.append(("➡️", f"user_parcel:page:{page + 1}"))
    if nav:
        rows.append(tuple(nav))

    operator_label = "☎️ Оператор" if lang == LANG_RU else "☎️ Оператор"
    rows.append(((operator_label, "operator:show"),))
    return build_inline_keyboard(tuple(rows))


def channel_join_keyboard(channel_username: str) -> InlineKeyboardMarkup:
    url = f"https://t.me/{channel_username.replace('@', '')}"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Ба канал обуна шудан",
                    url=url,
                )
            ],
        ]
    )


def pickup_cities_keyboard(warehouses, lang: str, include_back: bool = False) -> InlineKeyboardMarkup:
    rows = []

    for warehouse in warehouses:
        label = warehouse.city_name_ru if lang == LANG_RU else warehouse.city_name_tj
        rows.append(((label, f"city:{warehouse.city_key}"),))

    if include_back:
        back_label = "⬅️ Назад" if lang == LANG_RU else "⬅️ Бозгашт"
        rows.append(((back_label, "auth:back"),))

    return build_inline_keyboard(tuple(rows))
