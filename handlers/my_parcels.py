import logging
from datetime import date, datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from handlers.user_menu import get_current_user
from keyboards.inline_user import user_parcel_actions_keyboard, user_parcels_page_keyboard
from services.parcels import get_parcel_for_user, get_parcels_by_client_code
from texts import ru, tj
from texts.status import format_status
from utils.constants import LANG_RU, LANG_TJ, STATUS_ARRIVED_DESTINATION


router = Router(name="my_parcels")
logger = logging.getLogger(__name__)
PAGE_SIZE = 5


MY_PARCELS_MENU_LABELS = {tj.MENU_MY_PARCELS, ru.MENU_MY_PARCELS}
MY_PARCELS_MENU_LABELS.update({"Борҳои ман", "Мои грузы"})
TEXTS = {
    LANG_TJ: tj,
    LANG_RU: ru,
}


def _texts(lang: str):
    return TEXTS.get(lang, tj)


def _format_date(value: datetime | date | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%d.%m.%Y")


def _format_parcel_item(parcel, lang: str) -> str:
    texts = _texts(lang)
    return texts.MY_PARCELS_ITEM.format(
        track_code=parcel.track_code,
        dynamic_status=format_status(
            parcel.status_code,
            parcel.destination_city,
            lang,
        ),
        destination_city=parcel.destination_city,
        received_china_at=_format_date(parcel.received_china_at),
    )


def _format_parcel_view(parcel, lang: str) -> str:
    return _format_parcel_item(parcel, lang)


def _format_page_text(parcels, lang: str, page: int, total: int) -> str:
    texts = _texts(lang)
    start = page * PAGE_SIZE
    lines = [texts.MY_PARCELS_TITLE]
    if total:
        lines.append(f"Саҳифа: {page + 1}" if lang == LANG_TJ else f"Страница: {page + 1}")
    lines.append("")
    for index, parcel in enumerate(parcels, start=start + 1):
        lines.append(
            f"{index}. <code>{parcel.track_code}</code> · "
            f"{format_status(parcel.status_code, parcel.destination_city, lang)}"
        )
    return "\n".join(lines)


async def _safe_edit_or_answer(message: Message, text: str, **kwargs) -> None:
    try:
        await message.edit_text(text, **kwargs)
    except TelegramBadRequest:
        await message.answer(text, **kwargs)


async def _send_my_parcels(target, *, page: int = 0) -> None:
    message = target.message if isinstance(target, CallbackQuery) else target
    if message is None:
        return

    user = (
        await get_current_user(message)
        if not isinstance(target, CallbackQuery)
        else None
    )
    if isinstance(target, CallbackQuery):
        from services.users import get_user_by_telegram_id

        user = await get_user_by_telegram_id(target.from_user.id)

    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    texts = _texts(user.language)
    parcels = await get_parcels_by_client_code(user.client_code)
    if not parcels:
        await message.answer(texts.MY_PARCELS_EMPTY)
        return

    page = max(page, 0)
    start = page * PAGE_SIZE
    page_items = parcels[start:start + PAGE_SIZE]
    if not page_items and page > 0:
        page = 0
        start = 0
        page_items = parcels[:PAGE_SIZE]

    text = _format_page_text(page_items, user.language, page, len(parcels))
    keyboard = user_parcels_page_keyboard(
        page_items,
        user.language,
        page=page,
        page_size=PAGE_SIZE,
        total=len(parcels),
    )
    if isinstance(target, CallbackQuery):
        await _safe_edit_or_answer(message, text, reply_markup=keyboard)
    else:
        await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_(MY_PARCELS_MENU_LABELS))
async def show_my_parcels(message: Message) -> None:
    try:
        await _send_my_parcels(message)

    except Exception:
        logger.exception("[MY_PARCELS_ERROR] failed")
        user = await get_current_user(message)
        lang = getattr(user, "language", "tj") if user else "tj"

        if lang == "ru":
            text = (
                "❌ <b>Ошибка при загрузке ваших грузов.</b>\n\n"
                "<blockquote>Попробуйте позже или напишите оператору.</blockquote>"
            )
        else:
            text = (
                "❌ <b>Ҳангоми нишон додани борҳои шумо хатогӣ шуд.</b>\n\n"
                "<blockquote>Лутфан баъдтар такрор кунед ё ба оператор нависед.</blockquote>"
            )

        await message.answer(text)


@router.callback_query(F.data.startswith("user_parcel:page:"))
async def show_my_parcels_page(callback: CallbackQuery) -> None:
    try:
        page = int(callback.data.rsplit(":", 1)[1])
    except (ValueError, AttributeError):
        await callback.answer()
        return

    await _send_my_parcels(callback, page=page)
    await callback.answer()


@router.callback_query(F.data.startswith("user_parcel:view:"))
async def show_user_parcel(callback: CallbackQuery) -> None:
    from services.users import get_user_by_telegram_id

    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None or callback.message is None:
        await callback.answer()
        return

    try:
        parcel_id = int(callback.data.rsplit(":", 1)[1])
    except (ValueError, AttributeError):
        await callback.answer()
        return

    parcel = await get_parcel_for_user(parcel_id, user.id)
    if parcel is None:
        await callback.answer()
        return

    await _safe_edit_or_answer(
        callback.message,
        _format_parcel_view(parcel, user.language),
        reply_markup=user_parcel_actions_keyboard(
            user.language,
            parcel.id,
            include_delivery_actions=parcel.status_code == STATUS_ARRIVED_DESTINATION,
        ),
    )
    await callback.answer()
