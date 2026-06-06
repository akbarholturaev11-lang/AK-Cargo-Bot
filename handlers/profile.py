from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from handlers.user_menu import PROFILE_MENU_LABELS, get_current_user
from keyboards.inline_user import (
    profile_edit_keyboard,
    profile_language_keyboard,
)
from keyboards.reply import auth_back_keyboard, auth_phone_keyboard, user_main_menu
from services.warehouses import get_active_tj_pickup_warehouses
from services.users import (
    city_display_name,
    get_user_by_telegram_id,
    normalize_contact_phone,
    normalize_manual_phone,
    update_user_city,
    update_user_full_name,
    update_user_language,
    update_user_phone,
)
from texts import ru, tj
from utils.constants import CITY_NAMES, LANG_RU, LANG_TJ, LANGUAGE_CODES


router = Router(name="profile")
BACK_LABELS = {tj.BACK, ru.BACK, "Бозгашт", "Назад"}


class ProfileStates(StatesGroup):
    edit_name = State()
    edit_phone = State()


TEXTS = {
    LANG_TJ: tj,
    LANG_RU: ru,
}


def _texts(lang: str):
    return TEXTS.get(lang, tj)


def _language_name(lang: str) -> str:
    if lang == LANG_RU:
        return "Русский"
    return "Тоҷикӣ"


def _cancelled_text(lang: str) -> str:
    return "Бекор карда шуд." if lang == LANG_TJ else "Отменено."


def _format_profile(user) -> str:
    texts = _texts(user.language)
    return texts.PROFILE.format(
        full_name=user.full_name,
        phone=user.phone,
        city=city_display_name(user.city, user.language),
        client_code=user.client_code,
        language=_language_name(user.language),
    )


def _is_own_contact(message: Message) -> bool:
    if message.contact is None or message.from_user is None:
        return False
    return message.contact.user_id == message.from_user.id


def _contact_phone(message: Message) -> str | None:
    if message.contact is None:
        return None
    return normalize_contact_phone(message.contact.phone_number)


def _manual_phone(message: Message) -> str | None:
    if message.text is None:
        return None
    return normalize_manual_phone(message.text)


async def _edit_profile_message(
    message: Message,
    state: FSMContext,
    user,
) -> None:
    data = await state.get_data()
    profile_message_id = data.get("profile_message_id")
    await state.clear()

    if profile_message_id is None:
        await message.answer(
            _format_profile(user),
            reply_markup=profile_edit_keyboard(user.language),
        )
        return

    try:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=profile_message_id,
            text=_format_profile(user),
            reply_markup=profile_edit_keyboard(user.language),
        )
    except TelegramBadRequest:
        await message.answer(
            _format_profile(user),
            reply_markup=profile_edit_keyboard(user.language),
        )


def _profile_pickup_cities_keyboard(warehouses, lang: str):
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    rows = []
    for warehouse in warehouses:
        label = warehouse.city_name_ru if lang == LANG_RU else warehouse.city_name_tj
        rows.append([
            InlineKeyboardButton(
                text=label,
                callback_data=f"profile:city:{warehouse.city_key}",
            )
        ])

    rows.append([
        InlineKeyboardButton(
            text="⬅️ Назад" if lang == LANG_RU else "⬅️ Бозгашт",
            callback_data="profile:back",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _answer_profile(callback: CallbackQuery, user) -> None:
    if callback.message is None:
        return

    await callback.message.edit_text(
        _format_profile(user),
        reply_markup=profile_edit_keyboard(user.language),
    )


@router.message(F.text.in_(PROFILE_MENU_LABELS))
async def show_profile_from_menu(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    await state.clear()
    await message.answer(
        _format_profile(user),
        reply_markup=profile_edit_keyboard(user.language),
    )


@router.callback_query(F.data == "profile:show")
async def show_profile_callback(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None:
        await callback.answer()
        return

    await _answer_profile(callback, user)
    await callback.answer()


@router.callback_query(F.data == "profile:edit_name")
async def edit_name_start(callback: CallbackQuery, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None or callback.message is None:
        await callback.answer()
        return

    texts = _texts(user.language)
    await state.set_state(ProfileStates.edit_name)
    await state.update_data(profile_message_id=callback.message.message_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        texts.ASK_FULL_NAME,
        reply_markup=auth_back_keyboard(user.language),
    )
    await callback.answer()


@router.message(ProfileStates.edit_name, F.text.in_(BACK_LABELS))
@router.message(ProfileStates.edit_phone, F.text.in_(BACK_LABELS))
async def profile_edit_back(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    if user is None:
        await state.clear()
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    await message.answer(_cancelled_text(user.language), reply_markup=ReplyKeyboardRemove())
    await _edit_profile_message(message, state, user)


@router.message(ProfileStates.edit_name, F.text)
async def edit_name_finish(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    if user is None:
        await state.clear()
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    user = await update_user_full_name(user.id, message.text)
    await _edit_profile_message(message, state, user)


@router.message(ProfileStates.edit_name)
async def edit_name_invalid(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    lang = user.language if user is not None else LANG_TJ
    await message.answer(_texts(lang).ASK_FULL_NAME)


@router.callback_query(F.data == "profile:edit_phone")
async def edit_phone_start(callback: CallbackQuery, state: FSMContext) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None or callback.message is None:
        await callback.answer()
        return

    texts = _texts(user.language)
    await state.set_state(ProfileStates.edit_phone)
    await state.update_data(profile_message_id=callback.message.message_id)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        texts.ASK_PHONE,
        reply_markup=auth_phone_keyboard(user.language),
    )
    await callback.answer()


@router.message(ProfileStates.edit_phone, F.contact)
async def edit_phone_contact_finish(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    if user is None:
        await state.clear()
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    texts = _texts(user.language)
    if not _is_own_contact(message):
        await message.answer(
            texts.INVALID_PHONE,
            reply_markup=auth_phone_keyboard(user.language),
        )
        return

    phone = _contact_phone(message)
    if phone is None:
        await message.answer(
            texts.INVALID_PHONE,
            reply_markup=auth_phone_keyboard(user.language),
        )
        return

    updated_user = await update_user_phone(user.id, phone)
    if updated_user is None:
        await message.answer(texts.PHONE_ALREADY_USED)
        return

    await message.answer(texts.PROFILE_UPDATED, reply_markup=ReplyKeyboardRemove())
    await _edit_profile_message(message, state, updated_user)


@router.message(ProfileStates.edit_phone, F.text)
async def edit_phone_manual_finish(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    if user is None:
        await state.clear()
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    texts = _texts(user.language)
    phone = _manual_phone(message)
    if phone is None:
        await message.answer(
            texts.INVALID_PHONE,
            reply_markup=auth_phone_keyboard(user.language),
        )
        return

    updated_user = await update_user_phone(user.id, phone)
    if updated_user is None:
        await message.answer(texts.PHONE_ALREADY_USED)
        return

    await message.answer(texts.PROFILE_UPDATED, reply_markup=ReplyKeyboardRemove())
    await _edit_profile_message(message, state, updated_user)


@router.message(ProfileStates.edit_phone)
async def edit_phone_invalid(message: Message, state: FSMContext) -> None:
    user = await get_current_user(message)
    lang = user.language if user is not None else LANG_TJ
    await message.answer(
        _texts(lang).INVALID_PHONE,
        reply_markup=auth_phone_keyboard(lang),
    )


@router.callback_query(F.data == "profile:edit_city")
async def edit_city_start(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None or callback.message is None:
        await callback.answer()
        return

    texts = _texts(user.language)
    warehouses = await get_active_tj_pickup_warehouses()

    if not warehouses:
        text = (
            "❌ <b>Ҳоло ягон филиал дастрас нест.</b>\n\n"
            "<blockquote>Лутфан ба оператор нависед.</blockquote>"
            if user.language == LANG_TJ
            else
            "❌ <b>Пока нет доступных филиалов.</b>\n\n"
            "<blockquote>Пожалуйста, напишите оператору.</blockquote>"
        )
        await callback.message.answer(text)
        await callback.answer()
        return

    await callback.message.edit_text(
        texts.ASK_CITY,
        reply_markup=_profile_pickup_cities_keyboard(warehouses, user.language),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("profile:city:"))
async def edit_city_finish(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None:
        await callback.answer()
        return

    city_key = callback.data.rsplit(":", 1)[1]
    warehouses = await get_active_tj_pickup_warehouses()
    allowed_city_keys = {warehouse.city_key for warehouse in warehouses}

    if city_key not in allowed_city_keys:
        alert_text = (
            "Ҳоло дар ин шаҳр филиал мавҷуд нест."
            if user.language == LANG_TJ
            else
            "Пока в этом городе филиал недоступен."
        )
        await callback.answer(alert_text, show_alert=True)
        return

    city_name = CITY_NAMES[city_key][LANG_TJ]
    user = await update_user_city(user.id, city_name)
    await _answer_profile(callback, user)
    await callback.answer()


@router.callback_query(F.data == "profile:edit_language")
async def edit_language_start(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None or callback.message is None:
        await callback.answer()
        return

    texts = _texts(user.language)
    await callback.message.edit_text(
        texts.CHOOSE_LANGUAGE,
        reply_markup=profile_language_keyboard(user.language),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("profile:language:"))
async def edit_language_finish(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None:
        await callback.answer()
        return

    lang = callback.data.rsplit(":", 1)[1]
    if lang not in LANGUAGE_CODES:
        await callback.answer()
        return

    user = await update_user_language(user.id, lang)
    await _answer_profile(callback, user)
    await callback.answer()


@router.callback_query(F.data == "profile:back")
async def profile_back(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None or callback.message is None:
        await callback.answer()
        return

    texts = _texts(user.language)
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        texts.PROFILE_BACK,
        reply_markup=user_main_menu(user.language),
    )
    await callback.answer()
