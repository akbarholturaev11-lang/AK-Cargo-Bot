from datetime import date, datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from handlers.user_menu import get_current_user
from keyboards.inline_user import parcel_not_found_keyboard, user_parcel_actions_keyboard
from services.normalizer import normalize_track_code
from services.parcels import get_parcel_by_normalized_track_code
from services.status_media import get_status_image_file_id
from services.settings import get_setting
from services.users import get_user_by_telegram_id
from texts import ru, tj
from texts.status import format_status
from utils.constants import LANG_RU, LANG_TJ, STATUS_ARRIVED_DESTINATION
from utils.validators import is_admin


router = Router(name="parcel_search")


class ParcelSearchStates(StatesGroup):
    waiting_for_track_code = State()


SEARCH_MENU_LABELS = {tj.MENU_SEARCH_PARCEL, ru.MENU_SEARCH_PARCEL}
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


def _is_user_search_button(message: Message) -> bool:
    if message.text not in SEARCH_MENU_LABELS:
        return False
    if message.text == tj.MENU_SEARCH_PARCEL and message.from_user is not None:
        return not is_admin(message.from_user.id)
    return True


async def _delivery_days(lang: str) -> str:
    key = "delivery_days_ru" if lang == LANG_RU else "delivery_days_tj"
    default = "18–25 дней" if lang == LANG_RU else "18–25 рӯз"
    return await get_setting(key, default) or default


async def _format_parcel_found(parcel, lang: str) -> str:
    texts = _texts(lang)
    return texts.PARCEL_FOUND.format(
        track_code=parcel.track_code,
        dynamic_status=format_status(
            parcel.status_code,
            parcel.destination_city,
            lang,
        ),
        destination_city=parcel.destination_city,
        received_china_at=_format_date(parcel.received_china_at),
        delivery_days=await _delivery_days(lang),
    )


async def _send_status_message(
    message: Message,
    parcel,
    text: str,
    *,
    lang: str,
    include_delivery_actions: bool,
) -> None:
    image_file_id = await get_status_image_file_id(parcel.status_code)
    keyboard = user_parcel_actions_keyboard(
        lang,
        parcel.id,
        include_delivery_actions=include_delivery_actions,
    )

    if image_file_id:
        await message.answer_photo(
            photo=image_file_id,
            caption=text,
            reply_markup=keyboard,
        )
        return

    await message.answer(text, reply_markup=keyboard)


@router.message(_is_user_search_button)
async def start_parcel_search(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    await state.set_state(ParcelSearchStates.waiting_for_track_code)
    await message.answer(_texts(user.language).ASK_TRACK_CODE)


@router.callback_query(F.data == "parcel_search:again")
async def retry_parcel_search(callback: CallbackQuery, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None or callback.message is None:
        await callback.answer()
        return

    await state.set_state(ParcelSearchStates.waiting_for_track_code)
    await callback.message.answer(_texts(user.language).ASK_TRACK_CODE)
    await callback.answer()


@router.message(ParcelSearchStates.waiting_for_track_code, F.text)
async def search_parcel(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    if user is None:
        await state.clear()
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    texts = _texts(user.language)
    normalized_track_code = normalize_track_code(message.text)
    parcel = await get_parcel_by_normalized_track_code(normalized_track_code)
    await state.clear()

    if parcel is None:
        await message.answer(
            texts.PARCEL_NOT_FOUND,
            reply_markup=parcel_not_found_keyboard(user.language),
        )
        return

    await _send_status_message(
        message,
        parcel,
        await _format_parcel_found(parcel, user.language),
        lang=user.language,
        include_delivery_actions=(
            parcel.user_id == user.id
            and parcel.status_code == STATUS_ARRIVED_DESTINATION
        ),
    )


@router.message(ParcelSearchStates.waiting_for_track_code)
async def search_parcel_invalid(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    lang = user.language if user is not None else LANG_TJ
    await message.answer(_texts(lang).ASK_TRACK_CODE)
