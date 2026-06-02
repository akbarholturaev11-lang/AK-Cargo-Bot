from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.inline_user import language_keyboard
from keyboards.reply import user_main_menu
from services.settings import DEFAULT_SETTINGS, get_many_settings
from services.users import get_user_by_telegram_id
from states.auth_states import AuthStates
from utils.constants import LANG_RU


WELCOME_SETTING_KEYS = {
    "welcome_image_file_id": DEFAULT_SETTINGS["welcome_image_file_id"],
    "welcome_text_tj": DEFAULT_SETTINGS["welcome_text_tj"],
    "welcome_text_ru": DEFAULT_SETTINGS["welcome_text_ru"],
}


router = Router(name="start")


def _welcome_text_key(message: Message) -> str:
    return "welcome_text_ru"


async def _send_welcome_screen(message: Message) -> None:
    values = await get_many_settings(WELCOME_SETTING_KEYS)
    image_file_id = values["welcome_image_file_id"].strip()
    welcome_text = (
    "🚚 <b>Добро пожаловать в Akcorgo!</b>\n\n"
    "<blockquote>"
    "Ваш карго-сервис из Китая в Таджикистан.\n"
    "Выберите язык, чтобы продолжить."
    "</blockquote>"
)
    keyboard = language_keyboard()

    if image_file_id:
        await message.answer_photo(
            photo=image_file_id,
            caption=welcome_text,
            reply_markup=keyboard,
        )
        return

    await message.answer(welcome_text, reply_markup=keyboard)


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext) -> None:
    if message.from_user is None:
        return

    user = await get_user_by_telegram_id(message.from_user.id)
    if user is not None:
        await state.clear()
        await message.answer(
            user.full_name,
            reply_markup=user_main_menu(user.language),
        )
        return

    await state.clear()
    await state.set_state(AuthStates.choosing_language)
    await _send_welcome_screen(message)
