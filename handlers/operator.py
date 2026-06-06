from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from handlers.user_menu import get_current_user
from services.settings import DEFAULT_SETTINGS, get_many_settings
from services.users import get_user_by_telegram_id
from texts import ru, tj
from utils.constants import LANG_RU, LANG_TJ

router = Router(name="operator")


TEXTS = {
    LANG_TJ: tj,
    LANG_RU: ru,
}

OPERATOR_MENU_LABELS = {tj.MENU_OPERATOR, ru.MENU_OPERATOR}
PRICES_MENU_LABELS = {tj.MENU_PRICES, ru.MENU_PRICES}


def _texts(lang: str):
    return TEXTS.get(lang, tj)


def _format_prices_text(template: str, values: dict[str, str], lang: str) -> str:
    return template.format(
        price_per_kg_tjs=values["price_per_kg_tjs"],
        price_per_cube_tjs=values["price_per_cube_tjs"],
        delivery_days_tj=values["delivery_days_tj"],
        delivery_days_ru=values["delivery_days_ru"],
        delivery_days=values["delivery_days_ru"] if lang == LANG_RU else values["delivery_days_tj"],
    )


@router.message(F.text.in_(OPERATOR_MENU_LABELS))
async def show_operator(message: Message) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    await _send_operator(message, user)


@router.callback_query(F.data == "operator:show")
async def show_operator_callback(callback: CallbackQuery) -> None:
    user = await get_user_by_telegram_id(callback.from_user.id)
    if user is None or callback.message is None:
        await callback.answer()
        return

    await _send_operator(callback.message, user)
    await callback.answer()


async def _send_operator(message: Message, user) -> None:
    texts = _texts(user.language)

    values = await get_many_settings(
        {
            "operator_username": DEFAULT_SETTINGS["operator_username"],
            "operator_phone": DEFAULT_SETTINGS["operator_phone"],
            "operator_whatsapp": DEFAULT_SETTINGS["operator_whatsapp"],
            "operator_work_time": DEFAULT_SETTINGS["operator_work_time"],
        },
    )

    username = (values["operator_username"] or "").strip().replace("@", "")
    phone = (values["operator_phone"] or "").strip()
    whatsapp = (values["operator_whatsapp"] or "").strip()
    work_time = (values["operator_work_time"] or "").strip() or "09:00–18:00"

    if not username and not phone and not whatsapp:
        await message.answer(texts.OPERATOR_NOT_SET)
        return

    if user.language == LANG_RU:
        text = (
            "☎️ <b>Оператор</b>\n\n"
            "<blockquote>"
            f"Время работы: <b>{work_time}</b>\n\n"
            "Пожалуйста, подробно опишите проблему:\n"
            "— трек-код или код клиента\n"
            "— что именно не работает\n"
            "— скриншот или фото, если нужно\n\n"
            "Оператор ответит после проверки сообщения."
            "</blockquote>"
        )
        button_text = "👨‍💻 Написать оператору"
    else:
        text = (
            "☎️ <b>Оператор</b>\n\n"
            "<blockquote>"
            f"Вақти кор: <b>{work_time}</b>\n\n"
            "Лутфан мушкили худро пурра нависед:\n"
            "— трек-код ё коди мизоҷ\n"
            "— чӣ мушкил шуд\n"
            "— скриншот ё фото, агар лозим бошад\n\n"
            "Оператор баъд аз дидани паёми шумо ҷавоб медиҳад."
            "</blockquote>"
        )
        button_text = "👨‍💻 Ба оператор нависед"

    extra_contacts = []
    if phone:
        extra_contacts.append(f"📞 <code>{phone}</code>")
    if whatsapp:
        extra_contacts.append(f"💬 WhatsApp: <code>{whatsapp}</code>")

    if extra_contacts:
        text += "\n\n" + "\n".join(extra_contacts)

    keyboard = None
    if username:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text=button_text,
                        url=f"https://t.me/{username}",
                    )
                ]
            ]
        )

    await message.answer(text, reply_markup=keyboard)


@router.message(F.text.in_(PRICES_MENU_LABELS))
async def show_prices(message: Message) -> None:
    user = await get_current_user(message)
    if user is None:
        await message.answer(tj.CHOOSE_LANGUAGE)
        return

    texts = _texts(user.language)
    values = await get_many_settings(
        {
            "price_per_kg_tjs": DEFAULT_SETTINGS["price_per_kg_tjs"],
            "price_per_cube_tjs": DEFAULT_SETTINGS["price_per_cube_tjs"],
            "delivery_days_tj": DEFAULT_SETTINGS["delivery_days_tj"],
            "delivery_days_ru": DEFAULT_SETTINGS["delivery_days_ru"],
            "prices_image_file_id": DEFAULT_SETTINGS["prices_image_file_id"],
            "prices_text_tj": DEFAULT_SETTINGS["prices_text_tj"],
            "prices_text_ru": DEFAULT_SETTINGS["prices_text_ru"],
        },
    )
    template_key = "prices_text_ru" if user.language == LANG_RU else "prices_text_tj"
    prices_text = _format_prices_text(
        values[template_key],
        values,
        user.language,
    )
    image_file_id = values["prices_image_file_id"].strip()
    if image_file_id:
        await message.answer_photo(photo=image_file_id, caption=prices_text)
        return

    await message.answer(prices_text)
