from datetime import date, datetime

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from keyboards.builders import build_inline_keyboard
from keyboards.reply import ADMIN_MENU
from services.normalizer import normalize_track_code
from services.notifications import notify_arrival_destination
from services.parcels import (
    count_parcels_by_status,
    get_parcel_with_user,
    get_parcel_with_user_by_normalized_track_code,
    get_parcels_with_user_by_client_code,
    list_parcels_by_status,
    mark_arrival_notified,
    update_parcel_status,
)
from services.users import get_user_by_client_code, get_user_by_phone
from texts.status import format_status
from utils.constants import (
    LANG_TJ,
    STATUS_ARRIVED_DESTINATION,
    STATUS_CHINA_RECEIVED,
    STATUS_CODES,
    STATUS_ON_THE_WAY,
    STATUS_RECEIVED,
)
from utils.validators import is_admin


router = Router(name="admin_status")


ADMIN_SEARCH_LABEL = ADMIN_MENU[0][1]
ADMIN_STATUS_UPDATE_LABEL = ADMIN_MENU[1][0]
ADMIN_CHINA_RECEIVED_LABEL = ADMIN_MENU[2][0]
ADMIN_ON_THE_WAY_LABEL = ADMIN_MENU[2][1]
ADMIN_ARRIVED_LABEL = ADMIN_MENU[3][0]
STATUS_PAGE_SIZE = 8


class AdminParcelStatusStates(StatesGroup):
    waiting_for_search_track_code = State()
    waiting_for_status_track_code = State()


def _is_admin_message(message: Message) -> bool:
    return message.from_user is not None and is_admin(message.from_user.id)


def _is_admin_callback(callback: CallbackQuery) -> bool:
    return is_admin(callback.from_user.id)


async def _safe_edit_text(message: Message, text: str, **kwargs) -> None:
    try:
        await message.edit_text(text, **kwargs)
    except TelegramBadRequest as error:
        if "message is not modified" in str(error).lower():
            return
        raise


def _format_date(value: datetime | date | None) -> str:
    if value is None:
        return "-"
    return value.strftime("%d.%m.%Y")


def _format_parcel(parcel) -> str:
    user = parcel.user
    return (
        "Маълумоти бор\n\n"
        f"Трек-код: {parcel.track_code}\n"
        f"Ном: {user.full_name}\n"
        f"Телефон: {user.phone}\n"
        f"Коди мизоҷ: {parcel.client_code}\n"
        f"Склад: {parcel.destination_city}\n"
        f"Статус: {format_status(parcel.status_code, parcel.destination_city, LANG_TJ)}\n"
        f"Санаи қабул: {_format_date(parcel.received_china_at)}"
    )


def _status_keyboard(parcel) -> object:
    return build_inline_keyboard(
        (
            (
                (
                    "🇨🇳 Дар склади Чин",
                    f"admin_status:set:{parcel.id}:{STATUS_CHINA_RECEIVED}",
                ),
            ),
            (
                (
                    "🚚 Дар роҳ",
                    f"admin_status:set:{parcel.id}:{STATUS_ON_THE_WAY}",
                ),
            ),
            (
                (
                    format_status(
                        STATUS_ARRIVED_DESTINATION,
                        parcel.destination_city,
                        LANG_TJ,
                    ),
                    f"admin_status:set:{parcel.id}:{STATUS_ARRIVED_DESTINATION}",
                ),
            ),
            (
                (
                    format_status(
                        STATUS_RECEIVED,
                        parcel.destination_city,
                        LANG_TJ,
                    ),
                    f"admin_status:set:{parcel.id}:{STATUS_RECEIVED}",
                ),
            ),
        ),
    )


def _status_lists_keyboard():
    return build_inline_keyboard(
        (
            (("🇨🇳 Қабулшудаҳо", f"admin_status:page:{STATUS_CHINA_RECEIVED}:0"),),
            (("🚚 Дар роҳ", f"admin_status:page:{STATUS_ON_THE_WAY}:0"),),
            (("🏬 Расидаҳо", f"admin_status:page:{STATUS_ARRIVED_DESTINATION}:0"),),
            (("✅ Супорида шуд", f"admin_status:page:{STATUS_RECEIVED}:0"),),
            (("🔍 Ҷустуҷӯ", "admin_search:again"),),
        ),
    )


def _status_page_keyboard(parcels, status_code: str, page: int, total: int):
    rows = []
    for parcel in parcels:
        rows.append(
            (
                (
                    f"{parcel.track_code} · {parcel.client_code}",
                    f"admin_status:view:{parcel.id}",
                ),
            ),
        )

    nav = []
    if page > 0:
        nav.append(("⬅️", f"admin_status:page:{status_code}:{page - 1}"))
    if (page + 1) * STATUS_PAGE_SIZE < total:
        nav.append(("➡️", f"admin_status:page:{status_code}:{page + 1}"))
    if nav:
        rows.append(tuple(nav))

    rows.append((("📦 Рӯйхати статусҳо", "admin_status:lists"),))
    rows.append((("🔍 Ҷустуҷӯ", "admin_search:again"),))
    return build_inline_keyboard(tuple(rows))


def _search_results_keyboard(parcels):
    rows = tuple(
        (
            (
                f"{parcel.track_code} · {parcel.client_code}",
                f"admin_status:view:{parcel.id}",
            ),
        )
        for parcel in parcels[:10]
    )
    return build_inline_keyboard(
        rows
        + (
            (("🔍 Боз ҷустуҷӯ", "admin_search:again"),),
            (("📦 Рӯйхати статусҳо", "admin_status:lists"),),
        ),
    )


async def _find_parcel_by_message_track_code(message: Message):
    normalized_track_code = normalize_track_code(message.text or "")
    if not normalized_track_code:
        return None
    return await get_parcel_with_user_by_normalized_track_code(normalized_track_code)


async def _admin_search(query: str) -> tuple[str, object | None]:
    value = query.strip()
    if not value:
        return "Ҷустуҷӯ холӣ аст.", None

    normalized_track_code = normalize_track_code(value)
    parcel = await get_parcel_with_user_by_normalized_track_code(normalized_track_code)
    if parcel is not None:
        return _format_parcel(parcel), _status_keyboard(parcel)

    user = await get_user_by_client_code(value.upper())
    if user is None:
        user = await get_user_by_phone(value)

    if user is not None:
        parcels = await get_parcels_with_user_by_client_code(user.client_code)
        text = (
            "Мизоҷ ёфт шуд\n\n"
            f"Ном: {user.full_name}\n"
            f"Телефон: {user.phone}\n"
            f"Коди мизоҷ: {user.client_code}\n"
            f"Борҳо: {len(parcels)}"
        )
        if not parcels:
            return text + "\n\nБарои ин мизоҷ бор сабт нашудааст.", build_inline_keyboard(
                ((("🔍 Боз ҷустуҷӯ", "admin_search:again"),),),
            )
        return text, _search_results_keyboard(parcels)

    parcels = await get_parcels_with_user_by_client_code(value.upper())
    if parcels:
        return f"Борҳо бо коди {value.upper()}: {len(parcels)}", _search_results_keyboard(parcels)

    return "Ҳеҷ чиз ёфт нашуд.", build_inline_keyboard(
        ((("🔍 Боз ҷустуҷӯ", "admin_search:again"),),),
    )


async def _send_status_page(target, status_code: str, page: int = 0) -> None:
    page = max(page, 0)
    total = await count_parcels_by_status(status_code)
    parcels = await list_parcels_by_status(
        status_code=status_code,
        limit=STATUS_PAGE_SIZE,
        offset=page * STATUS_PAGE_SIZE,
    )
    title = format_status(status_code, "", LANG_TJ)
    text = f"📦 <b>{title}</b>\n\nҲамагӣ: {total}\nСаҳифа: {page + 1}"
    if not parcels:
        text += "\n\nҲозирча дар ин рӯйхат бор нест."

    keyboard = _status_page_keyboard(parcels, status_code, page, total)
    if isinstance(target, CallbackQuery):
        if target.message is not None:
            await _safe_edit_text(target.message, text, reply_markup=keyboard)
        await target.answer()
        return

    await target.answer(text, reply_markup=keyboard)


@router.message(F.text.in_({ADMIN_SEARCH_LABEL, "🔍 Ҷустуҷӯи бор"}))
async def start_admin_search(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    await state.clear()
    await state.set_state(AdminParcelStatusStates.waiting_for_search_track_code)
    await message.answer("Трек-код, коди мизоҷ ё телефонро ворид кунед.")


@router.callback_query(F.data == "admin_search:again")
async def start_admin_search_callback(callback: CallbackQuery, state: FSMContext) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    await state.clear()
    await state.set_state(AdminParcelStatusStates.waiting_for_search_track_code)
    if callback.message is not None:
        await callback.message.answer("Трек-код, коди мизоҷ ё телефонро ворид кунед.")
    await callback.answer()


@router.message(AdminParcelStatusStates.waiting_for_search_track_code, F.text)
async def admin_search_parcel(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    text, keyboard = await _admin_search(message.text or "")
    await state.clear()
    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_({ADMIN_STATUS_UPDATE_LABEL, "Иваз кардани статус"}))
async def start_status_update(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    await state.clear()
    await state.set_state(AdminParcelStatusStates.waiting_for_status_track_code)
    await message.answer("Трек-кодро ворид кунед.")


@router.message(AdminParcelStatusStates.waiting_for_status_track_code, F.text)
async def status_update_find_parcel(message: Message, state: FSMContext) -> None:
    if not _is_admin_message(message):
        return

    parcel = await _find_parcel_by_message_track_code(message)
    await state.clear()
    if parcel is None:
        await message.answer("Ин трек-код ёфт нашуд.")
        return

    await message.answer(
        _format_parcel(parcel),
        reply_markup=_status_keyboard(parcel),
    )


@router.callback_query(F.data.startswith("admin_status:set:"))
async def set_single_status(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) != 4:
        await callback.answer()
        return

    try:
        parcel_id = int(parts[2])
    except ValueError:
        await callback.answer()
        return

    status_code = parts[3]
    if status_code not in STATUS_CODES:
        await callback.answer()
        return

    before_update = await get_parcel_with_user(parcel_id)
    if before_update is None:
        if callback.message is not None:
            await callback.message.edit_text("Ин трек-код ёфт нашуд.")
        await callback.answer()
        return

    parcel = await update_parcel_status(parcel_id, status_code)
    if parcel is None:
        if callback.message is not None:
            await callback.message.edit_text("Ин трек-код ёфт нашуд.")
        await callback.answer()
        return

    notified = False
    if (
        status_code == STATUS_ARRIVED_DESTINATION
        and before_update.arrival_notified_at is None
    ):
        bot = callback.message.bot if callback.message is not None else callback.bot
        notified = await notify_arrival_destination(bot, before_update.user, parcel)
        if notified:
            await mark_arrival_notified(parcel.id)
            parcel = await get_parcel_with_user(parcel.id) or parcel

    if (
        status_code == STATUS_RECEIVED
        and before_update.status_code != STATUS_RECEIVED
        and parcel.user.telegram_id
    ):
        bot = callback.message.bot if callback.message is not None else callback.bot
        if before_update.user.language == "ru":
            text = (
                "✅ <b>Ваш груз получен</b>\n\n"
                "<blockquote>"
                "Вы получили товар со склада.\n"
                "🤝 Спасибо за доверие к Akcorgo!"
                "</blockquote>"
            )
        else:
            text = (
                "✅ <b>Бори шумо супорида шуд</b>\n\n"
                "<blockquote>"
                "Шумо товарро аз склад қабул кардед.\n"
                "🤝 Ташаккур барои боварӣ ба Akcorgo!"
                "</blockquote>"
            )

        try:
            from services.settings import get_setting
            image_id = await get_setting("status_image_received_file_id", "")
            if not image_id:
                image_id = await get_setting("status_image_file_id", "")

            if image_id:
                await bot.send_photo(
                    chat_id=parcel.user.telegram_id,
                    photo=image_id,
                    caption=text,
                )
            else:
                await bot.send_message(
                    chat_id=parcel.user.telegram_id,
                    text=text,
                )
            notified = True
        except Exception:
            notified = False

    text = _format_parcel(parcel) + "\n\nСтатус нав шуд."
    if status_code in {STATUS_ARRIVED_DESTINATION, STATUS_RECEIVED} and notified:
        text += "\nБа мизоҷ хабар фиристода шуд."

    if callback.message is not None:
        await _safe_edit_text(
            callback.message,
            text,
            reply_markup=_status_keyboard(parcel),
        )
    await callback.answer()


@router.callback_query(F.data == "admin_status:lists")
async def show_admin_status_lists(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    if callback.message is not None:
        await callback.message.edit_text(
            "📦 Рӯйхати статусҳо",
            reply_markup=_status_lists_keyboard(),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_status:page:"))
async def show_admin_status_page(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    parts = callback.data.split(":")
    if len(parts) != 4 or parts[2] not in STATUS_CODES:
        await callback.answer()
        return

    try:
        page = int(parts[3])
    except ValueError:
        await callback.answer()
        return

    await _send_status_page(callback, parts[2], page)


@router.callback_query(F.data.startswith("admin_status:view:"))
async def view_admin_status_parcel(callback: CallbackQuery) -> None:
    if not _is_admin_callback(callback):
        await callback.answer()
        return

    try:
        parcel_id = int(callback.data.rsplit(":", 1)[1])
    except ValueError:
        await callback.answer()
        return

    parcel = await get_parcel_with_user(parcel_id)
    if parcel is None:
        if callback.message is not None:
            await callback.message.edit_text("Ин трек-код ёфт нашуд.")
        await callback.answer()
        return

    if callback.message is not None:
        await _safe_edit_text(
            callback.message,
            _format_parcel(parcel),
            reply_markup=_status_keyboard(parcel),
        )
    await callback.answer()


async def _admin_send_parcels_by_status(message, status_code: str, title: str):
    if not _is_admin_message(message):
        return

    await _send_status_page(message, status_code, 0)


@router.message(F.text.in_({ADMIN_CHINA_RECEIVED_LABEL, "Қабулшудаҳо"}))
async def admin_china_received_list(message):
    await _admin_send_parcels_by_status(
        message=message,
        status_code="china_received",
        title=ADMIN_CHINA_RECEIVED_LABEL,
    )


@router.message(F.text.in_({ADMIN_ON_THE_WAY_LABEL, "Дар роҳ"}))
async def admin_on_the_way_list(message):
    await _admin_send_parcels_by_status(
        message=message,
        status_code="on_the_way",
        title=ADMIN_ON_THE_WAY_LABEL,
    )


@router.message(F.text.in_({ADMIN_ARRIVED_LABEL, "Расидаҳо"}))
async def admin_arrived_list(message):
    await _admin_send_parcels_by_status(
        message=message,
        status_code="arrived_destination",
        title=ADMIN_ARRIVED_LABEL,
    )
